# Round Protocol

## Contents

- [Definitions](#definitions)
- [Establish the contract](#establish-the-contract)
- [Lifecycle phase and execution status](#lifecycle-phase-and-execution-status)
- [Baseline delivery](#baseline-delivery)
- [Optimization round](#optimization-round)
- [Approval and authority](#approval-and-authority)
- [Durable state and resumption](#durable-state-and-resumption)
- [Closing conditions](#closing-conditions)
- [Failure and recovery](#failure-and-recovery)

## Definitions

A **baseline delivery** creates or reconciles the documented project contract,
implements the initially requested scope, and verifies the result. It is not an
optimization round unless the user explicitly defines it that way.

An **optimization round** is a current, evidence-backed review followed by user
selection, documentation-impact handling, implementation of approved scope,
bilateral reconciliation, verification, and explicit closure. The first round
establishes full coverage; later rounds may carry forward evidence after its
invalidation conditions are revalidated.

## Establish the contract

At the beginning determine and record:

- desired outcome, users, scope, non-goals, constraints, and acceptance criteria;
- whether the project is new or existing;
- authorized optimization-round count, if supplied;
- whether breaking changes and new dependencies are permitted;
- whether the final hygiene gate may delete material sufficiently proven dead or
  obsolete, and any exclusions from that authority;
- required verification, delivery boundaries, and external actions that remain
  separately gated.

Do not invent a round count. If none was supplied, finish the baseline and ask
whether to begin an optimization round.

## Lifecycle phase and execution status

Track two independent fields. `phase` describes workflow position:

```text
BASELINE -> FINALIZE (when no optimization round is authorized)
BASELINE -> ROUND_REVIEW -> USER_APPROVAL -> DOC_UPDATE -> IMPLEMENT
         -> RECONCILE -> VERIFY -> FINAL_GATES (final round only)
         -> ROUND_CLOSE -> ROUND_REVIEW or FINALIZE
```

`status` is one of:

- `ACTIVE`: work may continue in the current phase;
- `WAITING_USER`: a material decision or approval is required;
- `PAUSED`: work is intentionally suspended but resumable;
- `BLOCKED`: a concrete access, authority, evidence, or execution condition
  prevents progress;
- `CLOSED`: the baseline or round reached an authorized terminal boundary.

Only `ROUND_CLOSE` or `FINALIZE` may use `CLOSED`. Waiting, pausing, blocking, or
failing verification keeps the current round open. When a blocker is reported,
retain its phase and record the exact condition needed to resume.

Exactly one round may be active. Its boundary begins with current-state
revalidation and ends only after closing evidence is recorded. Multiple-round
authorization permits sequential repetition, not concurrent review or advance
thinking. A baseline
with no authorized optimization round may proceed directly to `FINALIZE` after
its own reconciliation and verification.

## Baseline delivery

For a new project, clarify material ambiguity and write `README.md` before
substantial implementation. The README or linked `docs/` files should cover the
purpose, users, use cases, scope, non-goals, requirements, constraints,
architecture, boundaries, data flow, important interfaces and algorithms, setup,
run/build/test commands, acceptance criteria, status, and limitations.

For an existing project, inspect repository instructions, documentation, source,
tests, configuration, schemas, dependencies, and operational artifacts. Code is
evidence of current behavior, not proof of intent. Reconcile factual drift and
when current behavior and apparent intent imply materially different product or
architecture choices, ask a concrete question that names the competing choices
and the decision needed. Do not wait passively or choose the forward contract
without that material product decision.

Implement the smallest coherent approved increment. If construction disproves a
documented assumption, update documentation deliberately; do not silently change
the requirement to fit the code. Afterwards, inspect the result and reconcile
documented claims and implemented behavior in both directions.

## Optimization round

1. Set phase to `ROUND_REVIEW` and status to `ACTIVE`. In the first round, build
   the complete inventory and coverage ledger. In a later round, compare current
   repository, instruction, scope, contract, dependency, and runtime state with
   recorded invalidation conditions. Carry forward only evidence whose
   conditions remain valid; refresh invalidated entries and affected
   cross-cutting areas. Re-inventory the whole scope after a material broad
   change or an explicit request for independent full passes.
2. Complete the applicable passes in `review-matrix.md`. Accumulate current
   findings without returning early or reserving known opportunities for later
   rounds.
3. Present the entire current proposal set and compact coverage summary. When
   proposals exist, set phase to `USER_APPROVAL` and status to `WAITING_USER`,
   then stop for selection. If none exist, record that result, keep status
   `ACTIVE`, and proceed to reconciliation and verification without an empty
   approval request.
4. For approved work, assess whether it changes documented behavior,
   architecture, commands, migration, or acceptance criteria. If it does, set
   phase to `DOC_UPDATE`, restore status to `ACTIVE`, and update the owning README
   or design documentation first. Otherwise record no documentation impact and
   proceed directly to implementation.
5. Set phase to `IMPLEMENT`. Make the approved implementation and test changes
   while preserving unrelated user work.
6. Set phase to `RECONCILE`. Inspect the resulting implementation and correct
   documented-but-unimplemented, implemented-but-undocumented, obsolete,
   incorrect-command, missing-failure-behavior, and unmet-acceptance-criterion
   drift.
7. Set phase to `VERIFY`. Run the strongest proportionate available tests,
   checks, builds, and inspections. Resolve regressions. If a failure cannot be
   resolved, set status to `BLOCKED` or `WAITING_USER`; do not close the round.
8. If this is the final round, set phase to `FINAL_GATES` and execute
   `final-round.md` before closure.
9. Set phase to `ROUND_CLOSE` and status to `CLOSED` only when all closing
   conditions pass. State
   explicitly that the round is complete.

When the user rejects every proposal, record the decision, restore status to
`ACTIVE`, skip `DOC_UPDATE` and `IMPLEMENT`, and continue through reconciliation,
verification, and any required final gates. Rejection is not a blocker.

If, before review, the user explicitly requests proposal-only rounds and directs
that every proposal be recorded as rejected, treat that direction as the
proposal decision for each authorized round. Complete the current review and
proposal set, record the rejection, skip `DOC_UPDATE` and `IMPLEMENT`, then run
read-only reconciliation, verification, final gates when applicable, and close
the round before beginning the next. Do not ask for selection under that policy,
and do not divide one review into artificial proposal batches to fill the round
count. Without this explicit rejection policy, proposals still stop at
`USER_APPROVAL / WAITING_USER`.

A round with no justified proposal still records coverage freshness,
verification or inspection evidence, material risks, and closing evidence. It
counts toward the authorized number. Continue to the next authorized round after
closure unless the user cancels or a concrete blocker prevents it.

## Approval and authority

Number proposals so the user can select them precisely. Rejection or deferral is
not approval. Changes required to correct a defect within the already requested
delivery may proceed when they are normal in-scope implementation; optional
optimization changes wait at `USER_APPROVAL`.

Never infer permission for deployments, publishing, breaking changes, new
external dependencies, destructive cleanup, or effects outside the scoped
repository. If final cleanup deletion was not authorized at contract start, ask
before deleting material; analysis and reporting may continue.

If the user changes scope during a round, keep the round open, update its
contract and documentation first, invalidate affected evidence, and repeat the
necessary review or verification. Start over only if the user explicitly cancels
or restarts the round. Cancellation closes the current scope but is not evidence
that its original acceptance criteria passed.

## Durable state and resumption

Keep resumption state in host or task storage by default. A project-local
iteration-state document is warranted only when the user or repository requires
a shared cross-task record and authorizes its location and persistence. That
record contains:

- `round_id`, `round_limit`, `phase`, `status`, and `baseline_revision`;
- `Skill runtime revision` plus `Runtime revision source`; the source is only a
  checked development manifest, an independently recomputed verified archive,
  a host binding, or `unknown`;
- outcome, scope, constraints, exclusions, and deletion authority;
- inventory and coverage ledger;
- findings and the complete proposal set;
- approved, rejected, deferred, and withdrawn items;
- documentation changes and implementation changes;
- verification commands, results, risks, blockers, and limitations;
- completion evidence and whether final gates have passed.

On resume, compare the record with repository status and current instructions.
If the repository changed, refresh affected evidence without starting a later
round. A missing, legacy, or invalid runtime revision is `unknown`: it permits
safe continuation only after repository state and current instructions are
revalidated, and it cannot establish behavior, host, compatibility, or release
provenance. A receipt alone never supplies the revision or its source. An
interrupted state remains open until its closure conditions are met.
Use `assets/iteration-state.md` as the copyable schema when a project-level
record is warranted.

## Closing conditions

Close a round only when:

- coverage is complete or every concrete limitation is disclosed;
- selected scope is implemented or explicitly withdrawn;
- required documentation-impact changes and bilateral reconciliation are
  complete;
- required verification completed and failures are resolved; unavailable or
  non-required checks are disclosed as limitations;
- risks, rejected/deferred proposals, blockers, and completion evidence are
  reported;
- required final hygiene and horizon gates passed.

Only after explicit closure may another authorized round begin. Until then, do
not open, read, inventory, plan, or brainstorm from any source for the next
round. Completion of all authorized rounds or user cancellation are terminal
stop conditions. A missing material decision, missing authority, or concrete
blocker changes status and pauses the open round; it does not close it. Absence
of new proposals is not an early-stop condition when more rounds remain
authorized.

## Failure and recovery

Classify each failure as `input`, `authority`, `environment`, `transient
dependency`, `implementation`, or `uncertain state`. When a tool fails after an
operation has changed some targets, create separate records for the tool failure
and the partial mutation. Identify attempted, changed, unchanged, failed,
skipped, and unknown subjects; do not summarize them as one failed command.

Retry only after re-resolving relevant state and only when the next bounded
attempt can add evidence. Never route around denied authority. If a required
verification remains unresolved, retain phase `VERIFY`, set status `BLOCKED` or
`WAITING_USER`, keep the same round open, and record the exact observable resume
condition. Recovery continues that round; it does not create or close a new one.

After a final round closes, selecting a horizon idea is not permission to act.
Ask the user directly whether they authorize a named future round and its
specific scope. Preserve the verified final state until both are authorized.
