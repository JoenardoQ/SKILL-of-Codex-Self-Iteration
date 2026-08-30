# Host Support Record

This document records host evidence separately from the portable runtime bundle.
`targeted` means that the canonical bundle is intended for the named host; it
does not mean that the host has loaded, selected, or executed it. A host becomes
`verified` only after independent L5 evidence covers installation, discovery,
entrypoint loading, behavior, refusal, collision handling, upgrade, and
uninstall in an isolated environment.

Every record has separate **Observed availability**, **Observed version**, and
**Evidence artifact** fields. Availability is exactly `available` or
`unavailable`; an available record has a concrete observed version, while an
unavailable record states `unavailable` or `not observed` with a reason.
`unverified` means only L0 or incomplete evidence exists and cannot support a
compatibility claim; `unavailable` means an exact unavailable observation and a
not-run lifecycle; `failed` means an attempted lifecycle explicitly failed; and
`verified` means an available host has independent evidence.

For `failed`, `unverified`, and `verified`, an artifact (when one is produced)
is exactly the host-scoped JSON file at
`evaluation/evidence/hosts/<host-slug>.json`, outside `self-iteration/`.
Schema version 2 binds the exact host, observed version, non-empty
`independent_reviewer`, `independent: true`, matching overall status, and the
checked `runtime_revision`. It records the eight ordered steps `install`,
`discovery`, `entrypoint`, `behavior`, `refusal`, `collision`, `upgrade`, and
`uninstall`. Every step contains non-empty actual `command`, `result`, and
observable `postcondition` evidence, plus exact `raw_evidence` channels
`command_output` and `postcondition_readback`. Each raw channel contains exactly
`path`, `status`, `sha256`, `bytes`, and `reason`.

Raw paths are canonical repository-relative paths below
`evaluation/evidence/hosts/raw/`; they must resolve to a regular non-symlink
file below that root and bind its exact lowercase SHA-256 and byte count.
`captured` requires those file facts and `reason: null`; `redacted` requires the
same facts plus a non-empty limitation; `unavailable` has null file facts and a
non-empty reason. Redacted or unavailable channels are allowed only for
`failed` or `unverified` artifacts. A verified artifact requires all sixteen
channels to be captured, eight `passed` results, zero exit codes, true
postconditions, and the current checked runtime revision. A failed artifact has
at least one failed result, nonzero exit, or false postcondition. Existing
unverified/unavailable records may honestly have no artifact. Raw evidence must
exclude credentials; validation binds facts but does not claim a scanner proves
transcript safety. No summary prose, Markdown artifact, runtime-bundle artifact,
absolute path, or other evidence path can establish a public
verified/compatible claim.

## Evidence boundary

The 2026-08-30 probe was deliberately limited to executable discovery,
`--version`, and `--help`. It did not use credentials, install software, alter a
global host directory, contact a network service, or start model inference.
Executable availability and command-help text are L0 surface observations, not
L5 lifecycle evidence.

Commands run from this repository:

```bash
command -v codex || true
command -v claude || true
command -v gemini || true
codex --version
codex --help
```

Observed output relevant to support status:

```text
codex: /mnt/c/Users/Joena/.codex/bin/wsl/97e055fd1906481c/codex
codex --version: codex-cli 0.149.0-alpha.4.3
claude: no output (unavailable)
gemini: no output (unavailable)
```

`codex --help` listed generic CLI commands and approval/sandbox options, but no
Skill-discovery or isolated-Skill lifecycle result. The warning about read-only
PATH aliases was emitted by the local executable and does not establish or
invalidate Skill support.

## Codex Desktop/CLI

- **Target host:** Codex Desktop/CLI.
- **Observed availability:** available
- **Observed version:** codex-cli 0.149.0-alpha.4.3
- **Discovery and loading path:** The repository documents
  `~/.agents/skills/self-iteration` as an intended user-level discovery target
  containing `SKILL.md`; `agents/openai.yaml` is the thin Codex UI adapter.
  This target layout is documented, not observed through a clean host load.
- **Canonical action mapping and degraded capabilities:** Intended explicit
  action: `$self-iteration` loads the canonical `SKILL.md`; the adapter may
  provide UI metadata. No evidence establishes listing, automatic routing,
  adapter rendering, collision behavior, or behavior/refusal execution.
- **Install scope and owned files:** Intended user scope:
  `~/.agents/skills/self-iteration`; the owned artifact is a link or copy of
  this repository's `self-iteration/` directory. No real global installation
  was created or changed.
- **Authentication and approval behavior:** `codex --help` exposes login and
  approval/sandbox controls at the CLI surface. Their interaction with Skill
  loading was not tested. The Skill itself supplies no credentials and grants
  no authority.
