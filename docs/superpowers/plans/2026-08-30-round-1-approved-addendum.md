# Optimization Round 1 — Approved Implementation Addendum

- Date: 2026-08-30
- Round: 1 of 3
- Lifecycle: `IMPLEMENT / ACTIVE`
- Implementation status: Packages B (Proposal 2 runtime revision), C
  (Proposal 5 host raw evidence), and D (Proposal 3 fail-closed repository
  validator) are implemented and locally verified; Package E remains pending.

## Decision and authority boundary

The Round-1 review completed before this addendum. The user approved Proposals
2, 3, 4, and 5 and explicitly rejected Proposal 1.

Approved scope:

1. Proposal 2 — versioned, domain-separated runtime revision with independent
   release-policy identity;
2. Proposal 3 — fail-closed JSON, Markdown-containment, and documented-verifier
   validation;
3. Proposal 4 — routing tuning/held-out minimal pairs, current tuning
   observations, and runtime wording only after an observed miss; and
4. Proposal 5 — raw host-evidence binding, dependent on Proposal 2.

Rejected and prohibited in this round:

- Proposal-1 staged behavior fixtures, runner/oracles, fresh behavior controls,
  and behavior control/candidate campaigns;
- candidate behavior results or `evaluation/eval-result.json`;
- held-out routing execution before Task 10;
- real host installation/lifecycle mutation or an L5/L6 claim;
- release archive/receipt generation, publication, Git mutation, new external
  dependencies, or Round-2 reading/planning; and
- semantic reading or use of the final-round instructions before the final
  authorized round. Generic byte hashing or static repository checks must never
  be represented as a final-gate assessment.

The implementation stays dependency-free on Python 3.9+. Every mutation remains
inside this repository and uses reviewable text files. No package below expands
the user's external, destructive, host-installation, or publication authority.

## Documentation-first gate already established

Before any code, schema, runtime, test, or evaluation implementation, the
following product contracts were updated:

- `README.md` — approved/rejected scope, pending state, technical boundary,
  Round-1 acceptance, and future Task-10 gates;
- `docs/superpowers/specs/2026-08-29-cross-host-self-iteration-design.md` —
  runtime/policy identities, host raw-evidence schema, fail-closed rules,
  routing pair IDs, conditional wording, and closure boundary; and
- `CHANGELOG.md` — the user decision and planning-only, non-release state.

This addendum is the exact implementation plan. If implementation disproves one
of its material assumptions, stop, update README/design first, and request a new
decision only when the correction changes user-approved semantics or scope.

## Planned product file set

Expected new deterministic development files:

```text
evaluation/runtime-manifest.json
scripts/runtime_revision.py
scripts/test_runtime_revision.py
scripts/test_repo_validator.py
scripts/test_routing_evidence_validator.py
```

Expected produced routing-tuning evidence, only after actual fresh observations:

```text
evaluation/evidence/routing-tuning/current/
  contract-reconciliation-tuning-positive-r1.md ... -r5.md
  contract-reconciliation-tuning-near-miss-r1.md ... -r5.md
```

Only if current tuning observes a miss and the approved predicate is applied:

```text
evaluation/evidence/routing-tuning/conditional-candidate/
  contract-reconciliation-tuning-positive-r1.md ... -r5.md
  contract-reconciliation-tuning-near-miss-r1.md ... -r5.md
```

No empty evidence directories or placeholder results are created. No held-out
evidence file is created in Round 1. Temporary negative fixtures stay inside
`tempfile.TemporaryDirectory`; they are not product evidence.

Expected existing-file changes during implementation:

```text
README.md
CHANGELOG.md
docs/host-support.md
docs/superpowers/specs/2026-08-29-cross-host-self-iteration-design.md
evaluation/eval-spec.json
scripts/test_host_support_validator.py
scripts/validate_repo.py
self-iteration/assets/iteration-state.md
self-iteration/SKILL.md
self-iteration/references/review-matrix.md
self-iteration/references/round-protocol.md
```

