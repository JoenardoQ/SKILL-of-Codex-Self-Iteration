# Comprehensive Review Matrix

## Build the inventory first

Inventory all relevant repository instructions, documentation, source roots,
entry points, modules, tests, configuration, schemas, dependencies, build and
deployment artifacts, generated boundaries, and operational material. Do not let
the first opened files or first discovered defect define review coverage.

For very large repositories, partition the scope and track every partition. If
access, evidence, or available execution prevents full coverage, identify the
unassessed areas precisely; never label a partial scan comprehensive.

## Necessity review and ledger

For every round, independently cover capability necessity, architecture
necessity, and redundancy/ownership before returning proposals. Inventory every
material subject, or an explicitly bounded homogeneous group, before proposing
changes. Capability necessity maps each subject to an approved outcome,
acceptance criterion, required operation, or demonstrated consumer. Architecture
necessity assesses abstractions, layers, indirections, extension points,
boundaries, shared subsystems, and dependencies against concrete consumers,
isolation or risk boundaries, host contracts, or approved near-term
requirements. Redundancy/ownership covers commands, functions, modules, data
paths, schemas, configuration, adapters, tests, and documentation, identifying
canonical ownership and safe consolidation.

The necessity ledger may be integrated with the coverage ledger. Produce it as a
table with these REQUIRED exact column headers, in this order, for every
material subject or bounded group:

| Subject/kind | Observed consumers and contract evidence | Status | Compatibility/dynamic-discovery risk | Result/rationale | Evidence limits |
| --- | --- | --- | --- | --- | --- |

Create one row per material subject or bounded group. Populate its subject and
boundary, observed consumers and approved-outcome, acceptance,
required-operation, or contract evidence, compatibility or discovery risk,
evidence-backed rationale, and evidence limits in their respective columns.

Set each `Status` cell to exactly one of these lowercase tokens:
`necessary`, `candidate remove`, `candidate merge`, `candidate simplify`, or
`unassessed`.

Before uncertainty supports retention or deletion, perform proportionate search
for callers and imports, exports and public APIs, configuration and schema
references, dynamic loading and registration, host adapters, tests and docs,
release and migration history, and operational evidence. Hypothetical consumers
are uncertainty, not affirmative necessity. Keep unresolved public or dynamic
surfaces `unassessed`, or make them risk-labeled proposals; never delete them
automatically.

Coverage is mandatory; removal, merge, and simplification proposals are
optional. Make one only when material positive net value remains after
compatibility, migration, reversibility, and opportunity costs. Assess
one-implementation abstractions and speculative extensibility; do not presume
they are defects. Keep correctness defects separate. Earlier rounds assess and
propose from current evidence; they do not inherit cleanup semantics.

## Coverage dimensions

Assess every materially applicable dimension:

- user outcome, product concept, scope, non-goals, and acceptance criteria;
- domain model, invariants, terminology, and ownership;
- architecture, module boundaries, coupling, cohesion, and dependency direction;
- data flow, state ownership, data structures, storage, schemas, and lifecycle;
- algorithms, complexity, numerical behavior, and resource bounds;
- interfaces, protocols, contracts, error semantics, and versioning;
- correctness, edge cases, concurrency, idempotency, and failure behavior;
- security, privacy, secrets, trust boundaries, and supply-chain exposure;
- performance, scalability, latency, memory, network, and operating cost;
- reliability, recovery, observability, diagnostics, and operability;
- maintainability, readability, duplication, dependencies, and extensibility;
- tests, fixtures, coverage quality, static analysis, and verification gaps;
- developer experience, setup, commands, feedback loops, and documentation;
- user experience, accessibility, localization, and misuse resistance;
- build, release, deployment, configuration, environment parity, and rollback;
- compatibility, public APIs, migrations, data evolution, and adoption risk.

Mark a dimension `not applicable` only with a reason grounded in the project.

## Complete three passes

1. **Breadth pass:** inspect every inventory area and coverage dimension,
   including the necessity ledger's material subjects, accumulating all findings
   without returning at the first upgrade.
2. **Cross-cutting pass:** look for contradictions, shared root causes,
   interactions, duplicated remedies, and second-order effects across boundaries;
   cross-check overlapping ownership.
3. **Completeness challenge:** revisit weak-evidence and no-finding entries,
   challenge unsupported necessity and no-change claims, consolidate duplicates,
   and map proposal dependencies.

Only after all three passes may proposals be ranked and returned.

## Coverage ledger

For each dimension record:

| Field | Required content |
| --- | --- |
| Dimension | Review area or repository partition |
| Evidence | Files, commands, runtime evidence, or design facts inspected |
| Status | Finding, no change justified, not applicable, or unassessed |
| Result | Findings or the evidence-backed reason for the status |
| Limits | Missing access, weak evidence, dynamic behavior, or other uncertainty |

A major repository area or applicable dimension without an entry keeps the round
open. Record evidence freshness and scope boundaries so a repository change or
scope decision can invalidate only the affected entries rather than silently
carrying stale findings forward. A material subject or bounded group without a
necessity-ledger entry also keeps the round open.

## Proposal set

Comprehensive review does not imply a minimum proposal count. A candidate becomes
a proposal only when available evidence supports a material improvement to the
approved outcome and its expected benefit exceeds its likely risk, cost,
complexity, compatibility impact, and opportunity cost. Difference, novelty, or
the ability to change something is not sufficient.

Report every candidate that meets this threshold; do not hide a valid finding to
avoid appearing forceful. Omit candidates that do not meet it; do not lower the
threshold, exaggerate benefits, or recommend negative optimization to fill a
list. If no candidate qualifies, omit the proposal set and proceed using the
no-proposal path in `round-protocol.md`.

Separate correctness and security defects from optional improvements. For every
qualifying proposal provide:

- stable number and priority;
- observed problem or opportunity with repository evidence;
- proposed change and expected user or engineering benefit;
- effort, risk, dependencies, reversibility, and compatibility impact;
- verification method and measurable acceptance criteria.

Report all qualifying opportunities reasonably discoverable from current
evidence. Do not knowingly defer findings to fill a later round. Later rounds
exist to reassess the changed whole, examine new interactions, and find deeper
or emergent issues, not to guarantee additional output. Return the proposal set
only after every inventory partition and applicable dimension has a ledger entry
and all three passes are complete or their concrete evidence limits are stated.
