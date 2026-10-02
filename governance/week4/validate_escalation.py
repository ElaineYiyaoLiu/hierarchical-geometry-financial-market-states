"""Check a signed-release evidence envelope against a previously frozen contract."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

from validate_pilot_exit import checked_evidence


def validate(record: dict, contract: dict, contract_bytes: bytes, root: Path) -> dict:
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Python 3.14 required")
    blockers = []
    try:
        if record.get("project_lead_raw_truth_accessed") is not False:
            raise ValueError("raw-truth firewall failed")
        if contract.get("status") != "APPROVED_FROZEN":
            raise ValueError("precision contract not approved/frozen")
        for key in ("trigger_formula", "trigger_inputs_and_aggregation",
                    "conservative_precision_resource_rule", "exact_signed_release_field_allowlist",
                    "signer_identity_and_verification", "before_inspection_freeze_evidence"):
            if not contract.get(key):
                raise ValueError(f"contract missing {key}")
        if not all(contract.get("approvals", {}).get(k) for k in ("PL", "Faculty")):
            raise ValueError("dual contract approval missing")
        if record.get("approved_precision_contract_sha256") != hashlib.sha256(contract_bytes).hexdigest():
            raise ValueError("approved contract checksum mismatch")
        if type(record.get("trigger")) is not bool:
            raise ValueError("custodian trigger must be binary")
        def date(key):
            d = datetime.fromisoformat(record[key].replace("Z", "+00:00"))
            if d.tzinfo is None:
                raise ValueError("timezone required")
            return d
        if date("initial_output_frozen_at_utc") >= date("checked_at_utc"):
            raise ValueError("initial outputs must freeze before check")
        total = 10 if record["trigger"] else 5
        if record.get("uniform_total_per_sentinel") != total:
            raise ValueError("uniform replicate total inconsistent with binary trigger")
        if not record.get("custodian"):
            raise ValueError("custodian required")
        for ref, digest in (("signed_release_ref", "signed_release_sha256"),
                            ("signature_verification_ref", "signature_verification_sha256")):
            checked_evidence(root, record.get(ref, ""), record.get(digest, ""))
        verification = json.loads((root / record["signature_verification_ref"]).read_text())
        if (verification.get("signature_valid") is not True or
            verification.get("signed_release_sha256") != record["signed_release_sha256"] or
            verification.get("signer") != record["custodian"]):
            raise ValueError("custodian signature verification attestation inconsistent")
        allowed = contract["exact_signed_release_field_allowlist"]
        if not isinstance(allowed, list) or set(record.get("released_fields", {})) - set(allowed):
            raise ValueError("released fields exceed approved allowlist")
        envelope = json.loads((root / record["signed_release_ref"]).read_text())
        for field in ("trigger", "initial_output_manifest_sha256", "released_fields"):
            if envelope.get(field) != record.get(field):
                raise ValueError(f"signed envelope mismatch: {field}")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        blockers.append(str(exc))
    return {"envelope_consistent": not blockers, "blockers": blockers,
            "decision": "REVIEWABLE" if not blockers else "BLOCKED",
            "supplemental_generation_authorized": False,
            "note": "Approving authority must independently verify signer and freeze provenance."}


if __name__ == "__main__":
    record_path, contract_path, evidence_root = map(Path, sys.argv[1:4])
    data = contract_path.read_bytes()
    result = validate(json.loads(record_path.read_text()), json.loads(data), data, evidence_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["envelope_consistent"]:
        raise SystemExit(1)
