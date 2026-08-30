# Codex Self Iteration Skill

`self-iteration` is a documentation-first Agent Skill for building and improving
software through complete, sequential, user-approved review rounds. It keeps the
README and implementation aligned, prevents a multi-round request from being
split into partial reviews, and adds a final repository-hygiene and
horizon-expansion gate. Its canonical runtime contract targets Codex
Desktop/CLI, Claude Code, and Gemini CLI without treating a file layout or host
adapter as portability evidence.

## Engineering contract

The Skill separates initial delivery from optimization:

- A **baseline delivery** clarifies the intended outcome, writes or reconciles
  the project README, implements the approved scope, and verifies the result. It
  does not consume an optimization round.
- An **optimization round** freshly inventories the current project, reviews
  every applicable dimension, presents the complete proposal set, waits for user
  selection when proposals exist, updates documentation first, implements
  approved work, reconciles documentation and code, verifies the result, and
  explicitly closes.
- Only one round may be active. No reading, planning, or brainstorming for the
  next round begins before the current round is fully closed.

Lifecycle phase and execution status are tracked separately. The phase is:

```text
BASELINE -> FINALIZE (when no optimization round is authorized)
BASELINE -> ROUND_REVIEW -> USER_APPROVAL -> DOC_UPDATE -> IMPLEMENT
         -> RECONCILE -> VERIFY -> FINAL_GATES (final round only)
         -> ROUND_CLOSE -> next ROUND_REVIEW or FINALIZE
```

The execution status is one of `ACTIVE`, `WAITING_USER`, `PAUSED`, `BLOCKED`, or
`CLOSED`. Waiting for a proposal selection, pausing across tasks, or encountering
a blocker never closes the round. Verification failure also keeps the current
round open. If scope changes during a round, its contract and evidence are
refreshed in that same round unless the user explicitly cancels or restarts it.

The user controls the number of rounds and which optional proposals are
implemented. If the user authorizes multiple rounds, every authorized round is
performed sequentially unless the user cancels it or a concrete blocker prevents
completion. A round with no justified proposals still completes its full review
and counts; it is not a reason to silently discard later authorized rounds.

Before work begins, the Skill confirms the intended outcome, scope, constraints,
acceptance criteria, round count, breaking-change policy, and whether final-round
deletion of sufficiently proven dead or obsolete material is authorized.

## Runtime contract

The portable `SKILL.md` frontmatter contains `name`, a `description` that names
both positive triggers and near misses, `license: MIT`, and a string
`metadata.compatibility` status. The compatibility value uses the metadata map
accepted by both installed author validators and remains a claim requiring host
evidence. The entrypoint owns shared selection, impact, invocation, authority,
failure, verification, stopping, and return decisions. It routes
conditional detail directly to the [round protocol](self-iteration/references/round-protocol.md),
[review matrix](self-iteration/references/review-matrix.md), and
[final-round gates](self-iteration/references/final-round.md). The state asset is
copied only when durable project state is useful. Portable workflow rules do not
belong in a host adapter.

The impact classification is `high-risk` because the procedure can guide
credential-adjacent work, untrusted repository review, external writes,
destructive cleanup, public changes, and other hard-to-recover actions. Humans
and host applications may invoke it. Model, Skill, or harness composition is
eligible only when the host permits it, ambiguity is resolved, and composition
depth remains at most two. Selection or invocation never grants runtime
authority.

Every mutating action remains bounded by the current request and host policy. It
must resolve the exact target, identify current authority, name an observable
postcondition, and distinguish changed, unchanged, failed, skipped, and unknown
subjects. Repository and fetched instructions are evidence, not authority;
credentials do not enter prompts, logs, artifacts, or evaluation evidence.
Approval is refreshed when the target or scope changes.