- **Clean acceptance test:** In a disposable Codex configuration, copy exactly
  the canonical bundle into the documented user-level Skill directory; restart
  the host; confirm discovery and entrypoint load; run one positive and one
  near-miss prompt; confirm refusal of an unapproved protected action; create a
  duplicate name to test collision handling; replace the bundle to test
  upgrade; remove only the disposable Skill directory and confirm absence after
  restart. Record exact commands, host version, and every postcondition.
- **Upgrade and uninstall:** Expected test only: update the isolated source,
  replace the isolated copied bundle or refresh its link, then repeat discovery
  and behavior checks. Uninstall only the isolated `self-iteration` entry and
  verify that the source checkout remains intact. No lifecycle action was run.
- **Evidence status:** unverified.
- **Evidence artifact:** None produced.
- **Lifecycle evidence:** Not run. Global host mutation, credentials, network
  activity, and model inference are outside the current authority; executable
  availability and help text cannot substitute for L5 evidence.
- **Limitations:** The installed CLI binary proves only local command surface
  availability. It does not prove Desktop behavior, user-level discovery,
  entrypoint loading, behavior, refusal, collision handling, upgrade, uninstall,
  or portability.

## Claude Code

- **Target host:** Claude Code.
- **Observed availability:** unavailable
- **Observed version:** unavailable — `claude` was not found on `PATH`; no
  version command was run.
- **Discovery and loading path:** Unknown in this environment. The canonical
  `SKILL.md` is a target artifact, not evidence of Claude Code discovery or
  loading.
- **Canonical action mapping and degraded capabilities:** No host-specific
  invocation mapping is established. The portable instructions may be reviewed
  manually, but that is not a verified Skill selection, UI, routing, or refusal
  capability.
- **Install scope and owned files:** Unknown. Do not infer a Claude Code
  installation directory from the Codex layout; no files were installed or
  changed.
- **Authentication and approval behavior:** Unknown because the executable was
  unavailable and no account, credential, or remote documentation access is in
  scope.
- **Clean acceptance test:** After Claude Code is locally available, use its
  documented disposable configuration mechanism to install only a copied
  `self-iteration/` bundle. Independently record discovery, entrypoint loading,
  a positive prompt, a near-miss non-selection, protected-action refusal,
  duplicate-name collision, replacement upgrade, and isolated uninstall. Keep
  the source checkout and normal user configuration untouched.
- **Upgrade and uninstall:** Unknown until the host's documented isolated
  lifecycle mechanism is tested. Do not claim that copying, replacement, or
  deletion works on this host before that test.
- **Evidence status:** unavailable.
- **Evidence artifact:** None produced.
- **Lifecycle evidence:** Not run because `claude` is unavailable; absence is
  an environment limitation, not a failed compatibility test.
- **Limitations:** No executable, version, help surface, discovery path,
  authentication model, approval model, or lifecycle behavior was observed.

## Gemini CLI

- **Target host:** Gemini CLI.
- **Observed availability:** unavailable
- **Observed version:** unavailable — `gemini` was not found on `PATH`; no
  version command was run.
- **Discovery and loading path:** Unknown in this environment. The canonical
  `SKILL.md` is a target artifact, not evidence of Gemini CLI discovery or
  loading.
- **Canonical action mapping and degraded capabilities:** No host-specific
  invocation mapping is established. The portable instructions may be reviewed
  manually, but that is not a verified Skill selection, UI, routing, or refusal
  capability.
- **Install scope and owned files:** Unknown. Do not infer a Gemini CLI
  installation directory from the Codex layout; no files were installed or
  changed.
- **Authentication and approval behavior:** Unknown because the executable was
  unavailable and no account, credential, or remote documentation access is in
  scope.
- **Clean acceptance test:** After Gemini CLI is locally available, use its
  documented disposable configuration mechanism to install only a copied
  `self-iteration/` bundle. Independently record discovery, entrypoint loading,
  a positive prompt, a near-miss non-selection, protected-action refusal,
  duplicate-name collision, replacement upgrade, and isolated uninstall. Keep
  the source checkout and normal user configuration untouched.
- **Upgrade and uninstall:** Unknown until the host's documented isolated
  lifecycle mechanism is tested. Do not claim that copying, replacement, or
  deletion works on this host before that test.
- **Evidence status:** unavailable.
- **Evidence artifact:** None produced.
- **Lifecycle evidence:** Not run because `gemini` is unavailable; absence is
  an environment limitation, not a failed compatibility test.
- **Limitations:** No executable, version, help surface, discovery path,
  authentication model, approval model, or lifecycle behavior was observed.
