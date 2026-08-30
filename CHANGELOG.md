# Changelog

All notable changes to this project are documented here. Releases use Semantic
Versioning through Git tags.

## Unreleased

### Round 1 planning state

- Implemented Proposal 3's fail-closed repository-validator boundaries and
  focused TDD suite. JSON entrypoints now report malformed parent or nested
  shapes without tracebacks; Markdown destinations reject lexical, Windows,
  UNC, percent-decoded, and symlink escapes; and aggregate validation requires
  every local verifier documented in README. No runtime bundle, manifest, real
  evidence, host state, or release artifact was changed.

- Implemented Proposal 5's schema-v2 host raw-evidence validator with temporary
  synthetic fixtures for exact fields, runtime binding, containment, file facts,
  status restrictions, and read-time identity drift. No real host lifecycle or
  raw-evidence artifact was created; current support records remain unverified
  or unavailable.

- Recorded the approved in-round A2 scope amendment: every optimization round
  must explicitly review capability necessity, architecture necessity, and
  redundancy/ownership through a per-material-subject necessity ledger. The
  amendment requires proportionate consumer/contract discovery, treats
  hypothetical consumers as uncertainty rather than necessity, preserves a
  no-forced-change threshold, and keeps final cleanup as the stronger separate
  execution gate. Its product documents, minimal runtime instruction/review-
  matrix edits, and isolated after-change pressure test are complete and the
  behavior rereview passed. The Package-B manifest was refreshed after A2 to
  `sha256:7fead2ced27f63e95725f251c217641363bded1bd1b12765265566ba9799dfd4`.
- Recorded the user's approval of Optimization Round-1 Proposals 2, 3, 4, and
  5: canonical runtime revision, raw host-evidence binding, fail-closed
  repository validation, and routing minimal-pair evidence with conditional
  wording only after an observed miss.
- Recorded Proposal 1 as rejected. Staged behavior fixtures, runner/oracles,
  fresh behavior controls, and the Proposal-1 campaign are not authorized for
  this round.
- Advanced the open round to `DOC_UPDATE / ACTIVE` and established the
  README/design-first contract and implementation addendum. Proposals 2 and 3
  are now implemented and locally verified; Proposal 4 remains pending.
- Completed Proposal 4 E1 locally: schema-v4 now has the closed tuning and
  held-out routing-pair inventory, and a deterministic validator plus temporary
  fixtures gates pair drift and any held-out evidence path. No routing outcome
  or product evidence was created; E2 observations remain pending.
- Completed Proposal 4 E2 with a comparable project-level fixture: the exact pre-change description passed all five positive and all five near-miss repetitions for both selection and entrypoint loading. The temporary conditional predicate was withdrawn byte-for-byte, so no conditional-candidate campaign was eligible. Ten current tuning records are preserved; held-out outcomes remain untouched.
- Defined Round-1 acceptance as reconciled approved scope, current runtime
  manifest, passing focused and aggregate validation, evidence-backed routing
  branching, preserved rejection scope, and disclosed limitations. Final
  candidate, held-out routing, real-host, package, publication, and portability
  claims remain future Task-10 gates; this planning state is not release
  evidence.

### Added

- Ten manually reviewed, final-runtime held-out routing observations: five
  substantial engineering-contract requests selected and loaded the Skill, and
  five bounded factual-correction near misses did neither. These are explicitly
  routing-only evidence, not a full candidate behavior or release-grade result.

- A dependency-free, domain-separated runtime revision helper, focused TDD
  suite, and checked development manifest. The helper recomputes revisions from
  checkout/archive bytes and normalized modes; it keeps receipt policy identity
  separate and provides future evaluation, host, and package binding checks
  without creating candidate, host, archive, or receipt evidence.

- Root project contract, installation and migration guidance, validation
  instructions, project status, compatibility targets, and acceptance criteria.
- Detailed round protocol, comprehensive review matrix, final-round gates,
  durable iteration-state template, and schema-v4 behavioral evaluations.
- Twenty preserved, manually reviewed no-Skill control samples covering four
  high-risk behavior cases.
- Per-host support records and focused host-evidence validator tests for Codex
  Desktop/CLI, Claude Code, and Gemini CLI.
- A focused control-evidence suite covering semantic Markdown sections,
  canonical execution metadata, exact verdict tokens, whitespace boundaries,
  and closed directory inventory.
- MIT license, deterministic release policy, and a dependency-free local
  repository validator.

### Changed

- Completed final Round-2 hygiene: removed the ignored temporary control plane and one-off E2 runner from the final tree, restored the canonical `Self Iteration` display label, and reconciled the current status, repository layout, and final-round evidence.

- Split the original monolithic Skill into a concise entry point and
  progressively loaded references.
- Distinguished baseline delivery from optimization rounds and lifecycle phase
  from execution status.
- Required full coverage within every round, strict sequential barriers, user
  approval, final repository hygiene, and horizon expansion.
- Clarified that comprehensive review has no proposal quota: all credible
  net-positive findings are reported, while unsupported or negative-value
  changes are omitted.
- Closed the architectural baseline without claiming candidate behavior,
  independent host lifecycle support, portability, publication, or release.
- Corrected Skill text and metadata file permissions from executable to regular
  text-file modes.
