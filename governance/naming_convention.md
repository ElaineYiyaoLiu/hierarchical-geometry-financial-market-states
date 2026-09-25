# Naming convention

Project artifacts should use stable, machine-readable names. Filenames use lowercase snake_case unless an external format requires otherwise.

Dataset and output identifiers must not encode hidden generator identity, latent hierarchy, experimental parameter values, or any other sealed information. Human-readable aliases should follow the same rule.

Versioned specifications should carry an explicit version in their contents and, where useful, in the filename. Frozen artifacts are identified by the freeze registry and checksum rather than by informal labels such as `final` or `latest`.

Temporary files, local caches, editor metadata, and machine-specific paths are not project artifacts and should not be committed.