The A2 scope amendment requires minimal edits to `self-iteration/SKILL.md` and
`self-iteration/references/review-matrix.md`; those runtime-byte changes make
the previously checked Package-B manifest stale, so regenerate and verify
`evaluation/runtime-manifest.json` before Package B Fix Round 2 resumes. This
four-document A2 amendment alone does not stale the manifest. Proposal 4 may
later make a further conditional `SKILL.md` wording edit only if fresh current
tuning observations demonstrate the approved routing miss; every such runtime
edit also requires manifest regeneration and checking before reconciliation.

## Shared technical contracts

### Runtime manifest schema and revision

`evaluation/runtime-manifest.json` is development metadata and is never packaged.
Its schema-version-1 object has exactly:

```text
schema_version
domain
algorithm
runtime_root
files
runtime_revision
```

`domain` names the versioned Self Iteration runtime-revision algorithm;
`algorithm` is `sha256`; and `runtime_root` is the canonical repository-relative
root `self-iteration`. `files` is sorted by canonical POSIX relative path. Every
entry has exactly:

```text
path
mode
bytes
sha256
```

Runtime revision v1 uses exact representation `sha256:<64 lowercase hex>` and
exact domain literal `self-iteration/runtime-revision/v1` (34 ASCII/UTF-8
bytes). Define `frame(x) = u64be(len(x)) + x`, with byte length and an unsigned
64-bit big-endian prefix. The SHA-256 input is exactly:

```text
frame(domain)
+ u64be(file_count)
+ for each entry sorted by canonical path UTF-8 bytes:
    frame(path UTF-8) + frame(mode ASCII) + frame(raw file bytes)
```

Every path is non-empty, runtime-root-relative, canonical POSIX, strict UTF-8,
already Unicode NFC, slash-separated, and unique after normalization. Reject
absolute paths, backslashes, NULs, empty segments, `.`, `..`, duplicate paths,
and any count/length that cannot fit u64. Sort by unsigned lexicographic ordering
of the canonical UTF-8 bytes.

For a checkout snapshot, derive mode from `lstat().st_mode` after rejecting
symlinks/non-regular files; normalize to ASCII `0755` exactly when the owner-
execute bit is set, otherwise `0644`. Read no-follow and fail on identity/size
change while reading. For a rootless author-packager ZIP, use each member path
directly and derive mode from the Unix bits in `external_attr >> 16` with the
same owner-execute rule. Reject directories, a leading Skill-directory/extra
root, duplicate or non-canonical members, members outside the exact expected
inventory, symlinks, and special entries; after these checks only kind zero or a
regular-file kind is valid.

The checked-in manifest's `bytes`/`sha256` fields and an author receipt's file
facts are readable cross-checks only. Runtime revision must be independently
recomputed from physical checkout/archive raw bytes and normalized modes.
Checkout location, timestamps, uid/gid, development files, and
`release-policy.json` are not revision inputs.

Lock the byte contract with at least these known-vector tests:

- empty inventory →
  `sha256:2d33a936115a451e4f077f46eb86826280294ea14ff05eddaca14879587abfb7`;
- one entry with path `SKILL.md`, mode `0644`, and six raw bytes `hello\n`
  (`68656c6c6f0a`) →
  `sha256:948f7d328239b17b56b91403847801b460626f1a55880a8c6d57c2f4354ffb3a`.

The schema-version-3 author receipt has exactly `schema_version`, `skill_name`,
`archive_sha256`, `archive_size`, `release_policy_sha256`, `inventory`, `files`,
and `validation`; every `files` entry has exactly `path`, `sha256`, `size`, and
`mode`. It has no `runtime_revision`. The release-policy identity remains the
lowercase SHA-256 of the exact policy file and is compared separately with
receipt field `release_policy_sha256`. A policy-only edit never changes runtime
revision.

### Binding hooks

- Future schema-version-3 evaluation result field `candidate_revision` must equal
  the current runtime revision. No result is created in Round 1.
- Host-evidence schema version 2 requires top-level `runtime_revision` for
  `failed`, `unverified`, and `verified` lifecycle artifacts.
- A future verified archive is read as bytes/modes to recompute its runtime
  revision; that value must match the development manifest and all candidate/
  host bindings. Receipt inventory/file facts are checked against the archive,
  but do not supply the revision. Its receipt policy digest is checked
  independently against the current policy file.
