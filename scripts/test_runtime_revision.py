"""Focused TDD coverage for the Proposal-2 runtime revision contract."""

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile


SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from runtime_revision import (  # noqa: E402
    DOMAIN,
    RuntimeRevisionError,
    calculate_revision,
    check_manifest,
    check_package_binding,
    classify_durable_state,
    inventory_checkout,
    inventory_zip,
    manifest_for_checkout,
    policy_digest,
    write_manifest,
)


EMPTY_REVISION = "sha256:2d33a936115a451e4f077f46eb86826280294ea14ff05eddaca14879587abfb7"
SINGLE_FILE_REVISION = "sha256:948f7d328239b17b56b91403847801b460626f1a55880a8c6d57c2f4354ffb3a"


def entry(path, mode, data):
    """Use literals so the independently checked vectors cannot mirror code."""
    return {"path": path, "mode": mode, "data": data}


def write_zip(path, members):
    """Create an author-packager-like rootless ZIP from literal member facts."""
    with zipfile.ZipFile(path, "w") as archive:
        for name, data, unix_mode in members:
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = (unix_mode << 16)
            archive.writestr(info, data)


class RevisionAlgorithmTests(unittest.TestCase):
    def test_known_vectors_are_exact_hand_checked_literals(self):
        self.assertEqual(calculate_revision([]), EMPTY_REVISION)
        self.assertEqual(
            calculate_revision([entry("SKILL.md", "0644", b"hello\n")]),
            SINGLE_FILE_REVISION,
        )

    def test_bytes_path_and_normalized_mode_change_revision(self):
        base = calculate_revision([entry("SKILL.md", "0644", b"hello\n")])
        self.assertNotEqual(base, calculate_revision([entry("SKILL.md", "0644", b"hello!\n")]))
        self.assertNotEqual(base, calculate_revision([entry("skill.md", "0644", b"hello\n")]))
        self.assertNotEqual(base, calculate_revision([entry("SKILL.md", "0755", b"hello\n")]))

    def test_invalid_canonical_paths_and_duplicate_paths_are_rejected(self):
        invalid = ["", "/SKILL.md", "a\\b", "a\x00b", "a//b", "./a", "a/../b"]
        for path in invalid:
            with self.subTest(path=repr(path)):
                with self.assertRaises(RuntimeRevisionError):
                    calculate_revision([entry(path, "0644", b"x")])
        with self.assertRaises(RuntimeRevisionError):
            calculate_revision([entry("a", "0644", b"x"), entry("a", "0644", b"y")])

    def test_non_nfc_and_u64_overflow_are_rejected_before_hashing(self):
        with self.assertRaises(RuntimeRevisionError):
            calculate_revision([entry("e\u0301", "0644", b"x")])
        with self.assertRaisesRegex(RuntimeRevisionError, "path_not_utf8"):
            calculate_revision([entry("surrogate-\udcff", "0644", b"x")])
        with self.assertRaises(RuntimeRevisionError):
            calculate_revision([], file_count=(1 << 64))


