# Week 3 numerical decision proposal

Status: proposal only; not approved; not frozen.

This document converts two unresolved Branch B pre-pilot items into explicit reviewable proposals. It does not change any frozen protocol choice. Approval and freeze must be recorded separately before pilot exchange.

## 1. Correlation-distance admissibility proposal

Protocol role: correlation distance is a comparison geometry and is confirmatory only when the observable profile satisfies a prespecified quantitative admissibility rule.

For an observable profile x with p = 12 finite coordinates, define

- mean: m = sum(x_k) / p
- centered norm: c = sqrt(sum((x_k - m)^2))
- raw norm: r = sqrt(sum(x_k^2))

Proposed relative non-constancy statistic:

    a(x) = c / r

with the deterministic convention that r = 0 is inadmissible.

Proposed admissibility rule:

- all 12 coordinates must be finite;
- r must be strictly positive;
- a(x) must be greater than 1e-12.

No quantiles or interpolation are used.

Dataset handling proposal:

- if every profile required for a dataset's train/validation/test processing is admissible, correlation distance remains eligible for confirmatory processing;
- if any required profile is inadmissible, the correlation geometry records DEGENERATE_DISTANCE for that dataset and is retained only as exploratory for that dataset;
- do not add jitter, floor the centered norm, drop the offending observation, or use another split to repair the profile.

Rationale:

- the statistic is dimensionless and invariant to common rescaling of the entire profile;
- exactly constant profiles fail deterministically;
- the rule prevents Pearson-correlation division by a numerically negligible centered norm;
- it introduces no train-fitted parameter and uses no hidden information.

## 2. General numerical-comparison tolerance proposal

These tolerances apply only to numerical comparisons and validity checks. They do not modify the scientific geometry definitions, fitter objective, hierarchy-support statistic, or acceptance rule.

Because common post-geometry dissimilarities are normalized to a maximum finite off-diagonal value of 1, propose a common absolute comparison tolerance

    tau_num = 1e-12

for:

- matrix symmetry checks;
- zero-diagonal checks;
- ultrametric-inequality comparisons;
- equality/tie comparisons of normalized ultrametric heights used for unresolved-tree handling.

Proposed comparison semantics:

- symmetry: abs(D_ij - D_ji) <= tau_num;
- zero diagonal: abs(D_ii) <= tau_num;
- ultrametric inequality: D_ij <= max(D_ik, D_kj) + tau_num;
- height tie: abs(h_a - h_b) <= tau_num.

Do not silently project or round a matrix merely because a check fails. A failed required validity check must propagate through the registered numerical-failure rule.

## 3. Approval boundary

Before these values become controlling:

1. Branch B reviews the formulas against the executable geometry/fitter implementation.
2. Project Lead confirms that the rules are implementation/numerical specifications permitted before pilot exchange and do not alter a frozen scientific target.
3. The approved version is entered in the appropriate Geometry Card / Common Fitter or numerical-rule record and freeze registry.
4. Python 3.14 tests cover exact-boundary, just-below, and just-above cases.

Until that approval is recorded, the corresponding blockers remain open.
