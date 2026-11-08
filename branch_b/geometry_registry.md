# Branch B geometry and fitter registry

Status: Week 1 registration record. Entries are proposed for development and are not yet frozen for pilot or confirmatory use.

## Observable geometries

### valuation_chebyshev
- Role: proposed primary valuation-based observable geometry
- Observable input: the 12 released features only; AUX is treated as the 12th observable
- Native dissimilarity family: Chebyshev-based
- Status: registered for development
- Preprocessing: coordinate-wise z-score standardization estimated from training only and applied unchanged to validation/test
- Standardization convention: `ddof=0`
- Common post-geometry normalization: divide by maximum finite off-diagonal dissimilarity; scale `<=1e-12` is `DEGENERATE_DISTANCE`
- Open specification items: favorable-feature sanity invariant/minimum criterion
- Restriction: no latent labels, true hierarchy, generator parameters, or fitted preliminary hierarchy may define the native dissimilarity

### standardized_euclidean
- Role: proposed primary comparison geometry
- Native dissimilarity: Euclidean distance after coordinate-wise z-score standardization
- Preprocessing: coordinate-wise z-score standardization estimated from training only and applied unchanged to validation/test
- Status: registered for development
- Standardization convention: `ddof=0`
- Common post-geometry normalization: divide by maximum finite off-diagonal dissimilarity; scale `<=1e-12` is `DEGENERATE_DISTANCE`

### correlation_distance
- Role: proposed comparison geometry, confirmatory only if its prespecified admissibility rule passes
- Native dissimilarity family: Pearson-correlation-based distance
- Preprocessing: none; Pearson correlation is computed on the released 12-feature profiles without coordinate standardization or other transformation
- Exactly constant profile: explicit `DEGENERATE_DISTANCE` because Pearson correlation is undefined
- Near-constant/admissibility rule: pending explicit Branch B meeting; no draft quantile/statistic/threshold construction is frozen
- Common post-geometry normalization: divide by maximum finite off-diagonal dissimilarity; scale `<=1e-12` is `DEGENERATE_DISTANCE`
- Status: registered for development

## Candidate Common Fitters

### gradient_descent_ultrametric
- Role: candidate Common Fitter
- Method family: gradient-descent ultrametric fitting
- Source: Chierchia & Perret, *Ultrametric Fitting by Gradient Descent*
- Registered objective: Dasgupta relaxation with differentiable soft-cardinality construction
- Ultrametric parameterization: min-max / subdominant-ultrametric operator
- Source-backed initialization: working edge weights initialized to input edge weights
- Optimizer family reported by source: AMSGrad
- Status: registered for development; not selected
- Project settings: complete graph; AMSGrad; learning rate 0.01; D05 relative-objective magnitude tolerance 1e-6 for 5 consecutive iterations, with r_t = abs(L_t - L_(t-1)) / max(abs(L_(t-1)), abs(L_0), 1e-12); maximum 1000 iterations; normalized weight <=1e-12 -> DEGENERATE_DISTANCE; equal-height ties -> unresolved multifurcation; zero-length branches preserved and structurally unresolved; DEGENERATE_TREE reserved for structural invalidity; deterministic primary execution with no random restarts
- D05 decision (2026-11-08; pre-implementation, not protocol lock): evaluate the finite objective after each complete projected optimizer update; increment the consecutive-small-change counter when r_t < 1e-6, otherwise reset it. Declare convergence at 5 consecutive qualifying updates. On reaching the 1000-update cap without convergence, report NUMERICAL_FIT with a distinct iteration-cap/nonconvergence subcode; report runtime expiry separately as TIMEOUT. Numerical calculation errors also use NUMERICAL_FIT with their own diagnostic subcode. Retain objective/relative-change history, final iteration, elapsed time, convergence flag, and failure details. The cap and timeout are independent limits; the exact runtime timeout remains pilot-dependent. These D05 numerical settings are agreed for implementation without performance calibration, but the fitter and the protocol are not frozen.
- D04 decision (2026-11-08, revised by team; candidate implementation rule, not formal project lock): give equal total weight to distinct infinitesimal-perturbation-realizable complete hierarchical resolutions while respecting strict existing edge-weight levels; within each resolution average full-objective limiting gradients uniformly over admissible strict tied-edge orderings. Use an **exact dynamic-programming state/count/Jacobian-sum algorithm for every tied set, at every size**; remove the former six-vertex trigger and do not preterminate based on tied-vertex count, estimated memory/work, or predicted infeasibility. DP must distinguish canonical labeled rooted hierarchies and preserve exact conditional counts, with no stochastic or approximate fallback. Continue exact permitted computation unless it completes, encounters an independently prescribed numerical failure, or the actual frozen runtime deadline expires; only actual expiry produces TIMEOUT, with diagnostics. Preserve tied multifurcations in reported trees. Seven tied vertices is a feasibility hypothesis to benchmark under Python 3.14, not a guaranteed capacity or performance gate. The exact DP correctness, memory behavior, feasible perturbation handling, source-conformant full-objective gradient, Python 3.14 benchmarks, and runtime deadline remain unverified or pending; do not mark full fitter frozen.
- D02 decision (2026-11-08; team-frozen candidate parameter, not full protocol lock): fix the Dasgupta soft-cardinality sigmoid beta at exactly 5 for this Common Fitter candidate; no manual post-observation tuning at calibration or later stages. Exact sigmoid and D06 self-mass semantics remain to be reconciled. The full candidate and project-level freeze gates remain separate.
- Open project-specific items: pilot-fixed timeout, exact Python 3.14 dependency versions, executable optimizer-kernel validation

The final executable Geometry Cards, Common Fitter Cards, geometry-specific selection rules, and geometry-neutral Common-Fitter selection rule are completed and frozen at their protocol-defined later gates.
