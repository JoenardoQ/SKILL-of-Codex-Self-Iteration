# Selected Proposals Round Report

## Lifecycle

- Phase: ROUND_CLOSE
- Status: CLOSED
- Baseline revision: `eab13e3e1020ac0dab497b0d08fb25c0b94c7988`
- Scope: implement selected proposals 1–6 while preserving the externally added
  `AAA Self Iteration` display label and stable `$self-iteration` invocation
- Authority: the user selected proposals `1-6`

## Necessity ledger

| Subject | Evidence | Decision |
| --- | --- | --- |
| Proposal-only lifecycle branch | The existing approval stop conflicted with the user's explicit pre-review auto-rejection policy; a no-Skill probe completed the requested flow | Add a narrow regression-prevention rule and evaluation variant |
| Candidate evidence validation | Removing one of ten active records still allowed aggregate validation to pass | Require an exact campaign and current runtime binding |
| `classify_durable_state` | No production caller; only its own import and test | Remove helper and self-test |
| Unreleased changelog | Mixed current claims with deleted architecture and superseded pending states | Replace with the net current contract and historical summary |
| Python debris ignore | Documented test commands can create bytecode artifacts | Add minimal root rules |
| `/tmp` recovery claim | Session-local paths are not durable repository recovery | Use Git history as the durable recovery source |

## Durable recovery

The durable pre-cleanup tree is Git commit `cb511bc`; cleanup is recorded by
commit `45c66f9`, and the later UI-label change by `eab13e3`. Git objects and the
remote branch provide repository recovery subject to normal Git retention.

The former `/tmp/codex-self-iteration-prune-backup-20260831/` path was useful
only as session-local operation evidence. It is historical, may disappear at
any time, and is not a supported recovery mechanism.

## Verification

- Passed all 64 focused tests: repository validator 31, runtime revision 22,
  and control evidence 11.
- Passed aggregate repository validation, exact runtime-manifest binding,
  external Skill validation, and external eval-spec validation.
- Refreshed ten held-out Codex routing observations against runtime revision
  `sha256:86076be9e335b5ba8316bf082f2306aef33fe1315cc55ecf5a7fd8e6623cf9dd`:
  positives selected/loaded 5/5; near misses selected/loaded 0/5.
- Ran one no-Skill proposal-only control and five final-Skill candidate
  repetitions. All six completed three sequential read-only rounds without a
  selection stop; candidate repetitions loaded the Skill 5/5, recorded every
  proposal as rejected, changed no files, and completed final gates.
- Built and verified a deterministic six-file archive in `/tmp`; archive
  integrity passed. The archive remains a temporary verification artifact, not
  a published release.
- The installed WSL Skill is a source link to the canonical runtime, so its bytes
  match by construction. No second Windows installed copy exists.
- Skill validation has zero errors and one reviewed advisory: the mandatory
  linear round protocol exceeds 200 lines without a contents section.

The selected-proposals round is `ROUND_CLOSE / CLOSED`.

## Limits

The retained candidate evidence covers Codex routing only. There is no complete
Skill-loaded behavior result, independent clean-host lifecycle, Claude Code or
Gemini CLI lifecycle, publication, or portability evidence.
