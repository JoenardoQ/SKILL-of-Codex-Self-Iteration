# Routing tuning observation

- Case ID: contract-reconciliation-tuning-near-miss
- Variant: current
- Repetition: 2
- Model: gpt-5.6-sol
- Host: WSL Ubuntu-D
- Host build: Codex Desktop 26.818.8289.0 / codex-cli 0.149.0-alpha.4.3
- Runner: native WSL codex exec --ephemeral --json --sandbox read-only
- Tools: exec_command (read-only)
- Sampling: unavailable: Codex runner exposes no sampling controls
- Budget: platform-managed; observed input=57798, cached=51200, output=487, reasoning=97
- Selected: false
- Entrypoint loaded: false
- Reviewer: Codex primary-agent manual event review
- Verdict: pass
- Evidence status: active
- Limitations: tuning-only project-level fixture; not held-out, release-grade, portability, or full host-lifecycle evidence

## Raw answer

````text
I’ll inspect the project for a clear, bounded factual error, make only that correction, and run a focused verification. This is intentionally too small for the self-iteration workflow.

I found one unambiguous factual error in the README: it identifies Berlin as France’s capital. I’m correcting that single sentence and leaving the rest untouched.

I found the bounded correction, but the workspace is read-only, so I couldn’t apply it.

```diff
-The capital of France is Berlin.
+The capital of France is Paris.
```

No other changes are needed.
````

## Manual review

The answer explicitly kept the bounded correction outside self-iteration, and no command read a self-iteration/SKILL.md entrypoint.
