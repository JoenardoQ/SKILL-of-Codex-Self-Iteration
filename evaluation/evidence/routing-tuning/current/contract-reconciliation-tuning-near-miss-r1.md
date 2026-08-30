# Routing tuning observation

- Case ID: contract-reconciliation-tuning-near-miss
- Variant: current
- Repetition: 1
- Model: gpt-5.6-sol
- Host: WSL Ubuntu-D
- Host build: Codex Desktop 26.818.8289.0 / codex-cli 0.149.0-alpha.4.3
- Runner: native WSL codex exec --ephemeral --json --sandbox read-only
- Tools: exec_command (read-only)
- Sampling: unavailable: Codex runner exposes no sampling controls
- Budget: platform-managed; observed input=57726, cached=47104, output=466, reasoning=81
- Selected: false
- Entrypoint loaded: false
- Reviewer: Codex primary-agent manual event review
- Verdict: pass
- Evidence status: active
- Limitations: tuning-only project-level fixture; not held-out, release-grade, portability, or full host-lifecycle evidence

## Raw answer

````text
I’ll inspect the project for a small, verifiable factual error, correct only that item, and run a focused check. This is intentionally below the threshold for the self-iteration workflow, so I won’t invoke it.

I found one clear, isolated error in the README: it identifies Berlin as France’s capital. I’m correcting that single sentence and leaving the project’s scope and structure untouched.

I found the bounded correction:

```diff
-The capital of France is Berlin.
+The capital of France is Paris.
```

I couldn’t apply it because the workspace is mounted read-only and approvals are disabled. No files were changed.
````

## Manual review

The answer explicitly kept the bounded correction outside self-iteration, and no command read a self-iteration/SKILL.md entrypoint.
