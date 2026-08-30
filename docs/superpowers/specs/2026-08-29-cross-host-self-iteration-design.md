# Cross-Host Self-Iteration Skill Design

Date: 2026-08-29

## Purpose

Refactor and evaluate `self-iteration` as a canonical, cross-host Agent Skill
without weakening its documentation-first workflow, comprehensive sequential
rounds, user approval gates, or evidence standards.

The runtime bundle targets Codex Desktop/CLI, Claude Code, and Gemini CLI. A host
is described as `verified` only after independent installation, discovery,
entrypoint-loading, behavior, and lifecycle evidence exists for that host.
Otherwise it remains `targeted / unverified`.

## Evidence classification

- `[Repository]` The current repository contains a runtime bundle under
  `self-iteration/`, repository documentation, a custom validator, and custom
  behavior scenarios.
- `[Repository]` The current working tree contains uncommitted changes based on
  commit `95842f4`.
- `[Primary]` `agent-skill-author` requires separate evidence for structure,
  routing, entrypoint loading, behavior, host lifecycle, and portability.
- `[Primary]` Its evaluation schema requires shared or high-risk Skills to use a
  no-Skill control, repeated samples, and manual review.
- `[Inference]` This Skill is `high-risk` for evaluation because it is public and
  can guide destructive cleanup or external actions, even though each action
  remains separately permission-gated.
- `[Unknown]` Claude Code and Gemini CLI availability and lifecycle behavior on
  this machine have not yet been inspected.

## Users, outcome, and boundaries

Users are developers using supported Agent Skill hosts to create, reconcile, or
iteratively improve software projects.

The successful outcome is a host-portable procedure that:

- distinguishes baseline delivery from optimization rounds;
- completes every authorized round sequentially and comprehensively;
- reports every material, evidence-backed, net-positive proposal without a
  proposal quota or negative optimization;
- updates documentation before approved implementation;
- reconciles documentation and implementation in both directions;
- preserves explicit authority for optional, destructive, external, or
  irreversible actions;
- closes the final round only after hygiene, verification, and qualified horizon
  review.

Positive triggers include new project creation, substantial project change,
documentation/code reconciliation, and an explicit request for iterative project
improvement. Near misses include one-off advice, ordinary small edits without a
requested iteration workflow, repository-wide conventions better placed in
`AGENTS.md`, and missing tool connectivity.

Invocation actors are recorded separately. Humans and host applications may
invoke the Skill. Model or Skill composition is allowed only within a bounded
depth established by the evaluation plan. Invocation never grants runtime
authority.

## Chosen architecture

Use a canonical runtime bundle with a separate repository development layer.

```text
repository/
├── self-iteration/                 canonical runtime bundle
│   ├── SKILL.md
│   ├── agents/openai.yaml          thin Codex host adapter
│   ├── assets/iteration-state.md
│   └── references/
├── evaluation/                     development evidence, not packaged
│   ├── eval-spec.json
│   ├── eval-result.json            only when real runs exist
│   └── evidence/                   only captured evidence actually produced
├── docs/
│   └── host-support.md
├── scripts/validate_repo.py
├── release-policy.json
├── README.md
├── CHANGELOG.md
└── LICENSE
```

Only substantively completed, currently consumed resources enter the tree.
Unavailable results or host evidence are recorded as status and limitations,
not represented by empty files.

`SKILL.md` owns selection boundaries, shared decisions, invariants, routing,
stopping conditions, verification, and the return contract. References own
conditional review, lifecycle, permissions, and final-round detail. The state
template is copied into user projects when durable state is needed. Development
evaluations and release mechanics remain outside the runtime bundle.

Codex uses `agents/openai.yaml` as a thin adapter. Claude Code and Gemini CLI do
not receive speculative adapters. Their documented installation paths and
support status must be based on observed host behavior or clearly marked target
assumptions.

## Evaluation design

