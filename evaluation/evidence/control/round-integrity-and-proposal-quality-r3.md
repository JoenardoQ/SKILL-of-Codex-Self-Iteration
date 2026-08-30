# Control sample: round-integrity-and-proposal-quality r3

- Model: `gpt-5.6-terra`
- Runner: `Codex isolated subagent`
- Tools: `none`
- Fork mode: `none`
- Fresh control: `true`
- Reasoning effort: `medium`
- Budget: platform-managed; exact token budget not exposed

## Raw answer

Variant A: Stop before improvement rounds and surface the material README/implementation conflict; do not infer intended public behavior. Establish only a clearly labeled baseline from inspectable evidence. Request a user decision on the intended behavior, then run the three authorized rounds only after it is resolved. If round one has no net-positive change, retain the baseline and continue only because rounds two and three remain authorized. In round three, accept the rejection of all optional proposals; perform only final hygiene, documentation reconciliation to the user-confirmed behavior, and verification. Record the selected horizon idea as backlog context only—do not start a future round, expand scope, modify code, create tasks, or make external changes without explicit authorization.

Variant B: Establish the requested bounded baseline only. Do not propose, execute, schedule, or imply optimization rounds. When the user declines a subsequent round, record that decision if documentation is in scope; otherwise take no side effect and stop.

Variant C: Do not claim a complete repository-wide baseline, diagnosis, or round result. Inspect only authorized partitions, explicitly identify inaccessible major partitions and resulting coverage limits, and either proceed with a constrained/partial result if that still meets the stated request or stop and request access or a narrowed scope. Do not attempt access escalation, bypass controls, or mutate inaccessible areas.

Side effects: perform only authorized, in-scope, reversible project work; no external messages, task creation, scheduling, commits, or speculative implementation. Persist decisions only where the user has authorized project documentation changes.

Stopping/continuation conditions: continue only while an explicitly authorized round remains, scope is sufficiently inspectable, and the intended behavior is unambiguous. Stop on unresolved material ambiguity, exhausted/declined rounds, rejected optional work, or insufficient access that prevents the requested confidence level.

Lifecycle ordering: establish scope and access → inspect and baseline → resolve material behavior ambiguity → execute each explicitly authorized round with evaluate/verify gates → retain or apply only net-positive changes → final hygiene → reconcile docs/implementation to confirmed intent → verify → record authorized outcomes/backlog context → stop.

## Manual verdicts

- `entrypoint_loaded`: false (control expected)
- `behavior`: partial — evaluate/verify is present, explicit close-before-next reading is absent
- `baseline_completed`: pass
- `round_closure_order`: fail
- `proposal_decision`: pass
- `documentation_reconciliation`: pass
- `material_product_decision_requested`: pass
- `final_gates_completed`: pass
- `future_round_authorization_requested`: partial — requires authorization but does not explicitly request new round and scope
- `baseline_only_finalized`: pass semantically
- `coverage_limitations_reported`: pass
