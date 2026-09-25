# Checksum policy

SHA-256 is the project checksum for exchanged datasets, manifests, frozen specifications, and submitted result artifacts.

Checksums are computed over the exact bytes of the artifact being registered or exchanged. A change to file contents creates a new checksum and must not be represented as the same frozen artifact.

Manifests should record the artifact path, byte count, SHA-256 digest, schema or specification version, and the identifier needed to reconcile the artifact across branches. Checksums must not expose sealed scientific information through filenames or identifiers.

For a frozen artifact, the digest recorded in `freeze_registry.csv` is the reference digest used for later verification.
