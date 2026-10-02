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
- Preprocessing: none; Pearson correlation is computed on the released 12-feature profiles without coordinate standardization or other transformation
- Near-constant statistic: relative robust spread R_rel(z) = [Q_0.95(z) - Q_0.05(z)] / max(median(|z|), s_min)
- Quantile levels: Q_0.05 and Q_0.95 adopted by Branch B on 2026-09-30
- Status: registered for development
- Open specification items: tau_nc, tau_deg, s_min, quantile interpolation convention, numerical tolerance, and deterministic degeneracy handling

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
- Project settings: complete graph; AMSGrad; learning rate 0.01; relative-objective tolerance 1e-8 for 10 consecutive iterations; maximum 1000 iterations; normalized weight <=1e-12 -> DEGENERATE_DISTANCE; equal-height ties -> unresolved multifurcation; zero-length branches preserved and structurally unresolved; DEGENERATE_TREE reserved for structural invalidity; deterministic primary execution with no random restarts
- Open project-specific items: pilot-fixed timeout, exact Python 3.14 dependency versions, executable optimizer-kernel validation

The final executable Geometry Cards, Common Fitter Cards, geometry-specific selection rules, and geometry-neutral Common-Fitter selection rule are completed and frozen at their protocol-defined later gates.
