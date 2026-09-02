# Iteration State

Prefer host or task state. Copy this file into the target project only when the
user or repository requires a shared cross-task record and authorizes its
location and persistence. Keep facts concise and update them at material phase
or status transitions.

## Identity

- Project:
- Baseline revision:
- Skill runtime revision:
- Runtime revision source: `unknown`
- Round ID:
- Authorized round limit:
- Is final authorized round: yes/no
- Phase: `BASELINE`
- Status: `ACTIVE`
- Last updated:

Valid phases are `BASELINE`, `ROUND_REVIEW`, `USER_APPROVAL`, `DOC_UPDATE`,
`IMPLEMENT`, `RECONCILE`, `VERIFY`, `FINAL_GATES`, `ROUND_CLOSE`, and
`FINALIZE`.

Valid statuses are `ACTIVE`, `WAITING_USER`, `PAUSED`, `BLOCKED`, and `CLOSED`.
Only `ROUND_CLOSE` or `FINALIZE` may use `CLOSED`.

## Contract

- Desired outcome:
- Users and use cases:
- Scope:
- Non-goals:
- Constraints:
- Acceptance criteria:
- Breaking changes permitted: yes/no
- New dependencies permitted: yes/no
- Final cleanup deletion authority and exclusions:
- Separately gated external actions:

## Inventory and coverage

- Evidence carried forward from prior round:
- Invalidation conditions checked:
- Evidence invalidated or refreshed:

| Dimension or area | Evidence inspected | Status | Result | Limits |
| --- | --- | --- | --- | --- |
| | | | | |

Unchecked major areas:

## Findings and proposals

| ID | Priority | Evidence | Proposed change | Benefit | Risk | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

## User decisions

- Approved:
- Rejected:
- Deferred:
- Withdrawn:
- Decision evidence:

## Delivery record

- Documentation changes:
- Implementation changes:
- Unrelated user changes preserved:
- Scope changes during this round:
- Evidence invalidated or refreshed after scope/repository changes:

## Verification

| Command or inspection | Result | Required | Limitations |
| --- | --- | --- | --- |
| | | | |

- Unresolved failures:
- Risks:
- Blockers and exact resume condition:

## Failure and side-effect record

| Subject | Failure class | Attempted action | Changed/unchanged/failed/skipped/unknown | Verification or postcondition | Recovery decision |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

- Tool or verification failure:
- Partial mutation or uncertain state:
- Retry bound and evidence expected from another attempt:

## Final gates

- Hygiene gate status and evidence:
- Deleted items and proof:
- Ambiguous retained items and reasons:
- Formatting/style result:
- README/code reconciliation result:
- Horizon review status:
- Proposed future round, if applicable:
- Specific future-round scope:
- Future-round authorization request evidence:
- Future-round authorization decision: requested/pending/approved/rejected
- Future-round authorization decision evidence:

## Closure evidence

- Coverage complete or limitations disclosed:
- Approved scope completed or withdrawn:
- Documentation and implementation reconciled:
- Required verification passed:
- Risks and blockers reported:
- Final gates passed or not applicable:
- Closure or cancellation statement:
- Supported-host evidence and unverified claims:
