# Checked integration validation - 2026-10-19

Tested code revision: `3380a9586e2ac98225531dfa1eefcf91c40bc181`.

Substantial decision-independent repairs from the [integration audit](integration_audit_2026-10-19.md) are implemented and tested. This is development evidence, not a scientific runner certificate or closure of all audit findings.

## Delivered changes

| Component | Commit | Scope |
| --- | --- | --- |
| [Structural fit and external-order validation](recovery_pipeline/result_validation.py) | `b3a92b59cb95405ed77cf1cf0878274c1c36be93` | Real numeric matrix shape/finiteness, diagnostics type, shared tree schema, structural validity, exact external sample order. No new numerical tolerances. |
| [Checked pipeline and delayed test access](recovery_pipeline/pipeline.py) | `e40848975b05d526d522f00ac31bb3a108b03ee3` | Named-fitter interface; mandatory structural checks before checked selection/return; test conversion/transform only after valid selection. |
| [Identity-bound checked bootstrap](bootstrap/checked.py) | `d49b7092663c9d4891b38734108e725c5335bde0` | External original and fit-row orders, explicit occurrence-to-original mappings, original multiplicities, checked LCA binding, every attempt through run_checked without unchecked fallback. |
| [58 synthetic cases](recovery_tests/test_checked_integration.py) | `05786ab9bc9b2e8fcc21e702932fbe2bc204c4b1` | Result rejection, identity mismatches, delayed test access, attempt preservation, unchanged draw sequence, and explicit duplicate-row conflict demonstrations. |
| [Existing staging test reconciled](recovery_tests/test_pipeline_split_integrity_regression.py) | `8e17ba0175ee4f1732f373d67e406a5416d76407` | Nonfinite test input is rejected after validation selection, before test geometry, with the same NONFINITE_INPUT failure code. |
| [Fitter readiness wording](fitters/gradient_descent.py) | `3380a9586e2ac98225531dfa1eefcf91c40bc181` | Docstring and exception now acknowledge unresolved CF decisions. Numeric settings and missing-kernel behavior are unchanged. |

The [API and migration guide](recovery_pipeline/checked_integration.md), committed separately in `ae874b2b32c70ca548a36a87240712395ae9d377`, describes the checked/unchecked distinction, caller responsibilities, schema dependency, and remaining certification work.

## What the new path establishes

`run_checked` receives validation/test sample orders independently of the fitted tree and requires `fit_with_sample_order`. It rejects an unnamed fitter rather than calling generic `fit` as a fallback. The configured and actual fitter identifiers must agree. Every checked validation result passes structural validation before the selector sees it, and every checked test result is validated before return.

Tree schema checks use the existing `interface_package/branch_b_output.schema.json` definitions unchanged, followed by the existing Branch B structural/order validator. Matrix checks require the expected dimensions, real numeric entries, and finiteness without repairing the values. The new checks do not choose symmetry, diagonal, ultrametric, or height-equivalence tolerances.

The checked bootstrap preserves the existing resampling recipe, random draw order, evaluator seeds, and attempt count. It passes repeated rows unchanged and records the explicit relationship between fit-row labels and original sample IDs. Fit-row labels name draw occurrences, not additional original observations. Both trees are bound to independent expected orders before existing LCA stability code is used.

Both RecoveryPipeline entry points now defer conversion and transformation of test values until a valid validation selection exists. The guarantee concerns calls made by that pipeline; it is not a sandbox against arbitrary external callback references or a claim that bootstrap source arrays are never read while preparing resamples.

## Actual Python 3.14 execution

| Scope | Run | Job | Result |
| --- | --- | --- | --- |
| Branch B support/recovery/failure suite | 39324459275 | 118306571712 | 260 passed in 0.73 s |
| Shared validator, same Branch B job | 39324459275 | 118306571712 | 15 passed in 0.09 s |
| Repository-wide pytest discovery | 39324459208 | 118306571466 | 401 passed in 0.77 s |

Both completed logs show checkout of the tested revision and CPython 3.14.8. The Branch B job additionally asserted major/minor `(3, 14)`. Suites overlap and counts must not be added. Durations are development test durations, not scientific runtime or capacity benchmarks.

- [Branch B run](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39324459275)
- [Repository-wide run](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39324459208)

The 58 new cases use synthetic observations, stub named fitters, and literal synthetic trees. The implementation-test seed `20261019` and four-attempt fixture are not production settings. The two duplicate-row cases use the real candidate's input validator but do not run its missing optimizer or choose a repair. No experimental bank was processed.