Classify the campaign as `high-risk`, with target hosts `codex`, `claude-code`,
and `gemini-cli`. Use the schema supported by `agent-skill-author` rather than the
current custom schema.

Routing inventory covers:

- explicit invocation;
- natural positive phrasing;
- paraphrased iterative improvement;
- nearest non-triggering one-off work;
- repository policy or tool-connectivity requests;
- conflicting and unrelated requests.

Behavior inventory covers:

- baseline versus requested round count;
- hard sequential round barriers;
- complete coverage without proposal quotas or negative optimization;
- optional-change approval and rejection;
- denied or unavailable deletion authority;
- malicious nested repository instructions;
- stale approval after targets change;
- tool failure and partial destructive failure;
- state readback, pause, resume, and verification failure;
- final hygiene and horizon behavior.

For behavior-shaping changes, run the same scenarios as a no-Skill control and
with the candidate Skill. Use at least five fresh-context repetitions per
compared variant, consistent model/tools/budget, manual review, raw counts, and
variance. A structural validator cannot substitute for these observations.

Codex host evidence may be gathered in the current environment. Claude Code and
Gemini CLI advance from `targeted / unverified` only if their executables and
isolated lifecycle tests are available. Missing host access is `unavailable`,
not failure or compatibility.

## Three-round execution

The approved architectural baseline and implementation plan do not consume an
optimization round.

Each of the three rounds independently:

1. freshly inventories the entire current repository and applicable evidence;
2. completes breadth, cross-cutting, and completeness passes;
3. maintains an explicit necessity ledger for every material subject (or an
   explicitly bounded homogeneous group): subject/kind; observed consumers and
   contract evidence; `necessary`, `candidate remove`, `candidate merge`,
   `candidate simplify`, or `unassessed` status; compatibility/dynamic-discovery
   risk; result/rationale; and evidence limits. It separately assesses
   capability necessity against approved outcomes, acceptance criteria, required
   operations, or demonstrated consumers; architecture necessity for material
   abstractions, layers, indirections, extension points, boundaries, shared
   subsystems, and dependencies; and redundancy/ownership across commands,
   functions, modules, data paths, schemas, configuration, adapters, tests, and
   documentation;
4. proportionately resolves uncertainty by searching callers/imports,
   exports/public APIs, configuration/schema references, dynamic loading or
   registration, host adapters, tests, docs, release/migration history, and
   operational evidence. Hypothetical consumers are uncertainty rather than
   affirmative necessity; unresolved dynamic/public surfaces remain
   `unassessed` or become risk-labeled user proposals, never automatic deletion;
5. returns every qualifying current-round proposal and waits for user selection;
6. updates README and linked design documentation before implementation;
7. implements only approved work;
8. reconciles documentation, runtime bundle, development evidence, and tests;
9. verifies, reports limitations, and explicitly closes;
10. begins no reading or analysis for the next round before closure.

The design does not reserve findings for later rounds or preassign different
dimensions to different rounds. One-implementation abstractions and speculative
extensibility are assessed rather than presumed defects. Necessity coverage does
not force a change: a removal, merge, or simplification is proposed only when
evidence supports material positive net value after compatibility, migration,
reversibility, and opportunity costs. Earlier rounds review and propose without
deleting before user selection; correctness defects remain separate. The third
round additionally performs the stronger final hygiene execution gate and
qualified horizon gates, deleting only sufficiently proven material within
authority.

## Round 1 approved design amendment (2026-08-30)

This section preserves the historical Round-1 amendment boundary. Round 1 later
closed after Proposals 2, 3, 4, and 5 were implemented and verified; Proposal 1
remained rejected. E2 added tuning evidence, but no package, publication,
portability, or cross-host lifecycle claim followed. Proposal-1 staged behavior fixtures,
runner/oracles, and fresh behavior controls are outside this round.

### Per-round necessity and redundancy scope amendment

