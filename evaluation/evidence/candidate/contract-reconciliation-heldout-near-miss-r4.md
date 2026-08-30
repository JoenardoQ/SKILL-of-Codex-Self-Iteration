# Final candidate held-out routing observation

- Case ID: contract-reconciliation-heldout-near-miss
- Variant: final-candidate
- Repetition: 4
- Candidate revision: sha256:86076be9e335b5ba8316bf082f2306aef33fe1315cc55ecf5a7fd8e6623cf9dd
- Model: gpt-5.6-sol
- Host: WSL Ubuntu-D
- Host build: Codex Desktop 26.818.8289.0 / codex-cli 0.149.0-alpha.4.3
- Runner: native WSL codex exec --ephemeral --json --sandbox read-only
- Tools: exec_command (read-only)
- Sampling: unavailable: Codex runner exposes no sampling controls
- Budget: platform-managed; observed input=75934, cached=67328, output=589, reasoning=132
- Selected: false
- Entrypoint loaded: false
- Reviewer: Codex primary-agent manual event review
- Verdict: pass
- Evidence status: active
- Limitations: held-out routing only; not a full candidate behavior campaign, release-grade evaluation result, portability result, or full host-lifecycle result

## Raw answer

````text
I’ll inspect the project for a clear, verifiable factual error and make only that narrow correction. I’m intentionally not invoking the self-iteration workflow because you explicitly excluded substantial iterative delivery.

I found one unambiguous factual error in the README: it identifies Berlin as France’s capital. I’ll change only that word and leave the rest untouched.

I found the correction, but the workspace is read-only, so I couldn’t apply it.

Required change in [README.md](/tmp/self-iteration-heldout-current/README.md:5):

```diff
-The capital of France is Berlin.
+The capital of France is Paris.
```
````

## Manual review

The answer explicitly treated the request as a bounded non-iterative edit; no successful command read a self-iteration/SKILL.md entrypoint.
