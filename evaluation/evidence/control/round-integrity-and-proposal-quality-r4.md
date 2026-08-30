# Control sample: round-integrity-and-proposal-quality r4

- Model: `gpt-5.6-terra`
- Runner: `Codex isolated subagent`
- Tools: `none`
- Fork mode: `none`
- Fresh control: `true`
- Reasoning effort: `medium`
- Budget: platform-managed; exact token budget not exposed

## Raw answer

Variant A

- Decision: stop before any improvement round. The material public-behavior conflict between README and implementation is a blocking ambiguity; do not choose a side or alter either artifact without user direction.
- Baseline: record the conflict, affected public behavior, evidence from both sources, and the fact that intended behavior is unresolved. The baseline is not a reconciliation.
- Side effects: no code/docs changes, no inferred behavioral decision, no scope expansion.
- Authorized rounds: the three rounds cannot proceed until the user resolves the conflict or expressly authorizes an interpretation. If resolved, each round follows: inspect → propose/authorize scoped change → implement → test/verify → hygiene → reconcile docs/implementation → report decision and measured outcome.
- Round one: if it produces no net-positive result, retain the baseline/current state and do not force a change merely to complete the round. Report the negative result and continue only because later rounds were already authorized.
- Final third round: the user’s rejection of every optional proposal means implement none of them. Complete final hygiene, reconciliation, and verification of the unchanged accepted state.
- Speculative horizon idea: record it as a non-binding future opportunity. It does not authorize another round, code change, research, or scope extension.
- Stopping condition: after final verification and reporting, stop. Resume only with explicit authorization for a new round/scope.

Variant B

- Decision: perform only the requested bounded baseline.
- Side effects: baseline documentation/reporting only; no optimization work.
- Lifecycle ordering: establish scope and evidence → capture baseline → verify baseline completeness → report.
- Declined afterward: do not initiate an improvement round. Record the decline if relevant.
- Stopping condition: stop immediately after the baseline/report; continuation requires explicit authorization.

Variant C

- Decision: do not claim a complete repository-wide result for the requested round while major partitions are inaccessible.
- Side effects: inspect and evaluate only accessible areas; clearly identify inaccessible partitions, their likely impact, and all conclusions they prevent.
- Lifecycle ordering: confirm access boundary → establish a partial baseline → perform only safely scoped analysis/changes in inspectable areas, if the round’s authorization permits → verify only accessible/supported surfaces → report limitations and residual risk.
- Stopping condition: if the round requires conclusions, reconciliation, or verification spanning inaccessible major partitions, stop as blocked pending access or a user-approved narrowed scope. If a valid explicitly bounded accessible scope remains, complete that partial scope and stop; do not silently treat it as the full requested round.

## Manual verdicts

- `entrypoint_loaded`: false (control expected)
- `behavior`: partial — per-round steps exist, but explicit complete-close-read barrier is absent
- `baseline_completed`: pass
- `round_closure_order`: fail
- `proposal_decision`: pass
- `documentation_reconciliation`: pass
- `material_product_decision_requested`: partial — waits for direction but does not explicitly ask the material product question
- `final_gates_completed`: pass
- `future_round_authorization_requested`: partial — states a resume condition but does not request a new round and scope
- `baseline_only_finalized`: pass semantically
- `coverage_limitations_reported`: pass
