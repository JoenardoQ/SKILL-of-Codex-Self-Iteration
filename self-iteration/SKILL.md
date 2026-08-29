---
name: self-iteration
description: Run documentation-first software delivery and user-approved optimization loops. Use when creating a project, making a substantial feature or architectural change, reconciling documentation with code, or iteratively improving an existing codebase.
---

# Self Iteration

Treat the project's documentation as an explicit engineering contract, keep it aligned with the implementation, and let the user control every optional optimization round.

## Establish the iteration contract

At the start, determine:

- whether the project is new or existing;
- the requested outcome, scope, constraints, and acceptance criteria;
- the maximum number of optimization rounds, if the user supplied one;
- whether breaking changes are permitted.

Do not invent a round limit. If the user has not chosen one, complete the current delivery and reconciliation, then ask whether to begin an optimization round.

## Preserve round completeness

Treat every optimization round as a complete review of the current project state, not as one installment of a review spread across several rounds.

- Do not return merely because one or several upgrade opportunities have been found.
- Continue until every materially applicable review dimension and relevant repository area has been examined.
- Report all upgrade opportunities reasonably discoverable from the available evidence in the current round. Do not knowingly reserve findings for later rounds.
- Use later rounds to reflect again on the updated system, revisit the same dimensions, examine interactions created by prior changes, and discover deeper or newly emergent opportunities.
- Never use the authorized round count as permission to divide one comprehensive review into partial batches.

Maintain a coverage ledger while reviewing. For each dimension, record the evidence inspected and either the findings, a reason no upgrade is justified, or why the dimension is not applicable or could not be assessed. A round is not complete while a relevant dimension or major repository area remains unchecked. If access, evidence, or time constraints prevent full coverage, disclose that limitation instead of presenting a partial scan as comprehensive.

## Enforce a hard round barrier

Allow exactly one active iteration round at a time. A round begins when reading and analysis of that round's project state begins. It includes the complete current-state inventory, comprehensive review, proposal set, user selection, documentation-first implementation, reconciliation, verification, and round-closing report.

Do not begin any reading, evidence gathering, pre-analysis, brainstorming, planning, coverage mapping, or tool work for round N+1 while round N remains open. Do not overlap rounds, prefetch the next review, or use unfinished work from the current round as the start of the next one. Authorization for multiple rounds permits sequential repetition; it does not permit parallel or speculative work on later rounds.

Close the current round only after:

- its coverage ledger is complete or every concrete limitation is disclosed;
- the user-selected scope is implemented or explicitly withdrawn;
- README and linked design updates are complete;
- implementation and documentation have been reconciled in both directions;
- relevant verification is complete and regressions are resolved or disclosed;
- remaining risks, deferred proposals, and blockers are reported;
- any required final-round hygiene and horizon-expansion gates have completed.

State explicitly that the round is complete. Only after that boundary, and only when the user has authorized another round, begin a fresh read of the newly established project state. Rebuild the coverage ledger and reassess earlier findings from evidence; do not treat the previous round's conclusions or deferred proposals as automatically valid.

## Baseline the project

For a new project, clarify material ambiguities and write `README.md` before substantial implementation.

For an existing project, inspect the repository instructions, current documentation, source, tests, configuration, schemas, and build commands. Treat the code as evidence of current behavior, not proof of intended behavior. Reconcile factual documentation drift before using the README as the forward-looking contract. Ask the user when current behavior and apparent intent conflict in a way that changes product or architecture decisions.

The README must provide a concise source of truth for the information relevant to the project:

- purpose, users, use cases, scope, and non-goals;
- functional and non-functional requirements;
- assumptions and constraints;
- architecture, module boundaries, data flow, and important interfaces;
- important algorithms or design decisions;
- setup, run, build, test, and verification commands;
- acceptance criteria, implementation status, and known limitations.

Use linked files under `docs/` when detail would make the README unwieldy. Clearly distinguish current, approved, proposed, and deferred behavior.

