# D13 — resampled-mean percentile interval: Branch B team selection

**Team response (November 15, 2026):** Branch B selects the **third method** from the November 15 D13 discussion: a percentile interval based on *resampling the successful bootstrap support scores and computing a mean for each secondary resample*.

**Further Branch B team confirmation (November 15, 2026):** The team also selects the recommended **nominal two-sided 95% confidence level** for this candidate method. This selects equal nominal tail probabilities of 0.025 and 0.975, not a particular finite-sample quantile algorithm, number of secondary resamples or coverage claim.

**Additional Branch B team selection (November 15, 2026):** Exactly **10,000 secondary resamples**, using the **inverse empirical-CDF / nearest-rank percentile rule without interpolation** for nominal two-sided **95%** endpoints. This selects computation settings for the proposed interval; it does not establish statistical coverage, approve seed derivation, or complete the required pilot-dependent freeze.

**Additional team confirmation (November 15, 2026):** Branch B selects **conditional Monte Carlo uncertainty in the mean successful-bootstrap support score** as the **proposed inferential interpretation**. This is conditional on the observed dataset, the fixed reference fit/procedure, and successful primary attempts. It is **not** a claim of population-level sampling coverage. The 10,000-resample, nominal two-sided 95%, nearest-rank 250th/9750th endpoint calculation remains unchanged. This interpretation is subject to statistical coverage review, protocol-conformance approval and the authorized post-pilot freeze.

**Status:** Branch B team-approved proposed method, level, secondary-resampling count, percentile endpoint convention, and conditional Monte Carlo interpretation. Not demonstrated coverage, Project Lead/statistical authorization, an executable scientific freeze, permission to calculate scientific support intervals, or approval for calibration/locked-test processing.

## Statistical target fixed by the protocol

For each successful primary bootstrap attempt `b`:

`Q_b = S_b - min(D_b, 1)`.

For the set `B_success` of successful attempts:

`Qhat = sum(Q_b for b in B_success)/len(B_success)`.

The target of the candidate confidence interval is the **conditional mean of successful-attempt Q**, as required by the governing hierarchy-support protocol. Failures are never silently discarded from the attempt accounting, although the numerical interval is conditional on successful attempts and therefore does not include their Q values.

## D13 team-selected interval family

1. Preserve the full original primary-bootstrap attempt ledger, successes, failure codes, distinct-common-observation counts, and applicable failure sensitivity records.
2. Take the successful primary-bootstrap `Q_b` scores only (assuming an approved minimum-success gate is satisfied).
3. For each secondary resample, draw with replacement from this successful-score collection at its original successful-sample count and compute the mean of the drawn scores.
4. Construct a percentile interval from the distribution of these **secondary-resample means**, *not* from the original individual `Q_b` values.
5. Report the primary-bootstrap `Qhat` as the point estimate; use the approved support-threshold comparison only after the D13 procedure and reliability/threshold freezes are complete.

**Selected computational rule:** Generate exactly `R = 10_000` secondary samples, each of size `B_success` drawn uniformly with replacement from the successful primary `Q_b` values. Compute one mean per secondary sample. Sort the 10,000 secondary means in ascending order as `qstar_(1) <= ... <= qstar_(10000)`. Report the candidate interval `[qstar_(ceil(0.025*10000)), qstar_(ceil(0.975*10000))]`, i.e. **the 250th and 9750th order statistics** using one-based indices. Repeated equal values are retained unchanged; no interpolation is applied. Keep the primary `Qhat` as the point estimate, distinct from the distribution of resampled means. This fixes the proposed count and endpoint order statistic, not coverage or an approved seed/reliability rule.

## Inferential target and limits of selected method

For fixed observable data and the frozen reference procedure, the proposed inferential target is the conditional expectation of `Q_b` **given successful execution of a primary bootstrap attempt**. The primary estimate is the empirical mean among successful primary attempts. A secondary empirical bootstrap of successful scores estimates finite-primary-replicate Monte Carlo uncertainty only if the successful primary scores satisfy the relevant conditional exchangeability/independence and stable procedure assumptions. Common fixed input data/reference do not alone establish or refute these assumptions.

A nominal 95% percentile interval is **not automatically exact finite-sample 95% coverage**, especially for small successful counts, discrete/tied/degenerate scores, skewness, or success depending on score-related observables. Empirical synthetic coverage is diagnostic evidence, not a substitute for a justified inferential guarantee. Any need to switch inferential targets or intervals requires another authorized decision.

## Required statistical review before execution or freeze

- **Dependence:** Primary-bootstrap Q scores share the full-split reference fit and common observable data. Conditional independence/exchangeability sufficient for naive resampling of scores and coverage for the intended mean has **not** been established. A statistically appropriate review must determine whether the proposed secondary-resampling unit/design is valid; changes needing a different method require a separately approved D13 revision.
- **Confidence level and endpoints:** Branch B selected nominal two-sided 95%, 10,000 secondary resamples, and inverse empirical-CDF nearest-rank endpoints (one-based positions 250 and 9750), preserving exact ties without interpolation. The level is **not** a demonstrated coverage guarantee. Implementation arithmetic, seed derivation, and validity under the primary-bootstrap dependence structure remain subject to review.
- **D12 reliability:** Minimum number of successful fits, minimum distinct common observations, permissible failure fraction, and full sensitivity treatment remain governed by the pilot/bounded revision gate; the method does not create new defaults for them.
- **D15 separation:** D15's separate inverse empirical-CDF selection applies to **calibration score thresholds**. D13 now independently selects the same order-statistic *type* for the 2.5% and 97.5% secondary-mean endpoints; neither decision changes the other's statistical target or freeze gate.
- **Blinded evaluation:** No fit failures may be reclassified to improve coverage or support; no hidden labels, true hierarchy, null truth, independent-validation or locked-test outcomes may be used to choose the interval rule.

## Next permitted steps

Prepare a technical protocol-conformance/statistical assessment and Python 3.14 **synthetic-only** conditional-coverage diagnostics for the selected interval and target, without freezing numerical settings or activating scientific support decisions. Present the dependence issue, selected nominal confidence level, 10,000-resample count, and nearest-rank endpoint rule for review at the authorized pilot-dependent freeze. Specify independent, recorded Branch B-owned secondary-resampling seed derivation before any authorized scientific execution. The registered Common Fitter remains fail-closed.

**Public Branch B pre-write verification:** This record contains only the user's selected observable-side interval methodology, protocol-defined public formulas, previously reviewed development decisions, and review requirements. It contains no restricted generating information, hidden conditions, generator-owned seeds, latent labels, true hierarchy, sealed evaluation values, true-hierarchy-dependent tests, or side-channel inference. Safe for the shared public review branch.
