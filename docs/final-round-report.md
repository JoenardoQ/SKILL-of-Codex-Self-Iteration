# Final Cleanup Round Report

## Lifecycle

- Phase: ROUND_CLOSE
- Status: CLOSED
- Scope: remove historical tests, inactive architecture, superseded evidence,
  and development debris without weakening the six-file runtime contract
- Deletion authority: explicitly granted by the user

## Necessity ledger

| Subject | Evidence | Decision |
| --- | --- | --- |
| Six-file runtime bundle | Host discovery path, package boundary, manifest | Keep |
| Runtime revision helper and tests | Manifest, archive, receipt, installed-tree binding | Keep |
| Repository validator and focused core tests | Current security, containment, schema, and command contracts | Keep |
| Twenty no-Skill behavior controls and validator | Direct evidence for current high-risk instructions | Keep |
| Final held-out routing evidence | Current positive/near-miss boundary | Keep |
| Historical Superpowers plans/specification | Completed implementation history; no runtime or validator consumer | Delete; Git history retains provenance |
| Completed routing-tuning evidence and race-hardened validator suite | Superseded by untouched final-runtime held-out observations | Delete |
| Host raw-evidence schema, descriptor reader, and synthetic lifecycle suite | No real host artifact or current workflow consumer | Delete |
| Concise host limitation matrix | Prevents unsupported compatibility claims | Keep in README |

## Authorized cleanup

The removed files are backed up for this session under
`/tmp/codex-self-iteration-prune-backup-20260831/`. The runtime bundle is not
changed. The repository contract is rewritten before deletion so no removed
path remains a documented current dependency.

## Verification

- Reduced the tracked working tree from 64 to 48 files and from about 593 KB to
  287 KB: 6,508 deleted lines and 186 added reconciliation lines.
- Passed all 62 active focused tests: repository safety 28, runtime revision 23,
  and control evidence 11.
- Passed aggregate repository validation, runtime-manifest binding, external
  eval-spec validation, Python 3.9 grammar inspection, product mode/debris
  checks, and final stale-reference searches.
- Skill validation remains valid with zero errors and one reviewed advisory:
  `references/round-protocol.md` is a mandatory linear read over 200 lines
  without a contents section.
- The canonical runtime bytes did not change; the installed Codex copy, WSL
  link, deterministic package, receipt, policy digest, and runtime revision
  remain exact and verified.

The cleanup round is `ROUND_CLOSE / CLOSED`.

## Limits

The retained candidate evidence covers Codex routing only. There is no complete
Skill-loaded behavior result, independent clean-host lifecycle, Claude Code or
Gemini CLI lifecycle, publication, or portability evidence.
