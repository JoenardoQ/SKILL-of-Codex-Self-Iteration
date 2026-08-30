"""Focused tests for the deterministic Package-E1 routing validator gate."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import validate_repo as validator

TUNING_CASE_IDS = (
    "contract-reconciliation-tuning-positive",
    "contract-reconciliation-tuning-near-miss",
)
VARIANTS = ("current", "conditional-candidate")


class RoutingEvidenceValidatorTests(unittest.TestCase):
    repository_root = Path(__file__).resolve().parents[1]

    def with_root(self) -> Path:
        directory = tempfile.TemporaryDirectory()
        previous_root = validator.ROOT
        validator.ROOT = Path(directory.name)
        self.addCleanup(setattr, validator, "ROOT", previous_root)
        self.addCleanup(directory.cleanup)
        return Path(directory.name)

    def evaluation_payload(self) -> dict[str, object]:
        return json.loads(
            (self.repository_root / "evaluation/eval-spec.json").read_text(
                encoding="utf-8"
            )
        )

    def run_aggregate(self, root: Path, setup: str = "") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                (
                    "import sys; from pathlib import Path; "
                    f"sys.path.insert(0, {str(self.repository_root / 'scripts')!r}); "
                    "import validate_repo as validator; "
                    f"validator.ROOT = Path({str(root)!r}); "
                    f"{setup}"
                    "raise SystemExit(validator.main())"
                ),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    @staticmethod
    def write_json(root: Path, payload: object) -> None:
        path = root / "evaluation/eval-spec.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    @staticmethod
    def routing_record(
        case_id: str,
        variant: str,
        repetition: int,
        *,
        selected: bool | None = None,
        loaded: bool | None = None,
        verdict: str = "pass",
    ) -> str:
        expected = case_id.endswith("positive")
        selected_value = expected if selected is None else selected
        loaded_value = expected if loaded is None else loaded
        return f"""# Routing tuning observation

- Case ID: {case_id}
- Variant: {variant}
- Repetition: {repetition}
- Model: fixture-model
- Host: fixture-host
- Host build: fixture-build
- Runner: fixture-runner
- Tools: none
- Sampling: unavailable: fixture has no sampling controls
- Budget: platform-managed
- Selected: {str(selected_value).lower()}
- Entrypoint loaded: {str(loaded_value).lower()}
- Reviewer: fixture-reviewer
- Verdict: {verdict}
- Evidence status: active
- Limitations: temporary fixture only

## Raw answer

fixture raw answer

## Manual review

