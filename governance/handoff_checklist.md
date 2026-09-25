# Handoff checklist

Use this checklist before a dataset or result package moves between branches.

## Before release

- Confirm the artifact matches the current schema version.
- Run the shared validator and record any failure before handoff.
- Check that filenames, identifiers, ordering, metadata, and packaging do not reveal restricted information.
- Generate the manifest and SHA-256 checksums from the exact files being released.
- Confirm that the release is allowed under the current data tier.

## On receipt

- Verify the manifest and checksums before analysis.
- Run the shared validator without modifying the received files.
- Record receipt and validation problems before processing begins.

## Before a freeze

- Record the frozen artifact, version, checksum, owner, approval, and UTC timestamp in `freeze_registry.csv`.
- Keep failed scheduled runs in the record rather than silently replacing them.
- Do not release sealed truth until the required Branch B outputs and failures have been submitted and frozen.
