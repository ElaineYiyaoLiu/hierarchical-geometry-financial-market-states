# Draft Support and Calibration Card

Status: consolidated November 17 PL documentary review of existing packet requirements and November 15 team proposals. Scientific approval, pilot-dependent settings and execution freezes remain separate.

## Support and Reliability

For each successful full-pipeline bootstrap attempt, use `Q_b=S_b-min(D_b,1)` and the arithmetic mean of successful scores. Each attempt independently resamples train, validation and test roles; preprocessing is fitted on its training draw, geometry parameters follow the frozen validation selection, and support uses its test draw. Preserve distinct original identities and all multiplicities. Do not reselect geometry definitions or the Common Fitter.

For attempt b, the common set is the eligible distinct original test identities shared by the full-test reference and bootstrap-test tree. Count each identity once. Apply common-set eligibility per attempt before counting it as successful. Undefined/constant rank comparisons and the packet's other unsuccessful outcomes remain failures in the ledger. Average ranks apply to tied rank comparisons.

For complete fixed-budget execution, `B=B_success+B_failure`, with failure rate `B_failure/B`. Retain the team's inclusive proposed reliability boundaries `B_success>=B_min`, `n_common,b>=n_min` and `B_failure/B<=f_max`. Numerical limits remain at their authorized pilot/bounded-revision gate. Missing rules or failed reliability yield an indeterminate support outcome. Missing/unexecuted attempts remain distinguishable from observed failures.

The existing score definition implies Q in [-2,1]. The failed-fit sensitivity point summary is `(sum_success Q_b-2*B_failure)/B`. Its full interval/decision method needs its own explicit statistical specification. Do not reuse the successful-only interval as an interval for this different summary.

## D13 Selected Interval Candidate

Preserve the team-selected conditional mean of successful Q scores as the candidate target. Draw 10,000 secondary samples with replacement, each of size B_success, and compute their means. Use the 250th and 9750th ordered means, one-based, for the nominal two-sided 95% interval; retain exact repeated values without interpolation. The original successful-score mean is the point estimate.

The arithmetic and reproduced generic studies have been reviewed. Statistical sufficiency of conditional Monte Carlo uncertainty, evaluator independence/state assumptions, finite-sample undercoverage, D12 integration and secondary seed derivation remain explicit acceptance requirements. An interval from individual Q percentiles would be a different procedure. No interval replacement is selected here.

## D15 Calibration Candidate

For each required family and fixed geometry/candidate-fitter pair, retain all attempts and apply the team-selected inverse empirical-CDF rule to eligible finite successful scores: `qhat_0.95=q_(ceil(0.95*N))`, one-based. Keep repeated values; do not interpolate or invent replacement scores. Preserve every required family, including families with failed or missing results.

The project threshold is the maximum of these family-specific quantiles. If any required family fails its approved minimum usable-count rule, calibration is incomplete and emits no valid final threshold. The numerical minimum, exact family inventory, unresolved eligibility semantics, permitted tier/seed provenance and authorization remain required. No threshold was calculated in this review.

Freeze permitted operational rules at their designated gate; construct/freeze thresholds before blind validation; selection mechanically activates the corresponding precomputed threshold without recalibration. Independent null validation remains separate. Each bank retains its required realization/seed separation.

## Support Decision and Reporting

After reliability and the applicable method/threshold gates pass, lower interval endpoint > threshold means supported; upper endpoint < threshold means not supported; otherwise indeterminate. Equality is indeterminate. Report failures, reliability, interval target, failure-sensitive analysis and geometry/family-specific outcomes. No pooled-family claim follows automatically from separate geometry results.

PL documentary findings: D12 framework, D15 candidate construction and the packet's interval-based decision ordering are consistent in principle. D13 statistical acceptance, numerical limits, implementation certification and actual approval records remain required. See the [existing six-item disposition](../decision_proposals/d12_d14_pl_disposition_2026-11-15.md) and [execution evidence](../reviews/2026-11-16-closeout/README.md).

Project Boundary: actual card content was inspected and is permitted for Branch B/public disclosure. It consolidates permitted definitions/proposals and changes no production code, seed rule, schema, evaluation definition or freeze.
