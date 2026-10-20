# Branch B implementation continuation — 2026-10-20

Status: **development changes committed; Python 3.14 execution not yet independently verified for these new revisions**. No pilot, calibration, locked-test, or unblinding processing was performed.

## Scope completed

- **F1**: the structural tree validator rejects declared internal nodes with no children, preventing extra undeclared terminal vertices from passing checked selection. No binary-branching requirement was introduced.
- **F2**: checked fitted-matrix validation rejects masked arrays and nested masked entries, and rejects Boolean scalars in nested and object-typed numeric representations before NumPy can silently promote them to ordinary numbers.
- **F3**: checked fitter diagnostics must be finite, JSON-native, cycle-free objects before reaching validation selection, matching the existing outgoing serialization contract. Fields are not silently removed.
- Added synthetic regression fixtures covering each F1–F3 counterexample and nested invalid diagnostics, plus a **development-only** repeatability rehearsal of the team's proposed master seed `36` and provisional `B=500` attempts. The latter exercises the existing seed engine; it does not assign official production seeds or freeze the bootstrap count.
- Recorded the team's clarification that D02/D07/D14 calibration is restricted to protocol-permitted **training observables**, subject to the existing scientific freeze and data-access gates.
- Documented D06 mass and nonlinear weighting alternatives without choosing a weight formula or changing the fitter's reciprocal-zero behavior.

## Source commits

- Tree and matrix/diagnostics repairs: `5c4bad6`, `163eae2`, `e0f1575`.
- Synthetic regressions: `99c2c33`, `e2a3845`, `efce4d1`.
- Seed 36 / B=500 development rehearsal: `b637ae7`.
- Training-only clarification: `490b9e9`.
- D06 investigation: `f933fe1`.

The preceding 19 October executed audit remains pinned and failed; these new changes do not retroactively convert its evidence into a pass.

## Verification limitation

Both existing GitHub Actions workflows are configured to execute Python 3.14 on changes to Branch B, but the current tool access did not expose the resulting new run IDs or job logs. Consequently **no passing Python 3.14 claim is made for this continuation**. The new tests must be inspected in actual Python 3.14 logs, and any failures repaired and retained, before describing F1–F3 as verified. Do not use a different Python version as a substitute.

## Still blocked by scientific specifications

- D06: exact treatment of original-identity multiplicities, pair coefficients, soft cluster mass, within-identity zero edges, and objective normalization.
- D04: mathematically defined admissible limiting-gradient average at tied min-max bottlenecks.
- D01–D05: complete source-conformant soft-area objective and derivative, projected AMSGrad update details, effective initialization and convergence arithmetic.
- D02/D07/D14: permitted **training-observable-only** calibration criteria, candidate ranges, numerical predicates, timeout scaling function, resource environment, and protocol freeze timing.
- D09: exact valuation favorable-feature recovery criterion.
- D10: provenance of the required historical minimum-effect freeze (team's proposed value 0.05 does not retroactively establish one).
- D11: explicit geometry-neutral selection statistic, priority order, tie and missingness rules; training data do not waive this protocol requirement.
- D12–D15: applicable reliability, interval target, operational-count and calibration-family specifications at their designated gates.
- F4: truthful failure-code mapping for undefined LCA rank correlation on structurally valid star trees; unsuccessful-bootstrap status is required by the Packet, but structural invalidity is not.

No project-level scientific freeze, common-fitter card, shared schema, or authorized processing gate was changed by this continuation. The production Common Fitter remains non-executable.

This note contains only public Branch B implementation facts, team-supplied choices and observable-only synthetic considerations; no restricted generating information or sealed ground truth.