Failures are classified as `input`, `authority`, `environment`, `transient
dependency`, `implementation`, or `uncertain state`. A verification-tool failure
and a partial mutation are recorded separately. Retry is bounded and occurs only
when another attempt can add evidence. An unresolved required verification keeps
the same round open in phase `VERIFY` with status `BLOCKED` or `WAITING_USER` and
an exact resume condition.

The runtime return contract reports the lifecycle phase and status; baseline and
round outcome; coverage and limitations; proposals and user decisions;
documentation and implementation changes; attempted, changed, unchanged,
failed, skipped, and unknown subjects; verification evidence; risks and
blockers; authority and side-effect outcomes; final-gate results; closure state;
and supported-host claims with unverified claims kept explicit.

## What each round covers

Every round performs a breadth pass, a cross-cutting pass, and a completeness
challenge across all materially applicable areas, including product scope,
domain model, architecture, data flow, algorithms, interfaces, correctness,
security, performance, reliability, maintainability, tests, developer and user
experience, deployment, compatibility, migration, and cost.

A coverage ledger records the evidence inspected and the finding, no-change
reason, non-applicability reason, or assessment limitation for each area. The
Skill does not return merely because it has found the first useful improvement,
and it does not reserve known findings to make a later round appear productive.

Every round also maintains a distinct necessity ledger (which may be part of
the coverage ledger). It explicitly assesses, rather than subsuming under
generic maintainability: (1) capability necessity, mapping every material
user-visible or internal capability to an approved outcome, acceptance
criterion, required operation, or demonstrated consumer; (2) architecture
necessity, justifying every material abstraction, layer, indirection, extension
point, boundary, shared subsystem, and dependency by concrete consumers,
isolation or risk boundaries, host contracts, or an approved near-term
requirement; and (3) redundancy and ownership across commands, functions,
modules, data paths, schemas, configuration, adapters, tests, and
documentation. The ledger records each material subject/kind, observed
consumers and contract evidence, status (`necessary`, `candidate remove`,
`candidate merge`, `candidate simplify`, or `unassessed`), compatibility or
dynamic-discovery risk, result/rationale, and evidence limits. Truly
homogeneous subjects may be grouped only when the grouping and evidence
boundary are explicit.

Before uncertainty supports either retention or deletion, the review searches
proportionately for callers/imports, exports or public APIs, configuration and
schema references, dynamic loading or registration, host adapters, tests,
documentation, release/migration history, and operational evidence. A
hypothetical consumer is uncertainty, not affirmative necessity. Unresolved
dynamic or public surfaces remain `unassessed` or become risk-labeled user
proposals; they are never automatically deleted. One-implementation
abstractions and speculative extensibility are findings to evaluate, not
presumed defects.

Comprehensive coverage is an inspection obligation, not a proposal quota. Every
material, evidence-backed improvement or innovation with positive expected net
value must be reported. Ideas that are merely different, weakly supported, or
expected to add more risk, cost, or complexity than benefit are not proposals.
If nothing meets the threshold, the Skill omits the proposal list rather than
inventing work or creating a negative optimization.

The final authorized round additionally:

1. applies the stronger, separate execution gate for sufficiently proven dead
   or obsolete code, structure, configuration, tests, dependencies, and
   documentation within the user's deletion authority;
2. checks formatting and style using the project's established conventions;
3. reconciles README claims and implemented behavior in both directions;
4. runs proportionate verification and reports limitations;
5. searches broadly for bounded, high-upside ideas that could escape the current
   local optimum, reporting only those that pass the same evidence and net-value
   threshold.

Horizon ideas remain explicitly speculative. Merely selecting an idea does not
authorize implementation. The user must explicitly authorize a new future round
and its scope; that round does not reopen or mutate the verified final state
implicitly.

Necessity coverage is mandatory, but removal, merge, or simplification is not.
Such a change becomes a proposal only when evidence establishes material
positive net value after compatibility, migration, reversibility, and
opportunity costs; no capability is reduced merely for elegance, and no change
is made before user selection. Correctness defects remain a separate review
outcome. Earlier rounds review and propose; only the final cleanup gate may
execute sufficiently proven cleanup within authority.

