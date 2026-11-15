# D13 synthetic statistical review handoff — November 15, 2026

**Status:** Branch B development evidence and interpretation for statistical / Project Lead review, **not** a scientific freeze, coverage certification, approval of D12 numerical thresholds, or authorization for calibration or locked-test processing.

## Candidate under assessment

The Branch B team selected conditional Monte Carlo uncertainty in the mean successful-bootstrap Q score. The candidate calculation is unchanged: `Q_b = S_b - min(D_b, 1)`; mean over successful primary attempts; exactly 10,000 secondary with-replacement resamples of successful scores, each of size `B_success`; nominal two-sided 95% nearest-rank endpoints 250 and 9750 (one-based). The complete primary attempt/failure ledger is separate, and D12 reliability/failure-sensitivity checks still require authorization and numerical freeze.

## User-reported Python 3.14 development evidence

- Earlier focused D13 suite: **25 passed**; full regression suite: **814 passed**.
- Expanded independent-score synthetic study (`d13-expanded-synthetic-2026-11-15-v1`, development seed 314159): **2,400/2,400 complete** across 400 outer trials in each of three synthetic distributions at sample sizes 24 and 100. User-provided summary gives:
  - Uniform: 374/400 (93.5%) at n=24; 386/400 (96.5%) at n=100.
  - Two-point: 384/400 (96.0%) at n=24; 383/400 (95.75%) at n=100.
  - Skewed beta: 368/400 (92.0%) at n=24, Wilson 95% interval 88.92%–94.28%; 380/400 (95.0%) at n=100.
  - The n=24 skewed-beta result suggests finite-sample undercoverage; preserve it explicitly. These Monte Carlo observations do not certify a nominal coverage guarantee. The two-point pilot at 48 outer trials had lower observed coverage, but the larger prespecified run did not reproduce that pattern.
- Separate synthetic sensitivity study (`d13-synthetic-sensitivity-2026-11-15-v1`, development seed 271828): **600/600 outer trials complete**, 200 per scenario, each with 60 attempted draws. User reports the full regression suite **825 passed in 8.88 seconds**. Source JUnit / exact environment / journal integrity have **not** been independently inspected.

## Sensitivity observations (user-provided completed aggregate summary)

| Synthetic scenario | Calculable intervals | Failed attempts / 12,000 | Coverage of specified study target | Wilson 95% interval | Distinct interpretation |
| --- | ---: | ---: | ---: | --- | --- |
| Independent failure | 200/200 | 5,976 | 185/200 = 92.5% | 88.00%–95.40% | Target is 0 both among successes and all potential scores |
| Score-dependent failure | 200/200 | 5,985 | 190/200 = 95.0% | 91.04%–97.26% | Targets success-conditional mean `1/3`; coverage for distinct all-attempt mean 0 was 9/200 (4.5%) |
| Shared random shift | 200/200 | 0 | 41/200 = 20.5% | 15.49%–26.63% | **Target tested is the mean after integrating out a shared shift, 0**, not a fixed-shift conditional mean |

In the score-dependent toy model, `Q~Uniform(-1,1)` and `P(success|Q=q)=(q+1)/2`; thus `E[Q|success]=1/3` while `E[Q]=0`. The very low coverage of zero is **expected target separation**, not a failure of the intended success-conditioned interval. Neither the example's ~50% failure rate nor the sample-size choices establish D12 reliability eligibility.

The shared-shift model deliberately introduces a random offset common to all primary scores within each outer trial. The 20.5% figure is coverage of a **marginal across-shift mean of zero**; it **cannot** be used to claim 20.5% coverage of the target conditional on a fixed shared shift. Under conditioning on that shift, the expected mean changes to the shift. The experiment is a warning about mixing conditioning levels, not a direct falsification of the approved fixed-data conditional Monte Carlo estimand.

## Latest local Python 3.14 validation report

**User report (November 15, 2026):** After running the new read-only `d13_evidence_audit.py` checks and latest full regression command, the team reports **all passing**. This is a team-reported execution outcome, not a claim that the reviewer has directly inspected the original `local-d13-evidence-audit.json`, latest JUnit XML, interpreter/dependency provenance, source hashes, or run-specific failure logs. The previously reported expanded and sensitivity study numerical summaries, including skewed-small-sample undercoverage, remain unchanged.

**Next reproducibility gate:** retain the original two evidence directories and the separately generated audit JSON and JUnit locally. Before certification, verify that both audits explicitly report `AUDIT_PASSED` with the expected 2,400/600 records, inspect original run provenance and hashes, and link approved evidence without indiscriminately copying machine-local artifacts to the public repository. This status is not statistical acceptance, project-level authorization, a pilot exit, or a post-pilot freeze.

## Statistical reviewer questions

1. Does the controlling protocol's intended interval target coincide with finite-primary-attempt Monte Carlo uncertainty for `E[Q|success, fixed original data and reference procedure]`? Confirm that the team-selected target is sufficient.
2. Are primary attempts conditionally iid/exchangeable given the actual frozen original-data/reference/seed protocol, notwithstanding selection on success? Distinguish shared fixed conditioning from newly random, adaptive, or across-attempt shared state.
3. Is the observed 92% skewed-small-sample coverage and known finite-sample percentile-bootstrap limitation acceptable for a nominal 95% interval? No change to method or D12 minimum-success threshold is authorized by these simulation findings.
4. Does the failed-fit sensitivity treatment required by the controlling protocol need additional paired summaries, and which D12 integration/failure-code semantics need pilot approval?
5. Is independent reproducibility evidence sufficient? Confirm actual interpreter/dependencies, committed source hashes, original `design.json`, full attempt journals, complete failures, JUnit, and any reproduction before signing off.
6. If the target or method is insufficient, request an **authorized explicit revision**. Do not select more favorable synthetic cases, retune endpoints, declare a new threshold, or silently modify a frozen choice.

## Next gates

Maintain all existing D13 arithmetic and team-approved settings without alteration. A statistical reviewer should explicitly accept/reject the conditional target and characterize the finite-sample coverage limitation. The Project Lead then verifies protocol compatibility, D12/D14 operational/failure constraints and the authorized post-pilot freeze. The production Common Fitter remains fail-closed; no confirmatory or locked-test execution is approved here.

**Actual-content public-repository pre-write check:** This note contains only Branch B-permitted, user-supplied aggregate **synthetic** development results and public-side algorithm/approval review requirements. It includes no hidden generating methods, generator-owned seeds, latent labels, true hierarchy, sealed evaluation information, hidden experimental conditions, raw sensitive data or side-channel inferences. It is safe for public disclosure.
