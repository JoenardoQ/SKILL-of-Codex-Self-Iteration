# Routing tuning observation

- Case ID: contract-reconciliation-tuning-near-miss
- Variant: current
- Repetition: 3
- Model: gpt-5.6-sol
- Host: WSL Ubuntu-D
- Host build: Codex Desktop 26.818.8289.0 / codex-cli 0.149.0-alpha.4.3
- Runner: native WSL codex exec --ephemeral --json --sandbox read-only
- Tools: exec_command (read-only)
- Sampling: unavailable: Codex runner exposes no sampling controls
- Budget: platform-managed; observed input=57763, cached=47104, output=484, reasoning=96
- Selected: false
- Entrypoint loaded: false
- Reviewer: Codex primary-agent manual event review
- Verdict: pass
- Evidence status: active
- Limitations: tuning-only project-level fixture; not held-out, release-grade, portability, or full host-lifecycle evidence

## Raw answer

````text
I’ll inspect the project for a clearly identifiable factual error, make only that narrow correction, and run a proportionate check. I’m not invoking the self-iteration workflow because this is explicitly a small, bounded edit rather than iterative delivery.

The bounded error is unambiguous: the README says France’s capital is Berlin. I’ll change only that city name and then verify the file.

I found the correction in `README.md`:

```diff
-The capital of France is Berlin.
+The capital of France is Paris.
```

I couldn’t apply it because the workspace is mounted read-only and write approval is disabled. No files were changed.
````

## Manual review

The answer explicitly kept the bounded correction outside self-iteration, and no command read a self-iteration/SKILL.md entrypoint.
