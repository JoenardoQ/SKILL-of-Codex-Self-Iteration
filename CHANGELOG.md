# Changelog

All notable changes to this project are documented here. Releases use Semantic
Versioning through Git tags.

## Unreleased

### Changed

- Added an explicit proposal-only rejection policy: when the user authorizes it
  before review, each round completes its full proposal set and read-only gates
  without a redundant selection stop or implementation.
- Added fail-closed validation for the exact ten-file final-runtime candidate
  routing campaign, including canonical inventory, visible metadata, current
  runtime binding, routing verdicts, fenced raw answers, and manual review.
- Removed the unused `classify_durable_state` helper and its self-referential
  unit test; durable-state behavior remains specified by the runtime protocol.
- Added minimal Python generated-debris ignores and made `.gitignore` part of
  the required documented repository structure.
- Reconciled the final-round recovery record around durable Git history. The
  former `/tmp` backup is referenced only as historical session-local evidence.

### Current evidence and limits

- The repository retains twenty manually reviewed no-Skill high-risk behavior
  controls and ten manually reviewed final-runtime Codex routing observations.
- Candidate routing records must bind to the current checked runtime revision;
  old records cannot remain marked active after runtime bytes change. The ten
  held-out observations were refreshed against the final runtime and passed the
  5/5 positive and 5/5 near-miss boundary.
- A temporary proposal-only regression campaign passed one no-Skill control and
  five final-Skill repetitions; it is bounded evidence for this lifecycle branch,
  not a full behavior or release-grade campaign.
- No full Skill-loaded behavior result, independent clean-host lifecycle,
  publication result, or cross-host portability result is claimed.

### Historical cleanup

- The prior cleanup removed completed plans, superseded routing-tuning samples,
  and uninstantiated host raw-evidence architecture while preserving the
  six-file runtime, active validators, high-risk controls, and held-out routing
  boundary. Git history retains the detailed intermediate planning record.
