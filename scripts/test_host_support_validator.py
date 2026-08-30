"""Focused fixtures for the host-support validator's evidence contract."""

from __future__ import annotations

import json
import errno
import os
from pathlib import Path
import tempfile
from typing import Optional
import unittest
from unittest.mock import patch

import validate_repo as validator


EXPECTED_PUBLIC_STATUSES = {
    "unverified": "targeted / unverified",
    "unavailable": "targeted / unverified",
    "failed": "targeted / failed",
    "verified": "verified / compatible",
}
HOST_SLUGS = {
    "Codex Desktop/CLI": "codex-desktop-cli",
    "Claude Code": "claude-code",
    "Gemini CLI": "gemini-cli",
}
EXPECTED_LIFECYCLE_STEP_IDS = (
    "install",
    "discovery",
    "entrypoint",
    "behavior",
    "refusal",
    "collision",
    "upgrade",
    "uninstall",
)
CURRENT_RUNTIME_REVISION = "sha256:531e531dda519c66add72150514fe36d2000eaa82c270e0de05d87abdb725978"
RAW_ROOT = Path("evaluation/evidence/hosts/raw")
INERT_RAW_TEXT = b"inert fixture transcript\n"
INERT_RAW_BYTES = 25
INERT_RAW_SHA256 = "4fec33d5d6d70b77d6b9f01891897349450cfbc06714fcbe3a904b95ce61b40e"


def version_for(status: str) -> str:
    return "fixture-cli 1.2.3" if status != "unavailable" else "unavailable — command not found"


def raw_record(host: str, step_id: str, channel: str) -> dict[str, object]:
    return {
        "path": str(RAW_ROOT / f"{HOST_SLUGS[host]}-{step_id}-{channel}.log"),
        "status": "captured",
        "sha256": INERT_RAW_SHA256,
        "bytes": INERT_RAW_BYTES,
        "reason": None,
    }


def evidence_payload(host: str, version: str, status: str) -> dict[str, object]:
    steps = []
    for step_id in EXPECTED_LIFECYCLE_STEP_IDS:
        result = "failed" if status == "failed" and step_id == "collision" else "passed"
        steps.append(
            {
                "id": step_id,
                "command": {
                    "argv": ["fixture-host", "lifecycle", step_id],
                    "cwd": "/tmp/host-support-fixture",
                    "exit_code": 0,
                },
                "result": result,
                "postcondition": {
                    "check_argv": ["fixture-check", step_id],
                    "expected": f"{step_id} condition exists for {host}.",
                    "observed": f"{step_id} condition exists for {host}.",
                    "passed": True,
                },
                "raw_evidence": {
                    "command_output": raw_record(host, step_id, "command"),
                    "postcondition_readback": raw_record(host, step_id, "readback"),
                },
            }
        )
    return {
        "schema_version": 2,
        "host": host,
        "observed_version": version,
        "independent_reviewer": "fixture independent reviewer",
        "independent": True,
        "overall_status": status,
        "runtime_revision": CURRENT_RUNTIME_REVISION,
        "lifecycle_steps": steps,
    }


