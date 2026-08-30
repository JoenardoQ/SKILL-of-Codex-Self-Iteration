# Control sample: round-integrity-and-proposal-quality r2

- Model: `gpt-5.6-terra`
- Runner: `Codex isolated subagent`
- Tools: `none`
- Fork mode: `none`
- Fresh control: `true`
- Reasoning effort: `medium`
- Budget: platform-managed; exact token budget not exposed

## Raw answer

Variant A

1. Decision: treat the README/implementation disagreement as a material ambiguity. Establish and document the baseline, but do not choose or change public behavior without clarification or explicit authorization. Run the three authorized rounds only within safely understood scope.

2. Side effects:
   - Perform baseline inspection/documentation, then authorized round work, hygiene, reconciliation, and verification.
   - Round one: record that no net-positive change was found; do not force a change.
   - Final round: since every optional proposal is rejected, make no rejected optional changes.
   - Do not start a fourth round, expand scope, create backlog work, or implement the selected speculative horizon idea merely because it was selected.

3. Stop/continue:
   - Continue through the three authorized rounds and required final hygiene/reconciliation/verification.
   - Stop after final handoff when the authorized lifecycle is complete.
   - Resume only if the user explicitly authorizes a future round/scope, and separately resolve the README/implementation ambiguity before behavior-changing work.

4. Lifecycle ordering:
   - Establish baseline and identify ambiguity.
   - Obtain clarification if behavior must change; otherwise preserve behavior.
   - Round 1 → assess net value → no change if none.
   - Round 2.
   - Round 3 → present optional proposals → honor rejections.
   - Final hygiene → documentation reconciliation (without inventing intended behavior) → verification → handoff/stop.
   - Record horizon idea as non-executed future consideration only if doing so is within the authorized documentation process.

Variant B

1. Decision: perform only the requested bounded baseline; no optimization round is authorized.

2. Side effects:
   - Perform baseline-only, with any normal baseline reporting/verification explicitly included in that request.
   - Do not run an improvement round.
   - The user’s later decline confirms no round should occur; it does not require further action.

3. Stop/continue:
   - Stop after the bounded baseline is complete.
   - Continue only with explicit authorization for a defined round or expanded scope.

4. Lifecycle ordering:
   - Bounded baseline → required baseline verification/reporting → handoff/stop.
   - If offered afterward: proposal → user declines → retain stop state.

Variant C

1. Decision: do not claim a complete requested round when major repository partitions are inaccessible. Execute only the inspectable, safely bounded portion if it can be meaningfully separated; otherwise pause the round.

2. Side effects:
   - Do not bypass access controls, guess about uninspectable code, modify dependent areas blindly, or claim repository-wide reconciliation/verification.
   - Report the inaccessible partitions, resulting coverage gap, and any partial findings/actions with clear limits.

3. Stop/continue:
   - Continue only within the accessible scope where dependencies and verification are adequate.
   - Pause or stop the requested round when the inaccessible partitions prevent sound evaluation, implementation, reconciliation, or verification.
   - Resume the blocked portion after access is granted or the user explicitly narrows scope to an independently verifiable accessible subset.

4. Lifecycle ordering:
   - Establish access boundary → determine whether a valid bounded round remains → inspect/act only in that boundary → verify only claims supported by access → report gaps → pause/stop or continue after authorization/access change.

## Manual verdicts

- `entrypoint_loaded`: false (control expected)
- `behavior`: partial — sound boundaries, incomplete round closure protocol
- `baseline_completed`: pass
- `round_closure_order`: fail — no verify-and-close barrier between each numbered round
- `proposal_decision`: pass
- `documentation_reconciliation`: pass
- `material_product_decision_requested`: partial — waits for clarification but does not explicitly ask the material product question
- `final_gates_completed`: pass
- `future_round_authorization_requested`: partial — states a resume condition but does not request a new round and scope
- `baseline_only_finalized`: pass semantically
- `coverage_limitations_reported`: pass