- Copied durable state adds `Skill runtime revision` and `Runtime revision
  source`. The source is a checked development manifest, an independently
  recomputed verified archive, host-provided binding, or `unknown`; a receipt
  alone is never a revision source and the value is never guessed.
- Legacy/missing/invalid state revisions are classified `unknown`. Safe resume
  remains possible after repository state and current instructions are
  revalidated, but unknown state cannot support behavior, host, compatibility,
  or release provenance.

### Host raw-evidence schema

Schema-version-2 `failed`, `unverified`, and `verified` host lifecycle artifacts
retain the current top-level fields and add `runtime_revision`. Every one of the
eight ordered lifecycle steps retains `id`, `command`, `result`, and
`postcondition` and adds:

```text
raw_evidence.command_output
raw_evidence.postcondition_readback
```

Each raw record contains exactly:

```text
path
status
sha256
bytes
reason
```

`status` is `captured`, `redacted`, or `unavailable`. `captured` uses a regular
file plus matching path/hash/bytes and a null reason. `redacted` also uses a
captured regular file plus matching facts and a non-empty redaction limitation.
`unavailable` uses null path/hash/bytes and a non-empty reason. A `verified`
artifact requires `captured` for both raw channels of all eight steps; all
existing pass requirements and runtime-revision match also remain mandatory.
`redacted` and `unavailable` are valid only for `failed` or `unverified` records,
must preserve an honest reason/limitation, and can never support compatibility.

Raw file paths are canonical repository-relative paths below
`evaluation/evidence/hosts/raw/`. Validation rejects absolute POSIX paths,
Windows drive/UNC paths, lexical traversal, resolved escapes, symlinks,
non-regular files, read-time identity changes, byte-count mismatch, and digest
mismatch. Raw evidence must exclude credentials; redaction never silently
upgrades evidence quality.

### Routing pair contract

Add four routing cases using only schema-v4's existing fields:

| Set | Positive ID | Near-miss ID | Expected observations |
| --- | --- | --- | --- |
| tuning | `contract-reconciliation-tuning-positive` | `contract-reconciliation-tuning-near-miss` | positive: both true; near miss: both false |
| held-out | `contract-reconciliation-heldout-positive` | `contract-reconciliation-heldout-near-miss` | positive: both true; near miss: both false |

Within each pair, all wording stays matched except the decision predicate:
establish/revise the engineering contract or explicitly request substantial/
iterative delivery, versus make one bounded factual correction without such a
workflow. Pair role is encoded in IDs and reasons rather than an unsupported JSON
field. Tuning and held-out prompts are distinct paraphrases.

Every recorded tuning sample includes case ID, variant (`current` or
`conditional-candidate`), repetition, model, host and build, runner/harness,
tools, sampling settings or explicit unavailability, budget, raw answer,
`selected`, `entrypoint_loaded`, reviewer, verdict, and limitations. Selection
and entrypoint loading are independent Boolean observations. `Evidence status`
is `active` when produced and may become `historical/withdrawn` only through the
rollback path below; the file remains at its exact product evidence path.

## Work package A — Documentation-first approved contract

**Status:** established before implementation.

**Exact files**

- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-08-29-cross-host-self-iteration-design.md`
- Modify: `CHANGELOG.md`
- Create: `docs/superpowers/plans/2026-08-30-round-1-approved-addendum.md`

**Interface**

- Consumes: user decision `approve 2,3,4,5; reject 1` and the audited Round-1
  proposal contract.
- Produces: implementation boundary, technical schemas, work order, acceptance,
  rollback, and separate future gates.

**RED evidence**

- Before these edits, product docs did not record the selection, Proposal-1
  rejection, runtime/policy split, P5 dependency, conditional P4 branch, or
  package-specific Round-1 postconditions.

**GREEN/postcondition**

- All four product documents name only approved work, explicitly exclude
  Proposal 1, say implementation is pending, and make no candidate, L5/L6,
  package, publication, or release claim.
- README links this addendum and the link resolves after creation.

**Steps**

1. Update README first.
2. Reconcile the design amendment.
3. Record planning state in CHANGELOG.
4. Create this exact addendum and inspect cross-document terminology.

**Rollback**

- Revert only the Round-1 planning blocks and this addendum with targeted
  patches. Preserve all pre-existing user work. A rollback returns the round to
  `DOC_UPDATE / BLOCKED` pending a corrected contract; the recorded user
  selection remains valid unless the user withdraws or changes it.

## Work package A2 — Per-round necessity and redundancy scope amendment

**Status:** complete. The documentation-first amendment, minimal runtime
follow-through, isolated after-change pressure test, and independent behavior
rereview are complete. The Package-B manifest was regenerated and checked after
A2 as `sha256:7fead2ced27f63e95725f251c217641363bded1bd1b12765265566ba9799dfd4`.
This remains an approved scope amendment within open Round 1, not a new round.

**Exact files**

- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-08-29-cross-host-self-iteration-design.md`
- Modify: this addendum
- Modify: `CHANGELOG.md`
- Preserve without modification: the pre-change necessity control report.

