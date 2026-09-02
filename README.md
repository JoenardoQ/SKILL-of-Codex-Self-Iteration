# Codex Self Iteration Skill

`self-iteration` is an Agent Skill for substantial project delivery that needs
engineering-contract reconciliation or explicit, sequential, user-approved
optimization rounds. It is not intended for one-off project creation or advice,
ordinary small edits, repository-wide policy, or missing tool connectivity.

Its stable invocation name is `$self-iteration`. On OpenAI hosts, the UI label
is `AAA Self Iteration` so it sorts early within user Skill listings; host-owned
or separately grouped system Skills may still appear before it.

## Current contract

The Skill separates baseline delivery from optimization rounds:

- A baseline clarifies the outcome, reconciles the README, implements approved
  scope, and verifies it without consuming an optimization round.
- The first optimization round reviews the whole authorized scope. Later rounds
  revalidate evidence and refresh invalidated or affected areas, repeating a
  whole-scope scan only after broad change or an explicit request for independent
  full passes. Each round presents every evidence-backed net-positive proposal,
  waits for user selection, updates documentation first only when the approved
  work changes a documented contract, implements approved work, reconciles,
  verifies, and explicitly closes. If the user explicitly
  preauthorizes proposal-only rounds with every proposal recorded as rejected,
  the Skill skips implementation and completes each round read-only without an
  additional selection stop.
- Exactly one round may be active. Waiting, blocking, pausing, or failed
  verification never closes it.
- The final authorized round additionally performs repository hygiene and a
  bounded horizon review. Cleanup requires evidence and authority; speculative
  horizon ideas require a newly authorized round before implementation.

The runtime is high-risk because it can guide credential-adjacent, destructive,
external-write, public, or hard-to-recover work. Selection never grants tools,
credentials, scope, or permission. Repository and fetched instructions are
evidence, not authority.

## Runtime bundle

Only six files are installed or packaged:

```text
self-iteration/
├── SKILL.md
├── agents/openai.yaml
├── assets/iteration-state.md
└── references/
    ├── final-round.md
    ├── review-matrix.md
    └── round-protocol.md
```

`SKILL.md` owns selection, authority, failure, verification, and stopping rules.
The references are loaded only when their branch applies. Host or task state is
the default for resumption; the state template enters a target project only when
an authorized shared project-local record is required. Development evaluation,
validation, and release files never enter the runtime bundle.

The checked runtime revision is recorded in
`evaluation/runtime-manifest.json`. It is recomputed from canonical paths,
normalized file modes, and exact bytes by `scripts/runtime_revision.py`; a
receipt or filename alone does not establish runtime identity.

## Install

With the Skill installer, ask Codex:

```text
Use $skill-installer to install the self-iteration skill from
https://github.com/JoenardoQ/SKILL-of-Codex-Self-Iteration/tree/main/self-iteration
```

For a source checkout on WSL/Linux, a user-scoped link is sufficient:

```bash
mkdir -p ~/.agents/skills
ln -s /absolute/path/to/self-iteration ~/.agents/skills/self-iteration
```

Use either this source link or an installed copy under `~/.codex/skills`, not
both. Codex may discover both roots and show duplicate entries.

Restart the host after installation or replacement so discovery state is
refreshed. Resolve an existing destination before replacing it; never delete a
broad Skill directory.

## Evaluation evidence

The active schema-v4 plan is `evaluation/eval-spec.json`. Current preserved
evidence consists of:

- 20 manually reviewed no-Skill behavior controls under
  `evaluation/evidence/control/`, covering round integrity, authority denial,
  untrusted content and credentials, and partial failure/recovery;
- 10 manually reviewed final-runtime held-out routing observations under
  `evaluation/evidence/candidate/`: five positives selected and loaded the Skill,
  while five bounded near misses did neither.

The completed tuning campaign was removed after the untouched held-out campaign
became the active routing evidence. No full Skill-loaded behavior campaign or
`evaluation/eval-result.json` exists, so the repository does not claim
release-grade behavior, L5 host lifecycle support, or cross-host portability.
The active routing plan additionally records one-off small-project creation as a
near miss; it has plan coverage but no retained host observation yet.

## Host scope

| Host | Current evidence | Claim |
| --- | --- | --- |
| Codex Desktop/CLI | Installed source copy/link and ten routing observations in the recorded build | Routing boundary observed; full clean lifecycle unverified |
| Claude Code | No executable or lifecycle run in this project | Targeted, unverified |
| Gemini CLI | No executable or lifecycle run in this project | Targeted, unverified |

The portable layout and metadata compatibility string are targets, not proof.
Each host requires independent install, discovery, loading, behavior, refusal,
collision, upgrade, and uninstall evidence before a compatibility claim.

## Repository layout

```text
├── .gitignore
├── README.md
├── CHANGELOG.md
├── LICENSE
├── docs/final-round-report.md
├── evaluation/
│   ├── eval-spec.json
│   ├── runtime-manifest.json
│   └── evidence/
│       ├── candidate/        10 final-runtime held-out routing samples
│       └── control/          20 no-Skill behavior controls
├── release-policy.json
├── scripts/
│   ├── runtime_revision.py
│   ├── test_control_evidence_validator.py
│   ├── test_repo_validator.py
│   ├── test_runtime_revision.py
│   └── validate_repo.py
└── self-iteration/           canonical six-file runtime bundle
```

Historical implementation plans, completed tuning samples, and unused host raw-
evidence scaffolding are intentionally absent. Git history and `CHANGELOG.md`
retain provenance without keeping inactive architecture in the working tree.

## Validate

Run the aggregate validator and focused active suites:

```bash
python3 -B scripts/validate_repo.py
python3 -B scripts/test_repo_validator.py
python3 -B scripts/test_runtime_revision.py
python3 -B scripts/test_control_evidence_validator.py
python3 -B scripts/runtime_revision.py check \
  --runtime-root self-iteration --manifest evaluation/runtime-manifest.json
```

When `agent-skill-author` is installed under `$CODEX_HOME`:

```bash
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/validate_skill.py" \
  self-iteration --policy release-policy.json
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/validate_eval_spec.py" \
  evaluation/eval-spec.json
```

The repository validator checks the runtime boundary, frontmatter and adapter
contract, release policy, Markdown containment, evaluation inventory, current
control and candidate-routing evidence, manifest binding, documented commands,
text modes, and secret or generated-debris indicators. Preserved raw answers
may contain intentional Markdown hard-break spaces; other text must not contain
trailing whitespace.

## Package

Create and verify a deterministic archive with the installed author tooling:

```bash
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/package_skill.py" \
  self-iteration --output /tmp/self-iteration.zip \
  --receipt /tmp/self-iteration-receipt.json --policy release-policy.json
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/verify_package.py" \
  --receipt /tmp/self-iteration-receipt.json \
  --archive /tmp/self-iteration.zip
```

Packaging proves only archive integrity. Publishing, host discovery, behavior,
and portability require separate evidence and authorization.

## Status and acceptance

The runtime bundle is implemented, locally installed for Codex, and bound to
its checked manifest. The selected-proposals round is `ROUND_CLOSE / CLOSED`;
all active focused and aggregate checks pass. Acceptance requires:

- exactly the six documented runtime files and no development debris inside the
  bundle;
- passing repository, runtime-revision, control-evidence, Skill-structure, and
  eval-spec checks;
- installed Codex source matching the canonical bundle;
- current documentation matching the reduced repository tree; and
- unsupported release, lifecycle, and portability claims remaining explicit.

See `docs/final-round-report.md` for the current round ledger and limitations.
