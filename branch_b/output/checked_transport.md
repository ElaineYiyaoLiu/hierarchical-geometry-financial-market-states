# Checked development input and output transport

These APIs connect explicit observable bytes, canonical sample identities, checked pipeline results, and verifiable output bytes. They do not run a scientific experiment, certify a method, publish files, or authorize access to a bank. Use Python 3.14; the execution evidence is in [the validation report](../output_transport_validation_2026-10-19.md).

## Input binding

`branch_b.observable_input.load_development_observable` accepts CSV and observable-manifest bytes, independently supplied SHA-256 checksums for both, and the expected dataset identifier, split, and schema version. It checks the existing observable schema, exact feature header and dimensions, file checksum, sample-order checksum, unique nonempty sample identifiers, and finite numeric feature values.

The loader preserves row and feature order. It does not sort, deduplicate, standardize, repair missing values, or decide correlation admissibility. The sample-order checksum uses the existing shared validator's JSON encoding recipe. Manifest fields and paths are not followed to fetch other files. Only the installed shared schema is opened.

The returned `LoadedDevelopmentObservable` has a detached read-only value array, an immutable sample-order tuple, the original manifest bytes, and input/schema digests. `manifest_record()` returns a new dictionary. Read-only arrays prevent accidental edits, not deliberate mutation; keep identifiers attached to their corresponding values when making working copies.

Trusted expected hashes and identities must come from the permitted handoff process. Computing a hash from an untrusted artifact and treating that same hash as external evidence does not authenticate it. A valid manifest is not release authorization.

## From checked pipeline results to exchange-shaped records

Continue to use `RecoveryPipeline.run_checked` and independent sample orders as described in [checked integration](../recovery_pipeline/checked_integration.md). The loader's sample order can supply those identities. The pipeline still requires an identity-aware fitter; it does not fall back to an unnamed fitter.

`complete_record_from_checked_pipeline` adapts a full-test checked result into the unchanged shared output shape. The caller supplies:

- The five expected identifiers: `dataset_id`, `split`, `geometry_id`, `common_fitter_id`, and `schema_version`.
- The canonical sample order and expected configuration-file reference.
- The actual fitter parameter record, hierarchy-support object, and bootstrap stability value.
- A context with exactly `runtime_seconds`, `peak_memory_bytes`, `software_environment`, `random_seeds`, `configuration_file`, and `creation_timestamp`.

The adapter copies geometry parameters, preprocessing, diagnostics, matrices, and tree from the checked result. It validates before converting numeric matrix arrays into JSON lists. It snapshots mutable records. It neither computes support nor fills absent support with a placeholder. The test suite's literal scores, decisions, timestamps, environment descriptions, and source identifiers are explicitly synthetic fixtures.

The full-test adapter rejects individual bootstrap-attempt records rather than presenting one attempt as the final dataset's support analysis. Internal candidate records and bootstrap logs are not silently inserted into the shared schema. Preserve those separately; this adapter is not a complete run archive.

`failure_record_for_development` requires an explicit failure code, parameter record, diagnostics, and the same provenance context. It preserves them without assigning a support decision. This development transport deliberately rejects failure records carrying support/stability fields rather than silently dropping those fields. It does not amend the more general shared schema or resolve the future protocol handling of partial scientific results.

Legacy `run` and `output.records` builders remain generic development interfaces. Their return values are not certificates.

## Validation and timestamp dependency

`validate_development_output` applies the existing Branch B output schema, exact expected identifiers, external sample order, configuration reference, timestamp format, matrix dimensions/finiteness, and tree structure. It also rejects nonfinite JSON values, nonstring keys, cycles, and non-JSON metadata types instead of silently converting them.

Install `branch_b/requirements-output-dev.txt` alongside the existing development dependencies. It pins `rfc3339-validator==0.1.4`, needed for the schema checker's date-time format. Missing date-time validation support raises `ConfigurationRequired`; it must not silently accept an arbitrary timestamp. The two CI workflows install this requirement and retain their actual dependency evidence. This is not an optimizer dependency choice or a complete transitive environment lock.

The supplied record timestamp and scientific execution environment are retained, not replaced with the serializer's current values. The serializer's actual environment is recorded separately in its receipt.

## Exact bytes and detached provenance

`prepare_development_output` takes a validated record, full source revision, configuration bytes and expected hash, input-manifest bytes and expected hash, and the same expected output identity/order. It returns `PreparedDevelopmentOutput(record_bytes, receipt_bytes)` without writing either file.

The record uses sorted-key, compact, ASCII-escaped JSON plus a final newline. NaN and Infinity are prohibited. This is the new component's development serialization contract, not a change to an approved exchange format. Original source values and supplied timestamps are not rounded or refreshed.

The detached receipt records output byte count and SHA-256, identity, source revision, configuration reference/hash, input-manifest hash, shared-output-schema digest, record timestamp, and the actual serializer interpreter/dependency versions. Its scope is `schema_structure_finiteness_only` and `scientific_authorization` is always false. The receipt is separate from the shared-schema record; no new top-level exchange fields were added.

A record containing an embedded `checksum` is rejected by this API because no self-checksum exclusion rule has been selected here. Keep the detached checksums. Do not remove an existing checksum or reinterpret its meaning without the applicable contract.

`verify_development_output` requires independent expected hashes for both record and receipt, plus expected identity/order, source revision, configuration reference/hash, and input-manifest hash. It checks the bytes, rejects duplicate JSON keys or noncanonical encodings, revalidates the decoded record, and checks receipt consistency. It returns a detached decoded record. Verification does not rewrite the producer environment.

A source-revision string and matching hashes bind declarations and bytes; they do not prove that the named source was executed, that configuration contents equal an approved method, or that a support decision was correctly calculated. Keep source, configuration, execution logs, and approval evidence separately. This component does not authenticate those external records or scan a repository for them.

## Inventory and failure accounting

`reconcile_development_inventory` takes an explicit list of planned output identities and a list of `(PreparedDevelopmentOutput, verification_arguments)` pairs. Every pair must include all independently sourced verification arguments required above.

It verifies each artifact and reports missing identities, unexpected identities, and all duplicate positions without dropping or replacing entries. Arrival order does not establish identity. A malformed or checksum-invalid artifact raises an artifact-validation error rather than being invented into a scientific fit failure.

`inventory_matches_plan` means every planned identity is accounted for exactly once, with no unexpected identities. An inventory consisting entirely of explicit failure records can satisfy that accounting condition. `schema_complete_records` and `failure_records` remain separate counts; neither is a protocol-valid bootstrap success count. The report's scope is `verified_transport_accounting_only`, with no scientific authorization.

## Boundaries still requiring scientific specifications

These APIs do not choose symmetry, diagonal, ultrametric-inequality, tree-height, or tree/matrix-consistency tolerances. They do not establish support reliability, determine a confidence interval, validate a frozen scientific configuration, or resolve duplicate-bootstrap reciprocal-weight behavior. The complete Common Fitter remains unavailable.

No new filesystem submission runner or production bank adapter is enabled. Before any future persistence or publication, review the actual bytes for Branch B permission and public-disclosure safety. A schema or checksum pass is not that review. The earlier four-file packaging snapshot remains pinned to its original reviewed source and does not include these new modules automatically.
