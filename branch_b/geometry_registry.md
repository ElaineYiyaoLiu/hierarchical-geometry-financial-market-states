# Branch B geometry and fitter registry

Status: Week 1 registration record. Entries are proposed for development and are not yet frozen for pilot or confirmatory use.

## Observable geometries

### valuation_chebyshev
- Role: proposed primary valuation-based observable geometry
- Observable input: the 12 released features only; AUX is treated as the 12th observable
- Native dissimilarity family: Chebyshev-based
- Status: registered for development
- Open specification items: exact train-estimated preprocessing and the complete executable mapping required by the Geometry Card
- Restriction: no latent labels, true hierarchy, generator parameters, or fitted preliminary hierarchy may define the native dissimilarity

### standardized_euclidean
- Role: proposed primary comparison geometry
- Native dissimilarity: standardized Euclidean distance
- Status: registered for development
- Open specification items: implementation details in the Geometry Card

### correlation_distance
- Role: proposed comparison geometry, confirmatory only if its prespecified admissibility rule passes
- Native dissimilarity family: Pearson-correlation-based distance
- Status: registered for development
- Open specification items: quantitative constant/near-constant admissibility rule and deterministic failure/ineligibility behavior

## Candidate Common Fitters

### gradient_descent_ultrametric
- Role: candidate Common Fitter
- Method family: gradient-descent ultrametric fitting
- Status: registered for development; not selected
- Open specification items: exact objective, initialization, stopping rule, randomness/seed rule, tie and zero-branch conventions, degeneracy handling, timeout, and numerical-failure behavior

The final executable Geometry Cards, Common Fitter Cards, geometry-specific selection rules, and geometry-neutral Common-Fitter selection rule are completed and frozen at their protocol-defined later gates.
