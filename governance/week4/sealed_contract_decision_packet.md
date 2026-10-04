# Sealed precision contract decision packet

Status: DRAFT_PENDING_APPROVAL. This packet prepares decisions; it selects no scientific threshold and records no approval.

## Requirements already defined

Use five initial replicates per frozen sentinel. Check the sealed binary trigger only after initial outputs freeze. A positive trigger permits a uniform total of ten; cell-targeted expansion and condition substitution are prohibited. PL receives only approved signed fields and has no raw pilot-truth access. Freeze the controlling contract before associated inspection.

## Decisions and evidence still required

| Field | Needed for closure | Owner |
|---|---|---|
| Trigger inputs and aggregation | Exact estimand/diagnostic, failure handling, aggregation across sentinels, units and eligible inputs | custodian + PL + Faculty |
| Binary formula | Executable formula, constants, comparison convention and deterministic missing/invalid-input behavior | custodian + PL + Faculty |
| Conservative resource/precision rule | Exact calculation, uncertainty convention, accounting of all scheduled failures and permitted output units | custodian + PL + Faculty |
| Release allowlist | Exact field names, types and units; no detailed truth-keyed performance | PL + Faculty |
| Signer | Real custodian identity, availability, independent key registration, key fingerprint and verification path | custodian + PL |
| Freeze chronology | Contract checksum, dated decisions and evidence of freeze before associated inspection | PL + Faculty |

## Transport implementation proposal

Use Ed25519 over canonical UTF-8 JSON: sorted keys, compact separators, ASCII escaping, finite JSON values and one final newline. Verify with an independently registered public key; never trust a key supplied in the release envelope. Bind the signed payload to scope, signer identity, approved contract checksum, frozen initial-output manifest checksum, UTC issue time, binary trigger, uniform replicate total and exact allowed released fields.

`sealed_transport.py` implements these transport checks. `validate_escalation.py` now invokes real verification with the public key registered in the reviewed contract and checks the identity-binding artifact checksum. It also requires the verification attestation to agree with the actual cryptographic result. A verified signature proves payload integrity and key possession. Actual identity, availability, authority, trigger calculation and before-inspection freeze require separate review.

The proposed signer registration is an object containing `algorithm` (Ed25519), `signer_id`, `release_scope` (pilot_sealed_release_v1), `public_key_ref`, `public_key_sha256`, `identity_key_binding_ref` and `identity_key_binding_sha256`. References are relative evidence files under the controlled evidence root. The binary public key is 32 bytes. A release embeds no trusted key of its own. This operational format is a proposal until its controlling contract is approved/frozen.

`sealed_calculation_candidate.json` supplies a concrete conservative planning candidate with explicit inputs, formula choices, failure accounting and optional field types. Its constants remain unselected; the normal planning bound is not an exact confidence guarantee. PL and Faculty must decide the calculation convention and release fields before associated inspection. No candidate is enabled in production by this packet.

`run_sealed_rehearsal.py` exercises actual signing and rejection of tampering, wrong keys, wrong identities, scope misuse and allowlist violations using dummy records. Its ephemeral private key stays in memory. The demo does not select the production trigger, release metrics or custodian.

## Approval-ready completion sequence

1. Custodian supplies the calculation specification and dated identity/availability record.
2. PL and Faculty decide the unresolved formula, conservative rule and exact allowlist.
3. Register and independently verify the custodian public key and fingerprint.
4. Complete the existing contract, collect dated decisions and exact-byte checksums, then record the freeze before associated inspection.
5. Run a custodian-operated dummy rehearsal under that approved contract and retain signed evidence.
6. Re-run the gate audit. Production remains blocked while any applicable gate is open.