**Interface**

- Consumes: the user's explicit requirement that every optimization round review
  capability necessity, architecture necessity, and redundancy/ownership, plus
  the pre-change control showing that generic maintainability did not provide
  the required coverage or consumer-resolution obligation.
- Produces: a mandatory per-round necessity ledger, evidence-resolution rules,
  proposal threshold, final-gate distinction, and a bounded continuation order.

**RED evidence**

- Before this amendment, duplicate or unused-looking surfaces were only noticed
  in generic maintainability; no dedicated three-surface coverage, ledger, or
  proportionate consumer-resolution rule was recorded. Speculative external
  consumers could suppress cleanup proposals without being affirmative
  necessity evidence.

**GREEN/postcondition**

- All four product documents independently state that capability necessity,
  architecture necessity, and redundancy/ownership are distinct mandatory
  review surfaces, and that every material subject has the required ledger
  fields/status or an explicit homogeneous-group evidence boundary.
- The documents require proportionate consumer/contract discovery before
  retention or deletion; hypothetical consumers are uncertainty, unresolved
  dynamic/public surfaces are `unassessed` or risk-labeled user proposals, and
  automatic deletion is prohibited.
- Coverage remains mandatory but change remains optional: a removal, merge, or
  simplification requires evidence of material positive net value after
  compatibility, migration, reversibility, and opportunity costs. Earlier
  rounds review/propose; final-round cleanup remains the stronger separate
  execution gate for sufficiently proven material within authority.

**Steps**

1. Amend the four product documents first.
2. Preserve the pre-change control report without modification.
3. Minimally modify runtime `self-iteration/SKILL.md` and
   `self-iteration/references/review-matrix.md` to implement the recorded
   contract.
4. Run the same isolated control fixture as an independent after-change
   pressure test, requiring explicit capability/architecture/redundancy ledger
   coverage and evidence-backed proposal-or-no-proposal reasoning.
5. Because Step 3 changes runtime bytes, regenerate and check
   `evaluation/runtime-manifest.json`.
6. Resume Package B Fix Round 2 and its scoped re-review before Packages C, D,
   and E.

The Package-B manifest that was checked before A2 remains current during Step 1
and Step 2 only; it becomes stale at Step 3, not during documentation-only
amendment.
This package grants no breaking change, external mutation, commit, publication,
or final-round authority.

**Rollback**

- Restore only this scope-amendment documentation with targeted patches while
  preserving the pre-change control. If runtime follow-through has begun,
  restore its owning files and regenerate/check the manifest only after the
  runtime bytes are restored. Do not delete unresolved dynamic/public surfaces
  or use this amendment as deletion authority.

## Work package B — Proposal 2 runtime revision

**Dependencies:** Work package A only.

**Exact files**

- Create: `scripts/runtime_revision.py`
- Create: `scripts/test_runtime_revision.py`
- Create: `evaluation/runtime-manifest.json` after the helper passes RED tests
- Modify: `scripts/validate_repo.py`
- Modify: `self-iteration/assets/iteration-state.md`
- Modify: `self-iteration/references/round-protocol.md`
- Reconcile: `README.md`, design, and `CHANGELOG.md`

**Interfaces**

