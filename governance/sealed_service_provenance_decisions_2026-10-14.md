# Sealed-service and provenance decision worksheet

Status: DRAFT_PENDING_REQUIRED_DECISIONS. Production use is false.

## Sealed precision contract

Complete each decision before associated inspection. Refer to the existing sealed_calculation_candidate.json; its constants remain unselected.

| Decision | Required answer and evidence | Owner |
|---|---|---|
| Eligible inputs | Define exact input record, opaque aggregation unit, source/output freeze checksum and treatment of every scheduled failure or indeterminate attempt | Custodian + PL + Faculty |
| Trigger | Select the exact formula, aggregation, comparison including equality, constants and missing/nonfinite/incomplete input behavior | Custodian + PL + Faculty |
| Precision convention | Select normal planning bound or a specified bounded-variable alternative; justify domain, dependence assumptions, confidence interpretation and suitability for the small pilot sample | PL + Faculty |
| Resource calculation | Freeze resource units, stage coverage, measurement rule, safety multiplier and concurrency assumption; retain failures in workload | PL + Faculty |
| Release fields | List the exact allowed field names, types, units and nullability; prohibit detailed truth-keyed performance and condition mappings | PL + Faculty |
| Signer registration | Actual custodian identity, independently verified public-key binding, availability and controlled signing process | Custodian + PL |
| Chronology | Actual signed decisions, exact contract checksum and freeze preceding associated inspection | PL + Faculty |

Candidate formulas are already available; this worksheet selects none. A binary trigger approval must cover its meaning and calculation, not only successful signature verification.

## Custodian operation evidence

Supply a dated identity/availability record and the independently registered public key with its fingerprint and identity-binding checksum. Keep the private signing key outside the shared repository.

Under the approved contract, the custodian operates a dummy rehearsal and retains the signed payload, its approved input/output bindings and verification result. Verify valid release and rejection of wrong key, signer, scope, contract/manifest binding, altered payload, missing/extra fields and inconsistent uniform expansion.

An agent-operated demo with an ephemeral key is development transport evidence; it does not establish real custodian operation.

## Minimum-effect historical evidence

| Evidence | Must identify |
|---|---|
| Original primary-metric decision | Exact metric/contrast, orientation, units, substantive positive effect value and rationale |
| Authority and signature | Actual original decision-maker, signature artifact and exact-byte checksum |
| Freeze record | Original UTC time, decision/version binding and completed freeze entry |
| Earliest relevant inspection | Earliest Branch B valuation-versus-comparator inspection on primary-family development data, with dated access/output records or a reviewed attestation |
| Chronology review | Freeze strictly precedes earliest relevant inspection; identify the records searched and uncertainty remaining |

Obtain original records from their approved source. If the original value or chronology cannot be established, retain BLOCKED and request an explicit protocol-compliant resolution. Do not reconstruct a historical scientific value from observed contrasts or backdate a current approval.

## Review completion record

For each decision record: decision ID, controlling protocol version, selected content, rationale, actual approver, original signature reference, approval checksum, UTC decision time, completed freeze ID and evidence of the applicable before-inspection boundary.

Missing items remain blank. Once complete, run the existing consistency and gate audits, followed by actual authority review. Formal generation and exchange require their separate approvals.