## Implement from the documented contract

Derive the implementation plan and code structure from the approved requirements and architecture. Implement the smallest coherent increment, preserve unrelated user changes, and align tests with the acceptance criteria.

If implementation reveals a false assumption, update the documentation deliberately and disclose the deviation. Do not silently redefine requirements to fit the code.

## Reconcile after construction

After implementation, inspect the resulting code and tests rather than relying on the earlier plan. Compare the documentation with observable implementation details and identify:

- documented but unimplemented behavior;
- implemented but undocumented behavior;
- obsolete architecture or module descriptions;
- incorrect setup, run, build, or test commands;
- missing constraints, failure behavior, or verification;
- acceptance criteria that are untested or unmet.

Correct factual drift, run the relevant available checks, and report:

- documentation changes;
- implementation changes;
- verification performed and its results;
- remaining discrepancies, assumptions, and risks.

Do not claim that documentation and code are consistent without inspecting both. Do not claim completion without proportionate verification.

## Conduct a comprehensive optimization review

Only after reconciliation, perform the full review before producing proposals. Cover every materially applicable dimension, including product concept and scope, domain model, architecture, module boundaries, data flow and state ownership, algorithms and complexity, data structures and storage, interfaces and contracts, correctness and invariants, concurrency, security and privacy, performance and scalability, reliability and recovery, observability, maintainability, testing, developer experience, user experience and accessibility, deployment, compatibility and migration, and operating cost.

Within the same round:

1. Inventory the relevant documentation, source areas, tests, configuration, schemas, dependencies, and operational artifacts so coverage is not driven only by the first files or issues encountered.
2. Complete a breadth pass across the full coverage ledger, accumulating findings without returning early.
3. Complete a cross-cutting pass for contradictions, shared root causes, interactions, second-order effects, and opportunities hidden by local fixes.
4. Challenge the apparent completeness of the findings: revisit dimensions with weak evidence, consolidate duplicates, and identify dependencies between proposals.
5. Only then rank and present the complete current-round proposal set together with a compact coverage summary.

For each proposal state:

- the observed problem or opportunity and repository evidence;
- the proposed change and expected benefit;
- effort, risk, dependencies, and compatibility impact;
- how the result would be verified.

Number and prioritize the proposals. Separate correctness or security defects from optional improvements.

## Enforce the user approval gate

Stop after presenting proposals. Do not implement an optional optimization until the user selects it. The user controls which proposals proceed and how many rounds run.

For each approved round:

1. Update the README and linked design documents first, including changed requirements, architecture, migration impact, and acceptance criteria.
2. Implement the approved code and test changes.
3. Reconcile documentation and implementation again.
4. Run proportionate verification and report the outcome.
5. Complete the current round's coverage, documentation, verification, risk, and blocker records without beginning the next review.
6. If this is the final round, complete the final-round hygiene and horizon-expansion gates before closing it.
7. Declare the current round complete.
8. Stop. If the user has authorized another round, begin its fresh inventory and comprehensive review only after the current round is closed; do not inspect only the area changed in the previous round.

Never interpret self-iteration as permission for unlimited autonomous changes, breaking changes, new external dependencies, deployments, publishing, or other actions outside the user's authorization.

## Complete the final-round hygiene gate

Before declaring the last authorized round complete, perform an additional repository-wide code and architecture hygiene pass. This gate also applies when the user decides that the current round will be the last one.

