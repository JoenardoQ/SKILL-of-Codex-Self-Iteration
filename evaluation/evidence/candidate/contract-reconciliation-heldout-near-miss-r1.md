# Final candidate held-out routing observation

- Case ID: contract-reconciliation-heldout-near-miss
- Variant: final-candidate
- Repetition: 1
- Candidate revision: sha256:390c5b82be4d780e3e95efacd901fd555cc36f676c24bc9a94847d43e4d1260f
- Model: gpt-5.6-sol
- Host: WSL Ubuntu-D
- Host build: Codex Desktop 26.818.8289.0 / codex-cli 0.149.0-alpha.4.3
- Runner: native WSL codex exec --ephemeral --json --sandbox read-only
- Tools: exec_command (read-only)
- Sampling: unavailable: Codex runner exposes no sampling controls
- Budget: platform-managed; exact per-run budget not exposed
- Selected: false
- Entrypoint loaded: false
- Reviewer: Codex primary-agent manual event review
- Verdict: pass
- Evidence status: active
- Limitations: held-out routing only; complete event streams were reviewed in-session but are not retained, so this is not a full candidate behavior campaign, release-grade evaluation result, portability result, or clean host-lifecycle result

## Raw answer

````text
I found the correction: [README.md](/tmp/self-iteration-heldout-current/README.md:3) should say “The capital of France is Paris.”

I couldn’t apply it because the workspace is read-only and write approval is disabled. No files were changed.
````

## Manual review

The complete in-session host event stream contained no read of `/home/joenardo/.agents/skills/self-iteration/SKILL.md`; the request remained a bounded correction.