def write_raw_evidence(root: Path, payload: dict[str, object]) -> None:
    for step in payload["lifecycle_steps"]:
        for record in step["raw_evidence"].values():
            if record["status"] not in {"captured", "redacted"}:
                continue
            path = root / record["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(INERT_RAW_TEXT)


def build_record(host: str, status: str, has_artifact: bool = False) -> str:
    availability = "unavailable" if status == "unavailable" else "available"
    version = version_for(status)
    lifecycle = {
        "unverified": "Lifecycle is pending and was not run; only incomplete L0 evidence exists.",
        "unavailable": "Not run because the executable is unavailable.",
        "failed": "Attempted independent lifecycle explicitly failed at collision handling.",
        "verified": "Independent lifecycle evidence completed in an isolated environment.",
    }[status]
    artifact = (
        f"[fixture evidence](evaluation/evidence/hosts/{HOST_SLUGS[host]}.json)"
        if has_artifact
        else "None produced."
    )
    return f"""## {host}

- **Target host:** {host}.
- **Observed availability:** {availability}
- **Observed version:** {version}
- **Discovery and loading path:** Fixture discovery path.
- **Canonical action mapping and degraded capabilities:** Fixture mapping.
- **Install scope and owned files:** Fixture user scope.
- **Authentication and approval behavior:** Fixture approval boundary.
- **Clean acceptance test:** Fixture acceptance test.
- **Upgrade and uninstall:** Fixture lifecycle plan.
- **Evidence status:** {status}.
- **Evidence artifact:** {artifact}
- **Lifecycle evidence:** {lifecycle}
- **Limitations:** Fixture limitation.
"""


def build_document(statuses: dict[str, str], artifact_statuses: set[str]) -> str:
    records = "\n".join(
        build_record(host, statuses[host], statuses[host] in artifact_statuses)
        for host in validator.HOST_SUPPORT_TARGETS
    )
    return f"# Fixture\n\n## Evidence boundary\n\nFixture boundary.\n\n{records}"


def build_readme(statuses: dict[str, str]) -> str:
    rows = "\n".join(
        f"| {host} | `{EXPECTED_PUBLIC_STATUSES[statuses[host]]}` | Fixture. |"
        for host in validator.HOST_SUPPORT_TARGETS
    )
    return f"""# Fixture

[host-support record](docs/host-support.md)

| Host | Status | Evidence |
| --- | --- | --- |
{rows}
"""


class HostSupportValidatorTests(unittest.TestCase):
    def assert_real_descriptors_closed(self, real_fstat, descriptors: list[int]) -> None:
        for descriptor in descriptors:
            with self.assertRaises(OSError) as raised:
                real_fstat(descriptor)
            self.assertEqual(raised.exception.errno, errno.EBADF)

    def validate_fixture(
        self, support_text: str, readme: str, root: Path
    ) -> list[str]:
        errors: list[str] = []
        validator.validate_host_support_document(support_text, readme, root, errors)
        return errors

    def make_fixture(
        self, statuses: dict[str, str], artifact_statuses: Optional[set[str]] = None
    ) -> tuple[tempfile.TemporaryDirectory[str], Path, str, str]:
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        evidence = root / "evaluation" / "evidence" / "hosts"
        evidence.mkdir(parents=True)
        artifact_statuses = artifact_statuses or {"failed", "verified"}
        for host, status in statuses.items():
            if status in artifact_statuses:
                path = evidence / f"{HOST_SLUGS[host]}.json"
                payload = evidence_payload(host, version_for(status), status)
                write_raw_evidence(root, payload)
                path.write_text(json.dumps(payload), encoding="utf-8")
        return directory, root, build_document(statuses, artifact_statuses), build_readme(statuses)

    def current_statuses(self) -> dict[str, str]:
        return {
            "Codex Desktop/CLI": "unverified",
            "Claude Code": "unavailable",
            "Gemini CLI": "unavailable",
        }

    def test_public_status_mapping_is_literal_contract(self) -> None:
        self.assertEqual(validator.HOST_PUBLIC_STATUSES, EXPECTED_PUBLIC_STATUSES)

    def test_lifecycle_step_order_is_literal_contract(self) -> None:
        self.assertEqual(validator.HOST_LIFECYCLE_STEP_IDS, EXPECTED_LIFECYCLE_STEP_IDS)

    def test_fenced_and_unclosed_comment_document_decoys_fail(self) -> None:
        directory, root, document, readme = self.make_fixture(self.current_statuses())
        with directory:
            fenced = "# Fixture\n\n## Evidence boundary\n\n```markdown\n" + document + "\n```\n"
            unclosed = "# Fixture\n\n## Evidence boundary\n\n<!--\n" + document
            for candidate in (fenced, unclosed):
                errors = self.validate_fixture(candidate, readme, root)
                self.assertTrue(any("exactly one ## Codex" in error for error in errors), errors)

    def test_duplicate_real_field_and_section_fail(self) -> None:
        directory, root, document, readme = self.make_fixture(self.current_statuses())
        with directory:
            duplicate_field = document.replace(
                "- **Target host:** Codex Desktop/CLI.",
                "- **Target host:** Codex Desktop/CLI.\n- **Target host:** Codex Desktop/CLI.",
                1,
            )
            duplicate_section = document + build_record("Codex Desktop/CLI", "unverified")
            errors = self.validate_fixture(duplicate_field, readme, root)
            self.assertTrue(any("fields do not match" in error for error in errors), errors)
            errors = self.validate_fixture(duplicate_section, readme, root)
            self.assertTrue(any("exactly one ## Codex" in error for error in errors), errors)

    def test_multiline_second_line_qualifier_is_used(self) -> None:
        directory, root, document, readme = self.make_fixture(self.current_statuses())
        with directory:
            document = document.replace(
                "- **Lifecycle evidence:** Lifecycle is pending and was not run; only incomplete L0 evidence exists.",
                "- **Lifecycle evidence:** Lifecycle is pending a clean acceptance test.\n  It was not run and remains incomplete.",
                1,
            )
            self.assertEqual(self.validate_fixture(document, readme, root), [])

    def test_readme_fenced_unclosed_or_orphan_rows_fail(self) -> None:
        directory, root, document, readme = self.make_fixture(self.current_statuses())
        with directory:
            table = readme[readme.index("| Host |") :]
            candidates = (
                "# Fixture\n\n[host-support record](docs/host-support.md)\n\n```markdown\n" + table + "```\n",
                "# Fixture\n\n[host-support record](docs/host-support.md)\n\n<!--\n" + table,
                "# Fixture\n\n[host-support record](docs/host-support.md)\n\n" + "\n".join(table.splitlines()[2:]),
            )
            for candidate in candidates:
                errors = self.validate_fixture(document, candidate, root)
                self.assertTrue(any("exactly one visible host-status row" in error for error in errors), errors)

    def test_readme_missing_and_overclaiming_fail(self) -> None:
        directory, root, document, readme = self.make_fixture(self.current_statuses())
        with directory:
            missing = self.validate_fixture(document, "# Fixture\n", root)
            overclaim = self.validate_fixture(
                document,
                readme.replace("`targeted / unverified`", "`verified / compatible`", 1),
                root,
            )
        self.assertTrue(any("visibly link" in error for error in missing), missing)
        self.assertTrue(any("must match unverified" in error for error in overclaim), overclaim)

    def test_all_four_statuses_accept_schema_bound_evidence(self) -> None:
        for status in ("unverified", "unavailable", "failed", "verified"):
            with self.subTest(status=status):
                statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
                statuses["Codex Desktop/CLI"] = status
                directory, root, document, readme = self.make_fixture(statuses)
                with directory:
                    self.assertEqual(self.validate_fixture(document, readme, root), [])

    def test_availability_version_and_status_mismatches_fail(self) -> None:
        directory, root, document, readme = self.make_fixture(self.current_statuses())
        with directory:
            candidates = (
                document.replace("- **Observed availability:** available", "- **Observed availability:** available-ish", 1),
                document.replace("- **Observed version:** fixture-cli 1.2.3", "- **Observed version:** unknown — probe date 2026.08.30", 1),
                document.replace("- **Observed availability:** available", "- **Observed availability:** unavailable", 1),
            )
            for candidate in candidates:
                errors = self.validate_fixture(candidate, readme, root)
                self.assertTrue(errors, errors)

    def test_available_version_requires_a_concrete_version_shape(self) -> None:
        directory, root, document, readme = self.make_fixture(self.current_statuses())
        with directory:
            v_prefixed = document.replace("fixture-cli 1.2.3", "v1.2.3", 1)
            self.assertEqual(self.validate_fixture(v_prefixed, readme, root), [])
            for bad_version in (
                "pending manual probe",
                "manual 2026.08.30",
                "2026.08.30",
                "version not checked yet",
            ):
                errors = self.validate_fixture(
                    document.replace("fixture-cli 1.2.3", bad_version, 1), readme, root
                )
                self.assertTrue(any("concrete observed version" in error for error in errors), errors)

    def test_failed_lifecycle_must_say_failed(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "failed"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            document = document.replace(
                "Attempted independent lifecycle explicitly failed at collision handling.",
                "Attempted independent lifecycle completed at collision handling.",
            )
            errors = self.validate_fixture(document, readme, root)
        self.assertTrue(any("attempted lifecycle failure" in error for error in errors), errors)

    def test_artifact_path_identity_and_independence_failures(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "verified"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            artifact = root / "evaluation" / "evidence" / "hosts" / "codex-desktop-cli.json"
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            payload["independent"] = False
            artifact.write_text(json.dumps(payload), encoding="utf-8")
            errors = self.validate_fixture(document, readme, root)
            self.assertTrue(any("independent must be true" in error for error in errors), errors)

            payload["independent"] = True
            payload["independent_reviewer"] = ""
            artifact.write_text(json.dumps(payload), encoding="utf-8")
            errors = self.validate_fixture(document, readme, root)
            self.assertTrue(any("non-empty independent_reviewer" in error for error in errors), errors)

            for bad_path in (
                "[bad](evidence.md)",
                "[bad](self-iteration/evidence.json)",
                "[bad](/tmp/evidence.json)",
            ):
                errors = self.validate_fixture(
                    document.replace(
                        "[fixture evidence](evaluation/evidence/hosts/codex-desktop-cli.json)", bad_path,
                    ),
                    readme,
                    root,
                )
                self.assertTrue(any("host-scoped JSON" in error for error in errors), errors)

    def test_artifact_host_version_and_summary_binding_fail(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "verified"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            artifact = root / "evaluation" / "evidence" / "hosts" / "codex-desktop-cli.json"
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            payload["host"] = "Wrong Host"
            payload["observed_version"] = "wrong-version"
            artifact.write_text(json.dumps(payload), encoding="utf-8")
            errors = self.validate_fixture(document, readme, root)
            self.assertTrue(any("exact host" in error for error in errors), errors)
            self.assertTrue(any("observed version" in error for error in errors), errors)

            artifact.write_text(json.dumps({"summary": "install discovery entrypoint behavior refusal collision upgrade uninstall"}), encoding="utf-8")
            errors = self.validate_fixture(document, readme, root)
            self.assertTrue(any("exact schema" in error for error in errors), errors)

    def test_lifecycle_schema_and_semantic_negative_cases(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "verified"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            artifact = root / "evaluation" / "evidence" / "hosts" / "codex-desktop-cli.json"

            def errors_for(mutator) -> list[str]:
                payload = evidence_payload("Codex Desktop/CLI", "fixture-cli 1.2.3", "verified")
                mutator(payload)
                artifact.write_text(json.dumps(payload), encoding="utf-8")
                return self.validate_fixture(document, readme, root)

            cases = (
                (
                    lambda payload: payload.pop("host"),
                    "exact schema",
                ),
                (
                    lambda payload: payload.__setitem__("extra", True),
                    "exact schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0].pop("command"),
                    "lifecycle step schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0].__setitem__("extra", True),
                    "lifecycle step schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"].__setitem__(
                        0,
                        {**payload["lifecycle_steps"][0], "command": "Exact command was recorded."},
                    ),
                    "command schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0]["command"].__setitem__("argv", []),
                    "command schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0]["command"].__setitem__(
                        "argv", ["Exact command was recorded."]
                    ),
                    "command schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0]["command"].pop("cwd"),
                    "command schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0]["command"].__setitem__("exit_code", "0"),
                    "command schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0]["command"].__setitem__("exit_code", True),
                    "command schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0]["command"].__setitem__("exit_code", False),
                    "command schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0]["command"].__setitem__("extra", True),
                    "command schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0].__setitem__("postcondition", {"passed": True}),
                    "postcondition schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0]["postcondition"].__setitem__("extra", True),
                    "postcondition schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0]["postcondition"].__setitem__("passed", "true"),
                    "postcondition schema",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0].__setitem__("result", "skipped"),
                    "lifecycle result",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0].__setitem__("result", True),
                    "lifecycle result",
                ),
                (
                    lambda payload: payload["lifecycle_steps"].pop(),
                    "exactly eight",
                ),
                (
                    lambda payload: payload["lifecycle_steps"].append(payload["lifecycle_steps"][0]),
                    "exactly eight",
                ),
                (
                    lambda payload: payload["lifecycle_steps"].reverse(),
                    "IDs/order",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][1].__setitem__("id", "install"),
                    "IDs/order",
                ),
                (
                    lambda payload: payload.__setitem__("overall_status", "failed"),
                    "overall_status",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0]["command"].__setitem__("exit_code", 1),
                    "passed results, zero exits",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0]["postcondition"].__setitem__("passed", False),
                    "passed results, zero exits",
                ),
                (
                    lambda payload: payload["lifecycle_steps"][0].__setitem__("result", "failed"),
                    "passed results, zero exits",
                ),
            )
            for mutator, expected in cases:
                errors = errors_for(mutator)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_failed_artifact_requires_a_failed_step(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "failed"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            artifact = root / "evaluation" / "evidence" / "hosts" / "codex-desktop-cli.json"
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            for step in payload["lifecycle_steps"]:
                step["result"] = "passed"
            artifact.write_text(json.dumps(payload), encoding="utf-8")
            errors = self.validate_fixture(document, readme, root)
        self.assertTrue(any("failed result, nonzero exit, or failed postcondition" in error for error in errors), errors)

    def test_failed_artifact_accepts_nonzero_exit_or_failed_postcondition(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "failed"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            artifact = root / "evaluation" / "evidence" / "hosts" / "codex-desktop-cli.json"

            payload = evidence_payload("Codex Desktop/CLI", "fixture-cli 1.2.3", "failed")
            for step in payload["lifecycle_steps"]:
                step["result"] = "passed"
            payload["lifecycle_steps"][0]["command"]["exit_code"] = 1
            artifact.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(self.validate_fixture(document, readme, root), [])

            payload = evidence_payload("Codex Desktop/CLI", "fixture-cli 1.2.3", "failed")
            for step in payload["lifecycle_steps"]:
                step["result"] = "passed"
            payload["lifecycle_steps"][0]["postcondition"]["passed"] = False
            artifact.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(self.validate_fixture(document, readme, root), [])

    def test_future_verified_json_evidence_passes(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "verified"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            self.assertEqual(self.validate_fixture(document, readme, root), [])

    def test_schema_v2_runtime_and_raw_shapes_are_exact(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "verified"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            artifact = root / "evaluation/evidence/hosts/codex-desktop-cli.json"

            def errors_for(mutator) -> list[str]:
                payload = evidence_payload("Codex Desktop/CLI", "fixture-cli 1.2.3", "verified")
                write_raw_evidence(root, payload)
                mutator(payload)
                artifact.write_text(json.dumps(payload), encoding="utf-8")
                return self.validate_fixture(document, readme, root)

            cases = (
                (lambda payload: payload.__setitem__("schema_version", 2.0), "schema_version must be 2"),
                (lambda payload: payload.__setitem__("schema_version", True), "schema_version must be 2"),
                (lambda payload: payload.pop("runtime_revision"), "runtime_revision"),
                (lambda payload: payload.__setitem__("runtime_revision", "sha256:" + "A" * 64), "runtime_revision"),
                (lambda payload: payload.__setitem__("runtime_revision", "sha256:" + "0" * 64), "runtime revision"),
                (lambda payload: payload["lifecycle_steps"][0].pop("raw_evidence"), "raw evidence schema"),
                (lambda payload: payload["lifecycle_steps"][0]["raw_evidence"].pop("command_output"), "raw evidence schema"),
                (lambda payload: payload["lifecycle_steps"][0]["raw_evidence"].pop("postcondition_readback"), "raw evidence schema"),
                (lambda payload: payload["lifecycle_steps"][0]["raw_evidence"].__setitem__("extra", {}), "raw evidence schema"),
                (lambda payload: payload["lifecycle_steps"][0].__setitem__("raw_evidence", "raw"), "raw evidence schema"),
                (lambda payload: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].pop("path"), "raw evidence record"),
                (lambda payload: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].pop("status"), "raw evidence record"),
                (lambda payload: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].pop("sha256"), "raw evidence record"),
                (lambda payload: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].pop("bytes"), "raw evidence record"),
                (lambda payload: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].pop("reason"), "raw evidence record"),
                (lambda payload: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].__setitem__("extra", True), "raw evidence record"),
                (lambda payload: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].__setitem__("bytes", "25"), "raw evidence record"),
                (lambda payload: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].__setitem__("bytes", True), "raw evidence record"),
                (lambda payload: payload["lifecycle_steps"][0]["raw_evidence"].__setitem__("command_output", "raw"), "raw evidence record"),
            )
            for mutator, finding in cases:
                with self.subTest(finding=finding):
                    errors = errors_for(mutator)
                    self.assertTrue(any(finding in error for error in errors), errors)

    def test_schema_v2_raw_path_and_file_fact_failures(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "verified"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            artifact = root / "evaluation/evidence/hosts/codex-desktop-cli.json"

            def errors_for(mutator) -> list[str]:
                payload = evidence_payload("Codex Desktop/CLI", "fixture-cli 1.2.3", "verified")
                write_raw_evidence(root, payload)
                mutator(payload, root)
                artifact.write_text(json.dumps(payload), encoding="utf-8")
                return self.validate_fixture(document, readme, root)

            def set_path(path: str):
                return lambda payload, _root: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].__setitem__("path", path)

            path_cases = (
                (set_path("/tmp/raw.log"), "raw evidence path"),
                (set_path("C:/raw.log"), "raw evidence path"),
                (set_path("evaluation/evidence/hosts/raw/C:/outside.log"), "raw evidence path"),
                (set_path("evaluation/evidence/hosts/raw/z:/outside.log"), "raw evidence path"),
                (set_path("\\\\server\\share\\raw.log"), "raw evidence path"),
                (set_path("evaluation/evidence/hosts/raw/../raw/escape.log"), "raw evidence path"),
                (set_path("evaluation\\evidence\\hosts\\raw\\raw.log"), "raw evidence path"),
                (set_path("evaluation/evidence/hosts/other.log"), "raw evidence path"),
                (lambda payload, _root: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].__setitem__("path", "evaluation/evidence/hosts/raw/missing.log"), "raw evidence file"),
                (lambda payload, _root: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].__setitem__("bytes", 24), "raw evidence bytes"),
                (lambda payload, _root: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].__setitem__("sha256", "0" * 64), "raw evidence sha256"),
                (lambda payload, _root: payload["lifecycle_steps"][0]["raw_evidence"]["command_output"].__setitem__("sha256", "A" * 64), "raw evidence record"),
            )
            for mutator, finding in path_cases:
                with self.subTest(finding=finding):
                    errors = errors_for(mutator)
                    self.assertTrue(any(finding in error for error in errors), errors)

            def symlink_leaf(payload, fixture_root):
                record = payload["lifecycle_steps"][0]["raw_evidence"]["command_output"]
                raw_path = fixture_root / record["path"]
                raw_path.unlink()
                raw_path.symlink_to(fixture_root / payload["lifecycle_steps"][1]["raw_evidence"]["command_output"]["path"])

            def symlink_component(payload, fixture_root):
                record = payload["lifecycle_steps"][0]["raw_evidence"]["command_output"]
                record["path"] = "evaluation/evidence/hosts/raw/component-link/escaped.log"
                component = fixture_root / RAW_ROOT / "component-link"
                outside = fixture_root / "outside"
                outside.mkdir()
                component.symlink_to(outside, target_is_directory=True)

            def directory_leaf(payload, fixture_root):
                record = payload["lifecycle_steps"][0]["raw_evidence"]["command_output"]
                raw_path = fixture_root / record["path"]
                raw_path.unlink()
                raw_path.mkdir()

            for mutator, finding in (
                (symlink_leaf, "raw evidence symlink"),
                (symlink_component, "raw evidence symlink"),
                (directory_leaf, "raw evidence regular file"),
            ):
                with self.subTest(finding=finding):
                    errors = errors_for(mutator)
                    self.assertTrue(any(finding in error for error in errors), errors)

    def test_schema_v2_conditional_status_and_verified_invariants(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "verified"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            artifact = root / "evaluation/evidence/hosts/codex-desktop-cli.json"

            def errors_for(mutator) -> list[str]:
                payload = evidence_payload("Codex Desktop/CLI", "fixture-cli 1.2.3", "verified")
                write_raw_evidence(root, payload)
                mutator(payload)
                artifact.write_text(json.dumps(payload), encoding="utf-8")
                return self.validate_fixture(document, readme, root)

            def set_channel(
                status: str,
                *,
                file_facts: bool,
                reason: object,
                channel: str = "command_output",
            ):
                def mutate(payload):
                    record = payload["lifecycle_steps"][0]["raw_evidence"][channel]
                    record["status"] = status
                    record["reason"] = reason
                    if not file_facts:
                        record["path"] = record["sha256"] = record["bytes"] = None
                return mutate

            cases = (
                (set_channel("captured", file_facts=True, reason="not allowed"), "captured raw evidence"),
                (set_channel("redacted", file_facts=False, reason="limited"), "redacted raw evidence"),
                (set_channel("redacted", file_facts=True, reason=""), "redacted raw evidence"),
                (set_channel("unavailable", file_facts=True, reason="not captured"), "unavailable raw evidence"),
                (set_channel("unavailable", file_facts=False, reason=""), "unavailable raw evidence"),
                (set_channel("redacted", file_facts=True, reason="inert limitation"), "verified host evidence"),
                (set_channel("unavailable", file_facts=False, reason="inert limitation"), "verified host evidence"),
                (set_channel("redacted", file_facts=True, reason="inert limitation", channel="postcondition_readback"), "verified host evidence"),
                (set_channel("unavailable", file_facts=False, reason="inert limitation", channel="postcondition_readback"), "verified host evidence"),
                (lambda payload: payload["lifecycle_steps"][0].__setitem__("result", "failed"), "passed results, zero exits"),
                (lambda payload: payload["lifecycle_steps"][0]["command"].__setitem__("exit_code", 1), "passed results, zero exits"),
                (lambda payload: payload["lifecycle_steps"][0]["postcondition"].__setitem__("passed", False), "passed results, zero exits"),
                (lambda payload: payload["lifecycle_steps"].pop(), "exactly eight"),
                (lambda payload: payload["lifecycle_steps"].reverse(), "IDs/order"),
                (lambda payload: payload["lifecycle_steps"][1].__setitem__("id", "install"), "IDs/order"),
            )
            for mutator, finding in cases:
                with self.subTest(finding=finding):
                    errors = errors_for(mutator)
                    self.assertTrue(any(finding in error for error in errors), errors)

    def test_v2_failed_and_unverified_records_allow_honest_limitations_only(self) -> None:
        for status in ("failed", "unverified"):
            with self.subTest(status=status):
                statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
                statuses["Codex Desktop/CLI"] = status
                directory, root, document, readme = self.make_fixture(statuses, {status})
                with directory:
                    artifact = root / "evaluation/evidence/hosts/codex-desktop-cli.json"
                    payload = json.loads(artifact.read_text(encoding="utf-8"))
                    channel = payload["lifecycle_steps"][0]["raw_evidence"]["command_output"]
                    channel["status"] = "redacted"
                    channel["reason"] = "inert fixture limitation"
                    payload["lifecycle_steps"][0]["raw_evidence"]["postcondition_readback"] = {
                        "path": None,
                        "status": "unavailable",
                        "sha256": None,
                        "bytes": None,
                        "reason": "inert fixture capture unavailable",
                    }
                    if status == "failed":
                        payload["lifecycle_steps"][0]["result"] = "failed"
                    artifact.write_text(json.dumps(payload), encoding="utf-8")
                    self.assertEqual(self.validate_fixture(document, readme, root), [])
                    overclaim = readme.replace("`targeted / " + status + "`", "`verified / compatible`", 1)
                    errors = self.validate_fixture(document, overclaim, root)
                    self.assertTrue(any("must match " + status in error for error in errors), errors)

    def test_schema_v2_rejects_same_size_raw_leaf_identity_drift(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "verified"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            artifact = root / "evaluation/evidence/hosts/codex-desktop-cli.json"
            payload = json.loads(artifact.read_text(encoding="utf-8"))

            def replace_between_stat_and_open(path: Path) -> None:
                replacement = path.with_name("replacement.log")
                replacement.write_bytes(INERT_RAW_TEXT)
                os.replace(replacement, path)

            errors: list[str] = []
            validator.validate_lifecycle_artifact(
                "Codex Desktop/CLI",
                "verified",
                "fixture-cli 1.2.3",
                "[fixture evidence](evaluation/evidence/hosts/codex-desktop-cli.json)",
                root,
                errors,
                before_raw_read=replace_between_stat_and_open,
            )
            self.assertTrue(any("read-time identity drift" in error for error in errors), errors)

    def test_schema_v2_rejects_raw_leaf_size_drift(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "verified"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            target = root / RAW_ROOT / "codex-desktop-cli-install-command.log"

            def resize_between_stat_and_open(path: Path) -> None:
                if path == target:
                    path.write_bytes(INERT_RAW_TEXT + b"x")

            errors: list[str] = []
            validator.validate_lifecycle_artifact(
                "Codex Desktop/CLI",
                "verified",
                "fixture-cli 1.2.3",
                "[fixture evidence](evaluation/evidence/hosts/codex-desktop-cli.json)",
                root,
                errors,
                before_raw_read=resize_between_stat_and_open,
            )
            self.assertTrue(any("read-time identity drift" in error for error in errors), errors)

    def test_schema_v2_rejects_parent_component_swap_before_open(self) -> None:
        statuses = dict.fromkeys(validator.HOST_SUPPORT_TARGETS, "unavailable")
        statuses["Codex Desktop/CLI"] = "verified"
        directory, root, document, readme = self.make_fixture(statuses)
        with directory:
            if not validator._safe_raw_descriptor_platform():
                errors = self.validate_fixture(document, readme, root)
                self.assertTrue(
                    any("safe descriptor traversal is unavailable" in error for error in errors),
                    errors,
                )
                return
            artifact = root / "evaluation/evidence/hosts/codex-desktop-cli.json"
            payload = evidence_payload("Codex Desktop/CLI", "fixture-cli 1.2.3", "verified")
            write_raw_evidence(root, payload)
            record = payload["lifecycle_steps"][0]["raw_evidence"]["command_output"]
            record["path"] = "evaluation/evidence/hosts/raw/nested/command.log"
            nested = root / RAW_ROOT / "nested"
            nested.mkdir()
            target = nested / "command.log"
            target.write_bytes(INERT_RAW_TEXT)
            artifact.write_text(json.dumps(payload), encoding="utf-8")

            def swap_parent(path: Path) -> None:
                if path != target:
                    return
                relocated = root / "relocated-nested"
                outside = root / "outside"
                nested.rename(relocated)
                outside.mkdir()
                try:
                    os.link(relocated / "command.log", outside / "command.log")
                    nested.symlink_to(outside, target_is_directory=True)
                except (NotImplementedError, OSError) as exc:
                    self.skipTest("safe parent-swap primitives unavailable: " + str(exc))

            errors: list[str] = []
            validator.validate_lifecycle_artifact(
                "Codex Desktop/CLI",
                "verified",
                "fixture-cli 1.2.3",
                "[fixture evidence](evaluation/evidence/hosts/codex-desktop-cli.json)",
                root,
                errors,
                before_raw_read=swap_parent,
            )
            self.assertTrue(any("parent component" in error for error in errors), errors)

    def test_raw_descriptor_fstat_failure_is_public_and_closed(self) -> None:
        if not validator._safe_raw_descriptor_platform():
            self.skipTest("safe descriptor primitives unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_file = root / RAW_ROOT / "nested" / "evidence.log"
            raw_file.parent.mkdir(parents=True)
            raw_file.write_bytes(INERT_RAW_TEXT)
            real_open = validator.os.open
            real_fstat = validator.os.fstat
            real_close = validator.os.close
            opened: list[int] = []
            close_attempts: list[int] = []
            injected = {"done": False}

            def record_open(path, *args, **kwargs):
                descriptor = real_open(path, *args, **kwargs)
                if path == "evaluation":
                    opened.append(descriptor)
                return descriptor

            def fail_new_directory_fstat(descriptor):
                if descriptor in opened and not injected["done"]:
                    injected["done"] = True
                    raise OSError("injected fstat failure")
                return real_fstat(descriptor)

            def record_close(descriptor):
                close_attempts.append(descriptor)
                return real_close(descriptor)

            errors: list[str] = []
            record = {
                "path": "evaluation/evidence/hosts/raw/nested/evidence.log",
                "status": "captured",
                "sha256": INERT_RAW_SHA256,
                "bytes": INERT_RAW_BYTES,
                "reason": None,
            }
            with patch.object(validator.os, "open", side_effect=record_open), patch.object(
                validator.os, "fstat", side_effect=fail_new_directory_fstat
            ), patch.object(validator.os, "close", side_effect=record_close):
                with patch.object(validator, "_safe_raw_descriptor_platform", return_value=True):
                    validator.validate_raw_evidence_record(
                        record, "verified", root, errors, "fixture host"
                    )
            self.assertTrue(
                any("raw evidence descriptor operation failed" in error for error in errors),
                errors,
            )
            self.assertTrue(opened, opened)
            self.assertIn(opened[0], close_attempts)
            self.assert_real_descriptors_closed(real_fstat, opened)

    def test_raw_parent_close_failure_is_public_and_closes_successors(self) -> None:
        if not validator._safe_raw_descriptor_platform():
            self.skipTest("safe descriptor primitives unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_file = root / RAW_ROOT / "nested" / "evidence.log"
            raw_file.parent.mkdir(parents=True)
            raw_file.write_bytes(INERT_RAW_TEXT)
            real_open = validator.os.open
            real_fstat = validator.os.fstat
            real_close = validator.os.close
            descriptors: dict[str, int] = {}
            close_attempts: list[int] = []
            injected = {"done": False}

            def record_open(path, *args, **kwargs):
                descriptor = real_open(path, *args, **kwargs)
                if path in {"evaluation", "evidence"}:
                    descriptors[path] = descriptor
                return descriptor

            def fail_after_parent_close(descriptor):
                close_attempts.append(descriptor)
                real_close(descriptor)
                if descriptor == descriptors.get("evaluation") and not injected["done"]:
                    injected["done"] = True
                    raise OSError("injected parent close failure")

            errors: list[str] = []
            record = {
                "path": "evaluation/evidence/hosts/raw/nested/evidence.log",
                "status": "captured",
                "sha256": INERT_RAW_SHA256,
                "bytes": INERT_RAW_BYTES,
                "reason": None,
            }
            with patch.object(validator.os, "open", side_effect=record_open), patch.object(
                validator.os, "close", side_effect=fail_after_parent_close
            ):
                with patch.object(validator, "_safe_raw_descriptor_platform", return_value=True):
                    validator.validate_raw_evidence_record(
                        record, "verified", root, errors, "fixture host"
                    )
            self.assertTrue(
                any("raw evidence descriptor operation failed" in error for error in errors),
                errors,
            )
            self.assertIn(descriptors["evaluation"], close_attempts)
            self.assertIn(descriptors["evidence"], close_attempts)
            self.assert_real_descriptors_closed(real_fstat, list(descriptors.values()))

    def test_raw_cleanup_closes_all_owners_without_masking_public_validation_error(self) -> None:
        if not validator._safe_raw_descriptor_platform():
            self.skipTest("safe descriptor primitives unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            relative = "evaluation/evidence/hosts/raw/nested/evidence.log"
            raw_file = root / relative
            raw_file.parent.mkdir(parents=True)
            raw_file.write_bytes(INERT_RAW_TEXT)
            real_open = validator.os.open
            real_dup = validator.os.dup
            real_stat = validator.os.stat
            real_fstat = validator.os.fstat
            real_close = validator.os.close
            descriptors: dict[str, int] = {}
            close_attempts: list[int] = []
            leaf_stats = {"count": 0}
            injected = {"done": False}

            def record_open(path, *args, **kwargs):
                descriptor = real_open(path, *args, **kwargs)
                if path == str(root):
                    descriptors["root"] = descriptor
                elif path == "nested":
                    descriptors["parent"] = descriptor
                elif path == "evidence.log":
                    descriptors["leaf"] = descriptor
                return descriptor

            def record_dup(descriptor):
                duplicate = real_dup(descriptor)
                descriptors["verification"] = duplicate
                return duplicate

            def fail_verified_leaf_stat(path, *args, **kwargs):
                if path == "evidence.log" and kwargs.get("dir_fd") is not None:
                    leaf_stats["count"] += 1
                    if leaf_stats["count"] == 2:
                        raise OSError("injected validation failure")
                return real_stat(path, *args, **kwargs)

            def fail_once_after_leaf_close(descriptor):
                close_attempts.append(descriptor)
                real_close(descriptor)
                if descriptor == descriptors.get("leaf") and not injected["done"]:
                    injected["done"] = True
                    raise OSError("injected cleanup failure")

            errors: list[str] = []
            record = {
                "path": relative,
                "status": "captured",
                "sha256": INERT_RAW_SHA256,
                "bytes": INERT_RAW_BYTES,
                "reason": None,
            }
            with patch.object(validator.os, "open", side_effect=record_open), patch.object(
                validator.os, "dup", side_effect=record_dup
            ), patch.object(validator.os, "stat", side_effect=fail_verified_leaf_stat), patch.object(
                validator.os, "close", side_effect=fail_once_after_leaf_close
            ):
                with patch.object(validator, "_safe_raw_descriptor_platform", return_value=True):
                    validator.validate_raw_evidence_record(
                        record, "verified", root, errors, "fixture host"
                    )
            self.assertTrue(any("raw evidence file is missing" in error for error in errors), errors)
            self.assertEqual(leaf_stats["count"], 2)
            for descriptor in descriptors.values():
                self.assertIn(descriptor, close_attempts)
            self.assert_real_descriptors_closed(real_fstat, list(descriptors.values()))

    def test_raw_verification_fstat_failure_is_public_descriptor_finding(self) -> None:
        if not validator._safe_raw_descriptor_platform():
            self.skipTest("safe descriptor primitives unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_file = root / RAW_ROOT / "nested" / "evidence.log"
            raw_file.parent.mkdir(parents=True)
            raw_file.write_bytes(INERT_RAW_TEXT)
            real_open = validator.os.open
            real_fstat = validator.os.fstat
            opened: list[int] = []
            injected = {"done": False}

            def record_open(path, *args, **kwargs):
                descriptor = real_open(path, *args, **kwargs)
                if path == "evaluation":
                    opened.append(descriptor)
                return descriptor

            def fail_verification_directory_fstat(descriptor):
                if len(opened) > 1 and descriptor == opened[1] and not injected["done"]:
                    injected["done"] = True
                    raise OSError("injected verification fstat failure")
                return real_fstat(descriptor)

            errors: list[str] = []
            record = {
                "path": "evaluation/evidence/hosts/raw/nested/evidence.log",
                "status": "captured",
                "sha256": INERT_RAW_SHA256,
                "bytes": INERT_RAW_BYTES,
                "reason": None,
            }
            with patch.object(validator.os, "open", side_effect=record_open), patch.object(
                validator.os, "fstat", side_effect=fail_verification_directory_fstat
            ):
                with patch.object(validator, "_safe_raw_descriptor_platform", return_value=True):
                    validator.validate_raw_evidence_record(
                        record, "verified", root, errors, "fixture host"
                    )
            self.assertTrue(
                any("raw evidence descriptor operation failed" in error for error in errors),
                errors,
            )
            self.assert_real_descriptors_closed(real_fstat, opened)


if __name__ == "__main__":
    unittest.main()