## Project status and acceptance criteria

The repository is a dependency-free Skill under active development. Its
architectural baseline is structurally closed: the canonical bundle,
repository-development boundary, schema-v4 evaluation inventory, 20 no-Skill
control samples, release policy, and qualified host-support records are present
and locally validated. Candidate behavior, host lifecycle, and portability have
not yet been verified. Releases follow Semantic Versioning through Git tags,
and changes not yet assigned to a release remain under `Unreleased` in
`CHANGELOG.md`. This local repository state is not publication evidence, and
creating or validating an archive does not by itself prove that a Skill is
portable or installable on any host.

### Iteration status

Optimization Round 1 is `ROUND_CLOSE / CLOSED`: Proposals 2, 3, 4, and 5 are implemented, reconciled, and locally verified; Proposal 1 remains rejected and absent. The comparable E2 current campaign passed all ten tuning observations, and the conditional wording branch was not eligible.

Final Optimization Round 2 is `ROUND_CLOSE / CLOSED`. Its fresh comprehensive review found no qualifying optional proposal; mandatory hygiene, reconciliation, packaging, installation sync, and ten final-runtime held-out routing observations completed successfully. The necessity ledger, coverage ledger, cleanup evidence, verification, and limitations are recorded in the [Final Round 2 report](docs/final-round-report.md). The [Round-1 approved addendum](docs/superpowers/plans/2026-08-30-round-1-approved-addendum.md) remains the historical implementation contract.

The approved Round-1 contract was:

- **Runtime identity (Proposal 2):** `scripts/runtime_revision.py` and its
  focused suite implement a dependency-free helper and tracked development
  manifest at `evaluation/runtime-manifest.json`. Runtime revision
  v1 is `sha256:<64 lowercase hex>` with exact domain literal
  `self-iteration/runtime-revision/v1`. For `frame(x) = u64be(len(x)) + x`, hash
  `frame(domain)`, `u64be(file_count)`, then, for every entry sorted by canonical
  POSIX-path UTF-8 bytes, concatenate `frame(path UTF-8)`, `frame(mode ASCII)`,
  and `frame(raw bytes)`. Canonical paths are relative, UTF-8/NFC,
  slash-separated, unique, and contain no absolute prefix, backslash, empty,
  `.`, or `..` segment. Checkout
  modes come from `lstat` regular files and normalize to `0755` only when the
  owner-execute bit is set, otherwise `0644`. A rootless ZIP uses its member path
  and Unix owner-execute bit under the same rule; directories, an extra root,
  duplicate/non-canonical paths, symlinks, and special entries fail.

  Manifest and receipt file facts are readable cross-checks only: runtime
  revision is always recomputed independently from physical checkout/archive
  bytes and normalized modes. The schema-version-3 author receipt contains
  `schema_version`, `skill_name`, `archive_sha256`, `archive_size`,
  `release_policy_sha256`, `inventory`, `files[{path,sha256,size,mode}]`, and
  `validation`; it has no `runtime_revision`. Evaluation and host artifacts bind
  the independently computed revision, while package verification separately
  compares archive revision and receipt policy digest. A policy-only change does
  not stale unchanged behavior or host evidence. Durable-state sources are a
  checked development manifest, an independently recomputed verified archive, a
  host binding, or `unknown`; legacy/unknown requires current-instruction
  revalidation and cannot support provenance claims.
