# D13 — conditional-mean inferential validation plan (development only)

**Status (2026-11-15):** Branch B has team-selected conditional Monte Carlo uncertainty for the mean Q among successful primary bootstrap attempts, holding the observed dataset and reference procedure fixed. This is not a formal statistical endorsement, project approval, post-pilot freeze, or permission to execute scientific support/calibration/locked tests.

## Registered candidate to validate, not change

- Point estimate: mean of successful primary `Q_b = S_b - min(D_b,1)`.
- Exactly 10,000 with-replacement secondary draws of size `B_success`, with a mean for each draw.
- Nominal two-sided 95% nearest-rank interval from one-based sorted mean positions 250 and 9750.
- Retain all attempted primary fits and all failures in the complete ledger; require pilot-frozen D12 reliability checks before any support decision.
- Explicit branch-owned secondary RNG required; final production seed-derivation namespaces not yet approved.

## Inferential question

Given the fixed observable original dataset and a frozen full-pipeline reference procedure, define `mu_success = E[Q_b | successful primary bootstrap fit, original data and reference procedure]`. The candidate interval estimates finite-primary-bootstrap Monte Carlo error in the sample mean of successful Q scores. It does **not** represent variation under resampling the original dataset nor a population-level confidence interval.

**Assumption review:** Are independent primary resampling attempts and per-attempt stochastic computations conditionally independent, identically distributed and exchangeable after selection on success? If success status changes the conditional score distribution, that changes `mu_success` but need not invalidate inference on that target; nonstationarity, shared adaptive state, dependence across attempts, or inconsistent selection can invalidate naive secondary resampling. A fixed shared reference fit alone does not establish dependence between independently sampled attempts.

## Evidence plan for statistical reviewer

1. **Arithmetic / support checks (Python 3.14 only):** Exact enumeration of all resampled means for tiny synthetic successful-score multisets; verify every reported endpoint lies on the allowed finite support and match point-estimate arithmetic. Existing tests already check deterministic RNG replay and rank positions 250/9750.
2. **Controlled simulation of conditional coverage:** For each *synthetic* independent distribution with known mean and independently generated primary samples, repeat the fixed D13 algorithm over independently generated outer trials. Record the number of outer trials, successful sample size, interval coverage count, coverage proportion, Wilson or exact binomial uncertainty interval, average/median width, endpoint ties and zero-width frequency. Development-only examples: constant-valued scores, two-point discrete scores, bounded skewed scores and near-symmetric scores. Choose trial counts and effective sample sizes for computational feasibility *before* inspecting the simulation summaries. The selected D13 algorithm itself must not be retuned using coverage results without an authorized method revision.
3. **Synthetic selection-on-success:** Independently generate pairs `(success, potential_Q)` under known score-dependent success probabilities. Compare coverage for the success-conditioned target with the all-attempt mean; preserve all failure events. Distinguish correct conditional inference from misleading all-attempt claims.
4. **Deliberate assumption violations:** Use explicitly synthetic shared per-trial random shifts, correlated primary attempts, or a nonstationary sequence to characterize undercoverage when conditional-iid fails. Label these as sensitivity diagnostics, not as evidence from any hidden experimental condition.
5. **Coverage limitations:** In small/discrete samples the percentile-of-means interval may be conservative or undercover and cannot be asserted to have finite-sample exact 95% coverage. If evidence or protocol interpretation requires a different interval or target, stop and seek new scientific approval; do not silently swap the estimator.
6. **Integration and failure accounting:** After authorized D12 and D14 operational rules are defined, verify ledger extraction, distinct common-ID counts, failure-coded ineligibility, separate sensitivity report and indeterminate gating on synthetic attempts. Do not enable any confirmatory support decision before its freeze.
7. **Review package:** Store actual Python 3.14 interpreter/dependency versions, git commit, exact synthetic script/configuration, branch-owned development RNGs, scenario definitions, generated diagnostic tables, JUnit, hashes and failures. Reviewer signs off separately on the conditional target, assumptions, observed synthetic coverage limits, protocol conformity and timing of the post-pilot freeze.

## Current tests

`branch_b/recovery_tests/test_development_d13_interval.py` tests the 10,000-draw arithmetic, reproducibility, invalid scores and rank positions. `branch_b/recovery_tests/test_development_d13_statistical_diagnostics.py` adds exact tiny-sample support checks and failure-conditioned target illustrations. These tests are **not** a full empirical coverage study and have not been run by the author in a verified Python 3.14 environment; local Python 3.14 execution and evidence are required.

## Review / approval outcome checklist

- [ ] Statistical reviewer accepts the **conditional Monte Carlo** target as sufficient for the controlling protocol's support interval.
- [ ] Synthetic conditional-iid and assumption-violation diagnostics are inspected, with documented uncertainty on empirical coverage and no concealed failures.
- [ ] Project Lead confirms that the chosen target and calculation conform to the controlling Branch B Packet; otherwise an approved revision is required.
- [ ] D12 pilot thresholds, failure sensitivity and D14 seed derivation are frozen at their permitted gates.
- [ ] D13 method, version, environment, tests, evidence and checksum are frozen at the authorized post-pilot gate.
- [ ] No calibration, blind-validation or locked-test execution is started merely because development tests pass.

**Public shared-repository pre-write review:** The actual file describes only team-approved Branch B observable-side Q statistics, generic synthetic development diagnostics and protocol approval boundaries. It contains no hidden generator, condition mapping, true hierarchy, latent labels, sealed evaluation records, generator-owned seeds or side-channel inference. Permitted for Branch B and safe for public release.