class InventoryTests(unittest.TestCase):
    def test_checkout_is_cross_root_and_timestamp_stable(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            for root in (Path(first), Path(second)):
                (root / "nested").mkdir()
                (root / "SKILL.md").write_bytes(b"hello\n")
                executable = root / "nested" / "run"
                executable.write_bytes(b"#!/bin/sh\n")
                executable.chmod(0o755)
                os.utime(root / "SKILL.md", (100, 100))
            self.assertEqual(
                calculate_revision(inventory_checkout(Path(first))),
                calculate_revision(inventory_checkout(Path(second))),
            )

    def test_checkout_rejects_symlink_and_special_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "regular").write_bytes(b"x")
            link = root / "link"
            try:
                link.symlink_to(root / "regular")
            except (NotImplementedError, OSError) as exc:
                self.skipTest(str(exc))
            with self.assertRaises(RuntimeRevisionError):
                inventory_checkout(root)

    def test_checkout_rejects_invalid_filesystem_utf8_name(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "runtime"
            root.mkdir()
            raw_path = os.fsencode(root) + b"/invalid-\xff"
            try:
                descriptor = os.open(raw_path, os.O_WRONLY | os.O_CREAT, 0o644)
            except (NotImplementedError, OSError, TypeError) as exc:
                self.skipTest(f"raw-byte filename creation unavailable: {exc}")
            try:
                os.write(descriptor, b"x")
            finally:
                os.close(descriptor)
            try:
                names = [child.name for child in os.scandir(root)]
                if not any("\udcff" in name for name in names):
                    self.skipTest("scandir does not expose the raw-byte name through surrogateescape")
                with self.assertRaisesRegex(RuntimeRevisionError, "path_not_utf8"):
                    inventory_checkout(root)
            finally:
                try:
                    os.unlink(raw_path)
                except OSError:
                    pass

    def test_checkout_rejects_fifo_special_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "runtime"
            root.mkdir()
            fifo = root / "pipe"
            try:
                os.mkfifo(fifo)
            except (AttributeError, NotImplementedError, OSError) as exc:
                self.skipTest(str(exc))
            with self.assertRaisesRegex(RuntimeRevisionError, "checkout_not_regular"):
                inventory_checkout(root)

    def test_checkout_rejects_identity_drift_before_read_through_controlled_seam(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "runtime"
            root.mkdir()
            target = root / "SKILL.md"
            target.write_bytes(b"before\n")
            replacement = Path(directory) / "replacement"
            replacement.write_bytes(b"after replacement\n")

            def replace_after_lstat(path):
                if Path(path) == target:
                    os.replace(replacement, target)

            with self.assertRaisesRegex(RuntimeRevisionError, "checkout_drift"):
                inventory_checkout(root, before_read=replace_after_lstat)

    def test_rootless_zip_inventory_matches_checkout_modes_and_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "runtime"
            root.mkdir()
            (root / "SKILL.md").write_bytes(b"hello\n")
            executable = root / "run"
            executable.write_bytes(b"#!/bin/sh\n")
            executable.chmod(0o755)
            archive = Path(directory) / "runtime.zip"
            write_zip(archive, [("SKILL.md", b"hello\n", 0o100644), ("run", b"#!/bin/sh\n", 0o100755)])
            checkout = inventory_checkout(root)
            archived = inventory_zip(archive, {item["path"] for item in checkout})
            self.assertEqual(calculate_revision(checkout), calculate_revision(archived))

    def test_zip_rejects_directory_extra_root_noncanonical_symlink_and_extra_members(self):
        cases = [
            [("folder/", b"", 0o40755)],
            [("self-iteration/SKILL.md", b"x", 0o100644)],
            [("a//b", b"x", 0o100644)],
            [("link", b"target", 0o120777)],
            [("SKILL.md", b"x", 0o100644), ("extra", b"x", 0o100644)],
        ]
        with tempfile.TemporaryDirectory() as directory:
            for index, members in enumerate(cases):
                with self.subTest(index=index):
                    archive = Path(directory) / f"bad-{index}.zip"
                    write_zip(archive, members)
                    with self.assertRaises(RuntimeRevisionError):
                        inventory_zip(archive, {"SKILL.md"})

    def test_zip_rejects_missing_expected_member(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "missing.zip"
            write_zip(archive, [("SKILL.md", b"x", 0o100644)])
            with self.assertRaisesRegex(RuntimeRevisionError, "archive_inventory_mismatch"):
                inventory_zip(archive, {"SKILL.md", "agents/openai.yaml"})

    def test_zip_rejects_duplicate_member(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "duplicate.zip"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                write_zip(archive, [("SKILL.md", b"first", 0o100644), ("SKILL.md", b"second", 0o100644)])
            with self.assertRaisesRegex(RuntimeRevisionError, "archive_duplicate_path"):
                inventory_zip(archive, {"SKILL.md"})

    def test_zip_rejects_non_symlink_special_member(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "special.zip"
            write_zip(archive, [("pipe", b"", stat.S_IFIFO | 0o644)])
            with self.assertRaisesRegex(RuntimeRevisionError, "archive_special_entry"):
                inventory_zip(archive, {"pipe"})


class ManifestAndBindingTests(unittest.TestCase):
    def _runtime(self, directory):
        root = Path(directory) / "runtime"
        root.mkdir()
        (root / "SKILL.md").write_bytes(b"hello\n")
        return root

    def test_manifest_round_trip_and_stale_or_malformed_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._runtime(directory)
            manifest = Path(directory) / "manifest.json"
            write_manifest(root, manifest, "self-iteration")
            self.assertEqual(check_manifest(root, manifest, "self-iteration"), [])
            (root / "SKILL.md").write_bytes(b"changed\n")
            self.assertIn("manifest_runtime_revision_mismatch", check_manifest(root, manifest, "self-iteration"))
            manifest.write_text("[]", encoding="utf-8")
            self.assertIn("manifest_not_object", check_manifest(root, manifest, "self-iteration"))

    def test_write_is_atomic_when_snapshot_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._runtime(directory)
            manifest = Path(directory) / "manifest.json"
            manifest.write_text('{"previous":true}\n', encoding="utf-8")
            (root / "bad").symlink_to(root / "SKILL.md")
            with self.assertRaises(RuntimeRevisionError):
                write_manifest(root, manifest, "self-iteration")
            self.assertEqual(manifest.read_text(encoding="utf-8"), '{"previous":true}\n')

    def test_atomic_manifest_write_preserves_repository_text_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._runtime(directory)
            manifest = Path(directory) / "manifest.json"
            write_manifest(root, manifest, "self-iteration")
            self.assertEqual(stat.S_IMODE(manifest.stat().st_mode), 0o644)

    def test_write_rejects_missing_parent_without_creating_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._runtime(directory)
            parent = Path(directory) / "missing-parent"
            manifest = parent / "runtime-manifest.json"
            with self.assertRaisesRegex(RuntimeRevisionError, "manifest_parent_missing"):
                write_manifest(root, manifest, "self-iteration")
            self.assertFalse(parent.exists())
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPTS / "runtime_revision.py"),
                    "write",
                    "--runtime-root",
                    str(root),
                    "--manifest",
                    str(manifest),
                ],
                cwd=SCRIPTS.parent,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 1)
            self.assertEqual(
                json.loads(completed.stdout),
                {"findings": ["manifest_parent_missing"], "ok": False},
            )
            self.assertFalse(parent.exists())

    def test_policy_digest_is_separate_from_runtime_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._runtime(directory)
            before = manifest_for_checkout(root, "self-iteration")["runtime_revision"]
            policy = Path(directory) / "release-policy.json"
            policy.write_bytes(b'{"policy":1}\n')
            first = policy_digest(policy)
            policy.write_bytes(b'{"policy":2}\n')
            self.assertNotEqual(first, policy_digest(policy))
            self.assertEqual(before, manifest_for_checkout(root, "self-iteration")["runtime_revision"])

    def test_package_checks_keep_archive_receipt_and_policy_failures_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._runtime(directory)
            manifest_path = Path(directory) / "manifest.json"
            write_manifest(root, manifest_path, "self-iteration")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            archive = Path(directory) / "runtime.zip"
            write_zip(archive, [("SKILL.md", b"wrong\n", 0o100644)])
            policy = Path(directory) / "policy.json"
            policy.write_bytes(b"policy\n")
            receipt = Path(directory) / "receipt.json"
            receipt.write_text(json.dumps({
                "schema_version": 3,
                "skill_name": "self-iteration",
                "archive_sha256": "0" * 64,
                "archive_size": 1,
                "release_policy_sha256": "0" * 64,
                "inventory": ["SKILL.md"],
                "files": [{"path": "SKILL.md", "sha256": "0" * 64, "size": 1, "mode": "0644"}],
                "validation": {},
            }), encoding="utf-8")
            findings = check_package_binding(manifest, archive, receipt, policy)
            self.assertIn("archive_runtime_revision_mismatch", findings)
            self.assertIn("receipt_archive_sha256_mismatch", findings)
            self.assertIn("receipt_file_facts_mismatch", findings)
            self.assertIn("receipt_policy_digest_mismatch", findings)

    def test_receipt_without_runtime_revision_is_valid_when_facts_match(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._runtime(directory)
            manifest = manifest_for_checkout(root, "self-iteration")
            archive = Path(directory) / "runtime.zip"
            write_zip(archive, [("SKILL.md", b"hello\n", 0o100644)])
            policy = Path(directory) / "policy.json"
            policy.write_bytes(b"policy\n")
            raw_archive = archive.read_bytes()
            receipt = Path(directory) / "receipt.json"
            receipt.write_text(json.dumps({
                "schema_version": 3,
                "skill_name": "self-iteration",
                "archive_sha256": hashlib.sha256(raw_archive).hexdigest(),
                "archive_size": len(raw_archive),
                "release_policy_sha256": policy_digest(policy),
                "inventory": ["SKILL.md"],
                "files": [{"path": "SKILL.md", "sha256": hashlib.sha256(b"hello\n").hexdigest(), "size": 6, "mode": "0644"}],
                "validation": {},
            }), encoding="utf-8")
            self.assertEqual(check_package_binding(manifest, archive, receipt, policy), [])

    def test_durable_legacy_state_is_unknown_but_safe_revalidated_resume_is_allowed(self):
        legacy = {"Phase": "IMPLEMENT"}
        classified = classify_durable_state(legacy, revalidated=True)
        self.assertEqual(classified["source"], "unknown")
        self.assertFalse(classified["provenance_established"])
        self.assertTrue(classified["safe_resume_allowed"])

    def test_cli_rejects_partial_optional_package_group_with_json_finding(self):
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "runtime_revision.py"), "check-bindings", "--manifest", "missing.json", "--archive", "only.zip"],
            cwd=SCRIPTS.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(json.loads(completed.stdout)["findings"], ["package_binding_group_incomplete"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