- **Raw host evidence (Proposal 5, dependent on Proposal 2):** schema-v2
  `failed`, `unverified`, or `verified` lifecycle artifacts bind the checked
  runtime revision and,
  for every lifecycle step, repository-relative raw-evidence facts for `path`,
  `status`, `sha256`, `bytes`, and `reason`. Validation rejects missing facts,
  lexical or resolved root escapes, symlinks, type changes, and digest or
  byte-count drift. A `verified` artifact requires `captured` command output and
  `captured` postcondition/readback for both raw channels of all eight steps.
  `redacted` or `unavailable` evidence is permitted only for `failed` or
  `unverified` records, records its limitation, and can never support
  compatibility. Credentials are never retained. Temporary synthetic fixtures
  cover the validator only; no synthetic fixture or local command probe is an
  L5 host or portability claim, and no real raw host evidence has been created.
- **Fail-closed repository validation (Proposal 3):** JSON entrypoints guard
  top-level and nested types before field access, local Markdown links remain
  contained in the repository across POSIX and Windows forms and symlink
  resolution, and every documented focused test entrypoint is required by the
  aggregate validator. Malformed inputs return stable findings instead of
  tracebacks.
- **Routing evidence (Proposal 4):** E1 locally verifies the closed schema-v4
  tuning/held-out minimal-pair inventory and deterministic evidence gate. E2
  preserves a full five-repetition `current` baseline even when an observation
  misses its case expectation; such a record uses `Verdict: fail` and remains
  evidence rather than being rejected as malformed. A wording change is then
  eligible only after a measured current miss. The complete
  `conditional-candidate` tuning pair also runs five fresh contexts per case,
  and every candidate observation must match its expectation with
  `Verdict: pass`. `selected` and `entrypoint_loaded` remain independent facts.
  The comparable E2 `current` campaign passed all ten observations (five
  positive and five near-miss), so the earlier conditional predicate edit was
  withdrawn and no `conditional-candidate` campaign was eligible. Codex now
  discovers the installed self-iteration skill. Task 10 then ran the untouched
  held-out pair against the after-all-edits runtime: all five positives selected
  the Skill and loaded its entrypoint, while all five near misses did neither.

Round 1 may close only after the approved development files, runtime/state
hooks, schema changes, negative fixtures, conditional routing branch, and
documentation are reconciled; every selected package's focused tests and the
complete dependency-free validation set pass; the manifest matches the final
Round-1 runtime tree; rejected Proposal-1 work remains absent; and limitations
are reported. This closure is not release-grade evidence. Task 10 must later
run the untouched held-out routing inventory, bind the final candidate and any
real host evidence to the after-all-edits runtime revision, and compare the
temporary package against that runtime revision and the current policy digest
before any release claim.

The current architectural baseline is accepted when:

- `self-iteration/SKILL.md` and the thin Codex UI metadata pass structural
  validation; actual Codex discovery remains an L5 host-evidence question;
- baseline delivery remains distinct from every requested optimization round;
- every round enforces comprehensive coverage, user selection, documentation-
  first implementation, bilateral reconciliation, verification, and closure;
- waiting, pausing, and blocking cannot be mistaken for round completion;
- the final round includes repository hygiene and horizon expansion;
- the schema-v4 evaluation campaign covers routing boundaries and high-risk
  behavior pressure cases;
- complete reviews neither suppress valid net-positive proposals nor force a
  minimum proposal count or negative optimization;
- the repository validator passes without third-party Python packages;
- README structure, commands, compatibility claims, and actual files agree.

The target hosts and current evidence status are:

| Host | Status | Current evidence and limitation |
| --- | --- | --- |
| Codex Desktop/CLI | `targeted / unverified` | A local `codex-cli 0.149.0-alpha.4.3` executable was observed, but no independent clean-host L5 lifecycle evidence is recorded. |
| Claude Code | `targeted / unverified` | The `claude` executable was unavailable during the local probe; no host adapter or lifecycle evidence is recorded. |
| Gemini CLI | `targeted / unverified` | The `gemini` executable was unavailable during the local probe; no host adapter or lifecycle evidence is recorded. |

