# Implementation log

## Week 1-3 PL integration status

The shared observable schema, manifest schema, Branch B output schema, validator, golden fixtures, naming/checksum rules, access matrix, and freeze registry are in place. Branch A has frozen H1-H6 for pilot use and completed a development handoff rehearsal against a pinned copy of the shared validator.

Branch B scientific implementation has not been performed by the Project Lead. Branch B method cards, valuation-geometry sanity evidence, Common-Fitter rule, and pilot processing artifacts remain Branch B-owned gates.


## Branch B Week 2 implementation status — 2026-09-30

Branch B Week 1 setup is complete and Python 3.14 CI is passing.

Implemented Week 2 infrastructure currently includes:
- geometry-specific preprocessing interfaces;
- train-fit standardization and identity preprocessing;
- Euclidean, Chebyshev, and correlation geometry machinery;
- common-normalization interface with fail-closed unresolved configuration;
- candidate Common-Fitter interface and source-backed gradient-descent configuration record;
- train/validation/test recovery-pipeline scaffold;
- full-split bootstrap resampling scaffold with failed-fit retention;
- hierarchy-support distortion, LCA-depth stability, Q statistic, and support-decision plumbing;
- rooted-triplet recovery;
- paired replicate-level contrast infrastructure;
- tree edge-list validation and output-record plumbing;
- protocol failure-code handling and Python 3.14 tests.

Remaining Week 2 technical blockers are the unresolved common normalization rule, complete correlation admissibility settings, and complete project-specific Common-Fitter settings. Faculty concept/governance approval is a separate external Week 2 gate.


### Week 2 structural recovery correction — 2026-09-30

The recovery audit identified an inconsistency between rooted-triplet evaluation and LCA-depth stability around zero-length/unresolved branches. Both now use resolved topological depth after contracting zero-length or explicitly unresolved edges. Positive branch-length magnitudes no longer affect rooted-triplet topology.

Verification under Python 3.14.7:
- shared validator: 15 passed;
- Branch B test suite: 34 passed;
- workflow run 36808137703: success.

This correction did not alter any frozen scientific threshold or access boundary.


## Branch B approved settings implementation — 2026-10-01

Implemented without changing the pending correlation-degeneracy specification:
- max-off-diagonal common normalization with 1e-12 degeneracy guard;
- ddof=0 train-only standardization default;
- complete-graph/AMSGrad fitter configuration;
- lr=0.01, relative objective tolerance 1e-8 for 10 consecutive iterations, max 1000;
- near-zero normalized edge guard at 1e-12;
- deterministic primary/no random restarts;
- unresolved multifurcation and zero-branch conventions;
- deterministic ultrametric-to-tree extraction that does not arbitrarily binary-resolve ties;
- recovery pipeline default now points to the approved common normalization.

The remaining fitter engineering task is the executable Python 3.14 implementation of the approved paper-based Dasgupta soft-cardinal/min-max optimization kernel. Correlation degeneracy/admissibility remains intentionally unresolved.


## Audit correction — correlation and remaining Week 2 integration gaps — 2026-10-01

The earlier correlation robust-spread draft (Q0.05/Q0.95 relative spread) was removed from executable Branch B methodology because Branch B explicitly deferred the correlation-degeneracy/admissibility decision to a later meeting. The repository now retains only the raw Pearson-distance primitive, no coordinate preprocessing, and an exact-constant mathematical failure guard.

Additional Week 2 integration gaps identified by audit:
- the Common Fitter configuration is approved but its executable Dasgupta/min-max kernel is still missing;
- the recovery pipeline does not yet implement the full validation-hierarchy selection -> frozen-parameter test-hierarchy sequence;
- the bootstrap engine resamples all three splits but still needs end-to-end integration proving preprocessing refit, validation reselection, test fitting, duplicate multiplicity handling, and LCA common-observation matching inside each replicate;
- general matrix/tree numerical comparison tolerances remain separate unresolved choices and are not inferred from the approved 1e-12 normalization/weight guards.
