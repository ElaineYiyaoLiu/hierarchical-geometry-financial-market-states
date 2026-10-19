# Observable-to-output transport validation - 2026-10-19

Tested code revision: `82bef433fcbaa455e12bf4695f34ce46a34b7e96`.

The remaining concrete input/output/provenance integration work identified after the [integration audit](integration_audit_2026-10-19.md) and [checked-pipeline repair](checked_integration_validation_2026-10-19.md) has been implemented and tested within the scopes below. This is development interface evidence, not end-to-end scientific golden testing or a runner certificate.

## Delivered implementation

| Component | Implementation commits | Delivered contract |
| --- | --- | --- |
| [Checked outgoing records and immutable byte receipts](output/checked.py) | `52ec3104051db3551f3622ff36b3cda8c06232de`, corrected in `f89942c02ae07fd58043ff03270c1cab8af7deac` | Existing shared output schema; exact external identity/order; structural/finiteness checks; explicit support/failure inputs; detached source/configuration/input/schema/output byte bindings. |
| [Planned-output reconciliation](output/inventory.py) | `1e21d6dc11ca3575f2bdac976e6c87d4457d49cb` | Verify every supplied artifact and preserve missing, duplicate, unexpected, complete, and failed-record accounting without replacement or omission. |
| [Observable manifest/CSV loader](observable_input.py) | `5511bdbcb25d2a778d59a9cf797584b12078f5e1` | External checksums, existing observable schema, exact feature header/dimensions, original sample-order checksum, finite values, and detached arrays/identities. No path discovery or bank access. |
| Required date-time format dependency | `4a842f16c1fd7fdbde4dd5158b27926d21f4d6e3` | [requirements-output-dev.txt](requirements-output-dev.txt) pins `rfc3339-validator==0.1.4`; absence of the date-time checker is now a configuration failure. |
| Existing Python 3.14 CI dependency installation | `b300fcbbaf5aa0a2e28cb043cac1bf92b015f4cf`, `3bae2fddad402dec21b9425206e15465cae2c606` | Each workflow's dependency-install command includes the new output requirement. Interpreter selection, test scopes, and existing dependency constraints were not replaced. |

[The usage and migration guide](output/checked_transport.md) was added separately in `9bfd17416715deefd79c2f8d0515ecdc24e9ec17`. It is documentation after the tested code revision, not a claim of a new scientific execution.

The comparison from `5890ccc24f414125e326f9a6311ecbecc353d465` to the tested revision contains three new implementation modules, three new test files, one new dependency file, and one dependency-install line changed in each of two workflows. It does not change a shared schema, a scientific method card, fitter/geometry/support/bootstrap numerical code, the seed policy, a freeze record, or the previously pinned packaging workflow.

## What was exercised

There are 130 new synthetic cases across:

- [test_checked_output_transport.py](recovery_tests/test_checked_output_transport.py), commit `1fbbae5b6eb8a739a9692797af2317c50f460c9e`: record/schema/order binding, detached ownership, deterministic serialization, explicit failures, malformed JSON and matrices, independent checksum expectations, receipt tampering, and checked-pipeline-to-output integration.
- [test_output_inventory.py](recovery_tests/test_output_inventory.py), commit `e376291c14b892cbdfea10fae2a0d7424f719f2a`: missing/extra/duplicate output accounting, all-failure inventories, swapped expectations, invalid artifacts, unchanged caller inputs, date-time checker absence, and valid/invalid timestamps.
- [test_observable_input_binding.py](recovery_tests/test_observable_input_binding.py), commit `82bef433fcbaa455e12bf4695f34ce46a34b7e96`: CSV/header/value/identity checks, external and internal hash mismatches, malformed manifests, original-order preservation, and the full synthetic transport path from three split CSV/manifest pairs through `run_checked` to verified output bytes.

The integration path uses identity preprocessing and a named stub fitter with a literal synthetic star tree. Supplied support values, decisions, timestamps, configuration bytes, and source identifiers are fixtures, not scientific estimates or approvals. The test seed `20261019` is implementation-test provenance only. No experimental bank, production seed assignment, scientific Common-Fitter run, hierarchy-support calibration, or threshold calculation occurred.

## Verified Python 3.14 execution

| Scope | Run | Job | Actual logged result |
| --- | --- | --- | --- |
| Branch B support/recovery/failure suite | 39327024654 | 118315399660 | 390 passed in 0.79 s |
| Shared validator, same Branch B job | 39327024654 | 118315399660 | 15 passed in 0.07 s |
| Repository-wide pytest discovery | 39327024764 | 118315400098 | 531 passed in 1.91 s |

Both completed job logs show checkout of the tested revision and CPython 3.14.8. The Branch B job also asserts major/minor `(3, 14)`. Counts overlap and must not be added. These durations describe development tests, not pilot performance, throughput, or capacity.

- [Branch B run and logs](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39327024654)
- [Repository-wide run and logs](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39327024764)

No local project test or scientific computation was executed under another interpreter. A local Python 3.14 installation attempt failed on network name resolution; the verified execution evidence comes from repository CI.

### Actual environments are not identical