Independent fixture review.
"""

    def write_current_inventory(self, root: Path, omitted: set[str] | None = None) -> None:
        self.write_variant_inventory(root, "current", omitted)

    def write_variant_inventory(
        self, root: Path, variant: str, omitted: set[str] | None = None
    ) -> None:
        directory = root / "evaluation/evidence/routing-tuning" / variant
        directory.mkdir(parents=True, exist_ok=True)
        for case_id in TUNING_CASE_IDS:
            for repetition in range(1, 6):
                if f"{case_id}:{repetition}" in (omitted or set()):
                    continue
                path = directory / f"{case_id}-r{repetition}.md"
                path.write_text(
                    self.routing_record(case_id, variant, repetition), encoding="utf-8"
                )

    def test_routing_inventory_rejects_pair_and_outcome_drift(self) -> None:
        """Break caught: missing/duplicate/drifted pair objects pass schema-v4."""
        payload = self.evaluation_payload()
        cases = payload["routing_cases"]
        self.assertEqual(
            {case["id"] for case in cases if str(case["id"]).startswith("contract-")},
            set(validator.ROUTING_PAIR_CASE_IDS),
        )
        mutations = {
            "missing": lambda rows: rows.pop(),
            "duplicate": lambda rows: rows.append(dict(rows[-1])),
            "collision": lambda rows: rows[-1].update(
                {"id": "contract-reconciliation-tuning-positive"}
            ),
            "unexpected": lambda rows: rows[-1].update({"pair_role": "held-out"}),
            "prompt": lambda rows: rows[-1].update({"prompt": "unpaired wording"}),
            "outcome": lambda rows: rows[-1].update({"should_trigger": True}),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                root = self.with_root()
                changed = json.loads(json.dumps(payload))
                mutate(changed["routing_cases"])
                self.write_json(root, changed)
                errors: list[str] = []
                validator.validate_evaluations(errors)
                self.assertTrue(errors, errors)

    def test_current_evidence_requires_exact_canonical_five_repetitions(self) -> None:
        """Break caught: incomplete, duplicate, or noncanonical current evidence passes."""
        root = self.with_root()
        self.write_current_inventory(root)
        errors: list[str] = []
        validator.validate_routing_evidence(errors)
        self.assertEqual(errors, [])
        duplicate = root / "evaluation/evidence/routing-tuning/current/contract-reconciliation-tuning-positive-r2.md"
        duplicate.write_text(
            self.routing_record(
                "contract-reconciliation-tuning-positive", "current", 1
            ),
            encoding="utf-8",
        )
        errors = []
        validator.validate_routing_evidence(errors)
        self.assertIn(
            "routing evidence evaluation/evidence/routing-tuning/current/contract-reconciliation-tuning-positive-r2.md duplicates a case repetition",
            errors,
        )

    def test_literal_current_and_conditional_candidate_inventories_are_accepted(self) -> None:
        """Break caught: the approved literal -rN filenames reject a full variant."""
        root = self.with_root()
        for variant in VARIANTS:
            self.write_variant_inventory(root, variant)
        errors: list[str] = []
        validator.validate_routing_evidence(errors)
        self.assertEqual(errors, [])
        alternate = root / "evaluation/evidence/routing-tuning/current/alternate.md"
        alternate.write_text(
            self.routing_record(TUNING_CASE_IDS[0], "current", 1), encoding="utf-8"
        )
        errors = []
        validator.validate_routing_evidence(errors)
        self.assertIn(
            "routing evidence evaluation/evidence/routing-tuning/current/alternate.md filename is not canonical",
            errors,
        )
        missing_root = self.with_root()
        self.write_current_inventory(
            missing_root,
            {"contract-reconciliation-tuning-near-miss:5"},
        )
        errors = []
        validator.validate_routing_evidence(errors)
        self.assertTrue(errors, errors)

    def test_current_miss_is_preserved_when_verdict_is_fail(self) -> None:
        """A measured baseline miss is evidence, not malformed evidence."""
        root = self.with_root()
        self.write_current_inventory(root)
        path = root / "evaluation/evidence/routing-tuning/current/contract-reconciliation-tuning-positive-r1.md"
        path.write_text(
            self.routing_record(
                TUNING_CASE_IDS[0], "current", 1,
                selected=False, loaded=False, verdict="fail",
            ),
            encoding="utf-8",
        )
        errors: list[str] = []
        validator.validate_routing_evidence(errors)
        self.assertEqual(errors, [])

    def test_verdict_must_match_observations_and_candidate_must_pass(self) -> None:
        """Break caught: verdict laundering or a failed candidate can close E2."""
        for variant, verdict, finding in (
            ("current", "pass", "verdict does not match observations"),
            ("conditional-candidate", "fail", "conditional candidate observations do not match case expectations"),
        ):
            with self.subTest(variant=variant):
                root = self.with_root()
                self.write_variant_inventory(root, variant)
                path = root / "evaluation/evidence/routing-tuning" / variant / "contract-reconciliation-tuning-positive-r1.md"
                path.write_text(
                    self.routing_record(
                        TUNING_CASE_IDS[0], variant, 1,
                        selected=False, loaded=False, verdict=verdict,
                    ),
                    encoding="utf-8",
                )
                errors: list[str] = []
                validator.validate_routing_evidence(errors)
                self.assertTrue(any(finding in error for error in errors), errors)

    def test_routing_evidence_rejects_metadata_boolean_and_raw_boundary_drift(self) -> None:
        """Break caught: conflated observations or altered raw sections are accepted."""
        root = self.with_root()
        self.write_current_inventory(root)
        path = root / "evaluation/evidence/routing-tuning/current" / (
            "contract-reconciliation-tuning-positive-r1.md"
        )
        original = path.read_text(encoding="utf-8")
        for name, changed in (
            ("boolean", original.replace("- Selected: true", "- Selected: selected")),
            (
                "conflated",
                original.replace("- Entrypoint loaded: true", "- Selected: true"),
            ),
            ("metadata", original.replace("- Model: fixture-model\n", "")),
            ("raw", original.replace("## Raw answer", "## Raw answer altered")),
        ):
            with self.subTest(name=name):
                path.write_text(changed, encoding="utf-8")
                errors: list[str] = []
                validator.validate_routing_evidence(errors)
                self.assertTrue(errors, errors)
                path.write_text(original, encoding="utf-8")

    def test_routing_record_reports_metadata_order_presence_and_boundaries(self) -> None:
        """Break caught: closed record grammar loses its precise failure reasons."""
        root = self.with_root()
        self.write_current_inventory(root)
        path = root / "evaluation/evidence/routing-tuning/current/contract-reconciliation-tuning-positive-r1.md"
        original = path.read_text(encoding="utf-8")
        mutations = (
            ("presence", original.replace("- Model: fixture-model\n", ""), "metadata field presence is invalid"),
            ("order", original.replace("- Model: fixture-model\n- Host: fixture-host", "- Host: fixture-host\n- Model: fixture-model"), "metadata field order is invalid"),
            ("raw", original.replace("## Raw answer", "## Altered raw"), "raw boundaries are invalid"),
            ("manual", original.replace("## Manual review", "## Altered manual"), "raw boundaries are invalid"),
        )
        for name, changed, finding in mutations:
            with self.subTest(name=name):
                path.write_text(changed, encoding="utf-8")
                errors: list[str] = []
                validator.validate_routing_evidence(errors)
                self.assertTrue(any(finding in error for error in errors), errors)
                path.write_text(original, encoding="utf-8")

    def test_descriptor_reader_rejects_open_and_read_time_leaf_drift(self) -> None:
        """Break caught: a checked routing leaf can be swapped or changed while read."""
        root = self.with_root()
        self.write_current_inventory(root)
        relative = Path("evaluation/evidence/routing-tuning/current/contract-reconciliation-tuning-positive-r1.md")
        path = root / relative
        actual_open = validator.os.open

        def replace_with_symlink(name, flags, *args, **kwargs):
            if name == relative.name and kwargs.get("dir_fd") is not None:
                path.unlink()
                path.symlink_to(root / "outside.md")
            return actual_open(name, flags, *args, **kwargs)

        (root / "outside.md").write_text("outside", encoding="utf-8")
        with mock.patch.object(validator.os, "open", side_effect=replace_with_symlink), mock.patch.object(
            validator, "_safe_raw_descriptor_platform", return_value=True
        ):
            with self.assertRaisesRegex(ValueError, "descriptor operation failed|identity drift"):
                validator.read_routing_evidence_file(relative)
        path.unlink()
        path.write_text(self.routing_record(TUNING_CASE_IDS[0], "current", 1), encoding="utf-8")
        actual_read = validator.os.read
        changed = False

        def mutate_after_first_chunk(fd, count):
            nonlocal changed
            chunk = actual_read(fd, count)
            if not changed and chunk:
                changed = True
                # Mutate the same inode after its content was observed; this is
                # deliberately not a rename/symlink substitution seam.
                writer = validator.os.open(str(path), validator.os.O_WRONLY)
                try:
                    validator.os.ftruncate(writer, len(chunk) + 1)
                finally:
                    validator.os.close(writer)
            return chunk

        with mock.patch.object(validator.os, "read", side_effect=mutate_after_first_chunk):
            with self.assertRaisesRegex(ValueError, "leaf read-time identity drift"):
                validator.read_routing_evidence_file(relative)
        path.write_text(self.routing_record(TUNING_CASE_IDS[0], "current", 1), encoding="utf-8")
        replaced = False

        def replace_name_after_first_chunk(fd, count):
            nonlocal replaced
            chunk = actual_read(fd, count)
            if not replaced and chunk:
                replaced = True
                replacement = path.with_name("replacement.md")
                replacement.write_text("replacement", encoding="utf-8")
                replacement.replace(path)
            return chunk

        # The retained leaf fd remains unchanged here; only reopening and
        # rebinding the directory entry after the read can catch this swap.
        with mock.patch.object(validator.os, "read", side_effect=replace_name_after_first_chunk):
            with self.assertRaisesRegex(ValueError, "leaf read-time identity drift"):
                validator.read_routing_evidence_file(relative)

    def test_heldout_prohibition_precedes_any_routing_leaf_read(self) -> None:
        """Break caught: held-out routing content becomes observable during E1."""
        root = self.with_root()
        heldout = root / "evaluation/evidence/routing-tuning/current/contract-reconciliation-heldout-positive-r1.md"
        heldout.parent.mkdir(parents=True, exist_ok=True)
        heldout.write_text("unreadable held-out content", encoding="utf-8")
        with mock.patch.object(validator, "read_routing_evidence_file", side_effect=AssertionError("read")):
            errors: list[str] = []
            validator.validate_routing_evidence(errors)
        self.assertEqual(len(errors), 1)
        self.assertIn("held-out routing evidence path is prohibited", errors[0])

    def test_routing_root_variant_and_leaf_require_their_declared_types(self) -> None:
        """Break caught: non-directory parents or non-file leaves reach the parser."""
        for level, expected in (
            ("root", "routing evidence root has an invalid type"),
            ("variant", "routing evidence variant has an invalid type"),
            ("leaf", "routing evidence leaf has an invalid type"),
        ):
            with self.subTest(level=level):
                root = self.with_root()
                if level == "root":
                    target = root / "evaluation/evidence/routing-tuning"
                    target.parent.mkdir(parents=True)
                    target.write_text("not a directory", encoding="utf-8")
                else:
                    self.write_current_inventory(root)
                    if level == "variant":
                        target = root / "evaluation/evidence/routing-tuning/current"
                        shutil.rmtree(target)
                        target.write_text("not a directory", encoding="utf-8")
                    else:
                        target = root / "evaluation/evidence/routing-tuning/current/contract-reconciliation-tuning-positive-r1.md"
                        target.unlink()
                        target.mkdir()
                errors: list[str] = []
                validator.validate_routing_evidence(errors)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_routing_evidence_named_case_variant_outcome_and_status_guards(self) -> None:
        """Break caught: each record guard must reject its own reachable drift."""
        root = self.with_root()
        self.write_current_inventory(root)
        path = root / "evaluation/evidence/routing-tuning/current/contract-reconciliation-tuning-positive-r1.md"
        original = path.read_text(encoding="utf-8")
        mutations = (
            ("case", original.replace("Case ID: contract-reconciliation-tuning-positive", "Case ID: wrong-case"), "has an invalid tuning case ID"),
            ("variant", original.replace("Variant: current", "Variant: conditional-candidate"), "variant does not match its directory"),
            ("repetition", original.replace("Repetition: 1", "Repetition: 6"), "repetition must be 1 through 5"),
            ("selected", original.replace("Selected: true", "Selected: false"), "verdict does not match observations"),
            ("loaded", original.replace("Entrypoint loaded: true", "Entrypoint loaded: false"), "verdict does not match observations"),
            ("status", original.replace("Evidence status: active", "Evidence status: historical"), "evidence status must be active"),
            ("sampling", original.replace("Sampling: unavailable: fixture has no sampling controls", "Sampling: unavailable"), "sampling unavailability needs a reason"),
        )
        for name, changed, finding in mutations:
            with self.subTest(name=name):
                path.write_text(changed, encoding="utf-8")
                errors: list[str] = []
                validator.validate_routing_evidence(errors)
                self.assertTrue(any(finding in error for error in errors), errors)
                path.write_text(original, encoding="utf-8")
        near_miss = path.with_name("contract-reconciliation-tuning-near-miss-r1.md")
        near_original = near_miss.read_text(encoding="utf-8")
        near_miss.write_text(
            near_original.replace("Selected: false", "Selected: true").replace(
                "Entrypoint loaded: false", "Entrypoint loaded: true"
            ),
            encoding="utf-8",
        )
        errors = []
        validator.validate_routing_evidence(errors)
        self.assertTrue(
            any("verdict does not match observations" in error for error in errors),
            errors,
        )

    def test_post_prescan_heldout_leaf_is_prohibited_without_a_reader_call(self) -> None:
        """Break caught: a held-out leaf injected after prescan reaches the reader."""
        root = self.with_root()
        self.write_current_inventory(root)
        heldout = root / "evaluation/evidence/routing-tuning/current/contract-reconciliation-heldout-positive-r1.md"
        original_status = validator.routing_evidence_path_status
        original_reader = validator.read_routing_evidence_leaf
        injected = False

        def inject_after_root(path, expected_directory, label, errors):
            nonlocal injected
            result = original_status(path, expected_directory, label, errors)
            if label == "root" and result and not injected:
                injected = True
                heldout.write_text("must never be read", encoding="utf-8")
            return result

        with mock.patch.object(validator, "routing_evidence_path_status", side_effect=inject_after_root), mock.patch.object(
            validator, "read_routing_evidence_leaf", side_effect=lambda parent_fd, leaf_name: (_ for _ in ()).throw(AssertionError(leaf_name)) if "heldout" in leaf_name.casefold() else original_reader(parent_fd, leaf_name)
        ) as reader:
            errors: list[str] = []
            validator.validate_routing_evidence(errors)
        self.assertTrue(any("held-out routing evidence path is prohibited" in error for error in errors), errors)
        self.assertFalse(any("heldout" in str(call) for call in reader.call_args_list), reader.call_args_list)
        with tempfile.TemporaryDirectory() as temporary:
            aggregate_root = Path(temporary) / "repository"
            shutil.copytree(self.repository_root, aggregate_root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            self.write_current_inventory(aggregate_root)
            setup_source = """original_status = validator.routing_evidence_path_status
