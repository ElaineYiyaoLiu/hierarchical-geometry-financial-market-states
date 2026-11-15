# Branch B D08 and D15 team selections — November 15, 2026

**Recorded team response:** Branch B approved the proposed D08 and D15 selections on November 15, 2026, following the Week 10 scientific decision-options review.

**Status:** Branch B team-selected proposals only. This record is **not** Project Lead authorization, an executable scientific freeze, a modification of the public freeze registry, permission to run calibration, or permission to process locked tests.

## D08 — Correlation admissibility: team-approved proposal

For each finite 12-coordinate observable profile `x`, define:

- `mean(x) = sum(x_k) / 12`
- `c(x) = sqrt(sum((x_k - mean(x))**2))`
- `r(x) = sqrt(sum(x_k**2))`
- `a(x) = c(x)/r(x)` when `r(x) > 0`.

**Proposed decision:** require all 12 coordinates to be finite, `r(x) > 0`, and `a(x) > 1e-12`. Equality to `1e-12` is inadmissible. A zero raw norm is inadmissible. Do not add jitter, floor centered norm, drop observations or repair data using another split. Under the existing Week 3 proposal, if any required profile is inadmissible, record `DEGENERATE_DISTANCE` for that dataset's correlation geometry and do not use that geometry confirmatorily on that dataset.

This adopts the complete formula and deterministic boundary described in `week3_numerical_rules_proposal.md`, not the separate unapproved D07 matrix/ultrametric numerical-comparison proposal.

**Pending:** Project Lead confirmation of protocol compatibility, applicable timing gate, approved correlation Geometry Card, verification/freeze evidence and authorized implementation. Nothing in this team response approves data-dependent threshold tuning.

## D15 — Calibration empirical quantile: team-approved proposal

For `N` eligible, usable calibration score observations of a prespecified nonhierarchical family and a fixed geometry × candidate-fitter combination, sort values `q_(1) <= ... <= q_(N)`. The proposed 95th-percentile estimator is:

`qhat_0.95 = q_(ceil(0.95 * N))` (one-based order-statistic index).

This is the inverse empirical-CDF / nearest-rank rule; it selects an observed value without interpolation and preserves equal repeated values. As required by the controlling protocol, the project threshold is the maximum of the family-specific 95th percentiles across prespecified nonhierarchical families for the same geometry × candidate fitter. Equality with a threshold remains indeterminate.

**Further team approval (November 15, 2026) — D15 failure and missing-score policy:**

- Preserve **all** attempted calibration records, including successful and unsuccessful attempts, failure diagnostics and Branch B-owned provenance. Never silently erase failed attempts from the attempt count.
- Preserve the **entire prespecified required nonhierarchical null-family inventory**. No family may be removed from the threshold maximum because it has missing or failed results.
- Within each required family and geometry x registered fitter, apply the approved inverse empirical-CDF quantile **only to eligible finite successful Q scores**. Missing, nonfinite, undefined or failed-fit outcomes are unusable and remain recorded with their observed failure information; do not invent a replacement score.
- If any required family has fewer than its **approved minimum usable calibration count**, mark calibration **incomplete** and do not emit a valid final geometry/fitter support threshold or use the incomplete calibration for confirmatory classification.
- Retain the originally approved strict comparison rule: threshold equality is **indeterminate**. No score, family, or attempt is silently excluded to improve the threshold.

**Still pending:** The **numerical minimum usable count**, failure-code/eligibility semantics where not already protocol-defined, exact required family inventory and permitted tier provenance, seed/score-level details, and the applicable **pre-calibration** Project Lead authorization and freeze. This new team decision does not choose numerical limits or authorize calibration execution. No calibration was performed and no numerical threshold was calculated.

## Other decisions unchanged

D07, D09–D14 and D16–D17 remain at their previously recorded statuses; no numerical tolerance, favorable-feature metric, Common-Fitter selection rule, bootstrap interval, reliability threshold, seed/timeout rule, or pilot gate is adopted by this record. D01–D06 team choices are unchanged. The registered production Common Fitter remains fail-closed.

## Next permitted action

Prepare synthetic Python 3.14 boundary tests for D08 and D15, and review the proposed formulas against existing Branch B interfaces. Do not implement a scientific production rule or execute calibration until the specified approvals and freezes are satisfied.

**Shared public repository pre-write check:** The actual text above consists exclusively of Branch B-permitted observable-side proposed statistics, the user's team approval, and documented public freeze boundaries. It contains no restricted generator details, hidden experimental conditions, generator seeds, latent hierarchy or labels, sealed truth, true hierarchy-dependent evaluations, or side-channel analysis; therefore it is safe for public disclosure.
