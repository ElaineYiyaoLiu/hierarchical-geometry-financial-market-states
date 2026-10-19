# Branch B development validation - 2026-10-19

This is a source-and-CI evidence report, not a scientific freeze, pilot acceptance, or processing authorization. Counts and environment details below were read from actual GitHub Actions job logs; no local scientific computation was performed.

## Verified revision and results

Tested commit: `0e3ce9803b15b465e47a365a293ee1118b173eb4`.

| Workflow / scope | Run | Job | Interpreter | Result |
| --- | --- | --- | --- | --- |
| Branch B Python 3.14 checks / shared validator | 39315303698 | 118275105971 | CPython 3.14.8 | 15 passed in 0.12 s |
| Same workflow / support, recovery, failure tests | 39315303698 | 118275105971 | CPython 3.14.8 | 148 passed in 0.63 s |
| validate / repository-wide pytest discovery | 39315303672 | 118275105508 | CPython 3.14.8 | 289 passed in 1.06 s |

These suites overlap; the counts must not be added as independent tests. Recorded durations are test-suite durations, not pilot throughput or full-job compute benchmarks.

- [Branch B run and logs](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39315303698)
- [Repository-wide run and logs](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39315303672)

The Branch B job explicitly asserted Python major/minor `(3, 14)`. Both inspected jobs printed Python 3.14.8. The local Python 3.14 installation attempt failed at DNS resolution; this does not affect the separately verified CI executions.

## Failures retained and corrected

The earlier [Branch B run 39314937252](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39314937252), at commit `112a3dce1aa4fd35ea06301e6bc2e2caea279204`, reported 146 passed and two failed. That result remains part of the development history.

1. The new malformed-input test incorrectly expected `INPUT_SCHEMA` for a matrix containing `None`. Its float conversion produced nonfinite values and the existing fitter returned `NONFINITE_INPUT`. Commit `fc5acdca1c6596f5a985a1a36e54cd1887013d00` corrected the test expectation, without changing the fitter or imputing missing values.
2. The empty-candidate test still matched an old error-message fragment. Commit `0e3ce9803b15b465e47a365a293ee1118b173eb4` aligned the assertion with the current nonempty-list guard. The test still requires `ConfigurationRequired` and no geometry calls.

No tests were removed, skipped, or marked expected-failure to obtain the passing result. No scientific input, threshold, selection criterion, or optimizer setting was changed by these two corrections.

## Environment and retained evidence

Both successful jobs used Ubuntu 24.04.5 and GitHub runner 2.337.0. The Branch B runner image was `ubuntu-24.04`, version `20261018.339.1`.

The Branch B job recorded:

```text
attrs==26.1.0
iniconfig==2.3.1
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
numpy==2.5.3
packaging==26.3
pluggy==1.7.0
Pygments==2.21.0
pytest==9.1.1
referencing==0.37.0
rpds-py==2026.9.1
```

The repository-wide job used pytest 8.4.2 rather than 9.1.1; its exact install log is retained with run 39315303672. It also installed NumPy 2.5.3 and jsonschema 4.26.0. The two environments must not be described as identical.

The Branch B job uploaded `branch-b-python314-test-evidence`, artifact `12215914893`, containing `branch-b-pip-freeze.txt`, `validator-junit.xml`, and `branch-b-junit.xml`.

GitHub-reported SHA-256: `912b1d64dd141095b081919ab60d8ef356c158c6f3078fef587e0649f7ad8e0a`. This digest was confirmed against artifact metadata, not independently recomputed locally. The reported expiry is 2027-01-17T19:57:45Z; copy through the approved retention process before expiry when permanent archiving is required.

The failed run retained its own evidence artifact `12217760789`, with job-reported SHA-256 `0e9e069045254a3139230d3f607fc453ecb04f03c04ac5d87466083309972d08`. It was not replaced by the corrected run.

## What is and is not established

The existing synthetic development suite now has verified Python 3.14 execution. This includes tests of the isolated min-max operator and tie-free Jacobian reference, pipeline isolation, failure handling, and tree validation.

Passing tests do not make the Common Fitter executable. Some tests intentionally confirm that its missing kernel raises `ConfigurationRequired`; others use stubs. The run is therefore not an end-to-end fitted-hierarchy golden report, a favorable-feature sanity result, pilot reproducibility evidence, or a calibration/validation result.

The current [Common-Fitter Card](draft_cards/gradient_descent_common_fitter.md) points to the [2026-10-02 source-conformance review](decision_proposals/common_fitter_source_conformance_2026-10-02.md), which explicitly leaves three decisions unapproved:

- **CF-SIGMOID:** adopt or revise the proposed soft-area sigmoid parameter 5.
- **CF-INIT:** confirm the card's input-weight initialization versus the reference software's default subdominant initialization.
- **CF-POSITIVITY:** choose and document the nonnegativity parameterization, including how it interacts with initialization.

No decision or approval is supplied by this report. Preserve the registered objective, graph, learning rate, convergence rules, and output conventions until the designated decision record authorizes a change. Correlation admissibility, valuation sanity evidence, complete method/selection freezes, and the relevant pilot and later-stage approvals remain separate requirements.
