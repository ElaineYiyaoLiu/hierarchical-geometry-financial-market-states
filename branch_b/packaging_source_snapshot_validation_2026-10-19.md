# Packaging source snapshot validation - 2026-10-19

The development packaging component now has a real, byte-verified source snapshot, not only literal-fixture unit tests. This report records the completed packaging check; it is not a scientific runner certificate or a method approval.

## Reviewed input and build procedure

- Payload source revision: `6975d4da8baf1e1374353466fe8420183da69152`.
- Workflow revision: `4d9736a16fd7e53367724da53f353b6207a2e3aa`.
- Content review: [four-file review and Git blob inventory](tools/packaging_source_snapshot_review_2026-10-19.md), committed in `cbb1024434dffacfaf379f7b4457b3eec35012e3`.
- Procedure: [reviewed-source snapshot workflow](../.github/workflows/branch-b-development-snapshot.yml).

The payload contains only `branch_b/__init__.py`, `branch_b/tools/development_bundle.py`, `branch_b/tools/development_bundles.md`, and `branch_b/recovery_tests/test_development_bundle.py`. Full contents were reviewed for Branch B permission and public disclosure before the workflow was committed. The job used a non-cone sparse checkout restricted to those files at the pinned revision and removed checkout credentials before building.

Before loading the reviewed bundler, each process verified the source revision, the exact Git tree entry and regular-file mode, the reviewed Git blob identifier, and the working file's equality to the blob bytes. It computed SHA-256 and byte counts over those exact reviewed bytes. Git object SHA-1 identifiers are provenance checks, not replacements for the project's SHA-256 integrity records.

## Actual result

[GitHub Actions run 39318399473](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39318399473), job `118285772101`, completed successfully. All build, comparison, and artifact-upload steps succeeded. These results were read from the completed job and full log.

The runtime printed CPython **3.14.8**, GCC 13.3.0. The runner was Ubuntu 24.04.5, runner version 2.337.0, image `ubuntu-24.04` version `20261012.334.1`. No additional Python dependencies were installed by this workflow; its recorded `pip freeze` output was empty.

Two fresh Python processes used Python hash seeds 0 and 1 and opposite input-mapping orders. Both produced the same source ZIP. A third Python 3.14 process verified both ZIPs against the externally recorded first-build archive digest and a newly checked source-file digest inventory, then compared the bytes and provenance records directly.

Verified checks:

- Four reviewed payload files; source revision and Git objects matched.
- Working bytes matched the inspected source objects.
- Both builds passed the bundle verifier without extracting or executing ZIP members.
- Both source ZIPs were byte-identical.
- Their source inventories, bundle manifests, archive-digest files, and producer records matched.
- The verification report retained `development_only` scope and `scientific_authorization: false`.

This establishes repeatability across processes within this recorded environment. It does not establish cross-platform/patch-version reproducibility, reproduce a scientific pipeline, or add to the earlier pytest test counts. No fitter or packaged test source was executed; only the reviewed bundler and explicit integrity checks ran.

## Retained artifact and checksums

Artifact: [branch-b-reviewed-packaging-snapshot](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39318399473/artifacts/12219401987), ID `12219401987`.

The artifact contains eight files: `packaging_source.zip`, `archive.sha256`, `source_inventory.json`, `bundle_manifest.json`, `producer_environment.json`, `reproducibility_report.json`, `installed-packages.txt`, and `SHA256SUMS`.

The source ZIP SHA-256, calculated and compared by the Python 3.14 job, is:

```text
941b5040d75ae59cd4a1f1a76484ce7e017b66f94d86215a20e3ecf3b23b3d8f
```

The outer GitHub artifact ZIP has a different SHA-256, reported by the upload step and confirmed against the artifact metadata:

```text
90f33e8fd36c9c8dfa3e085974371b5d50b0fd92e492ec087adb828aa419a39a
```

The inner source ZIP and the outer artifact envelope are different byte streams. The outer artifact digest has not been independently recomputed locally. The provider reports expiry at `2027-01-17T20:19:51Z`.

Other job-calculated SHA-256 values:

```text
abd1cbf9d7ac7033dae09ffbb4195234931c76ba6e65cfd055bde523a11f0efe  bundle_manifest.json
232240d984460ba887ee3638a5984594f835104d0186bb32f102d4feb404f8d6  source_inventory.json
ed37dd1995a6e37270d5983484bc4466356f50d704994fef198aed971e504d22  reproducibility_report.json
8b04ae0420fc3bbff503d1503da5c03d8e794fc561fea0269996288911717d11  producer_environment.json
```

The payload source revision and build-workflow revision are deliberately recorded separately. This source snapshot excludes the workflow and review document themselves; the pinned review reference and workflow commit identify them. It is not a complete source tree, dependency environment, or self-contained scientific runner.

## Remaining boundary

This closes an engineering step in development packaging and provenance. It does not resolve CF-SIGMOID, CF-INIT, CF-POSITIVITY, correlation admissibility, valuation sanity, or method/selection freezes. It does not modify the scientific code or enable the Common Fitter. No official pilot, calibration, blind validation, independent-bank processing, locked testing, or unblinding was performed.

The prior [bundle unit-test evidence](development_bundle_validation_2026-10-19.md) and [development-test history](development_validation_2026-10-19.md) remain unchanged. This report supplements them and makes no scientific completion or approval claim.
