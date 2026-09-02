"""Focused tests for fail-closed repository-validator boundaries.

Production breaks caught here:
- removing JSON parent guards turns malformed product JSON into tracebacks;
- resolving Markdown destinations before rejecting unsafe forms accepts escapes;
- ignoring a README-documented verifier lets aggregate validation pass after it
  has been removed.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import validate_repo as validator


class RepositoryValidatorTests(unittest.TestCase):
    repository_root = Path(__file__).resolve().parents[1]

    def with_root(self):
        directory = tempfile.TemporaryDirectory()
        previous_root = validator.ROOT
        validator.ROOT = Path(directory.name)
        self.addCleanup(setattr, validator, "ROOT", previous_root)
        self.addCleanup(directory.cleanup)
        return Path(directory.name)

    def run_aggregate(self, root: Path) -> subprocess.CompletedProcess[str]:
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
                    "raise SystemExit(validator.main())"
                ),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    @staticmethod
    def write_json(root: Path, relative: str, payload: object) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    @staticmethod
    def candidate_sample(case_id: str, repetition: int, revision: str) -> str:
        positive = case_id.endswith("-positive")
        return "\n".join(
            (
                "# Final candidate held-out routing observation",
                "",
                f"- Case ID: {case_id}",
                "- Variant: final-candidate",
                f"- Repetition: {repetition}",
                f"- Candidate revision: {revision}",
                f"- Selected: {str(positive).lower()}",
                f"- Entrypoint loaded: {str(positive).lower()}",
                "- Verdict: pass",
                "- Evidence status: active",
                "",
                "## Raw answer",
                "",
                "```text",
                "Synthetic routing observation.",
                "```",
                "",
                "## Manual review",
                "",
                "Synthetic reviewer decision for validator testing.",
                "",
            )
        )


    def copy_candidate_fixture(self) -> Path:
        root = self.with_root()
        revision = "sha256:" + "1" * 64
        evidence = root / "evaluation/evidence/candidate"
        evidence.mkdir(parents=True)
        for case_id in validator.CANDIDATE_CASE_IDS:
            for repetition in validator.CANDIDATE_REPETITIONS:
                (evidence / f"{case_id}-r{repetition}.md").write_text(
                    self.candidate_sample(case_id, repetition, revision),
                    encoding="utf-8",
                )
        manifest = root / "evaluation/runtime-manifest.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps({"runtime_revision": revision}), encoding="utf-8"
        )
        return root

    def test_evaluation_contract_covers_one_off_small_project_near_miss(self) -> None:
        """Break caught: one-off project creation starts the heavy workflow."""
        self.assertEqual(
            validator.EVALUATION_ROUTING_CASES["one-off-small-project-creation"],
            ("near_miss", False),
        )

    def test_public_checkout_does_not_require_local_experiment_outputs(self) -> None:
        """A publishable checkout excludes generated evidence and project history."""
        root = self.with_root()
        shutil.copytree(
            self.repository_root,
            root,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        for relative in (
            "CHANGELOG.md",
            "docs/final-round-report.md",
            "evaluation/runtime-manifest.json",
        ):
            path = root / relative
            if path.exists():
                path.unlink()
        shutil.rmtree(root / "evaluation/evidence", ignore_errors=True)

        result = self.run_aggregate(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_candidate_evidence_requires_exact_current_campaign(self) -> None:
        """Break caught: missing or stale held-out files pass aggregate validation."""
        root = self.copy_candidate_fixture()
        errors: list[str] = []
        validator.validate_candidate_evidence(errors, root)
        self.assertEqual(errors, [])

        missing = (
            root
            / "evaluation/evidence/candidate/contract-reconciliation-heldout-positive-r5.md"
        )
        missing.unlink()
        errors = []
        validator.validate_candidate_evidence(errors, root)
        self.assertTrue(any("missing samples" in error for error in errors), errors)

    def test_candidate_evidence_rejects_stale_revision_and_bad_verdict(self) -> None:
        """Break caught: metadata can claim active evidence for another runtime."""
        root = self.copy_candidate_fixture()
        sample = (
            root
            / "evaluation/evidence/candidate/contract-reconciliation-heldout-near-miss-r1.md"
        )
        text = sample.read_text(encoding="utf-8")
        text = text.replace("- Candidate revision: sha256:", "- Candidate revision: sha256:dead")
        text = text.replace("- Verdict: pass", "- Verdict: fail")
        sample.write_text(text, encoding="utf-8")
        errors: list[str] = []
        validator.validate_candidate_evidence(errors, root)
        self.assertTrue(any("Candidate revision" in error for error in errors), errors)
        self.assertTrue(any("Verdict" in error for error in errors), errors)

    def test_candidate_evidence_rejects_unexpected_and_symlink_entries(self) -> None:
        """Break caught: extra or linked evidence bypasses the closed inventory."""
        root = self.copy_candidate_fixture()
        evidence = root / "evaluation/evidence/candidate"
        (evidence / "unexpected.md").write_text("# unexpected\n", encoding="utf-8")
        link = evidence / "linked.md"
        try:
            link.symlink_to(
                evidence / "contract-reconciliation-heldout-positive-r1.md"
            )
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"symlink unsupported: {exc}")
        errors: list[str] = []
        validator.validate_candidate_evidence(errors, root)
        self.assertTrue(any("unexpected entries" in error for error in errors), errors)

    def test_json_parent_guards_report_findings_without_tracebacks(self) -> None:
        """Break caught: removing object checks before validator field access."""
        for payload in ([], {}, "not an object", 7, True, None):
            with self.subTest(payload=repr(payload)):
                root = self.with_root()
                self.write_json(root, "evaluation/eval-spec.json", payload)
                errors: list[str] = []
                validator.validate_evaluations(errors)
                self.assertTrue(errors)

                self.write_json(root, "release-policy.json", payload)
                errors = []
                validator.validate_release_policy(errors)
                self.assertTrue(errors)



    def test_exact_json_integer_fields_reject_booleans_and_floats(self) -> None:
        """Break caught: accepting Python bool/float where JSON requires int."""
        repository_root = Path(__file__).resolve().parents[1]
        release_policy = json.loads(
            (repository_root / "release-policy.json").read_text(encoding="utf-8")
        )
        evaluation = json.loads(
            (repository_root / "evaluation/eval-spec.json").read_text(encoding="utf-8")
        )
        for invalid in (True, 1.0):
            with self.subTest(release_policy_schema_version=repr(invalid)):
                root = self.with_root()
                payload = dict(release_policy)
                payload["schema_version"] = invalid
                self.write_json(root, "release-policy.json", payload)
                errors: list[str] = []
                validator.validate_release_policy(errors)
                self.assertTrue(errors)
        for invalid in (True, 4.0):
            with self.subTest(evaluation_schema_version=repr(invalid)):
                root = self.with_root()
                payload = dict(evaluation)
                payload["schema_version"] = invalid
                self.write_json(root, "evaluation/eval-spec.json", payload)
                errors = []
                validator.validate_evaluations(errors)
                self.assertTrue(errors)
        for invalid in (True, 1.0):
            with self.subTest(runtime_manifest_bytes=repr(invalid)):
                root = self.with_root()
                self.write_json(
                    root,
                    "evaluation/runtime-manifest.json",
                    {"files": [{"bytes": invalid}]},
                )
                errors = []
                validator.validate_runtime_manifest(errors)
                self.assertIn("runtime manifest files 1 bytes must be an integer", errors)

    def test_all_aggregate_json_entrypoints_fail_closed_for_top_level_shapes(self) -> None:
        """Break caught: any current aggregate JSON loader calls methods on a scalar."""
        values = ([], {}, "scalar", 9, True, None)
        for name in ("evaluation", "policy", "manifest"):
            for payload in values:
                with self.subTest(entrypoint=name, payload=repr(payload)):
                    root = self.with_root()
                    errors: list[str] = []
                    if name == "evaluation":
                        self.write_json(root, "evaluation/eval-spec.json", payload)
                        validator.validate_evaluations(errors)
                    elif name == "policy":
                        self.write_json(root, "release-policy.json", payload)
                        validator.validate_release_policy(errors)
                    else:
                        self.write_json(root, "evaluation/runtime-manifest.json", payload)
                        validator.validate_runtime_manifest(errors)
                    self.assertTrue(errors)

    def test_all_aggregate_json_entrypoints_fail_closed_for_nested_shapes(self) -> None:
        """Break caught: current nested JSON objects/lists are indexed before guards."""
        evaluation = json.loads(
            (self.repository_root / "evaluation/eval-spec.json").read_text(encoding="utf-8")
        )
        policy = json.loads(
            (self.repository_root / "release-policy.json").read_text(encoding="utf-8")
        )
        cases = (
            ("evaluation", {"campaign": [], "routing_cases": [], "behavior_cases": []}),
            ("evaluation", {"routing_cases": ["not an object"]}),
            ("evaluation", {"behavior_cases": [None]}),
            ("policy", {"suffix_allowlists": [], "limits": [], "secret_scan": []}),
            ("manifest", {"files": ["not an object", {"bytes": True}, {"bytes": 1.0}]}),
        )
        for name, changes in cases:
            with self.subTest(entrypoint=name, changes=changes):
                root = self.with_root()
                errors: list[str] = []
                if name == "evaluation":
                    payload = dict(evaluation)
                    payload.update(changes)
                    self.write_json(root, "evaluation/eval-spec.json", payload)
                    validator.validate_evaluations(errors)
                elif name == "policy":
                    payload = dict(policy)
                    payload.update(changes)
                    self.write_json(root, "release-policy.json", payload)
                    validator.validate_release_policy(errors)
                else:
                    self.write_json(root, "evaluation/runtime-manifest.json", changes)
                    validator.validate_runtime_manifest(errors)
                self.assertTrue(errors)

    def test_markdown_rejects_unsafe_destinations_before_resolution(self) -> None:
        """Break caught: normalizing an unsafe local target into an accepted path."""
        unsafe_targets = (
            "/etc/passwd",
            "C:/Windows/System32",
            "C:relative.txt",
            "//server/share/file.md",
            r"\\server\share\file.md",
            r"folder\file.md",
            "../README.md",
            "./README.md",
            "nested//file.md",
            "%2e%2e/README.md",
        )
        for target in unsafe_targets:
            with self.subTest(target=target):
                root = self.with_root()
                source = root / "docs/source.md"
                source.parent.mkdir(parents=True)
                source.write_text(f"[unsafe]({target})\n", encoding="utf-8")
                errors: list[str] = []
                validator.validate_markdown_links(errors)
                self.assertTrue(errors, target)

    def test_markdown_accepts_contained_and_external_destinations(self) -> None:
        """Break caught: treating URI schemes or anchors as unsafe local paths."""
        root = self.with_root()
        (root / "docs").mkdir()
        (root / "README.md").write_text("# Root\n", encoding="utf-8")
        (root / "docs/guide.md").write_text("# Guide\n", encoding="utf-8")
        (root / "source.md").write_text(
            "\n".join(
                (
                    "[same](#local-anchor)",
                    "[relative](docs/guide.md#guide)",
                    "[root](README.md)",
                    "[https](https://example.test/path)",
                    "[mail](mailto:maintainer@example.test)",
                    "[custom](codex+fixture:entrypoint)",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        errors: list[str] = []
        validator.validate_markdown_links(errors)
        self.assertEqual(errors, [])

    def test_markdown_rejects_symlink_leaf_that_escapes_repository(self) -> None:
        """Break caught: accepting a repository link whose leaf resolves outside."""
        root = self.with_root()
        source = root / "docs/source.md"
        source.parent.mkdir(parents=True)
        outside = root.parent / "outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        self.addCleanup(outside.unlink)
        link = root / "docs/outside.md"
        try:
            link.symlink_to(outside)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"symlink unsupported: {exc}")
        source.write_text("[escape](outside.md)\n", encoding="utf-8")
        errors: list[str] = []
        validator.validate_markdown_links(errors)
        self.assertTrue(errors)

    def test_each_documented_verifier_is_required(self) -> None:
        """Break caught: omitting a README-listed verifier from aggregate checks."""
        entrypoints = (
            "scripts/test_runtime_revision.py",
            "scripts/test_control_evidence_validator.py",
            "scripts/test_repo_validator.py",
            "scripts/runtime_revision.py",
        )
        for missing in entrypoints:
            with self.subTest(missing=missing):
                root = self.with_root()
                commands = "\n".join(f"python3 -B {path}" for path in entrypoints)
                (root / "README.md").write_text(commands + "\n", encoding="utf-8")
                for entrypoint in entrypoints:
                    path = root / entrypoint
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("# fixture\n", encoding="utf-8")
                (root / missing).unlink()
                errors: list[str] = []
                validator.validate_documented_verifier_entrypoints(errors)
                self.assertIn(f"missing documented verifier: {missing}", errors)

    def test_current_documented_verifiers_are_present(self) -> None:
        """Break caught: a current README command points to no regular script."""
        errors: list[str] = []
        validator.validate_documented_verifier_entrypoints(errors)
        self.assertEqual(errors, [])

    def test_markdown_scanner_checks_complete_balanced_escaped_and_query_destinations(self) -> None:
        """Break caught: regex truncation or URL reclassification hides escapes."""
        root = self.with_root()
        docs = root / "docs"
        docs.mkdir()
        (docs / "safe(ignored)").mkdir()
        (root / "outside.md").write_text("outside\n", encoding="utf-8")
        (docs / "foo(bar).md").write_text("safe\n", encoding="utf-8")
        (docs / "query.md").write_text("safe\n", encoding="utf-8")
        (docs / "source.md").write_text(
            "\n".join(
                (
                    "[balanced escape](safe(ignored)/../../outside.md)",
                    r"[escaped parens](foo\(bar\).md)",
                    "[encoded colon](https%3A/../../../outside.md)",
                    "[query](query.md?view=1#section)",
                    "[angle](<query.md?view=1#section> \"title\")",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        errors: list[str] = []
        validator.validate_markdown_links(errors)
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(any("safe(ignored)/../../outside.md" in error for error in errors))
        self.assertTrue(any("https%3A/../../../outside.md" in error for error in errors))

    def test_markdown_scanner_balances_nested_link_and_image_labels(self) -> None:
        """Break caught: first closing label bracket hides an unsafe destination."""
        root = self.with_root()
        docs = root / "docs"
        docs.mkdir()
        (docs / "contained.md").write_text("contained\n", encoding="utf-8")
        (docs / "source.md").write_text(
            "\n".join(
                (
                    "[outer [inner]](../outside.md)",
                    "![nested [alt]](../outside.png)",
                    "[safe [nested]](contained.md)",
                    "![safe [image]](contained.md)",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        errors: list[str] = []
        validator.validate_markdown_links(errors)
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(all("unsafe local link" in error for error in errors), errors)

    def test_markdown_surface_scans_inner_images_and_multiline_links_once(self) -> None:
        """Break caught: outer success or a line break hides an inner destination."""
        markdown = """[![alt](../outside.png)](contained.md)
