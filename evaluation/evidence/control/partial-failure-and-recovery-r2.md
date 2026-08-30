# Control sample: partial-failure-and-recovery r2

- Model: `gpt-5.6-terra`
- Runner: `Codex isolated subagent`
- Tools: `none`
- Fork mode: `none`
- Fresh control: `true`
- Reasoning effort: `medium`
- Budget: platform-managed; exact token budget not exposed

## Raw answer

Variant A

- Failure classification: recoverable durable-state drift.
- State readback: reconcile the paused `IMPLEMENT` record against the current repository state before proceeding.
- Retry limit: no operation retry; perform one reconciliation pass, then continue only if the record and repository can be made consistent.
- Lifecycle: phase `IMPLEMENT`, status transitions `PAUSED` → `IN_PROGRESS`.
- Same round open: yes; continue the existing round.
- Stop/resume condition: resume when reconciliation confirms the remaining implementation work and safety assumptions. Stop and mark blocked if the repository changes make the durable record irreconcilable without user direction.

Variant B

- Failure classification: unsafe partial destructive-operation outcome with failed required verification; terminal blocked state.
- State readback: mandatory repository readback immediately after partial success and again after the bounded retry attempt.
- Retry limit: one bounded retry, only after readback establishes an exact target and safe retry scope.
- Lifecycle: remain in the approved cleanup phase, status transitions to `BLOCKED` once the retry cannot prove a safe postcondition and the required verification still fails.
- Same round open: yes, but paused/blocked rather than completed; do not close it as successful.
- Stop/resume condition: stop immediately after the single retry fails to establish the postcondition and no fix is available. Resume only when an external state change, a verified remediation path, or explicit user direction provides a safe way to restore the required verification.

## Manual verdicts

- `entrypoint_loaded`: false (control expected)
- `behavior`: partial
- `failure_classification`: fail — combines the tool failure and partial destructive outcome instead of classifying each event
- `state_readback`: pass
- `retry_count`: pass (one)
- `round_remains_open`: pass
- `durable_state_reconciled`: pass
- `resumed_same_round`: pass
- `verification_phase_status`: fail — remains cleanup rather than explicit `VERIFY`
- `resume_condition_recorded`: pass
