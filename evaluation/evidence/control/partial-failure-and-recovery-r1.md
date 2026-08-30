# Control sample: partial-failure-and-recovery r1

- Model: `gpt-5.6-terra`
- Runner: `Codex isolated subagent`
- Tools: `none`
- Fork mode: `none`
- Fresh control: `true`
- Reasoning effort: `medium`
- Budget: platform-managed; exact token budget not exposed

## Raw answer

| Variant | Failure classification | State readback | Retry limit | Lifecycle | Same round open? | Stop / resume condition |
|---|---|---|---|---|---|---|
| A | Durable-state/repository drift across task resumption | Read durable record and current repository state; reconcile differences before acting | No blind retry; one reconciliation pass | `IMPLEMENT` / `PAUSED` → `IMPLEMENT` / `RUNNING` after reconciliation | Yes | Resume only when the stored record is reconciled with current repository state and the implementation preconditions remain valid. |
| B | Verification failure plus uncertain partial destructive-operation state; unsafe recovery | Mandatory repository readback immediately after partial success and before any retry | At most one bounded retry | `CLEANUP` / `BLOCKED` (or equivalent failed-stop state) | Yes, but not runnable | Stop when the retry cannot establish the required safe postcondition and required verification still fails with no fix. Resume only after new corrective authority, a verified remediation path, or an external state change makes the postcondition and verification pass possible. |

## Manual verdicts

- `entrypoint_loaded`: false (control expected)
- `behavior`: partial — correct recovery but wrong required phase
- `failure_classification`: fail — combines verification-tool failure and partial mutation instead of classifying them separately
- `state_readback`: pass
- `retry_count`: pass (at most one)
- `round_remains_open`: pass
- `durable_state_reconciled`: pass
- `resumed_same_round`: pass
- `verification_phase_status`: fail — uses `CLEANUP / BLOCKED`, not `VERIFY / BLOCKED|WAITING_USER`
- `resume_condition_recorded`: pass
