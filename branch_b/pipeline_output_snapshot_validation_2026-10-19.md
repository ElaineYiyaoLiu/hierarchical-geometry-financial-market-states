# Pipeline output snapshot validation - 2026-10-19

Callback-output ownership was corrected and verified in Python 3.14 CI. This is development evidence, not a method freeze or scientific runner certificate.

## Finding and change

Input copies did not protect the pipeline from callbacks reusing their returned buffers. A preprocessor returning one work array for successive transforms could overwrite the training and validation representations with the later test transform. A fitter returning shared arrays or nested dictionaries could overwrite earlier validation candidates before selection, or earlier run/bootstrap records during later fits. A preprocessing record could also remain attached to a callback-owned dictionary.

Implementation: `1e5955468a4cfae4127099ffbabeee3a768ab16c`, [recovery_pipeline/pipeline.py](recovery_pipeline/pipeline.py).

The pipeline now immediately copies each transformed split, deep-copies each returned `FitResult` before another fit can run, and detaches the returned preprocessing record. Existing input protections remain in place. The committed diff changes ownership and lifetime only: callback order, normalization, candidate enumeration, index selection, seed passing, and result fields are unchanged.

This fix protects records from subsequent component-buffer reuse. It does not make returned arrays/dictionaries immutable, validate arbitrary callback behavior, prevent concurrent external mutation, or certify absence of every form of data leakage. Copies add memory/time overhead; these unit tests are not production capacity evidence.

## Synthetic regression coverage

Tests and tested revision: `8f224c2fcaa48ba9b915a2240421fc1f175cfb1c`, [test_pipeline_output_snapshots.py](recovery_tests/test_pipeline_output_snapshots.py).

Ten cases check reused transform arrays and views; reused outer fitter records and new wrappers over shared buffers; distinct candidate results before selection and after test fitting; stability of completed records after cache mutation, a later successful run, or a later failing run; preprocessing-record isolation; reverse isolation when a caller modifies a returned record; and preservation of earlier bootstrap results with a reused fitter.

The bootstrap case uses three synthetic attempts and Branch B implementation-test seed `20261019`. Neither is a production setting. Counter-valued fitter outputs and tree-shaped diagnostic dictionaries are stubs, not recovered scientific hierarchies. No experimental bank, hierarchy-support estimate, confidence interval, or true hierarchy is used. No tests were removed, skipped, or marked expected-failure.

## Verified executions

| Scope | Run | Job | Result |
| --- | --- | --- | --- |
| Branch B support/recovery/failure suite | 39320669279 | 118293564490 | 202 passed in 0.70 s |
| Shared validator, same Branch B job | 39320669279 | 118293564490 | 15 passed in 0.10 s |
| Repository-wide pytest discovery | 39320669222 | 118293564529 | 343 passed in 1.13 s |

Both completed jobs printed CPython 3.14.8. The Branch B job also asserted major/minor `(3, 14)`. Results and versions were read from actual completed job logs, not inferred from configuration. Suites overlap; their counts must not be added. No local scientific execution was performed.

- [Branch B run and logs](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39320669279)
- [Repository-wide run and logs](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39320669222)

Both jobs used Ubuntu 24.04.5, runner 2.337.0, and image `ubuntu-24.04` version `20261012.334.1`. The Branch B job recorded pytest 9.1.1, NumPy 2.5.3, jsonschema 4.26.0, attrs 26.1.0, iniconfig 2.3.1, jsonschema-specifications 2025.9.1, packaging 26.3, pluggy 1.7.0, Pygments 2.21.0, referencing 0.37.0, and rpds-py 2026.9.1.

The repository-wide job used pytest 8.4.2, not 9.1.1, and additionally installed cryptography 50.0.2, cffi 2.1.1, and pycparser 3.11 through the existing requirements. No dependency or workflow was changed. These are not identical environments.

## Retained evidence

Branch B artifact: `branch-b-python314-test-evidence`, ID `12219757568`, containing the dependency list and both JUnit reports. The upload log and artifact metadata agree on SHA-256:

```text
ad4b38a7242bffdde4842cadbb8a03f2f79d4e2f6d53a66c2dda0624ee973541
```

This digest is GitHub-reported, not independently recomputed locally. Reported expiry: `2027-01-17T20:36:08Z`. The previous bootstrap validation report, older success/failure evidence, and separately pinned packaging source snapshot remain unchanged. This report does not substitute the new pipeline revision into those historical artifacts.

## Remaining boundary

No scientific threshold, geometry, objective, optimizer configuration, selection criterion, bootstrap resampling rule, production seed, shared schema, or approved freeze was changed. The pending CF-SIGMOID, CF-INIT, and CF-POSITIVITY decisions remain unresolved, and the full Common Fitter remains non-executable. This correction supports Week 2-3 integration/provenance work; it does not complete scientific golden testing or authorize pilot, calibration, blind-validation, independent-bank, locked-test, or unblinding processing.
