# Branch B decision-independent work queue — 2026-10-20

Status: implementation inventory and next-work plan, **not** a scientific freeze, golden report, approval, or completion certificate.

The controlling Branch B Packet governs methods and data roles. The Schedule determines deliverables, order and gates. Only observable and explicitly permitted Branch B materials may be used.

## Week 1 — setup deliverables

Schedule names: `geometry_registry.md`, `draft_cards/`, `branch_b_environment.txt`, `seed_namespace_b.yaml`, `schema_report_b.json`, `branch_b/README.md`.

Decision-independent work: verify that each file exists, refers to the controlling protocol and permitted seed namespace, contains no restricted data, and is internally consistent. Reconcile environment records with **actual** Python 3.14 execution. Do not assert a missing file is complete merely because related code exists.

Open gate: registration and environment evidence must be verified against the actual current files; no new geometry or fitter is silently registered.

## Week 2 — implementation deliverables

Schedule names: `preprocessing/`, `geometries/`, `fitters/`, `normalization/`, `recovery_pipeline/`, `bootstrap/`, `support_tests/`, `recovery_tests/`, `failure_tests/`.

Confirmed source inspection:
- `branch_b/recovery_pipeline/pipeline.py`: checked train-to-validation-selection-to-test orchestration; callback-supplied selection remains scientifically unspecified.
- `branch_b/fitters/gradient_descent.py`: non-executable fitter candidate; `fit()` intentionally raises `ConfigurationRequired`.
- `branch_b/bootstrap/engine.py`: deterministic resampling and failed-attempt retention.
- `branch_b/bootstrap/checked.py`: explicit original-identity bindings and checked pipeline integration.
- `branch_b/bootstrap/pipeline.py`: original-index multiplicity and projected LCA relations; now rejects lossy noninteger indices.
- `branch_b/support/stability.py`: average-tied ranks and Spearman comparison; undefined constant-rank handling still needs F4 failure-code reconciliation.
- `branch_b/serialization/tree.py`: checks canonical leaves and internal-node structure.
- `branch_b/recovery_pipeline/result_validation.py`: rejects masked/Boolean fitted matrices and nonfinite/non-JSON diagnostics before selection.
- `branch_b/recovery_tests/test_checked_integration.py`: synthetic regression fixtures, including seed-36/B-500 engineering rehearsal and original-index integrity.

**Not delivered**: executable approved Common Fitter, mathematical tied-gradient implementation, multiplicity-aware reciprocal-weight objective, fully specified validation selector. Do not describe this week as integration-ready.

Decision-independent next work: inspect every existing implementation module against protocol and schema; strengthen type/identity/serialization/failure tests; run and archive actual Python 3.14 CI evidence. Never replace unresolved numerical conventions with convenient defaults.

## Week 3 — pre-pilot deliverables

Schedule names: `recovery_golden_report.json`, `geometry_cards/`, `common_fitter_cards/`, `common_fitter_selection_rule.yaml`, `pilot_processing.yaml`, `bootstrap_dryrun_report.json`.

Decision-independent next work: prepare golden-case **harness and report schema** using only approved golden cases; inventory candidate-card fields and explicitly mark unresolved scientific parameters; prepare dry-run failure-accounting and provenance checks using synthetic fixtures. Do not fabricate reports or label unexecuted golden tests as passed.

Blocked: executable fitter, valuation sanity specification, geometry-neutral selector, pilot-specific precision/resource and freeze details.

## Weeks 4–6 — dependent deliverables

Week 4: `pilot_outputs/`, `pilot_output_manifest.json`, `pilot_failures.csv`, `compute_benchmark.csv`, `pilot_runtime_summary.pdf`. Require frozen pilot pipeline, authorized pilot exchange, permitted observable bank, and actual measured execution.

Week 5: `calibration_outputs/`, `calibration_output_manifest.json`, `threshold_registry.yaml`, `threshold_calculation_report.pdf`, `calibration_failures.csv`, `final_cards/`. Require approved Gate 5A and official calibration bank. Training-observable tuning is not a substitute for official calibration or permission to alter frozen rules.

Week 6: `blind_validation_outputs/`, `common_fitter_selection_report.pdf`, `selected_common_fitter.yaml`, `activated_thresholds.yaml`, `validation_runner.zip`, `validation_golden_report.json`. Require approved frozen rule and permitted blind-validation bank. Independent-bank scientific outputs remain unavailable until their gates.

## Scientific choices reserved for approval