Local Python 3.14 installation could not complete because network name resolution failed. No local project tests or scientific computations were executed under another interpreter; the execution evidence above comes from actual repository CI.

## Failed test evidence retained

The first inspected run of the newly added suite, `39324245279` (job `118305837898`), tested revision `05786ab9bc9b2e8fcc21e702932fbe2bc204c4b1` under CPython 3.14.8 and reported **259 passed, 1 failed**; the shared validator reported 15 passed.

All new cases passed. The older test `test_nonfinite_test_input_fails_before_geometry_fitting` expected zero geometry calls, reflecting the former eager test-input preflight. Deferring test access means validation geometry and selection now precede nonfinite test rejection. The revised test is named `test_nonfinite_test_input_is_rejected_after_selection_before_test_geometry`; it checks the same NONFINITE_INPUT code, the validation geometry's actual values, the geometry/selection sequence, no test geometry call, and preservation of the nonfinite input. No test was removed, skipped, or marked expected-failure.

That failed run remains available. Its retained artifact ID is `12222210156`; upload log and artifact metadata agree on provider-reported SHA-256:

```text
c9fda5f554fbe4556620da2d964180632eb843ba4573987909c38e037af1cee5
```

Reported expiry: `2027-01-17T21:02:05Z`.

## Environment and retained passing evidence

Both successful jobs used Ubuntu 24.04.5, runner 2.337.0, and image `ubuntu-24.04` version `20261012.334.1`. The Branch B job recorded NumPy 2.5.3, pytest 9.1.1, jsonschema 4.26.0, attrs 26.1.0, iniconfig 2.3.1, jsonschema-specifications 2025.9.1, packaging 26.3, pluggy 1.7.0, Pygments 2.21.0, referencing 0.37.0, and rpds-py 2026.9.1.

Repository-wide discovery used pytest 8.4.2 rather than 9.1.1, and also installed cryptography 50.0.2, cffi 2.1.1, and pycparser 3.11 through the existing development requirements. The environments are not identical. No dependency constraints, workflows, or shared schemas were changed; the structural checker uses the existing jsonschema dependency.

Passing Branch B artifact `branch-b-python314-test-evidence`, ID `12222190480`, retains the dependency listing and both JUnit reports. The upload log and artifact metadata agree on SHA-256:

```text
30ae7dfb93f8308af38037ae66656bef3ac155624d2c71870eaff9c67fed992b
```

Reported expiry: `2027-01-17T21:03:40Z`. Both artifact digests in this report are provider-reported; they were not independently recomputed locally. Prior test evidence, failed runs, and the separately pinned four-file packaging snapshot remain unchanged.

## Audit disposition and next boundary

- **A1 remains decision-blocked.** The duplicate-row/reciprocal-weight conflict is now demonstrated by two executed regressions. Nothing was deduplicated, reweighted, jittered, floored, omitted, or replaced.
- **A2 is partially addressed.** Structural and finite-matrix validation is mandatory on the new checked paths. Generic development entry points remain generic, not certified. Full numerical consistency, support reliability, approved configuration validation, and final output/export integration are not delivered here.
- **A3 is addressed for the checked path's association contract.** Expected identities no longer come from the returned tree; reordered/missing/extra identities are rejected and multiplicities are mapped explicitly. Manifest authenticity and correct input-to-ID association remain caller/loader responsibilities. Old positional helpers must not be used alone as a scientific identity guarantee.
- **A4 is repaired at the RecoveryPipeline call boundary.** Instrumented tests verify invalid selection cannot cause test conversion or transformation; the wider arbitrary-callback isolation problem is not claimed solved.
- **A5 wording is corrected.** Frozen configuration enforcement and approved numerical conventions still need the corresponding controlling records before a production entry point is enabled.

There is still material decision-independent work in final outgoing-record/schema/provenance integration, distinct from the unresolved numerical and statistical decisions. This report therefore does not reinstate a blanket claim that autonomous engineering work is exhausted.

No scientific decision, production seed assignment, method-card value, bootstrap statistical procedure, approved freeze, or official processing gate was changed. The complete Common Fitter remains non-executable. CF-SIGMOID, CF-INIT, CF-POSITIVITY, the bootstrap weighting reconciliation, and other reserved specifications remain for explicit scientific resolution.