The helper exports deterministic functions for inventory/revision calculation,
manifest write/check, state-revision classification, evidence-binding checks,
and package-binding checks. Its CLI exposes:

```text
runtime_revision.py write --runtime-root PATH --manifest PATH
runtime_revision.py check --runtime-root PATH --manifest PATH
runtime_revision.py check-bindings --manifest PATH
  [--eval-result PATH]
  [--host-evidence-dir PATH]
  [--archive PATH --receipt PATH --policy PATH]
```

Optional groups are validated as complete groups. Commands emit stable JSON
findings, return 0 only when all requested checks pass, and write only the exact
manifest target for `write`. Manifest replacement is atomic; a failed snapshot
leaves the previous manifest unchanged.

**RED fixtures/tests first**

Add temporary fixtures proving failure before the helper exists and then proving:

- the two fixed empty/single-file known vectors produce the exact documented v1
  revisions;
- runtime byte, canonical path, or normalized mode change changes revision;
- identical runtime trees at different roots/timestamps yield one revision;
- policy-only bytes change policy digest but not runtime revision;
- invalid UTF-8/NFC, absolute/backslash/empty/dot/dotdot/duplicate paths, symlink,
  special file, u64 overflow, and read-time drift fail;
- checkout owner-execute normalization matches rootless-ZIP mode normalization;
  ZIP directory, extra-root, extra/missing/duplicate/non-canonical, symlink, and
  special entries fail;
- stale/malformed manifest entries and revisions fail with named findings;
- synthetic eval/host binding mismatch fails;
- an independently recomputed synthetic archive revision mismatch, receipt
  archive/inventory/file-fact mismatch, and receipt policy mismatch fail as
  separate findings; a receipt with no runtime-revision field remains valid; and
- missing/legacy durable-state revision classifies as `unknown`, permits only
  revalidated safe continuation, and never reports provenance established.

**GREEN implementation**

1. Implement the exact domain/framing/path/sort/mode/archive contract and known
   vectors in stdlib only.
2. Implement atomic manifest write and read-only check commands.
3. Add binding functions without creating real eval, host, archive, or receipt
   artifacts.
4. Add the two durable-state fields and round-protocol population/unknown rules.
5. Require the helper, test, and current manifest in repository validation.
6. Generate the first manifest only after runtime contract edits in this package;
   check it immediately.

**Round-1 measurable postcondition**

- Focused tests cover every RED case and pass.
- The checked-in manifest exactly matches the then-current runtime tree.
- Physical checkout and rootless-archive revisions match the known vectors and
  each other without trusting manifest or receipt file facts as digest inputs.
- Policy-only mutation in a temporary fixture leaves runtime revision unchanged
  while its synthetic policy/receipt comparison fails independently.
- State legacy/unknown fixtures preserve safe resume but cannot establish
  provenance.
- No real candidate, host, or package evidence is created.

**Rollback**

- Remove only the three new B files and targeted B additions to existing files.
  Restore the prior state/protocol schema. Do not use Git reset and do not alter
  host evidence or unrelated documentation. If C has begun, roll C back first
  because C binds to B.

## Work package C — Proposal 5 host raw evidence

**Status:** implemented and locally verified with temporary synthetic fixtures;
no real host lifecycle or raw-evidence artifact was created.

**Dependencies:** Work package B. Proposal 3 helpers are optional reuse, not a
dependency; C must pass its own containment tests before D starts.

**Exact files**

- Modify: `docs/host-support.md`
- Modify: `scripts/validate_repo.py`
- Modify: `scripts/test_host_support_validator.py`
- Reconcile: `README.md`, design, and `CHANGELOG.md`
- Do not create: `evaluation/evidence/hosts/*.json` or raw host files without a
  real authorized lifecycle run

**Interface**

- Consumes: B's checked runtime revision and temporary schema-version-2 host
  fixtures.
- Produces: schema/status validation and raw file-fact diagnostics; it does not
  produce host evidence.

**RED fixtures/tests first**

Extend temporary host fixtures for:

- missing `runtime_revision`, step `raw_evidence`, either required channel, or
  any of the five raw fields;
