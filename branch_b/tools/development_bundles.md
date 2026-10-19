# Reviewed-byte development bundles

`development_bundle.py` provides deterministic packaging and independent integrity verification for small, explicitly reviewed Branch B snapshots. It is preparation for reproducible runner delivery, not the Week 6 certified `validation_runner.zip` and not a scientific processing command.

## Content boundary

Review actual contents for both Branch B permission and public disclosure before assembling the input mapping. Filenames, extensions, location in `branch_b`, and a matching digest are not evidence of permission. Do not supply bank observations, hidden information, secrets, or unreviewed artifacts.

The API accepts an explicit mapping of relative paths to immutable bytes. It does not walk directories, read local files, access the network, import packaged modules, or execute a fitter. The separately supplied reviewed digest mapping must cover exactly the same files. A changed byte invalidates the earlier content review's digest binding.

The review reference and source revision are caller assertions, not digital signatures or independently authenticated Git provenance. Verification is not a substitute for an authorized reviewer or a freeze record.

## Reproducibility contract

The project uses SHA-256 over exact bytes; see [the checksum policy](../../governance/checksum_policy.md). Each manifest records path, byte count, SHA-256, schema version, source revision, content-review reference, and actual producer Python implementation/version. Its scope is always `development_only`, with `scientific_authorization` set to false.

The ZIP container uses sorted entries, a fixed 1980-01-01 timestamp, regular non-executable file modes, and no compression. These container settings make builds reproducible without changing file contents. The fixed timestamp is not a source creation date. Equal payloads, review reference, source revision, and producer environment must produce equal ZIP bytes. Changing the Python patch version changes recorded provenance and therefore changes the archive digest.

Verification requires the expected archive SHA-256, expected source revision, and reviewed per-file digests from outside the archive. It checks all members and the manifest, rejects extra/missing/duplicate entries and unsafe path aliases, and reconstructs the canonical container. It does not extract or run members. A self-consistent replacement archive is insufficient when its bytes differ from the external review inventory.

The 512-file and 16 MiB payload bounds are operational limits for this small development utility. They are not experimental sample-size limits, failure thresholds, or a new rule for official submissions. Oversized snapshots fail rather than being silently truncated.

## Python 3.14 use

Both public operations refuse another Python major/minor version. Run the synthetic tests from the repository root:

```sh
python3.14 -m pytest branch_b/recovery_tests/test_development_bundle.py -q
```

Example using literally reviewed synthetic bytes only:

```python
from hashlib import sha256
from branch_b.tools.development_bundle import (
    build_development_bundle,
    verify_development_bundle,
)

# This literal is the entire example content; it is not an experimental input.
files = {"branch_b/example.txt": b"Synthetic development example only.\n"}
reviewed = {name: sha256(content).hexdigest() for name, content in files.items()}
dummy_revision = "1" * 40  # Explicit fixture, not real Git provenance.
archive = build_development_bundle(
    files,
    reviewed_sha256=reviewed,
    source_revision=dummy_revision,
    review_reference="literal synthetic example in development_bundles.md",
)
result = verify_development_bundle(
    archive,
    expected_sha256=sha256(archive).hexdigest(),
    reviewed_sha256=reviewed,
    expected_source_revision=dummy_revision,
)
assert result["integrity_verified"]
assert not result["scientific_authorization"]
```

For a real snapshot, record hashes only after inspecting the actual contents. Do not treat computing hashes as performing that inspection, and do not substitute a dummy revision for actual provenance.

## Remaining certification work

A future runner package needs its complete reviewed source/configuration inventory, approved method specification, applicable frozen thresholds and selection record, dependency/runtime evidence, executable tests, and the protocol's designated approvals. This utility establishes none of those scientific prerequisites. It cannot approve pilot exchange, calibration, Common-Fitter selection, independent-bank processing, locked testing, or unblinding.

The Common-Fitter decisions in the [source-conformance review](../decision_proposals/common_fitter_source_conformance_2026-10-02.md) remain pending. No optimizer setting or formal gate is modified by development packaging.