1. Re-inventory application and library entry points, modules, packages, types, classes, functions, methods, branches, imports, exports, dependencies, configuration, build targets, schemas, generated-code boundaries, tests, scripts, and documented architectural components.
2. Identify code and structure that is unreachable, unreferenced, duplicated, obsolete, superseded, or no longer connected to an approved requirement or runtime path. Continue across the whole repository; do not stop after finding the first cleanup candidates.
3. Establish evidence before deletion using the strongest applicable combination of reference search, call or dependency graphs, compiler and linter diagnostics, coverage, tests, build configuration, framework registration, runtime entry points, and repository conventions.
4. Delete every candidate that is sufficiently proven to be dead or obsolete, including associated tests, configuration, documentation, imports, dependencies, and architectural scaffolding that serve no remaining behavior. If a deletion changes documented architecture or behavior, update the README or linked design document before applying it.
5. Do not equate "not changed during the iterations" with "unused." Preserve or request a decision for ambiguous public APIs, reflection or dynamic-import targets, plugin hooks, framework-discovered code, serialization contracts, migrations, deployment paths, compatibility shims, generated or vendored files, and consumers outside the repository. Report these separately instead of guessing.
6. Run the repository's established formatter and style checks across the affected scope, then inspect remaining formatting and style inconsistencies. Follow existing conventions; do not introduce a new formatter or perform unrelated mass restyling without authorization.
7. Reconcile the README and linked design documents against the final code and architecture. Verify requirements, module maps, interfaces, algorithms, commands, status, limitations, and acceptance criteria in both directions: every material documentation claim must be supported by the implementation, and every material implemented behavior must be documented.
8. Run the strongest proportionate verification available after cleanup, including relevant tests, linting, formatting checks, type checks, builds, and dead-code or dependency analysis. Investigate regressions rather than weakening checks to make them pass.
9. Produce a final hygiene report listing deleted items and evidence, retained ambiguous candidates and reasons, formatting and style actions, documentation reconciliation, verification results, and any remaining limitations.

The final round is incomplete until this gate has either passed or its concrete blockers and unverified areas have been disclosed to the user.

## Escape the local maximum

After the final-round hygiene gate and its verification, perform a deliberate horizon-expansion review. Use the now-stable, documented project as a baseline, but do not limit the exploration to incremental improvements of the existing design.

Run a divergent pass before ranking ideas:

- restate the underlying user outcome independently of the current feature set and implementation;
- challenge or invert major product, domain, architecture, data, interface, operational, and business assumptions;
- consider eliminating a subsystem or workflow instead of optimizing it;
- explore alternative architectures, interaction models, algorithms, ownership boundaries, and delivery models;
- use relevant cross-domain analogies and ask what a fundamentally different field would do;
- examine 10x changes in scale, latency, cost, reliability, simplicity, reach, or user value;
- consider capabilities that become possible only after the completed iterations and cleanup;
- identify constraints that are essential, constraints that are historical accidents, and constraints that could be relaxed through a safe experiment.

Do not stop at the first creative idea. Search broadly enough to produce a diverse portfolio spanning adjacent breakthroughs, architectural or product reframes, and high-upside moonshots. Do not pad the portfolio with novelty for its own sake; prefer ideas that could materially change the attainable outcome.

For each horizon proposal, state:

- the leap and the local optimum it escapes;
- the assumption or constraint being challenged;
- why further incremental optimization is unlikely to reach the same outcome;
- expected upside and who benefits;
- major technical, product, security, operational, and adoption risks;
- cost, dependencies, reversibility, and migration implications;
- the smallest bounded experiment or prototype that could falsify the idea;
- measurable evidence that would justify adoption, revision, or rejection.

Keep horizon proposals separate from verified current-state findings and the ordinary optimization backlog. Label assumptions and speculation explicitly. Do not rewrite the README as if a horizon proposal were approved, and do not implement one without the user's explicit selection.

Present the portfolio only after the cleanup, formatting, documentation reconciliation, and verification results, so speculative possibilities cannot obscure the trustworthy final state. If no credible leap survives the review, report the explored directions and why they fail rather than inventing a recommendation.

The final round is not complete until this horizon-expansion review has been presented, or concrete blockers to performing it have been disclosed.

## Stop conditions

Stop when the authorized round count is reached, the user declines further work, no worthwhile evidence-backed proposal remains, a material product decision is missing, or required access or authorization is unavailable.
