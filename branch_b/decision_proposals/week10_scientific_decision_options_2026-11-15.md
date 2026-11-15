# Week 10 scientific decision options — Branch B discussion brief

**Status:** proposals for scientific review on November 15–18, 2026. No approval, freeze,
change to the registered fitter, calibration, pilot processing, locked testing, or unblinding.

**Source basis:** controlling Version 2 Branch B Packet, especially within-dataset
selection, hierarchy support, Appendix D, and primary comparison sections; the
Week 10 meeting goals; October 20 D07–D17 intake; Week 3 numerical proposal;
current draft geometry cards; and current public freeze registry. The November 8
D01–D06 team choices remain the development baseline, not reopened here.

## Decisions that can be discussed now

| ID | Proposed decision | Recommendation and reason | Approval and remaining dependency |
| --- | --- | --- | --- |
| D07 numerical checks | Candidate absolute tolerance 1e-12 for matrix symmetry, zero diagonal, ultrametric inequalities and extracted-height comparisons | **Continue reviewing** the existing proposal, but do **not approve a blanket height-tie tolerance** as a substitute for D04's exact working-edge tie rule. For accepted near-symmetric inputs, specify canonicalization and near-zero denominators first; orientation-dependent denominator screening is demonstrated by synthetic tests | PL approval and numerical-tolerances freeze required; interpretation of accepted residuals unresolved |
| D08 correlation admissibility | For each finite 12-coordinate profile, let a(x)=sqrt(sum_k (x_k-mean(x))^2)/sqrt(sum_k x_k^2). Require nonzero raw norm and a(x)>1e-12; otherwise correlation geometry ineligible on affected dataset, with DEGENERATE_DISTANCE under the documented proposal | **Recommend adopting the existing Week 3 proposal**, not choosing a data-tuned new threshold. Equality at 1e-12 is inadmissible; no jitter, dropping or split-wise repair | Branch B can select this proposal for PL sign-off; approved card/freeze still necessary |
| D11 Common Fitter selection | Historical proposal: lexicographic numerical-failure, distortion, stability, resources, with one fitter across all primary geometries | **Recommend retaining lexicographic priorities in principle**, but do not approve until exact eligibility, within-geometry ranks, equal geometry weights, direction, missing metrics, failures, stable sort/tie rule, and aggregation are specified. Raw distortions across geometries must never be pooled | Can choose procedure before blind validation; controlling protocol requires a geometry-neutral, scale-invariant, prespecified rule. Needs complete specification before freeze |
| D12 bootstrap reliability | Fixed attempt budget, strict minimum-success and distinct-common-observation checks, plus failure rate | **Recommend fixed attempts with explicit failures retained**. Do not pick minimum counts/failure fraction from an arbitrary synthetic performance result | Protocol assigns minimum successes, common-ID counts and failed-fit behavior to pilot/bounded operational approval |
| D13 support interval | Support point estimate is mean of successful Q_b=S_b-min(D_b,1); interval conditional on successful fits | **Recommend defining confidence target as mean successful-bootstrap Q**, distinct from a percentile interval describing the spread of individual Q_b. Candidate mean-CI methods require comparison (e.g., normal/Student-t approximation versus resampling successful Q_b means), chosen confidence level, handling of dependent/nested resampling, minimum successes and seed policy | Statistical method must be approved at protocol-permitted pilot freeze; do not silently treat percentiles of raw scores as a CI for the mean |
| D14 seed, attempts, runtime | Historical seed 36, B=500 proposal, golden-case runtime x2 idea | **Defer final values/rule** until approved actual pilot evidence and hardware/time scope. Namespaced, role-separated Branch B-owned seeds should be specified without consulting generator seeds | Pilot-dependent rules and approved computational/reproducibility gates control |
| D15 calibration quantile | Inverse empirical CDF for per-family empirical 95th-percentile of Q scores; threshold = max across prespecified nonhierarchical families for each geometry×candidate fitter | **Recommend nearest-rank / inverse empirical-CDF** q_0.95 = sorted(q)[ceil(0.95*N)-1], preserving exact repeated values, no interpolation. Record how insufficient usable calibration scores fail before blind validation. Threshold equality remains indeterminate by protocol | Quantile procedure can be chosen before calibration/blind validation; minimum usable count and failure treatment need approval |
| D09 valuation favorable-feature sanity | Historical selection of one recovery-number criterion, but no complete allowed control/metric/minimum | **Do not invent metric or cutoff.** Confirm authorized non-generating control and proof of criterion frozen before permitted inspection | Requires scientific definition and verified pre-inspection provenance |
| D10 minimum effect | Historical 0.05 absolute rooted-triplet accuracy contrast proposal | **Do not retroactively freeze.** Confirm historical approval and pre-inspection timing | Project-level timing/provenance gate; not an engineering default |
| D16–D17 | October 20 intake records deferred choices | **Do not infer content or invent answers from IDs.** Recover exact decision questions from the approved briefing and apply correct gate | Exact substantive decision wording/authority needs verification |

## Protocol-defined rules, not free decisions

- D01–D06 candidate mathematics is recorded; do not retune based on
  scientific performance.
- Train-fitted preprocessing; independently resampled train, validation and
  test split roles; test support only after validation-only selection.
- For successful bootstrap fits, Q_b=S_b-min(D_b,1). The support point
  estimate is the arithmetic mean over successful bootstrap replicates;
  unsuccessful fits and rates are reported separately; minimum-success and
  minimum-common-ID failures are indeterminate.
- At least 100 bootstrap repetitions in the full experiment. The protocol
  requires the specific pilot-dependent operational freeze.
- For each geometry×candidate fitter, per-family empirical 95th percentiles
  are computed and their maximum is the project threshold. Thresholds must
  be frozen before blind validation, with decision-level false-support checks
  using the independent null validation bank.
- Lower CI > threshold implies supported; upper CI < threshold implies not
  supported; otherwise indeterminate. Equality is indeterminate.
- Primary Monte Carlo comparison: paired replicate-level valuation minus
  comparator rooted-triplet accuracy, failures assigned accuracy zero where
  prescribed, with distinct successful-only sensitivity reporting. Do not
  substitute per-triplet pseudo-replication or a best-comparator omnibus claim
  without a frozen multiplicity procedure.

## Proposed meeting actions and gate status

1. Vote on D08's full candidate admissibility formula and D15's inverse-ECDF
   algorithm, **subject to PL approval and correct freeze timing**.
2. Request exact D11 ranking/aggregation and missingness/tie choices before
   adopting the proposed lexicographic selection; retain one common fitter.
3. Ask the statistical lead to distinguish interval for mean Q from distribution
   of individual Q_b and prespecify D13 after the permitted pilot review.
4. Keep D12/D14 pilot-dependent values provisional rather than guessing counts,
   timeouts or success thresholds now.
5. Resolve D07's near-symmetric matrix interpretation first; use D04 exact
   working-weight equalities regardless of a separate matrix validity tolerance.
6. Obtain written source/provenance for D09/D10 and the exact D16–D17 question
   texts before treating them as closed.
7. Archive actual Python 3.14 JUnit/dependency/checksum evidence before
   scientific implementation certification. Team reports of passing tests are
   not equivalent to inspected execution artifacts.

**Public Branch B write safety check:** This note contains only observable-side
protocol mathematics, pre-existing proposals, generic synthetic implementation
findings and governance-status summaries. No restricted generating implementation,
hidden configuration or conditions, generator-owned seeds, latent labels, sealed
ground truth, true hierarchy or side-channel inference is present. Safe to
publish on the shared review branch.