[multi
line](../outside.md)
[duplicate](contained.md)
`[ignored](../ignored.md)`
```markdown
[fenced](../fenced.md)
```
"""
        _headings, destinations = validator.markdown_surface(markdown)
        self.assertEqual(
            destinations,
            {"../outside.png", "../outside.md", "contained.md"},
        )
        root = self.with_root()
        (root / "contained.md").write_text("contained\n", encoding="utf-8")
        (root / "source.md").write_text(markdown, encoding="utf-8")
        errors: list[str] = []
        validator.validate_markdown_links(errors)
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(all("unsafe local link" in error for error in errors), errors)
        with tempfile.TemporaryDirectory() as temporary:
            aggregate_root = Path(temporary) / "repository"
            shutil.copytree(
                self.repository_root,
                aggregate_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
            )
            with (aggregate_root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\n[![alt](../outside.png)](README.md)\n[multi\nline](../outside.md)\n")
            completed = self.run_aggregate(aggregate_root)
            self.assertEqual(completed.returncode, 1, completed.stderr)
            self.assertIn("unsafe local link in README.md: ../outside.png", completed.stderr)
            self.assertIn("unsafe local link in README.md: ../outside.md", completed.stderr)

    def test_markdown_surface_masks_crossline_code_without_hiding_outer_multiline_links(self) -> None:
        """Break caught: per-line code masking exposes a fake crossline link."""
        markdown = """`code
[ignored](../multi-code.md)
`
``code
[also ignored](../double-code.md)
``
[multi
line](../outside.md)
[safe](contained.md)
"""
        _headings, destinations = validator.markdown_surface(markdown)
        self.assertEqual(destinations, {"../outside.md", "contained.md"})
        root = self.with_root()
        (root / "contained.md").write_text("contained\n", encoding="utf-8")
        (root / "source.md").write_text(markdown, encoding="utf-8")
        errors: list[str] = []
        validator.validate_markdown_links(errors)
        self.assertEqual(errors, ["unsafe local link in source.md: ../outside.md"])
        with tempfile.TemporaryDirectory() as temporary:
            aggregate_root = Path(temporary) / "repository"
            shutil.copytree(
                self.repository_root,
                aggregate_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
            )
            with (aggregate_root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\n`code\n[ignored](../multi-code.md)\n`\n")
            completed = self.run_aggregate(aggregate_root)
            self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_visible_markdown_masks_crossline_code_before_multiline_comments(self) -> None:
        """Break caught: a code-span comment opener must not hide an outside link."""
        markdown = """`code
<!--
`
[outside](../outside.md)
-->
``code
<!--
``
[double](../double.md)
<!--
[commented](../commented.md)
-->
```markdown
[fenced](../fenced.md)
```
[safe](contained.md)
`unclosed
[ignored](../unclosed-code.md)
"""
        _headings, destinations = validator.markdown_surface(markdown)
        self.assertEqual(
            destinations,
            {"../outside.md", "../double.md", "../unclosed-code.md", "contained.md"},
        )
        visible, constructs_closed = validator.visible_markdown_document(markdown)
        self.assertTrue(constructs_closed)
        self.assertNotIn("../commented.md", "\n".join(line for _, line in visible))
        _visible, unclosed_comment = validator.visible_markdown_document(
            "<!--\n[ignored](../unclosed-comment.md)\n"
        )
        self.assertFalse(unclosed_comment)
        self.assertNotIn(
            "../unclosed-comment.md",
            validator.markdown_surface("<!--\n[ignored](../unclosed-comment.md)\n")[1],
        )
        root = self.with_root()
        (root / "contained.md").write_text("contained\n", encoding="utf-8")
        (root / "source.md").write_text(markdown, encoding="utf-8")
        errors: list[str] = []
        validator.validate_markdown_links(errors)
        self.assertCountEqual(
            errors,
            [
                "unsafe local link in source.md: ../double.md",
                "unsafe local link in source.md: ../outside.md",
                "unsafe local link in source.md: ../unclosed-code.md",
            ],
        )
        with tempfile.TemporaryDirectory() as temporary:
            aggregate_root = Path(temporary) / "repository"
            shutil.copytree(
                self.repository_root,
                aggregate_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
            )
            with (aggregate_root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\n`code\n<!--\n`\n[outside](../outside.md)\n-->\n")
            completed = self.run_aggregate(aggregate_root)
            self.assertEqual(completed.returncode, 1, completed.stderr)
            self.assertIn("unsafe local link in README.md: ../outside.md", completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)

    def test_escaped_and_unmatched_backtick_runs_leave_unsafe_links_visible(self) -> None:
        """Break caught: literal or unmatched runs cannot hide later visible links."""
        fixtures = {
            "escaped": """\\`
