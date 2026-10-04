"""Real Ed25519 signing with explicitly dummy input; no production approvals."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
from pathlib import Path

import cryptography
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from sealed_transport import canonical_bytes, sign, verify


def rehearse(output: Path) -> dict:
    if output.exists():
        raise FileExistsError("use a new rehearsal output directory")
    # The ephemeral private key is held in memory and never written or uploaded.
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes_raw()
    contract_digest = hashlib.sha256(b"DUMMY CONTRACT, NO APPROVAL").hexdigest()
    manifest_digest = hashlib.sha256(b"DUMMY INITIAL MANIFEST").hexdigest()
    payload = {"scope": "DUMMY_REHEARSAL_ONLY", "signer_id": "DUMMY_CUSTODIAN",
               "contract_sha256": contract_digest,
               "initial_output_manifest_sha256": manifest_digest,
               "issued_at_utc": "2026-10-04T00:00:00Z", "trigger": False,
               "uniform_total_per_sentinel": 5,
               "released_fields": {"dummy_resource_units": 12}}
    arguments = {"trusted_public_key": public, "expected_signer": "DUMMY_CUSTODIAN",
                 "expected_scope": "DUMMY_REHEARSAL_ONLY",
                 "expected_contract_sha256": contract_digest,
                 "expected_initial_manifest_sha256": manifest_digest,
                 "allowed_release_fields": ["dummy_resource_units"]}
    checks = {}
    envelope = sign(payload, private)
    verification = verify(envelope, **arguments)
    checks["valid_signed_dummy_release"] = verification["signature_valid"]
    expanded = {**payload, "trigger": True, "uniform_total_per_sentinel": 10}
    checks["uniform_expansion_transport"] = verify(sign(expanded, private), **arguments)["signature_valid"]
    tests = {}
    tampered = copy.deepcopy(envelope)
    tampered["payload"]["trigger"] = True
    tests["tampered_payload_rejected"] = (tampered, arguments)
    extra = copy.deepcopy(payload)
    extra["released_fields"]["unapproved_detail"] = 1
    tests["extra_release_field_rejected"] = (sign(extra, private), arguments)
    missing = copy.deepcopy(payload)
    missing["released_fields"] = {}
    tests["missing_release_field_rejected"] = (sign(missing, private), arguments)
    tests["wrong_key_rejected"] = (envelope, {**arguments, "trusted_public_key":
        Ed25519PrivateKey.generate().public_key().public_bytes_raw()})
    tests["wrong_signer_rejected"] = (envelope, {**arguments, "expected_signer": "OTHER"})
    tests["rehearsal_as_production_rejected"] = (envelope, {**arguments, "expected_scope": "PRODUCTION"})
    tests["wrong_manifest_rejected"] = (envelope, {**arguments, "expected_initial_manifest_sha256": "0" * 64})
    for name, (bad_envelope, kwargs) in tests.items():
        try:
            verify(bad_envelope, **kwargs)
        except ValueError:
            checks[name] = True
        else:
            raise RuntimeError(name)
    report = {"record": "sealed_transport_dummy_rehearsal", "development_only": True,
              "scope": "DUMMY_REHEARSAL_ONLY", "python": platform.python_version(),
              "cryptography": cryptography.__version__, "checks": checks,
              "custodian_operational_availability_verified": False,
              "approved_precision_contract": False, "raw_pilot_truth_used": False,
              "pilot_generation_authorized": False, "pilot_exchange_authorized": False}
    output.mkdir(parents=True)
    for name, record in (("signed_dummy_release.json", envelope),
                         ("signature_verification.json", verification), ("report.json", report)):
        (output / name).write_bytes(canonical_bytes(record))
    (output / "dummy_public_key.hex").write_text(public.hex() + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    print(json.dumps(rehearse(parser.parse_args().output), indent=2, sort_keys=True))
