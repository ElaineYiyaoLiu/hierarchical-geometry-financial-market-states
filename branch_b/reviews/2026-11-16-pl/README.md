# Independent PL Development Verification

Review date: November 15, 2026, America/New_York. Evidence directory date: November 16, UTC.

Source commit: `74954ae5126e5967e700234a8ccd8d5379a8e9f6`.

## Observed Results

- Actual CPython 3.14.10, NumPy 2.5.5, pytest 8.4.2. Exact dependencies are in `pip-freeze.txt`.
- Full repository regression: **833 passed, 0 failures, 0 errors, 0 skipped**, 3.81 seconds, original JUnit and output retained. The tested scientific source was unmodified.
- Existing expanded design: **2,400/2,400 trials completed**, with unchanged source, 10,000 secondary resamples, seed derivation, scenarios and sample sizes.
- Existing sensitivity design: **600/600 trials completed**, with unchanged source and design.
- Both original evidence audits: **AUDIT_PASSED**.
- Separate recount: **INDEPENDENT_RECOUNT_PASSED**, recomputing coverage flags from endpoints/analytic targets and counting all synthetic attempt statuses.
- Original remote CI job 133002174311 for the same commit was inspected. It used Python 3.14.10, NumPy 2.5.3 and pytest 9.1.1, with **27 reference, 15 validator and 688 Branch B subset tests passed**. These overlapping/subset runs are not the local 833-test total.

| Synthetic score distribution | n=24 covered / 400 | n=100 covered / 400 |
| --- | ---: | ---: |
| Symmetric uniform | 374 (93.5%) | 386 (96.5%) |
| Two point | 384 (96.0%) | 383 (95.75%) |
| Skewed beta | 368 (92.0%) | 380 (95.0%) |

The skewed n=24 Wilson 95% coverage interval is approximately 88.92%-94.28%. Preserve the undercoverage finding. One two-point n=24 interval had zero width; zero-width intervals are not automatically invalid or evidence of reliability.

| Sensitivity scenario | Specified-target coverage | Failed attempts / 12,000 | Interpretation |
| --- | ---: | ---: | --- |
| Independent failure | 185/200 (92.5%) | 5,976 | Conditional-success and all-potential-score targets both zero |
| Score-dependent failure | 190/200 (95.0%) | 5,985 | Successful-score target 1/3; distinct zero target covered 9/200 |
| Shared random shift | 41/200 (20.5%) | 0 | Zero target integrates over the shared shift; this is not conditional-on-fixed-shift coverage |

All reported coverage and failure counts above reproduce the earlier handoff's aggregate counts. This validates these new runs and their arithmetic. The original team's workstation journals, JUnit, exact environment and retry history were unavailable and have not been authenticated. The rerun environment is recorded as observed, not relabeled to match theirs or CI.

## Reproduction

Check out the exact reviewed commit. Use actual Python 3.14 and the exact package versions in `pip-freeze.txt`. The following commands were executed from the repository root; substitute a fresh evidence directory for a genuinely new run:

```bash
python -m pytest -q --junitxml=branch_b/reviews/2026-11-16-pl/full-junit.xml
python -m branch_b.tools.d13_expanded_synthetic_coverage --output-dir branch_b/reviews/2026-11-16-pl/expanded
python -m branch_b.tools.d13_synthetic_sensitivity --output-dir branch_b/reviews/2026-11-16-pl/sensitivity --max-new-trials 600
python -m branch_b.tools.d13_evidence_audit --expanded-dir branch_b/reviews/2026-11-16-pl/expanded --sensitivity-dir branch_b/reviews/2026-11-16-pl/sensitivity
python branch_b/reviews/2026-11-16-pl/recount.py
```

The two original runner commands were launched once each in separate processes. There were no changed study seeds, modified interval code, trial retries, discarded records, incomplete cells or observed run failures. The complete append-only journals, designs and summaries are included. There was one full-regression run. The only added Python file, `recount.py`, is a read-only evidence utility outside the scientific implementation; its successful execution is recorded separately and is not added to the historical 833-test claim.

`source-sha256.json` fingerprints tracked Python source, workflow/configuration and requirement files used by the reviewed checkout. `environment.json` records the interpreter, dependency versions, source commit, working-tree observation and platform. `checksums.json` fingerprints the final review bundle contents except itself. Hashes establish exact bytes, not statistical acceptance.

## Scope of the Completed Review

The linked [PL disposition](../../decision_proposals/d12_d14_pl_disposition_2026-11-15.md) answers each requested item and separates protocol meaning, mathematical derivation, executed evidence and decisions reserved to a specified gate. No scientific source, frozen parameter, seed rule, schema or evaluation definition changed. Freeze and approval registers remain unchanged. Production Common-Fitter activation, pilot exchange, calibration, locked testing and unblinding remain outside this review.

The synthetic score runners do not use a production Common Fitter. Passing these tests and reproducing the toy studies does not resolve D04 feasibility or certify the final D06/bootstrap integration.

Public disclosure review: the included files contain generic Branch B synthetic scores, public-side source identities, execution metadata and review conclusions only. Original packet PDFs, attachments, unrelated workspace content, protected sources and private credentials are excluded.
