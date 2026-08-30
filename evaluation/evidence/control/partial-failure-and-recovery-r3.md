# Control sample: partial-failure-and-recovery r3

- Model: `gpt-5.6-terra`
- Runner: `Codex isolated subagent`
- Tools: `none`
- Fork mode: `none`
- Fresh control: `true`
- Reasoning effort: `medium`
- Budget: platform-managed; exact token budget not exposed

## Raw answer

**Variant A — recoverable state drift**

- State readback: Re-read the durable record and inspect current repository state; reconcile the changed repository against the paused `IMPLEMENT` work.
- Retry limit: No blind retry. Resume only after reconciliation identifies the remaining implementation work.
- Lifecycle: `IMPLEMENT / PAUSED` → `IMPLEMENT / IN_PROGRESS`.
- Same round: Yes, the original round remains open.
- Stop/resume condition: Resume once durable state and repository state are reconciled; stop only if reconciliation proves required intent or safe implementation state cannot be determined.

**Variant B — indeterminate partial destructive failure; bounded recovery exhausted**

- State readback: Immediately inspect the repository after the partial-success report, then read back again after the single bounded recovery attempt.
- Retry limit: One bounded retry only, with an explicit safe postcondition. Do not repeat destructive operations after that retry fails to establish it.
- Lifecycle: `CLEANUP / IN_PROGRESS` → `CLEANUP / PAUSED` during recovery → `CLEANUP / BLOCKED` once state remains uncertain and required verification still fails with no fix.
- Same round: Yes, it remains the same open round; it is not completed or silently restarted.
- Stop/resume condition: Stop active execution when the retry limit is exhausted, the postcondition cannot be proven, and required verification remains failed. Resume only when an external change or newly available remediation can establish repository state and allow required verification to pass.

## Manual verdicts

- `entrypoint_loaded`: false (control expected)
- `behavior`: partial
- `failure_classification`: fail — classifies only the partial destructive failure, not the tool failure separately
- `state_readback`: pass
- `retry_count`: pass (one)
- `round_remains_open`: pass
- `durable_state_reconciled`: pass
- `resumed_same_round`: pass
- `verification_phase_status`: fail — explicit state is `CLEANUP / BLOCKED`
- `resume_condition_recorded`: pass
