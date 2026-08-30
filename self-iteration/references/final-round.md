# Final-Round Gates

Read and execute this file only for the last authorized round or when the user
declares the current round final. The round stays open through both gates.

## Repository hygiene gate

1. Re-inventory entry points, modules, packages, types, functions, methods,
   branches, imports, exports, dependencies, configuration, build targets,
   schemas, generated boundaries, tests, scripts, and documented components.
2. Across the whole repository, find unreachable, unreferenced, duplicated,
   obsolete, superseded, or requirement-orphaned material. Do not stop after the
   first cleanup candidate.
3. Establish deletion evidence using the strongest applicable combination of
   reference search, call or dependency graphs, compiler/linter diagnostics,
   coverage, tests, build configuration, framework registration, runtime entry
   points, and repository conventions.
4. Within the user's deletion authority, remove every sufficiently proven dead
   or obsolete candidate and its orphaned tests, configuration, documentation,
   imports, dependencies, and architectural scaffolding. Update documented
   architecture or behavior before deletion when the contract changes.
5. Do not equate untouched with unused. Preserve or request a decision for
   ambiguous public APIs, reflection or dynamic imports, plugin hooks,
   framework-discovered code, serialization contracts, migrations, deployment
   paths, compatibility shims, generated/vendor files, and external consumers.
6. Run established formatters and style checks across the affected scope and
   inspect remaining inconsistency. Do not introduce a formatter or unrelated
   mass restyling without authorization.
7. Reconcile README and linked design claims against final code in both
   directions: requirements, architecture, interfaces, algorithms, commands,
   status, limitations, and acceptance criteria.
8. Run the strongest proportionate tests, lint, format checks, type checks,
   builds, and dead-code or dependency analysis. Investigate regressions instead
   of weakening checks.
9. Report deleted items and evidence, retained ambiguous candidates and reasons,
   style actions, documentation reconciliation, verification, and remaining
   limitations.

If deletion authority is absent, request it before destructive changes and report
the candidates. Concrete blockers or unverified regions must be disclosed.

## Horizon-expansion gate

After hygiene verification, deliberately search beyond incremental improvement:

- restate the underlying user outcome without the current feature set;
- challenge or invert product, domain, architecture, data, interface,
  operational, delivery, and business assumptions;
- consider eliminating a subsystem or workflow rather than optimizing it;
- explore alternative architectures, algorithms, interaction and ownership
  models, and cross-domain analogies;
- examine 10x changes in scale, latency, cost, reliability, simplicity, reach, or
  user value;
- distinguish essential constraints from historical accidents and constraints
  testable through a safe experiment;
- consider capabilities enabled only by the completed iterations and cleanup.

Search broadly rather than stopping at the first creative idea. Apply the same
proposal threshold as `review-matrix.md`: a horizon idea qualifies only when it
is evidence-backed enough for its speculative stage, materially advances the
approved outcome, and has positive expected net value after risk, cost,
complexity, migration, and opportunity cost are considered. Novelty alone does
not qualify, and an idea expected to make the approved outcome worse is a
negative optimization.

Report every qualifying idea and, when several qualify, present a diverse,
non-padded portfolio spanning adjacent breakthroughs, architecture or product
reframes, and credible high-upside moonshots. There is no minimum count. If no
idea qualifies, omit the horizon proposal portfolio and close the gate without
listing rejected explorations or manufacturing innovation. Report rejected
directions only when the user explicitly requests an audit trail.

For each horizon proposal state:

- the leap, the local optimum escaped, and challenged assumption;
- why incremental optimization cannot plausibly reach the same outcome;
- expected upside and beneficiaries;
- technical, product, security, operational, and adoption risks;
- cost, dependencies, reversibility, and migration implications;
- the smallest bounded falsification experiment;
- evidence thresholds for adoption, revision, or rejection.

Keep speculative horizon proposals separate from verified findings and backlog.
Do not rewrite the README or implement an idea merely because the user selected
it. Require explicit authorization for a new future round and its scope; that
round does not reopen the verified final state automatically.

## Final completion

Present hygiene and verification results before any horizon portfolio. The final
round cannot close until both gates pass or their concrete blockers are reported;
the horizon gate may pass with zero qualifying proposals after a complete search.
