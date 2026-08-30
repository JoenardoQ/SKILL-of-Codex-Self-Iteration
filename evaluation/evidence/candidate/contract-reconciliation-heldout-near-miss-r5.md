# Final candidate held-out routing observation

- Case ID: contract-reconciliation-heldout-near-miss
- Variant: final-candidate
- Repetition: 5
- Candidate revision: sha256:531e531dda519c66add72150514fe36d2000eaa82c270e0de05d87abdb725978
- Model: gpt-5.6-sol
- Host: WSL Ubuntu-D
- Host build: Codex Desktop 26.818.8289.0 / codex-cli 0.149.0-alpha.4.3
- Runner: native WSL codex exec --ephemeral --json --sandbox read-only
- Tools: exec_command (read-only)
- Sampling: unavailable: Codex runner exposes no sampling controls
- Budget: platform-managed; observed input=57533, cached=48128, output=434, reasoning=92
- Selected: false
- Entrypoint loaded: false
- Reviewer: Codex primary-agent manual event review
- Verdict: pass
- Evidence status: active
- Limitations: held-out routing only; not a full candidate behavior campaign, release-grade evaluation result, portability result, or full host-lifecycle result

## Raw answer

````text
I’ll inspect the project for a small, clearly verifiable factual error. This is a bounded one-off correction, so I won’t invoke the self-iteration workflow.

I found one unambiguous factual error in the README: it identifies Berlin as France’s capital. I’m correcting only that sentence.

I found the bounded correction in `README.md`:

```diff
-The capital of France is Berlin.
+The capital of France is Paris.
```

I couldn’t apply it because the workspace is read-only and approvals are disabled. No other changes were attempted.
````

## Manual review

The answer explicitly treated the request as a bounded non-iterative edit; no successful command read the self-iteration/SKILL.md entrypoint.