Both successful jobs used Ubuntu 24.04.5 and runner 2.337.0. The Branch B job used image `ubuntu-24.04` version `20261018.339.1`; repository-wide discovery used image version `20261012.334.1`. Do not collapse these into one identical host environment.

The Branch B dependency listing records:

```text
attrs==26.1.0
iniconfig==2.3.1
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
numpy==2.5.3
packaging==26.3
pluggy==1.7.0
Pygments==2.21.0
pytest==9.1.1
referencing==0.37.0
rfc3339-validator==0.1.4
rpds-py==2026.9.1
six==1.17.0
```

Repository-wide discovery used pytest 8.4.2 instead of 9.1.1 and also installed cryptography 50.0.2, cffi 2.1.1, and pycparser 3.11 through the existing requirements. Both jobs installed the new rfc3339-validator dependency and six 1.17.0. The output requirement is a direct dependency pin, not a complete transitive lock or cross-environment reproducibility guarantee.

### Passing evidence retained

Branch B artifact `branch-b-python314-test-evidence`, ID `12222114027`, retains the dependency listing and both JUnit reports. Upload log and artifact metadata agree on the provider-reported SHA-256:

```text
1f2262d33e40a3c4eb2c7af7844b3d19ac91e8d7f9739b48b59413a364d30a29
```

Reported expiry: `2027-01-17T21:22:51Z`. The artifact was not independently downloaded and rehashed locally.

## Real failure found and corrected

The first inspected transport test run, `39325724196`, job `118310933083`, tested revision `1fbbae5b6eb8a739a9692797af2317c50f460c9e` under CPython 3.14.8. It reported **328 passed, 1 failed** in the Branch B suite, plus 15 shared-validator passes.

The failing case was `test_transport_rejects_malformed_or_lossy_records[invalid_timestamp]`: an invalid timestamp did not raise. The installed jsonschema stack had no active date-time checker because its optional format dependency was absent. A `FormatChecker` object alone did not establish format enforcement.

The repair installed the declared format dependency in both workflows, added a fail-closed check that date-time validation is available, and included the actual dependency version in the receipt. The original failing assertion was retained. Additional tests cover checker absence, invalid calendar/timezone values, and preservation of valid supplied timestamp strings. No test was removed, skipped, or marked expected-failure to obtain the passing result.

The failed run and its evidence remain available; intermediate push-triggered runs are not erased by the final success. Its artifact ID is `12222510827`, with upload-log and metadata SHA-256:

```text
6a4d0b31e39b79dc9d4cca0b4589f4be51161183a66edecb5ec91b2d095bcc6a
```

Reported expiry: `2027-01-17T21:13:00Z`. This digest is likewise provider-reported, not locally recomputed. Prior validation reports, environments, checksums, and the original four-file packaging snapshot have not been relabeled or replaced.

## Meaning and limits of a passing result

The new path binds explicit input bytes to canonical sample identities and checked output bytes. It preserves supplied failure codes without making a support decision and reconciles an explicit planned inventory without silently dropping records. An inventory may be fully accounted for while every scientific fit failed; the report does not call that scientific success.

These functions perform no filesystem publication and enable no official bank runner. They accept only explicitly supplied input bytes/records and open the existing installed schemas. Matching hashes do not establish authorization, public-disclosure permission, approved configuration semantics, or proof that a declared source revision was executed. Actual source/runtime/approval evidence remains necessary.

The outgoing adapter requires separately supplied hierarchy support and stability. It does not calculate or validate their statistical meaning. Numerical symmetry/diagonal/ultrametric/tree-consistency checks remain outside this structural-only transport until the governing conventions are resolved. Complete candidate/replicate logs must be preserved separately; the exchange-shaped record is not a complete archive of internal state.

The audit's A2 and A3 now have additional input/output integration coverage on the checked path, not blanket closure across all generic APIs. A4's delayed test-access repair and A5's corrected readiness wording are unchanged. A1's duplicate-bootstrap/reciprocal-weight conflict remains unresolved and explicitly tested as a conflict, not repaired.

## Decision checkpoint

The specific substantial decision-independent integration tasks identified in the audit and follow-up have now been implemented and verified to their stated structural/transport scopes. No further bounded task has been identified in this pass that would complete the pending scientific milestones without the missing method specifications. Pause autonomous scientific implementation here rather than describe more generic tests or another wrapper as milestone completion.

The earliest blockers remain CF-SIGMOID, CF-INIT, CF-POSITIVITY and the executable loss/gradient specification; the multiplicity/pair-weighting/reciprocal-zero reconciliation; and the separately reserved numerical comparison conventions. Correlation admissibility, valuation sanity, geometry search/common selection, pilot-stage operational decisions, and formal processing approvals remain downstream prerequisites.

This checkpoint is not a new freeze or a claim that every possible software defect is eliminated. A demonstrated material implementation defect can reopen bounded engineering work. Otherwise resume substantial scientific integration after the corresponding authorized choices or missing controlling records are supplied and reconciled.

No pending scientific decision was resolved by these commits. No production seed, statistical procedure, approved method value, shared schema, freeze, pilot/calibration/blind-validation/locked-test gate, or unblinding authorization was changed.