- D04: limiting-gradient averaging over tied bottlenecks.
- D06: objective on original-ID multiplicities, including mass-aware soft cardinality and zero-edge treatment.
- D09: favorable-feature recovery-number criterion.
- D10: minimum-effect historical freeze chronology.
- D11: exact geometry-neutral selection statistic and tie/failure/missingness rules.
- D02/D07/D14: training-observable-only calibration *procedures* and their allowed freeze windows.
- D12–D15: operational reliability, intervals, thresholds and resources at the prescribed freeze points.
- F4: undefined Spearman must count as unsuccessful without incorrectly declaring a structurally valid tree invalid.

## Verification and provenance

Recent commits add lossless bootstrap identity guards and synthetic tests, but they are **not yet verified by an observed Python 3.14 test run**. The local runtime has Python 3.13 only. A Python 3.14 installation attempt failed due unavailable DNS/network; no Python 3.13 scientific execution was substituted. GitHub Actions workflows request Python 3.14, but current tool access did not expose new job evidence.

No pilot/calibration/blind-validation/locked-test data were opened, generated, processed, or written. No hidden generating information, sealed truth, generator seeds or restricted side channels were used. The work queue itself is safe to disclose publicly and does not alter any freeze.

## Subsequent engineering continuation — 2026-10-20

A new `branch_b/golden/readiness.py` inventory validator now enumerates the nine Week 3 golden-test domains and requires explicit Python 3.14 execution-version and SHA-256 evidence for any case claimed as passed or failed. Pending and blocked cases cannot claim execution evidence. Its returned `scientific_golden_certified` and `pilot_authorization` fields are always false: even a fully populated synthetic inventory is **not** the required `recovery_golden_report.json`.

`branch_b/recovery_tests/test_golden_readiness.py` provides synthetic positive and negative evidence checks. These tests were committed but not executed under Python 3.14 in this continuation. The approved golden cases, mathematical expectations, tolerances, and required cross-component coverage remain external to this inventory and must not be fabricated.

Bootstrap input and attempt-accounting modules were further strengthened to reject lossy indices, reject invalid sizes/seeds, preserve evaluator-independent draws, and report missing/duplicate attempt provenance. These are engineering checks, not decisions on D06 weighting, bootstrap reliability or confidence-interval coverage.

## Further Week 2 input-integrity work — 2026-10-20

`branch_b/fitters/gradient_descent.py` now rejects masked, Boolean, complex, text and object-valued matrices before coercing input to floating point. This is an input-schema safeguard, **not** a change to the registered numerical method or an executable fitter. Synthetic tests are in `branch_b/recovery_tests/test_fitter_input_integrity.py`.

The Week 3 golden readiness inventory checks *declared* Python 3.14 and SHA-256 metadata syntax; it does **not** read the referenced evidence or verify which interpreter actually executed a case. This limitation is explicit in its documentation. Current GitHub commit-status queries returned no attached statuses and the accessible commit-workflow query returned no PR-triggered runs for the new test commit. Therefore no new Python 3.14 test pass or golden certification is claimed.

## Additional decision-independent input guards — 2026-10-20

- `bootstrap_split_indices` now rejects Boolean, fractional, nonpositive and noninteger split sizes, and requires an explicit NumPy Generator. This closes the direct-call gap not covered by the higher-level bootstrap engine's argument validation.
- `GradientDescentUltrametricFitter` now requires strictly positive integer convergence-patience and maximum-iteration settings; Boolean or fractional values no longer pass the configuration gate. The numerical defaults themselves were not changed.
- New synthetic regression tests cover both guards in `support_tests/test_bootstrap_attempt_audit.py` and `recovery_tests/test_fitter_input_integrity.py`.

All updates are engineering checks only. No new Python 3.14 execution evidence was obtained, and none of these changes completes the scientific Common Fitter or the Week 3 golden report.

## Audit remediation: input boundaries and checked failure propagation — 2026-10-20

- Observable preprocessing now validates original matrix types before conversion. Common normalization reuses the same real-numeric input check without altering the frozen max-offdiagonal formula.
- The legacy `run_recovery_pipeline_bootstrap` remains available for development compatibility, but is explicitly marked unchecked and cannot certify sample identity. Its input matrices now use the same observable validation as the checked route.
- Synthetic tests in `recovery_tests/test_matrix_boundary_integrity.py` cover malformed observable, geometry, and bootstrap inputs, unchanged normalization, and copy isolation.
- Additional checked-pipeline tests verify that malformed geometry output is rejected before the fitter or validation selector, and that bootstrap failures retain their attempt records and draw indices.

No production runner was certified, no scientific threshold was changed, and Python 3.14 execution evidence is still required. Remaining audit items include numerical fit conformance, the failure-code registry reconciliation for undefined Spearman, and the executable Common Fitter.