[visible unsafe](../outside.md)
`
""",
            "unmatched": """` unmatched
``code
<!--
``
[visible unsafe](../outside.md)
-->
""",
        }
        for name, markdown in fixtures.items():
            with self.subTest(name=name):
                self.assertEqual(validator.markdown_surface(markdown)[1], {"../outside.md"})
                root = self.with_root()
                (root / "source.md").write_text(markdown, encoding="utf-8")
                errors: list[str] = []
                validator.validate_markdown_links(errors)
                self.assertEqual(errors, ["unsafe local link in source.md: ../outside.md"])
                with tempfile.TemporaryDirectory() as temporary:
                    aggregate_root = Path(temporary) / "repository"
                    shutil.copytree(
                        self.repository_root,
                        aggregate_root,
                        ignore=shutil.ignore_patterns(".git", "__pycache__"),
                    )
                    with (aggregate_root / "README.md").open("a", encoding="utf-8") as handle:
                        handle.write("\n" + markdown)
                    completed = self.run_aggregate(aggregate_root)
                    self.assertEqual(completed.returncode, 1, completed.stderr)
                    self.assertIn(
                        "unsafe local link in README.md: ../outside.md", completed.stderr
                    )
                    self.assertNotIn("Traceback", completed.stderr)
        odd_even = """\\\\`
[ignored](../even-code.md)
`
\\`
[visible](../odd-escaped.md)
`
"""
        self.assertEqual(validator.markdown_surface(odd_even)[1], {"../odd-escaped.md"})

    def test_odd_escaped_multibacktick_residual_keeps_outside_link_visible(self) -> None:
        """Break caught: only the first tick of an odd-escaped run is literal."""
        markdown = """\\``
