# Final candidate held-out routing observation

- Case ID: contract-reconciliation-heldout-near-miss
- Variant: final-candidate
- Repetition: 4
- Candidate revision: sha256:531e531dda519c66add72150514fe36d2000eaa82c270e0de05d87abdb725978
- Model: gpt-5.6-sol
- Host: WSL Ubuntu-D
- Host build: Codex Desktop 26.818.8289.0 / codex-cli 0.149.0-alpha.4.3
- Runner: native WSL codex exec --ephemeral --json --sandbox read-only
- Tools: exec_command (read-only)
- Sampling: unavailable: Codex runner exposes no sampling controls
- Budget: platform-managed; observed input=57544, cached=47104, output=442, reasoning=71
- Selected: false
- Entrypoint loaded: false
- Reviewer: Codex primary-agent manual event review
- Verdict: pass
- Evidence status: active
- Limitations: held-out routing only; not a full candidate behavior campaign, release-grade evaluation result, portability result, or full host-lifecycle result

## Raw answer

````text
I’ll inspect the project for a clear, bounded factual error and correct just that one item. I’m not using the self-iteration skill because this is explicitly a small, non-iterative correction.

I found one unambiguous factual error in the README: it identifies Berlin as France’s capital. I’ll change only that statement and leave the rest untouched.

I found the correction, but the workspace is read-only, so I couldn’t apply it.

In [README.md](/tmp/self-iteration-heldout-final/README.md:5), change:

```text
The capital of France is Berlin.
```

to:

```text
The capital of France is Paris.
```
````

## Manual review

The answer explicitly treated the request as a bounded non-iterative edit; no successful command read the self-iteration/SKILL.md entrypoint.