A target host becomes **verified** only after independent installation,
discovery, entrypoint-loading, behavior, and lifecycle evidence. No host is
verified by the repository contents alone. Codex's `agents/openai.yaml` is a
thin adapter; the Skill instructions otherwise have no runtime dependency. The
optional local validator requires Python 3.9 or newer. Bash examples target
Linux and macOS; PowerShell examples target Windows PowerShell 7 or newer.

The complete [host-support record](docs/host-support.md) distinguishes observed
command availability from the still-unverified discovery, execution, refusal,
collision, upgrade, and uninstall lifecycle. Source-layout instructions below
are intended setup guidance, not proof that a particular host has installed or
loaded the Skill.

The evaluation campaign is **high-risk** because the Skill can guide work across
`credentials`, `untrusted_content`, `external_write`, `destructive`, `public`,
and `hard_to_recover` surfaces. The active specification is
`evaluation/eval-spec.json`, which requires a no-Skill control, five fresh
repetitions per compared variant, and manual review. Invocation does not grant
authority: each protected operation still requires the user's explicit
permission and an observable postcondition.

All 20 required no-Skill behavior controls are recorded under
`evaluation/evidence/control/`. Their raw answers are preserved verbatim. The
controls exposed lifecycle failures that justify the current round-barrier,
material-decision, future-authorization, and failure-recovery instructions.
Ten final-runtime held-out routing samples are recorded under
`evaluation/evidence/candidate/`. They verify only the tested Codex routing
boundary. Candidate behavior cases remain unrun and no
`evaluation/eval-result.json` exists, so these records are not release-grade,
host-lifecycle, or portability evidence.

## Install

The commands in this section describe the repository's intended Codex-oriented
source layout. Before treating them as a host installation procedure, check the
[host-support record](docs/host-support.md) and run that host's clean acceptance
test. No current target host is marked compatible or verified by these commands
alone.

### With the Skill installer

Ask Codex:

```text
Use $skill-installer to install the self-iteration skill from
https://github.com/JoenardoQ/SKILL-of-Codex-Self-Iteration/tree/main/self-iteration
```

Restart Codex after installation so the Skill list is refreshed.

### Linux and macOS

Clone the repository and expose the Skill from the user-level discovery folder:

```bash
git clone https://github.com/JoenardoQ/SKILL-of-Codex-Self-Iteration.git
mkdir -p ~/.agents/skills
ln -s "$PWD/SKILL-of-Codex-Self-Iteration/self-iteration" \
  ~/.agents/skills/self-iteration
```

If symbolic links are unsuitable on the target system, copy the
`self-iteration` directory into `~/.agents/skills/` instead.

### Windows PowerShell

Clone the repository and create the discovery directory:

```powershell
git clone https://github.com/JoenardoQ/SKILL-of-Codex-Self-Iteration.git
New-Item -ItemType Directory -Force "$HOME\.agents\skills"
```

With Windows Developer Mode enabled, link the Skill:

```powershell
New-Item -ItemType SymbolicLink `
  -Path "$HOME\.agents\skills\self-iteration" `
  -Target "$PWD\SKILL-of-Codex-Self-Iteration\self-iteration"
```

Otherwise, copy it:

```powershell
Copy-Item -Recurse `
  "$PWD\SKILL-of-Codex-Self-Iteration\self-iteration" `
  "$HOME\.agents\skills\self-iteration"
```

Restart Codex after linking or copying the Skill.

### Update, migrate, and uninstall

To update a cloned installation:

```bash
git -C SKILL-of-Codex-Self-Iteration pull --ff-only
```

On a new computer, clone the repository again and recreate the discovery link;
do not copy an old machine's absolute symbolic link. If the installation was
copied rather than linked, back up local modifications and replace the copied
`self-iteration` directory from the updated clone. Run the repository validator
after every migration or update.

To uninstall a linked installation, remove only the
`~/.agents/skills/self-iteration` link. Remove a copied installation directory
only after confirming that it is not the working source repository.

## Use

