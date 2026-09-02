# Codex Self Iteration Skill

[简体中文](README.zh-CN.md)

`self-iteration` is an Agent Skill for substantial project delivery that
requires engineering-contract reconciliation or explicit, sequential,
user-approved optimization rounds. It keeps scope, authority, evidence, and
round state explicit without treating an invocation as permission to mutate
external systems.

## When to use it

Use the Skill when a project needs a baseline delivery followed by one or more
deliberate improvement rounds, or when implementation and documentation must be
reconciled against an agreed engineering contract.

Do not use it for one-off advice, ordinary small edits, repository-wide policy,
or missing tool connectivity.

## Install

Ask Codex to download the Skill from GitHub:

```text
Use $skill-installer to install
https://github.com/JoenardoQ/SKILL-of-Codex-Self-Iteration/tree/main/self-iteration
```

Start a new Codex task after installation. Do not link the installed Skill to a
development checkout; reinstall from GitHub when updating it.

## Runtime behavior

The Skill separates baseline delivery from optimization rounds:

1. The baseline defines the outcome, reconciles the documented contract,
   implements approved work, and verifies the result.
2. Each optimization round reviews the authorized scope, presents
   evidence-backed proposals, waits for user decisions, implements only selected
   work, reconciles documentation, and closes explicitly.
3. Exactly one round may be active. Waiting, failure, or blocked verification
   does not close it.
4. The final authorized round also performs bounded repository hygiene and a
   horizon review. Future work still needs separate authorization.

Selection never grants tools, credentials, publication rights, or permission
for destructive or external actions.

## State and privacy

Host or task state is the default resumption mechanism. The runtime template
`self-iteration/assets/iteration-state.md` may be copied into a target project
only when a durable project-local handoff is authorized. That generated state
belongs to the target project and may contain project history, so maintainers
must decide its retention and publication policy there.

This source repository does not publish its own iteration ledgers, round
reports, runtime manifests, model transcripts, reviewer decisions, or generated
evaluation results. The ignore rules keep those local.

## Repository contents

```text
SKILL-of-Codex-Self-Iteration/
├── .gitignore
├── README.md
├── README.zh-CN.md
├── LICENSE
├── evaluation/
│   └── eval-spec.json
├── release-policy.json
├── scripts/
│   ├── runtime_revision.py
│   ├── test_control_evidence_validator.py
│   ├── test_repo_validator.py
│   ├── test_runtime_revision.py
│   └── validate_repo.py
└── self-iteration/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/iteration-state.md
    └── references/
        ├── final-round.md
        ├── review-matrix.md
        └── round-protocol.md
```

Only `self-iteration/` is installed. The evaluation specification, validation
scripts, tests, and release policy are maintainer resources. The evaluation
specification contains planned synthetic cases and acceptance criteria; it is
not a campaign result.

## Maintainer evaluation

Generated evaluation material must remain outside Git. The supported local-only
locations include `evaluation/evidence/`, `evaluation/results/`,
`evaluation/raw/`, and `evaluation/runtime-manifest.json`.

The repository validator accepts a public checkout without those paths. If a
maintainer creates a complete local manifest or evidence corpus, the same
validator checks it instead of silently ignoring malformed data.

## Validation and packaging

Run the public repository checks:

```bash
python3 -B scripts/validate_repo.py
python3 -B scripts/test_repo_validator.py
python3 -B scripts/test_runtime_revision.py
python3 -B scripts/test_control_evidence_validator.py
```

To create and check a local runtime manifest:

```bash
python3 -B scripts/runtime_revision.py write \
  --runtime-root self-iteration \
  --manifest evaluation/runtime-manifest.json
python3 -B scripts/runtime_revision.py check \
  --runtime-root self-iteration \
  --manifest evaluation/runtime-manifest.json
```

When Agent Skill Author is installed under `$CODEX_HOME`, validate and package
the runtime bundle:

```bash
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/validate_skill.py" \
  self-iteration --policy release-policy.json
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/validate_eval_spec.py" \
  evaluation/eval-spec.json
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/package_skill.py" \
  self-iteration --output /tmp/self-iteration.zip \
  --receipt /tmp/self-iteration-receipt.json --policy release-policy.json
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/verify_package.py" \
  --receipt /tmp/self-iteration-receipt.json \
  --archive /tmp/self-iteration.zip
```

## Limitations

Static validation checks structure, references, policies, fixtures, and
repository boundaries. It does not prove host discovery, correct Skill
selection, behavioral improvement, external side effects, or portability.
Those claims require fresh independently reviewed runs in each target host.

## License

[MIT](LICENSE)