- runtime-revision mismatch;
- missing file, wrong byte count, wrong SHA-256, absolute/drive/UNC/traversal
  path, resolved symlink escape, symlink, non-regular file, and read-time drift;
- `verified` plus redacted or unavailable raw evidence in either channel of any
  step, failed step, nonzero exit, false postcondition, or incomplete eight-step
  inventory;
- captured evidence with a non-null reason, redacted evidence without a safe
  file/reason, and unavailable evidence with file facts; and
- honest failed/unverified/unavailable records that cannot map to
  `verified / compatible`.

**GREEN implementation**

1. Document schema version 2 and the raw evidence root.
2. Extend exact-field and conditional-field validation.
3. Resolve lexical and physical containment before reading; reject symlinks and
   special files; compare stat identity before/after reading.
4. Compare byte count and SHA-256, runtime revision, step/status summary, and
   public host claim.
5. Preserve current real support rows as unverified/unavailable; do not fabricate
   files to satisfy the new schema.
6. Keep redaction and credential exclusion explicit without claiming a heuristic
   scanner proves transcript safety. Redaction tests use inert placeholders and
   never place credential-like material in fixtures or logs.

**Round-1 measurable postcondition**

- Every negative synthetic fixture returns the intended named finding.
- A complete synthetic verified fixture passes only when both channels of all
  eight steps are `captured` with matching runtime/raw facts.
- Current host-support records remain honest and no L5/L6 evidence appears.
- Host-focused and aggregate validation pass after C alone with B.

**Rollback**

- Restore schema-v1 documentation, constants, and tests only if no real v2
  evidence was produced. Preserve B. If any real evidence unexpectedly exists,
  stop as `uncertain state` and request a decision rather than deleting it.

## Work package D — Proposal 3 fail-closed validator

**Dependencies:** Work package A only. D must not import, call, or require any
B/C-specific module, manifest, host schema, evidence file, or generated output.
It may use only shared primitives already owned and retained in
`scripts/validate_repo.py`; D owns the JSON type-guard, Markdown-containment, and
documented-entrypoint behavior even if another selected package later calls a
shared primitive.

**Exact files**

- Create: `scripts/test_repo_validator.py`
- Modify: `scripts/validate_repo.py`
- Reconcile validation commands in: `README.md`
- Reconcile: design and `CHANGELOG.md`

**Interface**

- `python3 -B scripts/test_repo_validator.py` exercises repository-validation
  boundaries in temporary roots.
- `python3 -B scripts/validate_repo.py` continues to return 0 for a valid tree
  and 1 with stable findings for invalid input; malformed product input never
  escapes as an uncaught exception.

**RED fixtures/tests first**

- top-level JSON `[]`, scalar, and `null` for evaluation and every other JSON
  entrypoint touched by the validator;
- malformed nested campaign/case/host/manifest objects;
- local Markdown absolute POSIX, Windows drive, UNC, lexical `..`, and
  resolved-symlink escape targets;
- valid internal paths, same-file anchors, relative anchors, and external URLs;
  and
- removal of each README-documented test entrypoint, especially
  `scripts/test_host_support_validator.py` and all new Round-1 suites.

**GREEN implementation**

1. Guard type before `.get()`, `set()`, membership, or iteration at every JSON
   boundary and return after an invalid parent shape.
2. Normalize Markdown targets without confusing URI schemes with Windows drive
   paths; reject unsafe lexical forms before existence checks and require the
   resolved target to stay under repository root.
3. Reject symlink-resolved external targets while preserving valid internal
   Markdown and anchors.
4. Make the closed required-entrypoint inventory match README commands.
5. Keep D-owned shared primitives in `scripts/validate_repo.py`; do not import B
   or C modules and do not split the validator merely for style.

**Round-1 measurable postcondition**

- The three originally reproduced defects are RED before fixes and GREEN after.
- All defined malformed JSON values return findings, never traceback.
- All escape forms fail and valid internal/external link forms pass.
- Removing any documented focused suite prevents aggregate success.
- The new focused suite and all existing focused suites pass.

**Rollback**

