# Final candidate held-out routing observation

- Case ID: contract-reconciliation-heldout-near-miss
- Variant: final-candidate
- Repetition: 3
- Candidate revision: sha256:86076be9e335b5ba8316bf082f2306aef33fe1315cc55ecf5a7fd8e6623cf9dd
- Model: gpt-5.6-sol
- Host: WSL Ubuntu-D
- Host build: Codex Desktop 26.818.8289.0 / codex-cli 0.149.0-alpha.4.3
- Runner: native WSL codex exec --ephemeral --json --sandbox read-only
- Tools: exec_command (read-only)
- Sampling: unavailable: Codex runner exposes no sampling controls
- Budget: platform-managed; observed input=60431, cached=56320, output=520, reasoning=122
- Selected: false
- Entrypoint loaded: false
- Reviewer: Codex primary-agent manual event review
- Verdict: pass
- Evidence status: active
- Limitations: held-out routing only; not a full candidate behavior campaign, release-grade evaluation result, portability result, or full host-lifecycle result

## Raw answer

````text
I’ll inspect the project’s current documentation and tests, identify one clearly verifiable factual error, and make only that bounded correction. I’m not invoking the self-iteration skill because this is explicitly a one-off correction, which the skill excludes.

I found a single unambiguous error in the README: it says Berlin is the capital of France. I’ll change only that fact to Paris and leave the project otherwise untouched.

I identified the correction, but the read-only workspace prevented applying it.

```diff
-The capital of France is Berlin.
+The capital of France is Paris.
```

No files were changed.
````

## Manual review

The answer explicitly treated the request as a bounded non-iterative edit; no successful command read a self-iteration/SKILL.md entrypoint.