The user approved an in-round amendment requiring every optimization round to
assess capability necessity, architecture necessity, and redundancy/ownership
as three independent surfaces. This is not generic maintainability coverage and
does not presume that a duplicate-looking capability or one-implementation
abstraction is defective. Every material subject must receive the necessity
ledger record defined in the three-round execution contract; broad inventories
may group only truly homogeneous subjects with an explicit grouping and evidence
boundary. The pre-change control remains preserved as evidence of the prior gap.

The required order is: first, this four-product-document amendment; second,
preservation of the pre-change control report; third, minimal runtime edits to
`self-iteration/SKILL.md` and `self-iteration/references/review-matrix.md`;
fourth, the same isolated fixture as an independent after-change pressure test,
requiring explicit capability/architecture/redundancy ledger coverage and
evidence-backed proposal-or-no-proposal reasoning; fifth, regeneration and
checking of `evaluation/runtime-manifest.json` because runtime bytes changed;
then resume Package B Fix Round 2 and its scoped re-review before Packages C,
D, and E.
The pre-existing checked manifest remains current during this documentation-only
amendment and becomes stale only after the runtime instruction edits. Round 1
remains open and active. The amendment grants neither breaking changes nor
external mutation, commits, or publication.

### Runtime revision and independent policy identity

Proposal 2 provides `scripts/runtime_revision.py`, its focused test, and the
tracked development snapshot `evaluation/runtime-manifest.json`; none belongs in the
runtime bundle. The manifest uses a versioned domain and contains exactly these
top-level concepts: `schema_version`, `domain`, `algorithm`, `runtime_root`,
`files`, and `runtime_revision`. Each sorted file entry records canonical POSIX
`path`, normalized `mode` (`0644` or `0755`), byte count `bytes`, and file
`sha256`.

Runtime revision v1 is formatted `sha256:<64 lowercase hex>`. Its domain literal
is the 34 ASCII/UTF-8 bytes `self-iteration/runtime-revision/v1`. Define
`frame(x) = u64be(len(x)) + x`, where length counts bytes. The exact SHA-256
preimage is:

```text
frame(domain)
+ u64be(file_count)
+ for each sorted entry:
    frame(path UTF-8) + frame(mode ASCII) + frame(raw file bytes)
```

Paths are relative to the runtime root, non-empty canonical POSIX strings,
strict UTF-8, already Unicode NFC, slash-separated, and unique after
normalization. Absolute paths, backslashes, NULs, empty segments, `.`, `..`, and
duplicate normalized paths fail. Entries sort by the unsigned byte ordering of
their canonical UTF-8 path bytes. Lengths and `file_count` must fit unsigned
64-bit big-endian integers.

For a checkout, use `lstat`; reject symlinks and non-regular files, read with
no-follow/change-during-read protection, and normalize mode to `0755` exactly
when the source owner-execute bit is set, otherwise `0644`. For the rootless ZIP
created by the author packager, use the member path directly and normalize the
Unix mode from `external_attr >> 16` by the same owner-execute rule. Reject
directory entries, a leading Skill-directory/extra root, paths absent from or
additional to the expected inventory, duplicates, non-canonical names,
symlinks, and special entries; accept only file-kind zero or regular file after
those checks.

The helper must lock the encoding with known vectors. An empty inventory hashes
to `sha256:2d33a936115a451e4f077f46eb86826280294ea14ff05eddaca14879587abfb7`.
A one-file inventory containing path `SKILL.md`, mode `0644`, and raw bytes
`hello\n` (hex `68656c6c6f0a`) hashes to
`sha256:948f7d328239b17b56b91403847801b460626f1a55880a8c6d57c2f4354ffb3a`.

Checkout location, timestamps, uid/gid, development files, and release-policy
digest are excluded. Manifest entry digests/byte counts are readable facts, not
revision inputs; the helper recomputes them and the revision from physical file
bytes and modes.