Invoke the Skill explicitly and state the desired number of rounds:

```text
Use $self-iteration to establish the baseline and improve this project for two
complete rounds. Ask for my selection before implementing optional proposals.
```

For an existing project:

```text
Use $self-iteration to reconcile the README with the current code, then run one
complete optimization round. Breaking changes are not allowed.
```

To make the workflow the default across projects, add a global Codex instruction
that says substantial project creation and architectural changes must use
`$self-iteration`. Keep explicit invocation available for tasks where automatic
activation is not desired. Repository-specific instructions and the user's
current request still take precedence.

## Durable state and resumption

Short runs may keep their round ledger in the active task plan. Longer or
cross-task runs should store an iteration-state document in the project. The
record includes the round ID and limit, lifecycle state, baseline revision,
scope, coverage, findings, approved items, documentation and implementation
changes, verification, risks, blockers, and closing evidence.

Copy `self-iteration/assets/iteration-state.md` into the target project when a
durable record is needed. It tracks lifecycle `phase` independently from
execution `status` so a paused or blocked round cannot appear closed.

On resume, the active agent validates this record against the repository before
continuing. It never assumes that an interrupted round closed or that an earlier
proposal is still valid after the project changed.

## Repository layout and boundaries

`self-iteration/` is the canonical runtime bundle. It contains only the files a
host needs to load and follow the Skill. Repository-development material—host
support records, evaluation specifications and evidence, release policy, tests,
plans, and generated release artifacts—must remain outside that directory.
The architectural baseline has the following product tree. Temporary
`.superpowers/` development-control planes are excluded from the final tree;
they are not part of the repository product or runtime bundle.

```text
.
├── CHANGELOG.md
├── LICENSE
├── README.md
├── docs/
│   ├── final-round-report.md
│   ├── host-support.md
│   └── superpowers/
│       ├── plans/2026-08-29-cross-host-self-iteration-plan.md
│       ├── plans/2026-08-30-round-1-approved-addendum.md
│       └── specs/2026-08-29-cross-host-self-iteration-design.md
├── evaluation/
│   ├── eval-spec.json
│   ├── runtime-manifest.json       development metadata, never packaged
│   └── evidence/
│       ├── control/          20 preserved no-Skill samples
│       ├── candidate/        10 final-runtime held-out routing samples
│       └── routing-tuning/current/  10 active E2 tuning samples
├── release-policy.json
├── scripts/
│   ├── test_control_evidence_validator.py
│   ├── test_host_support_validator.py
│   ├── test_repo_validator.py
│   ├── test_routing_evidence_validator.py
│   ├── test_runtime_revision.py
│   ├── runtime_revision.py
│   └── validate_repo.py
├── self-iteration/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── assets/iteration-state.md
│   └── references/
│       ├── final-round.md
│       ├── review-matrix.md
│       └── round-protocol.md
```

`SKILL.md` contains activation rules and non-negotiable invariants. The reference
files contain the detailed protocol and are loaded only when relevant. The
schema-v4 evaluation specification tests routing, decisions, and lifecycle
invariants rather than exact wording. It separates an executable inventory from
evaluation results: passing its structural validator does not claim a full
candidate behavior campaign, host-lifecycle run, or portability result.

### Evaluation migration map

The consolidated behavior cases retain every decision invariant from the retired
15-scenario inventory; none was discarded as redundant without a replacement.

