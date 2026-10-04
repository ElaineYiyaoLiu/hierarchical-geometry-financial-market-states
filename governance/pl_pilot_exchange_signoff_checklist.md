# Project Lead pilot-exchange signoff checklist

Current reconciliation: 2026-10-04. Overall decision: **BLOCKED**.

## Verified execution scope

- Branch A audited code passed 32 tests, frozen readiness and primary development handoff byte reproduction under actual Python 3.14.7 / NumPy 2.5.3. Evidence: `governance/branch_a_execution_attestation_2026-10-04.json`. Formal all-family certification remains open.
- Public audited code passed 79 tests under the recorded Python 3.14.7 / NumPy 2.5.3 environment. Evidence: `governance/current_ci_evidence_2026-10-04.json`. This supersedes the earlier CI collection failure for that execution scope.
- The archived gate audit covered all 20 gate IDs and verified 11 evidence checksums at its recorded source/register. Evidence: `governance/pre_pilot_gate_audit_2026-10-04.json`. A changed register requires a new audit.
- Observable-only and raw-truth access boundaries are recorded in `pilot_access_audit.md`; the public-safe sentinel view is in `pilot_sentinel_registry.csv`. Final operational verification remains required.

## Remaining applicable gates

| Gate | Current closure requirement |
|---|---|
| Configuration completeness | Every applicable pre-pilot field has complete evidence, approval and freeze references |
| Branch A all-family runner | Formal dispatch/accounting/packaging certification and final restricted-side attestation |
| Branch B method package | Existing method decisions, source conformance, cards and final pipeline verification remain separate gates; not reviewed by this A/PL close-out |
| Custodian operational availability | Real identity, independent key registration, dated availability and custodian-operated rehearsal |
| Sealed precision contract | Approved formula, input aggregation, conservative rule, exact release allowlist, signature verification and before-inspection checksum freeze |
| Minimum-effect provenance | Original substantive value, dated approval/freeze and proof that freeze preceded earliest relevant development-contrast inspection |
| Faculty concept/governance | Dated signed decision with reviewed versions, checksums and conditions |
| Faculty pilot exchange | Separate dated signed decision after applicable gates close |
| Final PL exchange | Final complete gate audit and explicit dated PL decision |

## Prepared close-out material

- `governance/week4/sealed_contract_decision_packet.md` lists unresolved decisions and the executable transport proposal.
- `governance/week4/sealed_transport.py` and `run_sealed_rehearsal.py` verify actual Ed25519 signatures on dummy records. The demo is not a custodian availability or approval attestation.
- `governance/minimum_effect_provenance_review_2026-10-04.md` and the adjacent template record the missing historical evidence without selecting a value.
- `governance/faculty_review_package_2026-10-02.md` is reconciled to current execution evidence.

The consolidated register is `governance/approval_evidence_register.csv`. Scoped, pending, historical and demo evidence retain their scope. Pending freeze rows grant no authority. Record READY only after all applicable gates close with reviewed evidence and corresponding decisions. A pilot-exchange decision applies only to protocol-defined pilot exchange; later research stages require their own approvals.
