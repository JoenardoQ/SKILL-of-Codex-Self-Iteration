# Changelog

All notable changes to this project are documented here. Releases use Semantic
Versioning through Git tags.

## Unreleased

### Changed

- Narrowed automatic selection to substantial delivery that needs contract
  reconciliation or explicit iterative rounds; one-off project creation is now
  a near miss.
- Changed later rounds from mandatory whole-repository rescans to evidence
  invalidation and affected-area review while retaining complete first-round
  coverage and explicit full-pass requests.
- Made host or task storage the default for iteration state; project-local state
  now requires an explicit shared-state consumer, location, and persistence
  authorization.
- Added a documentation-impact branch and a decision-focused return contract so
  internal refactors do not churn docs or expose routine process ledgers.
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
- The one-off small-project near miss also abstained in 5/5 session-only host
  observations; those event streams are not retained as release-grade evidence.
- Five no-Skill controls and five current-Skill observations exercised the new
  unchanged-state round behavior. Both variants avoided full rescans,
  unauthorized project state, unnecessary documentation updates, and process-
  heavy output; the event streams were reviewed in-session but are not retained
  as release-grade evidence.
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
