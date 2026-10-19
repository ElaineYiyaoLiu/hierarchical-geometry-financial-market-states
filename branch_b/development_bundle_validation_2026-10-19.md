# Development bundle validation - 2026-10-19

Development packaging and integrity verification are implemented and tested. This is not the Week 6 scientific runner certificate, a protocol freeze, or an authorization to process a bank.

## Delivered components

- [Bundle builder/verifier](tools/development_bundle.py), added in `9aa842600975bed13f83bd8b158bf87b29afeca8`.
- [Synthetic tests](recovery_tests/test_development_bundle.py), added in `2cd45803de10f72e6f1c4443be068dc9750f3ca6`.
- [Usage and scope](tools/development_bundles.md), added in `6975d4da8baf1e1374353466fe8420183da69152`.

The implementation creates canonical uncompressed ZIP archives from an explicit mapping of reviewed bytes. It verifies against externally supplied archive and per-file SHA-256 digests, records exact byte counts and source-revision assertions, and rejects changed or mismatched inventories. It neither scans directories nor imports, extracts, or executes the packaged files. Actual content review remains mandatory; hashes and paths do not establish permission.

Every package is marked development-only and cannot declare scientific authorization. Both public operations require Python 3.14. The operational size limits and fixed ZIP timestamp are documented packaging choices, not scientific thresholds or source creation dates.

## Verified execution

Tested revision: `6975d4da8baf1e1374353466fe8420183da69152`.

| Scope | Run | Job | Result |
| --- | --- | --- | --- |
| Branch B support/recovery/failure suite | 39316786831 | 118280221409 | 181 passed in 0.63 s |
| Shared validator, same Branch B workflow | 39316786831 | 118280221409 | 15 passed in 0.11 s |
| Repository-wide pytest discovery | 39316786867 | 118280221055 | 322 passed in 0.64 s |

Both jobs printed CPython 3.14.8; the Branch B job also asserted major/minor `(3, 14)`. Results were read from actual job logs, not inferred from workflow configuration. Suites overlap: do not sum these counts as independent tests. Durations are test-suite durations, not pilot throughput or capacity evidence.

The 33 new packaging cases cover reproducible byte output, manifest round trips, externally bound file digests and source revisions, changed bytes, path aliases, case and file/directory collisions, missing/extra/duplicate members, altered manifests, noncanonical containers, runtime guards, and operational size limits. All use literal synthetic bytes and an explicitly synthetic revision. No experimental bank was loaded.

- [Branch B run](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39316786831)
- [Repository-wide run](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39316786867)

## Environment and evidence retention

Both inspected jobs used Ubuntu 24.04.5, runner 2.337.0, and runner image `ubuntu-24.04` version `20261012.334.1`.

The Branch B job used pytest 9.1.1, NumPy 2.5.3, jsonschema 4.26.0, attrs 26.1.0, iniconfig 2.3.1, jsonschema-specifications 2025.9.1, packaging 26.3, pluggy 1.7.0, Pygments 2.21.0, referencing 0.37.0, and rpds-py 2026.9.1. No dependency was added for the bundle utility: it uses the Python standard library.

The repository-wide job used pytest 8.4.2 rather than 9.1.1. It also installed cryptography 50.0.2, cffi 2.1.1, and pycparser 3.11 through the existing development requirements. The two test environments must not be described as identical.

Retained Branch B artifact: `branch-b-python314-test-evidence`, ID `12218950603`. It contains the dependency listing and both JUnit reports. GitHub-reported SHA-256, confirmed against artifact metadata:

`4c20e2bf7c268f50e667e5b0e27569df4fb783561b50076bf2a508168d9dcea5`

The reported expiry is 2027-01-17T20:08:17Z. The digest was read from GitHub, not independently recalculated locally. Earlier passing and failed evidence described in [the previous validation report](development_validation_2026-10-19.md) remains part of the history; this report does not replace it.

## Scientific boundary

This completes an engineering component for reproducible development snapshots. It does not deliver a full source/configuration runner inventory, reproduce a dependency installation, validate a fitted hierarchy, or issue `validation_golden_report.json` as a scientific certificate.

CF-SIGMOID, CF-INIT, and CF-POSITIVITY remain pending in the [Common-Fitter source-conformance record](decision_proposals/common_fitter_source_conformance_2026-10-02.md). The optimizer has not been enabled. Correlation admissibility, valuation sanity, complete method/selection freezes, bank receipts, and designated approvals remain separate prerequisites. No official pilot, calibration, blind-validation, independent-bank, locked-test, or unblinding gate was advanced by this work.
