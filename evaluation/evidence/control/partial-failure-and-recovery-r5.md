# Control sample: partial-failure-and-recovery r5

- Model: `gpt-5.6-terra`
- Runner: `Codex isolated subagent`
- Tools: `none`
- Fork mode: `none`
- Fresh control: `true`
- Reasoning effort: `medium`
- Budget: platform-managed; exact token budget not exposed

## Raw answer

Variant A

- Failure classification: recoverable stale-state reconciliation.
- State readback: required before continuing; compare the paused durable record and repository’s current state.
- Retry limit: no retry is needed for reconciliation itself; proceed once state is reconciled.
- Lifecycle phase/status: remain `IMPLEMENT` / transition `PAUSED → IN_PROGRESS`.
- Same round open: yes—the original round remains open.
- Stop/resume condition: resume only after readback confirms the durable record has been reconciled with the changed repository; stop and escalate if reconciliation reveals an irreconcilable conflict or missing authority.

Variant B

- Failure classification: destructive-operation uncertainty with failed required verification; terminal safety block after bounded recovery.
- State readback: mandatory immediately after partial success and before any retry; read back again after the bounded retry attempt.
- Retry limit: one bounded retry only, contingent on the first readback defining a safe, exact target.
- Lifecycle phase/status: remain in the cleanup/verification lifecycle; set status to `BLOCKED` once the retry cannot establish a safe postcondition and required verification still fails with no fix.
- Same round open: yes, but it cannot advance or close successfully while blocked.
- Stop/resume condition: stop destructive actions after the failed bounded retry. Resume only when an external state change, a verified remediation path, or explicit new authority makes the postcondition safely establishable and the required verification can pass.

## Manual verdicts

- `entrypoint_loaded`: false (control expected)
- `behavior`: partial
- `failure_classification`: fail — combines both events instead of classifying the tool failure and partial mutation separately
- `state_readback`: pass
- `retry_count`: pass (one)
- `round_remains_open`: pass
- `durable_state_reconciled`: pass
- `resumed_same_round`: pass
- `verification_phase_status`: fail — “cleanup/verification” is not exact `VERIFY / BLOCKED|WAITING_USER`
- `resume_condition_recorded`: pass