- Remove only `scripts/test_repo_validator.py` and the targeted guards/link/
  required-file call sites. Restore README commands in the same rollback. D owns
  its shared primitives: preserve any primitive still used by surviving B/C
  validation, and remove it only when no retained caller/contract needs it. A B
  or C rollback must likewise never remove a D-owned primitive while D remains.
  If ownership or callers cannot be resolved safely, stop as `uncertain state`
  instead of deleting shared code.

## Work package E — Proposal 4 routing minimal pairs

**Dependencies:** Work package A only. It is independent of rejected Proposal 1
and does not require a staged behavior runner/oracle.

**Exact files**

- Modify: `evaluation/eval-spec.json`
- Modify: `scripts/validate_repo.py`
- Create: `scripts/test_routing_evidence_validator.py`
- Produce after real observations: ten `current` routing-tuning Markdown files
  under the exact directory above
- Produce only after an observed miss and conditional wording change: ten
  `conditional-candidate` routing-tuning Markdown files
- Modify documentation first on an observed miss: `README.md`, then design
- Conditional modify on observed miss only: `self-iteration/SKILL.md`
- Regenerate on any conditional runtime edit: `evaluation/runtime-manifest.json`
- Reconcile: `CHANGELOG.md`

**Interface**

- The schema-v4 eval inventory keeps its existing fields and adds only the four
  IDs in the shared routing-pair contract.
- The focused evidence suite validates exact tuning inventory, five repetitions
  per case/variant, canonical metadata, raw section boundaries, Boolean
  `selected`/`entrypoint_loaded`, manual verdict, and absence of held-out result
  files.
- Observation uses an available selection/loading harness in fresh contexts; it
  records unavailable host settings explicitly and never treats answer quality
  as proof of entrypoint loading.

**RED fixtures/tests first**

- missing/duplicate pair member, tuning/held-out ID collision, unexpected field,
  prompt pair differing beyond the approved predicate, wrong expected outcome,
  or missing required observation;
- tuning evidence with missing/duplicate repetition, wrong case/variant,
  non-Boolean or conflated observations, incomplete environment/reviewer/
  limitation metadata, or altered raw boundary; and
- any Round-1 evidence path/result for a held-out ID.

**GREEN implementation and observation branch**

1. Add the tuning and held-out pair objects to `evaluation/eval-spec.json` and
   update repository constants/tests without adding a schema field.
2. Validate the inventory with repository and Primary eval-spec validators.
3. Run five fresh current-description observations per tuning case, separately
   recording selection and entrypoint loading. Do not execute held-out cases.
4. Manually inspect every current tuning record.
5. Resolve the evidence branch once: if all current tuning expectations pass,
   record `pass_no_runtime_change` in README/CHANGELOG and leave `SKILL.md`
   byte-for-byte unchanged; if either observation misses, preserve that evidence,
   record the failure in README first, and then apply only the approved predicate
   (engineering-contract establishment/revision or explicit substantial/
   iterative delivery triggers; a bounded factual correction abstains).
6. After a conditional wording change, run five new fresh repetitions per tuning
   case as `conditional-candidate`, inspect all ten, and regenerate/check the
   runtime manifest. Do not broaden wording for any unobserved failure.

**Round-1 measurable postcondition**

- Both pairs validate and differ only by the named predicate; tuning and
  held-out IDs/prompts are distinct.
- Exactly five fresh current samples per tuning case are preserved and reviewed;
  any conditional candidate has its own five fresh samples per case.
- `selected` and `entrypoint_loaded` are independently reported for every run.
- Passing current behavior causes no runtime edit; an observed miss causes only
  the approved predicate plus matched tuning rerun.
- No held-out outcome/evidence exists, and no precision/recall release claim is
  made in Round 1.

**Rollback**

- Never delete, move, or copy actual tuning observations during rollback. Keep
  every file at its exact product evidence path and change only its `Evidence
  status` to `historical/withdrawn` with the rollback reason. Withdraw the four
  active routing cases, active-validator requirements, and any conditional
  runtime wording; regenerate the B manifest if runtime bytes change. Retain the
  minimum schema/parser/docs needed to explain and validate the historical
  evidence. If that minimum conflicts with the rolled-back schema or ownership
  cannot be resolved, stop as `uncertain state` rather than deleting evidence.
  Never remove or rewrite the pre-existing behavior-control corpus.