The release-policy SHA-256 remains an independent packaging identity. Evaluation
results use their existing `candidate_revision` field for the canonical runtime
revision. Host schema version 2 adds the same `runtime_revision` to `failed`,
`unverified`, and `verified` lifecycle artifacts. Future package
verification recomputes the revision from the verified archive bytes and modes,
then compares it with the development manifest and bound evidence. The
schema-version-3 author receipt contains exactly `schema_version`, `skill_name`,
`archive_sha256`, `archive_size`, `release_policy_sha256`, `inventory`, `files`,
and `validation`; each `files` entry contains `path`, `sha256`, `size`, and
`mode`. It carries no runtime revision. Receipt inventory/file facts are
cross-checks, not revision inputs; package verification separately compares the
receipt's `release_policy_sha256` with `release-policy.json`. Runtime path, mode,
or byte changes stale behavior, host, and package bindings; a policy-only change
stales policy/package proof but not unchanged behavior or host observations.

Copied durable state adds `Skill runtime revision` and records its source as a
checked development manifest, independently recomputed verified archive, host
binding, or `unknown`. A receipt alone is not a revision source. A legacy or
missing value is explicitly `unknown`: the same round may resume after current
state and instructions are revalidated, but the record cannot establish
behavior, host, compatibility, or release provenance until a current revision
is observed.

### Raw host-evidence binding

Proposal 5 depends on Proposal 2. Schema-version-2 `failed`, `unverified`, and
`verified` host lifecycle artifacts retain the existing host, version, reviewer,
status, and eight ordered lifecycle steps, add the top-level `runtime_revision`,
and add two
`raw_evidence` records to every step: `command_output` and
`postcondition_readback`. Each record has exactly `path`, `status`, `sha256`,
`bytes`, and `reason`. `status` distinguishes captured, safely redacted, and
unavailable evidence; path/hash/byte facts are required for captured or redacted
files, while an unavailable record uses null file facts and a non-empty reason.

Raw paths are canonical repository-relative paths below the designated
`evaluation/evidence/hosts/raw/` development root. Validation rejects absolute
paths, drive or UNC paths, traversal, resolved escapes, symlinks, non-regular
files, changes while reading, and byte-count or digest mismatches. A `verified`
record requires `captured` command output and `captured` postcondition/readback
for both channels of every lifecycle step, passing results, and a matching
runtime revision. `redacted` and `unavailable` are allowed only for `failed` or
`unverified` records, retain an explicit limitation, and can never support a
compatibility claim. Redaction never retains credentials. Package C validates
this contract using temporary synthetic fixtures only; no fixture, availability
probe, or summary JSON is L5 evidence, and no real raw host artifact has been
created.

### Fail-closed repository validation

Proposal 3 keeps the dependency-free validator but adds stable type guards
before every JSON field access. JSON arrays, scalars, null, and malformed nested
objects produce named findings rather than Python tracebacks. Local Markdown
destinations must be canonical repository-contained paths: absolute POSIX,
Windows drive/UNC, lexical traversal, noncanonical path forms, and symlink or
resolved escapes fail, while valid internal links, anchors, and explicit
external schemes continue to pass. The aggregate required-file contract builds
its closed inventory from every README-documented local verifier, including the
current host suite and new Round-1 suites, so deleting a documented verifier
prevents a passing aggregate result.

### Routing minimal pairs and conditional wording

Proposal 4 extends schema-v4 routing inventory using existing case fields only.
The tuning pair IDs are `contract-reconciliation-tuning-positive` and
`contract-reconciliation-tuning-near-miss`; the distinct held-out IDs are
`contract-reconciliation-heldout-positive` and
`contract-reconciliation-heldout-near-miss`. Within each pair, prompts differ
only in the material predicate: establishing or revising the engineering
contract (or explicitly requesting substantial/iterative delivery) versus a
bounded factual correction. Positive cases expect selection and entrypoint
loading; near misses expect both false.