injected = [False]
def status(path, expected_directory, label, errors):
    result = original_status(path, expected_directory, label, errors)
    if label == "root" and result and not injected[0]:
        injected[0] = True
        path = validator.ROOT / "evaluation/evidence/routing-tuning/current/contract-reconciliation-heldout-positive-r1.md"
        path.write_text("must never be read", encoding="utf-8")
    return result
original_reader = validator.read_routing_evidence_leaf
def reader(parent_fd, leaf_name):
    if "heldout" in leaf_name.casefold():
        raise AssertionError(leaf_name)
    return original_reader(parent_fd, leaf_name)
validator.routing_evidence_path_status = status
validator.read_routing_evidence_leaf = reader
"""
            setup = f"exec({setup_source!r}); "
            completed = self.run_aggregate(aggregate_root, setup)
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("held-out routing evidence path is prohibited", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_dangling_routing_root_is_rejected_direct_and_aggregate(self) -> None:
        """Break caught: lexical absence follows a dangling routing-root symlink."""
        root = self.with_root()
        link = root / "evaluation/evidence/routing-tuning"
        link.parent.mkdir(parents=True)
        try:
            link.symlink_to(root / "missing-routing-root", target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symlinks unsupported: {exc}")
        errors: list[str] = []
        validator.validate_routing_evidence(errors)
        self.assertIn(f"routing evidence root must not be a symlink: {link.relative_to(root)}", errors)
        with tempfile.TemporaryDirectory() as temporary:
            aggregate_root = Path(temporary) / "repository"
            shutil.copytree(self.repository_root, aggregate_root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            shutil.rmtree(aggregate_root / "evaluation/evidence/routing-tuning")
            aggregate_link = aggregate_root / "evaluation/evidence/routing-tuning"
            aggregate_link.parent.mkdir(parents=True, exist_ok=True)
            aggregate_link.symlink_to(aggregate_root / "missing-routing-root", target_is_directory=True)
            completed = self.run_aggregate(aggregate_root)
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("routing evidence root must not be a symlink", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_routing_directory_view_drift_is_fail_closed(self) -> None:
        """Break caught: entries can be added, removed, or replaced after enumeration."""
        for change in ("add", "remove", "replace"):
            with self.subTest(change=change):
                root = self.with_root()
                self.write_current_inventory(root)
                directory = root / "evaluation/evidence/routing-tuning/current"
                original_reader = validator.read_routing_evidence_leaf
                changed = False

                def mutate_view(parent_fd, leaf_name):
                    nonlocal changed
                    text = original_reader(parent_fd, leaf_name)
                    if not changed:
                        changed = True
                        target = directory / "contract-reconciliation-tuning-positive-r5.md"
                        if change == "add":
                            (directory / "added.md").write_text("added", encoding="utf-8")
                        elif change == "remove":
                            target.unlink()
                        else:
                            replacement = directory / "replacement.md"
                            replacement.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")
                            replacement.replace(target)
                    return text

                with mock.patch.object(validator, "read_routing_evidence_leaf", side_effect=mutate_view):
                    errors: list[str] = []
                    validator.validate_routing_evidence(errors)
                self.assertIn(
                    "routing evidence directory view drift: evaluation/evidence/routing-tuning/current",
                    errors,
                )

    def test_whole_variant_rebinding_is_rejected_before_replacement_bytes(self) -> None:
        """Break caught: retained A view can otherwise validate bytes from renamed B."""
        root = self.with_root()
        self.write_current_inventory(root)
        routing_root = root / "evaluation/evidence/routing-tuning"
        current = routing_root / "current"
        replacement = root / "replacement"
        replacement.mkdir()
        for case_id in TUNING_CASE_IDS:
            for repetition in range(1, 6):
                (replacement / f"{case_id}-r{repetition}.md").write_text(
                    self.routing_record(case_id, "current", repetition).replace("fixture raw answer", "B-MARKER"),
                    encoding="utf-8",
                )
        original_view = validator._routing_directory_view
        original_reader = validator.read_routing_evidence_leaf
        swapped = False
        observed: list[str] = []
        view_calls = 0

        def swap_after_initial_view(descriptor):
            nonlocal swapped, view_calls
            view = original_view(descriptor)
            view_calls += 1
            if view_calls == 2 and not swapped:
                swapped = True
                current.rename(routing_root / "current-a")
                replacement.rename(current)
            return view

        def record_reader(parent_fd, leaf_name):
            text = original_reader(parent_fd, leaf_name)
            observed.append(text)
            return text

        with mock.patch.object(validator, "_routing_directory_view", side_effect=swap_after_initial_view), mock.patch.object(
            validator, "read_routing_evidence_leaf", side_effect=record_reader
        ):
            errors: list[str] = []
            validator.validate_routing_evidence(errors)
        self.assertTrue(any("parent component read-time identity drift" in error for error in errors), errors)
        self.assertFalse(any("B-MARKER" in text for text in observed), observed)
        with tempfile.TemporaryDirectory() as temporary:
            aggregate_root = Path(temporary) / "repository"
            shutil.copytree(self.repository_root, aggregate_root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            self.write_current_inventory(aggregate_root)
            aggregate_replacement = aggregate_root / "replacement"
            aggregate_replacement.mkdir()
            for case_id in TUNING_CASE_IDS:
                for repetition in range(1, 6):
                    (aggregate_replacement / f"{case_id}-r{repetition}.md").write_text(
                        self.routing_record(case_id, "current", repetition).replace("fixture raw answer", "B-MARKER"),
                        encoding="utf-8",
                    )
            setup_source = """original_view = validator._routing_directory_view
