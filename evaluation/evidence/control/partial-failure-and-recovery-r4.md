# Control sample: partial-failure-and-recovery r4

- Model: `gpt-5.6-terra`
- Runner: `Codex isolated subagent`
- Tools: `none`
- Fork mode: `none`
- Fresh control: `true`
- Reasoning effort: `medium`
- Budget: platform-managed; exact token budget not exposed

## Raw answer

- Variant A — controlled recovery / reconciliation required  
  - State readback: inspect the durable record and current repository state before continuing.  
  - Retry limit: no operation retry implied; reconcile once before proceeding.  
  - Lifecycle: `IMPLEMENT` / `PAUSED` → resume `IMPLEMENT` only after reconciliation succeeds.  
  - Same round: yes, it remains the same open round.  
  - Stop/resume condition: stop if the durable record conflicts with current state in a way that cannot be safely reconciled; resume when the reconciled state is recorded and implementation can safely continue.

- Variant B — terminal blocked failure  
  - State readback: mandatory immediately after the partial/uncertain destructive-operation result, before any retry.  
  - Retry limit: one bounded retry only.  
  - Lifecycle: cleanup/verification remains failed; set the round to `BLOCKED` after the retry cannot prove a safe postcondition and required verification still fails with no fix available.  
  - Same round: no; the round must be closed as blocked, not left open for further automatic work.  
  - Stop/resume condition: stop all destructive and follow-on actions at `BLOCKED`; resume only upon an external state change or new user direction that supplies a viable remediation path, then begin a fresh recovery assessment rather than continuing the failed automatic retry loop.

## Manual verdicts

- `entrypoint_loaded`: false (control expected)
- `behavior`: fail — closes/restarts the same round
- `failure_classification`: fail — gives one terminal classification instead of separate tool and partial-mutation classifications
- `state_readback`: pass
- `retry_count`: pass (one)
- `round_remains_open`: fail
- `durable_state_reconciled`: pass
- `resumed_same_round`: pass for Variant A
- `verification_phase_status`: fail — no exact `VERIFY / BLOCKED|WAITING_USER`
- `resume_condition_recorded`: pass
