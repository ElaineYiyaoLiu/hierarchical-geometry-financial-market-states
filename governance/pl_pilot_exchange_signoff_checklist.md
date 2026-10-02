# Project Lead pilot-exchange signoff checklist

Status: **current evidence reconciliation - 2026-10-02**. No pilot-exchange approval is granted by this file.

Legend:
- [x] evidence currently supports this item
- [ ] still requires evidence or approval before READY
- [~] recorded but requires final operational/current-commit verification

## A. Configuration and boundary checks

- [ ] `configuration_completeness.json` has no unresolved pre-pilot field.
  - Current state: unresolved Branch B and Faculty gates remain.
- [x] Observable-only handoff boundary remains intact.
  - Evidence: `pilot_access_audit.md`.
- [x] Shared-repository public-disclosure boundary is recorded as passing.
  - Evidence: `pilot_access_audit.md`.
- [x] Project Lead raw pilot-truth prohibition remains recorded.
  - Evidence: `pilot_access_audit.md`, `pilot_precision_plan.yaml`.
- [~] Sealed-service / independent-custodian path is recorded.
  - Final release still requires operational availability verification.
- [x] Public-safe seven-sentinel registry is frozen.
  - Evidence: `pilot_sentinel_registry.csv`.
- [x] No formal pilot observable package has been generated/exchanged according to the current Branch A golden record and PL exchange packet.
  - Evidence: private Branch A `generator_golden_report.json`; shared `pilot_exchange_packet.md`.

## B. Branch A evidence

- [x] Pilot configuration remains frozen in the restricted Branch A repository.
- [x] Formal pilot root seed remains approved and frozen in the restricted Branch A repository.
- [ ] Generator golden / reproduction evidence is current for the exact latest Branch A commit.
  - Current issue: the private repository received reconciliation/documentation commits after the existing golden report; rerun/current-commit evidence is still required.
- [~] Existing Branch A golden evidence records Python 3.14.7 / NumPy 2.5.3.
  - Final signoff requires the current exact-commit run, not metadata-only carry-forward.
- [x] Exact condition mappings, seed values, latent labels, truth, and generator implementation remain restricted by the recorded access boundary.

## C. Branch B decision closure

- [ ] Correlation-distance admissibility rule is explicitly approved and recorded.
- [ ] General numerical comparison tolerances are explicitly approved and recorded.
- [ ] Dasgupta soft-area sigmoid convention is explicitly approved and recorded.
- [ ] Common-Fitter initialization rule is explicitly approved and recorded.
- [ ] Common-Fitter non-negativity parameterization is explicitly approved and recorded.
- [ ] Valuation favorable-feature sanity invariant and minimum passing criterion are prespecified and recorded before designated-control inspection.

## D. Branch B implementation and verification

- [ ] Executable Common Fitter is complete.
- [ ] Common Fitter source-conformance tests pass.
- [ ] Actual Python 3.14-compatible scientific dependency versions are recorded.
- [ ] Bootstrap original-identity LCA stability integration passes Python 3.14 CI.
  - Implementation is complete; current-commit CI evidence is pending.
- [ ] Geometry / Common Fitter / support / interval / tree / triplet / bootstrap / failure / serialization golden tests pass on the final pre-pilot code.
- [ ] Executable Geometry Cards are complete.
- [ ] Candidate Common Fitter Cards are complete.
- [ ] Geometry-specific search rules are frozen where required.
- [ ] Geometry-neutral Common-Fitter selection rule is frozen where required.
- [ ] Pilot processing configuration is complete.
- [ ] Shared schema / output conformance passes on the final current code.
  - Earlier Python 3.14 CI evidence passed, but later bootstrap changes require current-commit verification.

## E. Faculty approvals

- [ ] Faculty concept / governance approval is recorded.
- [ ] Faculty pilot-exchange approval is recorded.

## F. Current Project Lead decision

**BLOCKED**

The evidence reconciliation supports the access boundary, public-safe sentinel registry, restricted Branch A pilot configuration/seed status, and existing Branch A Python 3.14 golden record. READY is not yet available because current-commit Branch A execution evidence, Branch B method decisions/implementation/CI evidence, and Faculty approvals remain open.

READY may be recorded only when every applicable item above is satisfied with evidence references.

A future READY decision authorizes only the protocol-defined pilot observable exchange. It does not authorize locked-test generation, locked-test processing, unblinding, or any post-pilot scientific redesign.

## 2026-10-02 execution reconciliation

- [x] Audited Branch A base snapshot passed 23 tests, frozen readiness and primary development observable/sealed byte reproduction under actual Python 3.14.7 / NumPy 2.5.3. Public aggregate attestation: `governance/branch_a_readiness_attestation_2026-10-02.json`. Final preparation code has separate verification. This does not close all-family formal-bank certification.
- [x] Shared audited base passed 15 validator and 47 Branch B tests locally under Python 3.14.7. See `governance/week3_execution_evidence_2026-10-02.json`.
- [ ] Repaired shared workflow must pass at its new head; prior CI failed during collection.
- [ ] All-family production dispatch, accounting and packaging certification.
- [ ] Approved/frozen sealed binary trigger, conservative calculation rule and exact signed release-field allowlist before associated inspection.
- [ ] Operational custodian identity, signature verification and availability.
- [ ] Minimum-effect-size frozen value and before-inspection provenance reconciled.

Existing checkboxes above are historical reconciliation; these scoped records supersede only their stated execution items. Exchange remains BLOCKED. `approval_evidence_register.csv` holds the consolidated current mapping. Pending freeze-registry rows grant no authority.