view_calls = [0]
def view(descriptor):
    value = original_view(descriptor)
    view_calls[0] += 1
    if view_calls[0] == 2:
        routing = validator.ROOT / "evaluation/evidence/routing-tuning"
        (routing / "current").rename(routing / "current-a")
        (validator.ROOT / "replacement").rename(routing / "current")
    return value
original_reader = validator.read_routing_evidence_leaf
def reader(parent_fd, leaf_name):
    value = original_reader(parent_fd, leaf_name)
    if "B-MARKER" in value:
        raise AssertionError("replacement bytes read")
    return value
validator._routing_directory_view = view
validator.read_routing_evidence_leaf = reader
"""
            completed = self.run_aggregate(aggregate_root, f"exec({setup_source!r}); ")
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("parent component read-time identity drift", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_directory_view_owns_duplicate_descriptors_and_fails_closed_on_cleanup(self) -> None:
        """Break caught: retained snapshot duplicates leak or cleanup errors are accepted."""
        if not Path("/proc/self/fd").is_dir():
            self.skipTest("fd accounting unavailable")
        root = self.with_root()
        self.write_current_inventory(root)
        before = len(list(Path("/proc/self/fd").iterdir()))
        for _ in range(8):
            errors: list[str] = []
            validator.validate_routing_evidence(errors)
            self.assertEqual(errors, [])
        invalid = root / "evaluation/evidence/routing-tuning/current/extra.txt"
        invalid.write_text("invalid", encoding="utf-8")
        for _ in range(8):
            errors = []
            validator.validate_routing_evidence(errors)
            self.assertTrue(errors)
        after = len(list(Path("/proc/self/fd").iterdir()))
        self.assertLessEqual(after - before, 1)
        descriptor = validator.os.open(
            str(root / "evaluation/evidence/routing-tuning/current"),
            validator.os.O_RDONLY | validator.os.O_DIRECTORY,
        )
        self.addCleanup(validator.os.close, descriptor)
        actual_dup = validator.os.dup
        actual_close = validator.os.close
        duplicates: set[int] = set()

        def record_dup(fd):
            value = actual_dup(fd)
            duplicates.add(value)
            return value

        def fail_duplicate_close(fd):
            if fd in duplicates:
                actual_close(fd)
                raise OSError("forced cleanup failure")
            return actual_close(fd)

        with mock.patch.object(validator.os, "dup", side_effect=record_dup), mock.patch.object(
            validator.os, "close", side_effect=fail_duplicate_close
        ):
            with self.assertRaisesRegex(ValueError, "directory view cleanup failed"):
                validator._routing_directory_view(descriptor)
        for fd in duplicates:
            with self.assertRaises(OSError):
                validator.os.fstat(fd)

    def test_public_initial_view_failures_close_root_and_variant_descriptors(self) -> None:
        """Break caught: an initial snapshot failure leaks its already-open parent fd."""
        if not Path("/proc/self/fd").is_dir():
            self.skipTest("fd accounting unavailable")
        for branch in ("root", "variant"):
            with self.subTest(branch=branch):
                root = self.with_root()
                self.write_current_inventory(root)
                actual_open = validator.os.open
                actual_fstat = validator.os.fstat
                original_view = validator._routing_directory_view
                opened: list[int] = []
                calls = 0

                def record_open(name, flags, *args, **kwargs):
                    fd = actual_open(name, flags, *args, **kwargs)
                    if branch == "root" and name == str(root / "evaluation/evidence/routing-tuning"):
                        opened.append(fd)
                    if branch == "variant" and name == "current" and kwargs.get("dir_fd") is not None:
                        opened.append(fd)
                    return fd

                def fail_selected_view(fd):
                    nonlocal calls
                    calls += 1
                    if branch == "root" or (branch == "variant" and calls % 2 == 0):
                        raise ValueError("injected initial view failure")
                    return original_view(fd)

                before = len(list(Path("/proc/self/fd").iterdir()))
                with mock.patch.object(validator.os, "open", side_effect=record_open), mock.patch.object(
                    validator, "_routing_directory_view", side_effect=fail_selected_view
                ):
                    for _ in range(3):
                        errors: list[str] = []
                        validator.validate_routing_evidence(errors)
                        self.assertTrue(errors, errors)
                after = len(list(Path("/proc/self/fd").iterdir()))
                self.assertLessEqual(after - before, 1)
                self.assertTrue(opened)
                for fd in opened:
                    with self.assertRaises(OSError):
                        actual_fstat(fd)

    def test_public_duplicate_snapshot_cleanup_closes_real_fd(self) -> None:
        """Break caught: a reported duplicate-close failure leaves the real fd open."""
        root = self.with_root()
        self.write_current_inventory(root)
        actual_dup = validator.os.dup
        actual_close = validator.os.close
        actual_fstat = validator.os.fstat
        duplicates: set[int] = set()

        def record_dup(fd):
            duplicate = actual_dup(fd)
            duplicates.add(duplicate)
            return duplicate

        def close_then_report(fd):
            if fd in duplicates:
                actual_close(fd)
                raise OSError("injected cleanup report")
            return actual_close(fd)

        with mock.patch.object(validator.os, "dup", side_effect=record_dup), mock.patch.object(
            validator.os, "close", side_effect=close_then_report
        ):
            errors: list[str] = []
            validator.validate_routing_evidence(errors)
        self.assertIn("routing evidence root is unsafe", errors)
        self.assertTrue(duplicates)
        for fd in duplicates:
            with self.assertRaises(OSError):
                actual_fstat(fd)

    def test_snapshot_scandir_iterator_and_stat_failures_close_duplicate(self) -> None:
        """Break caught: view enumeration failures leave their duplicated fd reachable."""
        root = self.with_root()
        self.write_current_inventory(root)
        directory = root / "evaluation/evidence/routing-tuning/current"
        actual_dup = validator.os.dup
        actual_fstat = validator.os.fstat

        class BrokenIterator:
            def __enter__(self):
                return self

            def __exit__(self, *unused):
                return False

            def __iter__(self):
                raise OSError("iterator failure")

        class BrokenStatEntry:
            name = "entry"

            @staticmethod
            def stat(*unused, **kwargs):
                raise OSError("stat failure")

        class BrokenStatIterator:
            def __enter__(self):
                return self

            def __exit__(self, *unused):
                return False

            def __iter__(self):
                return iter([BrokenStatEntry()])

        for name, scandir_side_effect in (
            ("scandir", OSError("scandir failure")),
            ("iterator", BrokenIterator),
            ("stat", BrokenStatIterator),
        ):
            with self.subTest(name=name):
                descriptor = validator.os.open(
                    str(directory), validator.os.O_RDONLY | validator.os.O_DIRECTORY
                )
                self.addCleanup(validator.os.close, descriptor)
                duplicates: list[int] = []

                def record_dup(fd):
                    duplicate = actual_dup(fd)
                    duplicates.append(duplicate)
                    return duplicate

                side_effect = (
                    scandir_side_effect
                    if isinstance(scandir_side_effect, OSError)
                    else lambda unused, factory=scandir_side_effect: factory()
                )
                with mock.patch.object(validator.os, "dup", side_effect=record_dup), mock.patch.object(
                    validator.os, "scandir", side_effect=side_effect
                ):
                    with self.assertRaisesRegex(ValueError, "directory view is unsafe"):
                        validator._routing_directory_view(descriptor)
                self.assertEqual(len(duplicates), 1)
                with self.assertRaises(OSError):
                    actual_fstat(duplicates[0])

    def test_heldout_routing_evidence_path_is_prohibited_without_reading_it(self) -> None:
        """Break caught: a held-out result path is accepted during E1."""
        root = self.with_root()
        heldout = root / "evaluation/evidence/routing-tuning/current/contract-reconciliation-heldout-positive-r1.md"
        heldout.parent.mkdir(parents=True, exist_ok=True)
        heldout.write_text("not inspected", encoding="utf-8")
        errors: list[str] = []
        validator.validate_routing_evidence(errors)
        self.assertEqual(
            errors,
            ["held-out routing evidence path is prohibited: evaluation/evidence/routing-tuning/current/contract-reconciliation-heldout-positive-r1.md"],
        )
        with tempfile.TemporaryDirectory() as temporary:
            aggregate_root = Path(temporary) / "repository"
            shutil.copytree(
                self.repository_root,
                aggregate_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
            )
            aggregate_heldout = (
                aggregate_root
                / "evaluation/evidence/routing-tuning/current/contract-reconciliation-heldout-positive-r1.md"
            )
            aggregate_heldout.parent.mkdir(parents=True, exist_ok=True)
            aggregate_heldout.write_text("not inspected", encoding="utf-8")
            completed = self.run_aggregate(aggregate_root)
            self.assertEqual(completed.returncode, 1, completed.stderr)
            self.assertIn("held-out routing evidence path is prohibited", completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)

    def test_routing_root_variant_and_leaf_symlinks_are_rejected(self) -> None:
        """Break caught: routing evidence may be supplied through a symlink."""
        for level in ("root", "variant", "leaf"):
            for external in (False, True):
                with self.subTest(level=level, external=external):
                    root = self.with_root()
                    target_root = Path(tempfile.mkdtemp()) if external else root / "internal"
                    self.addCleanup(shutil.rmtree, target_root, ignore_errors=True)
                    if level == "root":
                        target = target_root / "routing-tuning"
                        target.mkdir(parents=True)
                        link = root / "evaluation/evidence/routing-tuning"
                        link.parent.mkdir(parents=True)
                    elif level == "variant":
                        target = target_root / "current"
                        target.mkdir(parents=True)
                        link = root / "evaluation/evidence/routing-tuning/current"
                        link.parent.mkdir(parents=True)
                    else:
                        self.write_current_inventory(root)
                        target = target_root / "record.md"
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text("outside", encoding="utf-8")
                        link = root / "evaluation/evidence/routing-tuning/current/contract-reconciliation-tuning-positive-r1.md"
                        link.unlink()
                    try:
                        link.symlink_to(target, target_is_directory=level != "leaf")
                    except OSError as exc:
                        self.skipTest(f"symlinks unsupported: {exc}")
                    errors: list[str] = []
                    validator.validate_routing_evidence(errors)
                    self.assertTrue(any("must not be a symlink" in error for error in errors), errors)
                    with tempfile.TemporaryDirectory() as temporary:
                        aggregate_root = Path(temporary) / "repository"
                        shutil.copytree(
                            self.repository_root,
                            aggregate_root,
                            ignore=shutil.ignore_patterns(".git", "__pycache__"),
                        )
                        copied_routing = aggregate_root / "evaluation/evidence/routing-tuning"
                        if level == "root":
                            shutil.rmtree(copied_routing)
                        elif level == "variant":
                            shutil.rmtree(copied_routing / "current")
                        aggregate_target_root = (
                            Path(temporary) / "external" if external else aggregate_root / "internal"
                        )
                        if level == "root":
                            aggregate_target = aggregate_target_root / "routing-tuning"
                            aggregate_target.mkdir(parents=True)
                            aggregate_link = aggregate_root / "evaluation/evidence/routing-tuning"
                            aggregate_link.parent.mkdir(parents=True, exist_ok=True)
                        elif level == "variant":
                            aggregate_target = aggregate_target_root / "current"
                            aggregate_target.mkdir(parents=True)
                            aggregate_link = aggregate_root / "evaluation/evidence/routing-tuning/current"
                            aggregate_link.parent.mkdir(parents=True, exist_ok=True)
                        else:
                            self.write_current_inventory(aggregate_root)
                            aggregate_target = aggregate_target_root / "record.md"
                            aggregate_target.parent.mkdir(parents=True, exist_ok=True)
                            aggregate_target.write_text("outside", encoding="utf-8")
                            aggregate_link = aggregate_root / "evaluation/evidence/routing-tuning/current/contract-reconciliation-tuning-positive-r1.md"
                            aggregate_link.unlink()
                        aggregate_link.symlink_to(
                            aggregate_target, target_is_directory=level != "leaf"
                        )
                        completed = self.run_aggregate(aggregate_root)
                        self.assertEqual(completed.returncode, 1, completed.stderr)
                        self.assertIn(
                            f"routing evidence {level} must not be a symlink",
                            completed.stderr,
                        )
                        self.assertNotIn("Traceback", completed.stderr)


    def test_final_candidate_heldout_path_is_not_rejected_by_tuning_guard(self) -> None:
        """Task 10 candidate evidence is outside the E1 tuning-only guard."""
        root = self.with_root()
        path = root / "evaluation/evidence/candidate/contract-reconciliation-heldout-positive-r1.md"
        path.parent.mkdir(parents=True)
        path.write_text("final candidate evidence", encoding="utf-8")
        errors: list[str] = []
        validator.validate_routing_evidence(errors)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
