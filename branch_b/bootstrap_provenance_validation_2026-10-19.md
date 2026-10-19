# Bootstrap provenance validation - 2026-10-19

An internal provenance correction and its synthetic regression checks are complete. This report is development evidence, not a bootstrap-method freeze, scientific golden report, or bank-processing authorization.

## Finding and correction

The existing [Branch B seed policy](seed_namespace_b.yaml) requires all stochastic steps to be recorded. The bootstrap engine already generated a separate evaluator seed for each attempt, but only passed it to the callback. `BootstrapReplicate` did not retain it. A callback that failed, or returned a result without a seed, therefore left no evaluator seed in that returned record. The engine also exposed its stored sampling-index arrays directly to callback mutation.

Implementation commit: `9adca3e58d40f1f99590450191c2febdc7848ee7`, [bootstrap/engine.py](bootstrap/engine.py).

- Every engine-produced record now contains the exact `replicate_seed` supplied to the evaluator, on success or failure.
- The evaluator receives copies of the sampling-index arrays. The record retains the original draw even when the callback changes its arguments before failing or retains those arguments after returning.
- The existing seed derivation, random-number draw order, split resampling, attempted-replicate ordering, exception capture, and failure classifications are unchanged. No retry or replacement was added.

The new field is internal metadata, not an edit to the shared result schema. Its default is `None` for older manually constructed records. `None` means unrecorded; this change does not invent or backfill historical seeds. Code serializing the whole dataclass must account for the extra internal field rather than adding it silently to a frozen exchange schema.

The returned arrays remain ordinary arrays, not an immutable audit archive. Callers must still preserve their records appropriately. Replaying a real evaluation additionally requires the original observable inputs, configuration, source revision, dependency environment, and any applicable authorization. Possessing a seed does not authorize a rerun.

## Regression coverage

Test commit and tested revision: `fa70b9a70cdc196ad000505f2a1b058676e34a13`.

The 11 cases in [test_bootstrap_record_provenance.py](recovery_tests/test_bootstrap_record_provenance.py) check:

- Seed retention for successful values, successful `None` returns, structured failures, and unexpected failures.
- Preservation of original draws against mutation before both successful and failing returns, including later mutation through retained callback references.
- Exact agreement with the pre-change random draw recipe for two Branch B development seeds in the tested environment.
- Manual replay of synthetic randomness from a failed record, while verifying the engine itself attempts each replicate only once.
- Compatibility of older positional record construction, with a clearly unrecorded seed.
- Propagation of the recorded seed and original draws through the recovery-pipeline bootstrap adapter on success and failure.

All data and evaluators are synthetic. The adapter test uses a recording stub, not a scientific fitter. No experimental bank, true hierarchy, confidence-interval calculation, or production seed is used. No tests were removed, skipped, or marked expected-failure to obtain the results below.

## Verified Python 3.14 execution

| Scope | Run | Job | Result |
| --- | --- | --- | --- |
| Branch B support/recovery/failure suite | 39319562457 | 118289779232 | 192 passed in 0.44 s |
| Shared validator, same Branch B workflow | 39319562457 | 118289779232 | 15 passed in 0.07 s |
| Repository-wide pytest discovery | 39319562474 | 118289779691 | 333 passed in 1.12 s |

Both completed jobs printed CPython 3.14.8. The Branch B job also asserted major/minor `(3, 14)`. Counts were read from the actual job logs. The suites overlap; do not sum them as independent tests. Suite durations are not pilot throughput or capacity evidence.

- [Branch B run](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39319562457)
- [Repository-wide run](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39319562474)

Both jobs used Ubuntu 24.04.5, runner 2.337.0, image `ubuntu-24.04` version `20261012.334.1`. The Branch B job recorded pytest 9.1.1, NumPy 2.5.3, jsonschema 4.26.0, attrs 26.1.0, iniconfig 2.3.1, jsonschema-specifications 2025.9.1, packaging 26.3, pluggy 1.7.0, Pygments 2.21.0, referencing 0.37.0, and rpds-py 2026.9.1.

The repository-wide job used pytest 8.4.2, not 9.1.1, and installed cryptography 50.0.2, cffi 2.1.1, and pycparser 3.11 through the existing requirements. No dependency or workflow was changed for this correction. The two test environments must not be described as identical.

Retained Branch B artifact: `branch-b-python314-test-evidence`, ID `12219348665`, containing the dependency listing and both JUnit reports. The upload log and artifact metadata agree on SHA-256:

```text
cbbcec26c63c212135b3c78ba124b27e7fc11b9ca4648b17c45f6d177b738488
```

The digest is GitHub-reported, not independently recomputed locally. The reported artifact expiry is `2027-01-17T20:28:13Z`. Earlier validation evidence and the separately pinned packaging snapshot remain unchanged.

## Scope and remaining boundary

This addresses part of the Week 2-3 bootstrap failure-accounting and reproducibility work. It does not complete full-pipeline scientific golden testing or runner certification. Exact-stream regression results apply to these development fixtures and the recorded environment; arbitrary callback determinism and cross-version reproducibility are not established.

No bootstrap count, successful-replicate threshold, interval method, scientific failure policy, production seed namespace, geometry, fitter objective, optimizer setting, or selection rule was chosen or changed. No shared schema or approved freeze record was edited. CF-SIGMOID, CF-INIT, CF-POSITIVITY and the other pending scientific decisions remain untouched; the Common Fitter remains non-executable. No official pilot, calibration, blind-validation, independent-bank, locked-test, or unblinding processing was performed.