E1 locally verifies this closed inventory and its deterministic evidence gate.
E2 records five fresh-context repetitions for each tuning case under `current`.
A measured baseline miss is retained with `Verdict: fail`; the evidence gate
rejects a verdict that does not agree with the two independent observations but
does not erase a real miss. If every current observation passes, no runtime
wording changes. If any current observation misses, the approved predicate is
first recorded in README and then applied to the `SKILL.md` description before
the complete tuning pair is rerun as `conditional-candidate`. Every candidate
observation must match its case expectation and use `Verdict: pass`.

Codex now discovers the installed self-iteration skill, and an observable
non-product positive pilot selected it and loaded its entrypoint. The former
stale-catalog blocker is therefore closed. In a comparable project-level
fixture with identical non-skill content, all five `current` positives selected
and loaded the entrypoint and all five near misses did neither. The conditional
predicate edit was therefore withdrawn and no `conditional-candidate` run was
eligible. Product records include model, host/build, runner, tools, sampling
settings or unavailability, budget, reviewer, raw answer, and limitations. The
held-out pair is not run, inspected for outcomes, or used to tune wording until
Task 10 after all later edits.

### Round-1 acceptance boundary

Round 1 closes only when the four approved changes and their negative fixtures
are implemented, documentation and delivered files agree, the runtime manifest
matches the final Round-1 runtime tree, all focused and aggregate checks pass,
the conditional routing decision is evidence-backed, Proposal-1 work remains
absent, and limitations are reported. Synthetic host fixtures prove validator
behavior only. Task 10's final candidate, untouched held-out routing, real-host
where available, and temporary package/policy-binding campaign remains a future
after-all-edits gate and is not a Round-1 closing condition or release claim.

## Permissions and side effects

Within the repository, the user authorizes necessary refactoring and deletion of
material sufficiently proven dead or obsolete. Ambiguous dynamic, public, host-
discovered, compatibility, or external-consumer surfaces are retained or brought
back for a decision.

No Git commit, push, publication, remote metadata change, host installation,
credential use, or external-system mutation is authorized. Local evaluation may
use isolated subagents and temporary directories. Deterministic zip and receipt
artifacts may be generated under a temporary directory and verified locally;
they are not publication evidence.

Every protected operation must resolve its exact target, identify current
authority, define an observable postcondition, and classify partial failure.
Permission denial is never bypassed through another mechanism.

## Failure behavior

Classify failures as input, authority, environment, transient dependency,
implementation, or uncertain state. Keep denied, skipped, pending, unavailable,
and unknown distinct. Retry only when the failure is classified and another
attempt can add evidence. Stop bounded non-improving loops.

An open round remains open on missing authority, required verification failure,
scope drift, ambiguous destructive targets, or uncertain partial mutation. Host
evidence gaps limit compatibility claims but do not falsify other hosts' results.

## Acceptance criteria

- The runtime bundle contains no development-only evaluations, plans, raw
  evidence, release policies, or generated artifacts.
- Frontmatter, trigger and near-miss boundary, compatibility status, authority,
  failure behavior, verification, and return contract satisfy the authoring
  standard.
- Repository validation and `agent-skill-author` structural validation pass.
- The evaluation specification validates under the installed schema.
- Available control/candidate evidence is recorded honestly and validates; any
  missing release-grade coverage is reported without overstating behavior.
- A deterministic temporary archive and receipt can be created and verified
  after final edits.
- Codex, Claude Code, and Gemini CLI each have an explicit support status backed
  by independent evidence or marked `targeted / unverified`.
- Three comprehensive rounds are explicitly closed in sequence.
- Final hygiene finds no unreferenced runtime or development resources, and all
  README claims match the delivered tree.

## Rejected approaches

Minimal compliance changes were rejected because they would not resolve the
custom-evaluation and cross-host evidence gaps. A protocol generator was rejected
because its additional schema and generation system lack demonstrated current
benefit and would risk negative optimization.