| Retired scenario | Active pressure case and retained invariant |
| --- | --- |
| New project with two optimization rounds | `round-integrity-and-proposal-quality`: baseline separation, sequential counted rounds, and per-round approval. |
| Existing README conflicts with code | `round-integrity-and-proposal-quality`: ask the user for the material product decision before choosing a forward contract. |
| A round finds no proposals | `round-integrity-and-proposal-quality`: count the complete no-proposal round and continue. |
| Multiple rounds are preauthorized | `round-integrity-and-proposal-quality`: round count is distinct from optional-change approval. |
| Pause and resume mid-round | `partial-failure-and-recovery`: later-task resume from durable `IMPLEMENT`/`PAUSED` state, repository reconciliation, and continuation of the same open round. |
| Final cleanup meets dynamic code | `authority-denial-and-staleness`: retain or seek evidence for ambiguous dynamic use. |
| User rejects all proposals | `round-integrity-and-proposal-quality`: record rejection without implementation. |
| A horizon idea is selected | `round-integrity-and-proposal-quality`: preserve verified state and request fresh future-round and scope authorization before implementation. |
| Huge repository cannot be scanned completely | `round-integrity-and-proposal-quality`: name omitted partitions and evidence limits, qualify the review, and prohibit hidden coverage gaps. |
| Baseline only, with no optimization round | `round-integrity-and-proposal-quality`: proceed directly to `FINALIZE` and prohibit an invented `ROUND_REVIEW`. |
| Final cleanup lacks deletion authority | `authority-denial-and-staleness`: preserve protected state and keep the decision open. |
| Required verification fails | `partial-failure-and-recovery`: retain `VERIFY` with `BLOCKED` or `WAITING_USER` and an exact resume condition. |
| Scope changes during an open round | `partial-failure-and-recovery`: update documentation first and refresh affected evidence. |
| Final round rejects every optional proposal | `round-integrity-and-proposal-quality`: final hygiene, reconciliation, verification, and horizon gates still run. |
| Review pressure does not create a proposal quota | `round-integrity-and-proposal-quality`: report only evidence-backed net-positive changes. |

## Validate

Run the dependency-free repository validator:

```bash
python3 -B scripts/validate_repo.py
```

The validator checks the repository contract, control-evidence structure,
runtime-bundle boundary, product-document links, host-support claims, and text
file modes. Verbatim `Raw answer` sections may retain Markdown hard-break spaces;
their seven canonical metadata fields and exact-token manual verdict outcomes
remain validated. The ignored `.superpowers/` control plane is deliberately
outside the product-document link scan.

Run the focused control-evidence and host-support validator suites:

```bash
python3 -B scripts/test_repo_validator.py
python3 -B scripts/test_runtime_revision.py
python3 -B scripts/test_host_support_validator.py
python3 -B scripts/test_control_evidence_validator.py
python3 -B scripts/test_routing_evidence_validator.py
python3 -B scripts/runtime_revision.py check \
  --runtime-root self-iteration --manifest evaluation/runtime-manifest.json
```

On Windows PowerShell:

```powershell
py -3 scripts/validate_repo.py
```

When `agent-skill-author` is installed under your Codex home directory, run its
validator with the repository release policy. Set `CODEX_HOME` to that
installation root first (Codex commonly sets it already):

```bash
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/validate_skill.py" \
  self-iteration --policy release-policy.json
```

Then validate the repository evaluation specification. The no-Skill behavior
controls are already recorded; E1's routing schema and evidence gate are locally verified, and E2 preserves
ten passing current-description tuning observations. The final-runtime held-out routing pair now has ten passing manually reviewed
observations; the full behavior candidate campaign remains unrun. For
workflow changes, verify both the intended decision and the explicitly forbidden
shortcut. Structural validation and local packaging cannot prove candidate
behavior, host lifecycle behavior, or portability.

```bash
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/validate_eval_spec.py" \
  evaluation/eval-spec.json
```

## Scope and limitations

This repository supplies instructions, not an autonomous background service. The
quality of a review remains bounded by available repository access, runnable
tooling, evidence, and user decisions. The Skill must disclose incomplete scans
and verification gaps instead of presenting them as comprehensive success.

The Skill does not grant permission for deployments, publishing, new external
dependencies, breaking changes, deletion of ambiguous public or dynamically
discovered interfaces, or other actions outside the user's authorization.

## License

Released under the [MIT License](LICENSE).
