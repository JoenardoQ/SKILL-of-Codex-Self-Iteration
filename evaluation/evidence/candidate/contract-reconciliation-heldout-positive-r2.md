# Final candidate held-out routing observation

- Case ID: contract-reconciliation-heldout-positive
- Variant: final-candidate
- Repetition: 2
- Candidate revision: sha256:390c5b82be4d780e3e95efacd901fd555cc36f676c24bc9a94847d43e4d1260f
- Model: gpt-5.6-sol
- Host: WSL Ubuntu-D
- Host build: Codex Desktop 26.818.8289.0 / codex-cli 0.149.0-alpha.4.3
- Runner: native WSL codex exec --ephemeral --json --sandbox read-only
- Tools: exec_command (read-only)
- Sampling: unavailable: Codex runner exposes no sampling controls
- Budget: platform-managed; exact per-run budget not exposed
- Selected: true
- Entrypoint loaded: true
- Reviewer: Codex primary-agent manual event review
- Verdict: pass
- Evidence status: active
- Limitations: held-out routing only; complete event streams were reviewed in-session but are not retained, so this is not a full candidate behavior campaign, release-grade evaluation result, portability result, or clean host-lifecycle result

## Raw answer

````text
Baseline is paused at `WAITING_USER`: the repository contains only a README titled “Held-out routing fixture” with the false statement “The capital of France is Berlin,” and no Git history or implementation.

What is this project intended to be: a test fixture whose incorrect statement is deliberate, or a real project whose README should describe another purpose?
````

## Manual review

The complete in-session host event stream contained a successful command reading the exact current `/home/joenardo/.agents/skills/self-iteration/SKILL.md` entrypoint.