## Work package F — Reconcile, verify, and close Round 1

**Dependencies:** selected packages B, C, D, and E complete.

**Exact files**

- Reconcile: `README.md`, `CHANGELOG.md`, `docs/host-support.md`, design, this
  addendum, `evaluation/eval-spec.json`, runtime state/protocol, all changed
  scripts/tests, and `evaluation/runtime-manifest.json`
- Record only actual tuning evidence produced by E
- Update ignored Round-1 delivery/closure report; do not create Round-2 product
  or planning files

**Interface**

- Consumes: completed package postconditions and current repository readback.
- Produces: one reconciled Round-1 tree, verification ledger, limitations, and an
  explicit `ROUND_CLOSE / CLOSED` statement only if every required gate passes.

**RED/reconciliation challenge**

Search for documented-but-unimplemented, implemented-but-undocumented,
obsolete-command, stale-manifest, schema/version, conditional-branch,
Proposal-1 leakage, and host/release overclaim drift. Any hit keeps the round
open and returns to the owning package.

**GREEN verification order**

```bash
python3 -B scripts/test_runtime_revision.py
python3 -B scripts/test_host_support_validator.py
python3 -B scripts/test_repo_validator.py
python3 -B scripts/test_routing_evidence_validator.py
python3 -B scripts/test_control_evidence_validator.py
python3 -B scripts/runtime_revision.py check \
  --runtime-root self-iteration \
  --manifest evaluation/runtime-manifest.json
python3 -B scripts/validate_repo.py
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/validate_skill.py" \
  self-iteration --policy release-policy.json
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/validate_eval_spec.py" \
  evaluation/eval-spec.json
```

Also parse all repository Python files with Python-3.9-compatible grammar,
inspect the final changed-file inventory and modes, check documentation links and
whitespace, and confirm no result/archive/receipt/host-lifecycle/held-out or
Proposal-1 artifact was introduced. Aggregate static tools may mechanically
traverse the final-round file as generic text; reviewers must not inspect or use
its instruction content and must keep its final-gate semantics unassessed.

**Round-1 closing postcondition**

- All B-E package postconditions pass on the same final Round-1 tree.
- Runtime manifest matches after every possible conditional runtime edit;
  release-policy identity remains separate.
- Documentation and implementation agree in both directions.
- Proposal 1 remains rejected and absent.
- Current tuning result and any conditional branch are recorded honestly;
  held-out routing remains untouched.
- Host support remains unverified/unavailable unless future real L5 evidence
  exists; no synthetic result changes it.
- Attempted, changed, unchanged, failed, skipped, and unknown subjects, plus
  risks/limitations, are reported.
- Only then set `ROUND_CLOSE / CLOSED`. Do not read or plan Round 2 before that
  explicit closure.

**Rollback/failure behavior**

- Classify any failure as input, authority, environment, transient dependency,
  implementation, or uncertain state. Retry only when bounded and evidence-
  producing.
- Restore only the owning package with targeted patches and rerun downstream
  checks. Roll C back before B; other approved packages are independently
  reversible.
- A required unresolved failure leaves Round 1 open in `VERIFY / BLOCKED` or
  `VERIFY / WAITING_USER` with an exact resume condition. It never advances to
  Round 2 or masquerades as release evidence.

## Future Task-10 gates — explicitly non-closing for Round 1

After all later edits, Task 10 must independently:

1. run the untouched held-out routing pair for five fresh repetitions per case
   and apply the plan-owned release gates;
2. run the final Skill-loaded candidate campaign, without relabeling historical
   or Round-1 tuning evidence as release-grade;
3. bind the final eval result and each real available-host artifact to the final
   runtime revision;
4. capture and validate real raw host lifecycle evidence for any actually tested
   host, while unavailable hosts remain unverified;
5. create and verify a temporary package, recompute its runtime revision from
   archive bytes/modes, compare it with the final manifest/evidence, and
   separately compare the receipt policy digest; and
6. complete final hygiene and horizon gates before any release or portability
   statement.

None of these future actions is required to close Round 1, and none has been
performed or preapproved by this addendum beyond the existing Task-10 local
verification boundary.