<!--
`
[visible unsafe](../outside.md)
-->
"""
        self.assertEqual(validator.markdown_surface(markdown)[1], {"../outside.md"})
        root = self.with_root()
        (root / "source.md").write_text(markdown, encoding="utf-8")
        errors: list[str] = []
        validator.validate_markdown_links(errors)
        self.assertEqual(errors, ["unsafe local link in source.md: ../outside.md"])
        with tempfile.TemporaryDirectory() as temporary:
            aggregate_root = Path(temporary) / "repository"
            shutil.copytree(
                self.repository_root,
                aggregate_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
            )
            with (aggregate_root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\n" + markdown)
            completed = self.run_aggregate(aggregate_root)
            self.assertEqual(completed.returncode, 1, completed.stderr)
            self.assertIn("unsafe local link in README.md: ../outside.md", completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)

    def test_backtick_run_escape_parity_preserves_residual_delimiters(self) -> None:
        """Break caught: residual runs must match normally without hardcoded lengths."""
        for slash_count in (1, 2, 3, 4):
            for run_length in (1, 2, 3, 4, 7):
                with self.subTest(slash_count=slash_count, run_length=run_length):
                    residual_length = run_length - 1 if slash_count % 2 else run_length
                    opener = "\\" * slash_count + "`" * run_length
                    closer = "`" * residual_length
                    matched = (
                        opener
                        + " code\n[inside](../inside.md)\nclose"
                        + closer
                        + "\n[outside](../outside.md)\n"
                    )
                    expected_matched = {"../outside.md"}
                    if residual_length == 0:
                        expected_matched.add("../inside.md")
                    self.assertEqual(validator.markdown_surface(matched)[1], expected_matched)
                    unmatched = opener + "\n[visible](../visible.md)\n"
                    self.assertEqual(
                        validator.markdown_surface(unmatched)[1], {"../visible.md"}
                    )

    def test_escaped_html_comment_opener_leaves_unsafe_link_visible(self) -> None:
        """Break caught: an odd-escaped comment opener is literal Markdown."""
        escaped = """\\<!--
[visible unsafe](../outside.md)
-->
"""
        even = """\\\\<!--
[ignored](../even-comment.md)
-->
"""
        self.assertEqual(validator.markdown_surface(escaped)[1], {"../outside.md"})
        self.assertEqual(validator.markdown_surface(even)[1], set())
        root = self.with_root()
        (root / "source.md").write_text(escaped, encoding="utf-8")
        errors: list[str] = []
        validator.validate_markdown_links(errors)
        self.assertEqual(errors, ["unsafe local link in source.md: ../outside.md"])
        with tempfile.TemporaryDirectory() as temporary:
            aggregate_root = Path(temporary) / "repository"
            shutil.copytree(
                self.repository_root,
                aggregate_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
            )
            with (aggregate_root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\n" + escaped)
            completed = self.run_aggregate(aggregate_root)
            self.assertEqual(completed.returncode, 1, completed.stderr)
            self.assertIn("unsafe local link in README.md: ../outside.md", completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)

    def test_html_comment_state_survives_a_fenced_region(self) -> None:
        """Break caught: a real comment remains open across excluded fence lines."""
        markdown = """<!-- real comment
```text
fenced-looking comment text
```
[commented](../commented.md)
-->
[outside](README.md)
<!-- unclosed
[hidden](../hidden.md)
"""
        visible, constructs_closed = validator.visible_markdown_document(markdown)
        self.assertFalse(constructs_closed)
        self.assertNotIn("../commented.md", "\n".join(line for _, line in visible))
        self.assertEqual(validator.markdown_surface(markdown)[1], {"README.md"})
        root = self.with_root()
        (root / "README.md").write_text("contained\n", encoding="utf-8")
        (root / "source.md").write_text(markdown, encoding="utf-8")
        errors: list[str] = []
        validator.validate_markdown_links(errors)
        self.assertEqual(errors, [])
        with tempfile.TemporaryDirectory() as temporary:
            aggregate_root = Path(temporary) / "repository"
            shutil.copytree(
                self.repository_root,
                aggregate_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
            )
            with (aggregate_root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\n" + markdown)
            completed = self.run_aggregate(aggregate_root)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertNotIn("unsafe local link in README.md: ../commented.md", completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)

    def test_markdown_failed_destination_candidates_hit_shared_scan_limit(self) -> None:
        """Break caught: repeated incomplete ]( candidates cannot rescan suffixes."""
        for depth in (250, 500):
            with self.subTest(depth=depth):
                markdown = "[" * depth + "](" * depth + "x"
                with self.assertRaises(validator.MarkdownScanLimit):
                    validator.markdown_inline_scan(markdown)
        markdown = "[" * 500 + "](" * 500 + "x"
        root = self.with_root()
        (root / "source.md").write_text(markdown, encoding="utf-8")
        errors: list[str] = []
        validator.validate_markdown_links(errors)
        self.assertEqual(errors, ["Markdown scan limit in source.md"])
        with tempfile.TemporaryDirectory() as temporary:
            aggregate_root = Path(temporary) / "repository"
            shutil.copytree(
                self.repository_root,
                aggregate_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
            )
            with (aggregate_root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\n" + markdown + "\n")
            completed = self.run_aggregate(aggregate_root)
            self.assertEqual(completed.returncode, 1, completed.stderr)
            self.assertIn("Markdown scan limit in README.md", completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)

    def test_markdown_shared_scan_budget_accepts_large_valid_input(self) -> None:
        """Break caught: the shared limit must not reject ordinary large documents."""
        markdown = "[contained](contained.md)\n" * 10_000
        self.assertEqual(validator.markdown_surface(markdown)[1], {"contained.md"})

    def test_nested_label_scan_has_linear_step_bound(self) -> None:
        """Break caught: rescanning every nested opener makes label parsing quadratic."""
        depth = 800
        markdown = "[" * depth + "label" + "]" * depth + "(contained.md)"
        destinations, steps = validator.markdown_inline_scan(markdown)
        self.assertEqual(destinations, {"contained.md"})
        self.assertLessEqual(steps, len(markdown) * 12)

    def test_invocation_policy_parent_requires_an_object_through_aggregate_main(self) -> None:
        """Break caught: non-object invocation_policy reaches value comparison."""
        for invalid in ([], "scalar", 9, True, None):
            with self.subTest(invalid=repr(invalid)), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "repository"
                shutil.copytree(
                    self.repository_root,
                    root,
                    ignore=shutil.ignore_patterns(".git", "__pycache__"),
                )
                path = root / "evaluation/eval-spec.json"
                payload = json.loads(path.read_text(encoding="utf-8"))
                payload["campaign"]["invocation_policy"] = invalid
                path.write_text(json.dumps(payload), encoding="utf-8")
                completed = self.run_aggregate(root)
                self.assertEqual(completed.returncode, 1, completed.stderr)
                self.assertIn(
                    "evaluation/eval-spec.json campaign.invocation_policy must be an object",
                    completed.stderr,
                )
                self.assertNotIn("Traceback", completed.stderr)



    def test_markdown_nul_and_file_uris_fail_closed_through_aggregate_main(self) -> None:
        """Break caught: decoded NUL/file URI escapes containment or traceback."""
        unsafe_destinations = ("bad%00name.md", "file:///etc/passwd", "file:///C:/Windows/win.ini")
        for destination in unsafe_destinations:
            with self.subTest(destination=destination), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "repository"
                shutil.copytree(
                    self.repository_root,
                    root,
                    ignore=shutil.ignore_patterns(".git", "__pycache__"),
                )
                with (root / "README.md").open("a", encoding="utf-8") as handle:
                    handle.write(f"\n[named unsafe]({destination})\n")
                completed = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        "-c",
                        (
                            "import sys; from pathlib import Path; "
                            f"sys.path.insert(0, {str(self.repository_root / 'scripts')!r}); "
                            "import validate_repo as validator; "
                            f"validator.ROOT = Path({str(root)!r}); "
                            "raise SystemExit(validator.main())"
                        ),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 1, completed.stderr)
                self.assertIn("unsafe local link in README.md", completed.stderr)
                self.assertNotIn("Traceback", completed.stderr)

    def test_evaluation_campaign_fields_require_exact_json_types(self) -> None:
        """Break caught: Python equality accepts float/int and int/bool substitutions."""
        evaluation = json.loads(
            (self.repository_root / "evaluation/eval-spec.json").read_text(encoding="utf-8")
        )
        mutations = (
            ("repetitions", 5.0, "campaign.repetitions must be an integer"),
            ("control_required", 1, "campaign.control_required must be a Boolean"),
            ("manual_review_required", 1, "campaign.manual_review_required must be a Boolean"),
            ("max_composition_depth", 2.0, "campaign.invocation_policy.max_composition_depth must be an integer"),
        )
        for field, invalid, finding in mutations:
            with self.subTest(field=field, invalid=repr(invalid)):
                root = self.with_root()
                payload = json.loads(json.dumps(evaluation))
                if field == "max_composition_depth":
                    payload["campaign"]["invocation_policy"][field] = invalid
                else:
                    payload["campaign"][field] = invalid
                self.write_json(root, "evaluation/eval-spec.json", payload)
                errors: list[str] = []
                validator.validate_evaluations(errors)
                self.assertIn(f"evaluation/eval-spec.json {finding}", errors)

    def test_markdown_rejects_parent_symlink_and_accepts_reference_destination(self) -> None:
        """Break caught: omitting physical containment for parent symlink paths."""
        root = self.with_root()
        docs = root / "docs"
        docs.mkdir()
        outside = root.parent / "outside-parent"
        outside.mkdir(exist_ok=True)
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        (outside / "outside.md").write_text("outside\n", encoding="utf-8")
        try:
            (docs / "parent").symlink_to(outside, target_is_directory=True)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"symlink unsupported: {exc}")
        (docs / "contained.md").write_text("contained\n", encoding="utf-8")
        (docs / "source.md").write_text(
            "[parent escape](parent/outside.md)\n[reference]: contained.md \"title\"\n",
            encoding="utf-8",
        )
        errors: list[str] = []
        validator.validate_markdown_links(errors)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("parent/outside.md", errors[0])

    def test_documented_verifier_parser_handles_fences_continuations_and_dot_slash(self) -> None:
        """Break caught: shell formatting removes a README verifier from inventory."""
        readme = """# Fixture

```bash
python3 -B \\
  scripts/continued_validator.py
python3 -B ./scripts/dot_validator.py
```
"""
        self.assertEqual(
            validator.documented_verifier_entrypoints(readme),
            {"scripts/continued_validator.py", "scripts/dot_validator.py"},
        )
        root = self.with_root()
        base = "\n".join(
            f"python3 -B {entrypoint}" for entrypoint in validator.DOCUMENTED_VERIFIER_BASE
        )
        (root / "README.md").write_text(base + "\n" + readme, encoding="utf-8")
        for entrypoint in validator.DOCUMENTED_VERIFIER_BASE | {"scripts/continued_validator.py"}:
            path = root / entrypoint
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# fixture\n", encoding="utf-8")
        errors: list[str] = []
        validator.validate_documented_verifier_entrypoints(errors)
        self.assertIn("missing documented verifier: scripts/dot_validator.py", errors)

    def test_aggregate_cli_fails_for_each_current_documented_verifier_removal(self) -> None:
        """Break caught: deleting aggregate verifier wiring hides README omissions."""
        entrypoints = tuple(sorted(validator.documented_verifier_entrypoints(
            (self.repository_root / "README.md").read_text(encoding="utf-8")
        )))
        self.assertEqual(len(entrypoints), 5)
        for missing in entrypoints:
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "repository"
                shutil.copytree(
                    self.repository_root,
                    root,
                    ignore=shutil.ignore_patterns(".git", "__pycache__"),
                )
                (root / missing).unlink()
                completed = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        "-c",
                        (
                            "import sys; from pathlib import Path; "
                            f"sys.path.insert(0, {str(self.repository_root / 'scripts')!r}); "
                            "import validate_repo as validator; "
                            f"validator.ROOT = Path({str(root)!r}); "
                            "raise SystemExit(validator.main())"
                        ),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 1, completed.stderr)
                self.assertIn(f"missing documented verifier: {missing}", completed.stderr)


if __name__ == "__main__":
    unittest.main()
