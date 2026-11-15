# D13 — resampled-mean percentile interval: Branch B team selection

**Team response (November 15, 2026):** Branch B selects the **third method** from the November 15 D13 discussion: a percentile interval based on *resampling the successful bootstrap support scores and computing a mean for each secondary resample*.

**Further Branch B team confirmation (November 15, 2026):** The team also selects the recommended **nominal two-sided 95% confidence level** for this candidate method. This selects equal nominal tail probabilities of 0.025 and 0.975, not a particular finite-sample quantile algorithm, number of secondary resamples or coverage claim.

**Status:** Branch B team-selected **method direction**, not an operationally complete interval procedure, demonstrated coverage, Project Lead authorization, pilot-dependent freeze, permission to calculate scientific support intervals, or approval for calibration/locked-test processing.

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

This records the intended method family. It does not determine interval coverage, the number of secondary resamples, quantile interpolation/index rules for interval endpoints, random seed derivation, or other operating settings.

## Required statistical review before execution or freeze

- **Dependence:** Primary-bootstrap Q scores share the full-split reference fit and common observable data. Conditional independence/exchangeability sufficient for naive resampling of scores and coverage for the intended mean has **not** been established. A statistically appropriate review must determine whether the proposed secondary-resampling unit/design is valid; changes needing a different method require a separately approved D13 revision.
- **Confidence level and endpoints:** Nominal two-sided 95% was selected by Branch B, with nominal 0.025/0.975 tails. Endpoint quantile rule, handling of ties, finite-sample conventions, and secondary-resample count remain open. The level is not a demonstrated coverage guarantee.
- **D12 reliability:** Minimum number of successful fits, minimum distinct common observations, permissible failure fraction, and full sensitivity treatment remain governed by the pilot/bounded revision gate; the method does not create new defaults for them.
- **D15 separation:** The team-selected inverse empirical-CDF order statistic in D15 applies to **calibration score thresholds**. It does not automatically prescribe D13 interval endpoint quantiles or their finite-sample rule.
- **Blinded evaluation:** No fit failures may be reclassified to improve coverage or support; no hidden labels, true hierarchy, null truth, independent-validation or locked-test outcomes may be used to choose the interval rule.

## Next permitted steps

Prepare a technical protocol-conformance/statistical assessment and Python 3.14 **synthetic-only** interface tests for the candidate interval, without freezing numerical settings or activating scientific support decisions. Present the dependence issue, team-selected nominal confidence level, resampling count and endpoint rule for review at the authorized pilot-dependent freeze. The registered Common Fitter remains fail-closed.

**Public Branch B pre-write verification:** This record contains only the user's selected observable-side interval methodology, protocol-defined public formulas, previously reviewed development decisions, and review requirements. It contains no restricted generating information, hidden conditions, generator-owned seeds, latent labels, true hierarchy, sealed evaluation values, true-hierarchy-dependent tests, or side-channel inference. Safe for the shared public review branch.
