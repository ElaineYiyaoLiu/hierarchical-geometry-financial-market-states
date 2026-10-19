# Reviewed packaging source snapshot - 2026-10-19

Scope: an actual source snapshot of the development packaging component, not a scientific runner, a method freeze, or a bank-processing authorization.

## Contents reviewed for this snapshot

The complete contents of the following files were inspected at source revision `6975d4da8baf1e1374353466fe8420183da69152`. They contain only public Branch B package declarations, standard-library packaging code, literal synthetic packaging tests, and usage documentation. They contain no experimental observations, generator implementation, hidden configuration, latent labels, true hierarchy, generator-owned seeds, credentials, or sealed evaluation information. These specific contents are permitted for Branch B and safe for public disclosure.

| File | Reviewed Git blob identifier |
| --- | --- |
| `branch_b/__init__.py` | `1500ee800b43bebc7e60fbef269204483f0adbb4` |
| `branch_b/tools/development_bundle.py` | `d2c256e0d2dd3d32275881b9475e8c704e47bc36` |
| `branch_b/tools/development_bundles.md` | `238445876bbe6bf496d6c5b96bd3585996da3c33` |
| `branch_b/recovery_tests/test_development_bundle.py` | `fc4437cc5e60af3d673f239404cc7ee8e442f183` |

The Git blob identifiers bind this review to the inspected repository objects. They are not substitutes for the project's SHA-256 checksums. The workflow calculates SHA-256 over the exact reviewed bytes under Python 3.14 and records both identifiers, byte counts, and the actual source revision in an external inventory.

A changed source revision, blob, or payload inventory needs a new content review. A filename or a matching checksum by itself is not a permission decision. This record makes no scientific approval.

## End-to-end check

The dedicated workflow `.github/workflows/branch-b-development-snapshot.yml` checks out only the four listed files at the pinned revision. It verifies the checked-out revision, each Git tree entry's regular-file mode and blob identity, and each working file against the exact Git blob bytes before loading the reviewed bundler.

Two separate Python 3.14 processes build packages with different Python hash seeds and reversed input-mapping order. A third process compares their ZIP bytes and inventories. This tests repeatability within the recorded environment; it does not establish cross-platform or cross-version equivalence. The Python hash seeds are interpreter test controls, not experimental random seeds.

The workflow retains the source ZIP, external inventory, bundle manifest, SHA-256 file, producer environment, installed-package listing, and reproducibility check. These are development artifacts. The source revision is the pinned payload revision, while the workflow revision is recorded separately. The ZIP's fixed timestamp is a container convention, not a source creation date.

The source ZIP intentionally excludes the workflow itself and this review record; their references and workflow commit identify the build procedure. It is not a self-contained environment or a full runner delivery. No dependencies are installed by this packaging check, and no fitter, experiment, or packaged test source is executed. Only the reviewed bundle builder/verifier is loaded.

## Boundaries

This snapshot does not enable the Common Fitter, resolve CF-SIGMOID, CF-INIT, or CF-POSITIVITY, or satisfy scientific runner certification. No official dataset bank is read. No scientific configuration, threshold, selection rule, frozen record, or approval is changed.

Execution results must be established from actual completed workflow logs and artifacts, not inferred from this review or the presence of a workflow file.
