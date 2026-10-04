"""Synthetic approved-looking fixtures test integrity, never real approvals."""
import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sealed_transport import sign, verify, canonical_bytes
from validate_escalation import validate


def save(root, name, content):
    (root / name).write_bytes(content)
    return hashlib.sha256(content).hexdigest()


@pytest.fixture
def fixture(tmp_path):
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes_raw()
    key_sha = save(tmp_path, "key.raw", public)
    binding_sha = save(tmp_path, "binding.txt", b"SYNTHETIC IDENTITY FIXTURE, NOT AN ATTESTATION")
    contract = {"status": "APPROVED_FROZEN", "approvals": {"PL": "SIMULATED", "Faculty": "SIMULATED"},
        "trigger_formula": "SIMULATED", "trigger_inputs_and_aggregation": "SIMULATED",
        "conservative_precision_resource_rule": "SIMULATED", "before_inspection_freeze_evidence": "SIMULATED",
        "exact_signed_release_field_allowlist": ["dummy_resource"],
        "signer_identity_and_verification": {"algorithm": "Ed25519", "signer_id": "TEST_CUSTODIAN",
            "release_scope": "pilot_sealed_release_v1", "public_key_ref": "key.raw", "public_key_sha256": key_sha,
            "identity_key_binding_ref": "binding.txt", "identity_key_binding_sha256": binding_sha}}
    data = canonical_bytes(contract)
    digest = hashlib.sha256(data).hexdigest()
    payload = {"scope": "pilot_sealed_release_v1", "signer_id": "TEST_CUSTODIAN", "contract_sha256": digest,
        "initial_output_manifest_sha256": "a" * 64, "issued_at_utc": "2026-10-04T00:02:00Z",
        "trigger": False, "uniform_total_per_sentinel": 5, "released_fields": {"dummy_resource": 1}}
    envelope = sign(payload, private)
    release_sha = save(tmp_path, "release.json", canonical_bytes(envelope))
    verification = verify(envelope, trusted_public_key=public, expected_signer="TEST_CUSTODIAN",
        expected_scope="pilot_sealed_release_v1", expected_contract_sha256=digest,
        expected_initial_manifest_sha256="a" * 64, allowed_release_fields=["dummy_resource"])
    verification["signed_release_sha256"] = release_sha
    verification_sha = save(tmp_path, "verification.json", canonical_bytes(verification))
    record = {"status": "COMPLETE", "generation_authorized_by_template": False,
        "project_lead_raw_truth_accessed": False, "approved_precision_contract_sha256": digest,
        "trigger": False, "uniform_total_per_sentinel": 5, "custodian": "TEST_CUSTODIAN",
        "initial_output_frozen_at_utc": "2026-10-04T00:01:00Z", "checked_at_utc": "2026-10-04T00:03:00Z",
        "initial_output_manifest_sha256": "a" * 64, "authorized_release_fields": ["dummy_resource"],
        "released_fields": {"dummy_resource": 1}, "signed_release_ref": "release.json",
        "signed_release_sha256": release_sha, "signature_verification_ref": "verification.json",
        "signature_verification_sha256": verification_sha}
    return tmp_path, private, contract, data, record


def test_registered_key_integrity_is_reviewable_and_non_authorizing(fixture):
    root, _, contract, data, record = fixture
    result = validate(record, contract, data, root)
    assert result["decision"] == "REVIEWABLE"
    assert result["supplemental_generation_authorized"] is False


def test_forged_signature_valid_attestation_cannot_pass(fixture):
    root, _, contract, data, record = fixture
    envelope = json.loads((root / "release.json").read_text())
    envelope["payload"]["released_fields"]["dummy_resource"] = 99
    record["released_fields"]["dummy_resource"] = 99
    record["signed_release_sha256"] = save(root, "release.json", canonical_bytes(envelope))
    verification = json.loads((root / "verification.json").read_text())
    verification["signed_release_sha256"] = record["signed_release_sha256"]
    record["signature_verification_sha256"] = save(root, "verification.json", canonical_bytes(verification))
    assert "signature" in " ".join(validate(record, contract, data, root)["blockers"])


@pytest.mark.parametrize("change", ["wrong_key", "missing_binding", "dummy_scope", "missing_release", "wrong_attestation", "path_escape"])
def test_registration_and_release_guards(fixture, change):
    root, _, contract, data, record = fixture
    if change == "wrong_key":
        (root / "key.raw").write_bytes(Ed25519PrivateKey.generate().public_key().public_bytes_raw())
    elif change == "missing_binding":
        (root / "binding.txt").unlink()
    elif change == "dummy_scope":
        contract["signer_identity_and_verification"]["release_scope"] = "DUMMY_REHEARSAL_ONLY"
    elif change == "missing_release":
        record["released_fields"] = {}
    elif change == "wrong_attestation":
        verification = json.loads((root / "verification.json").read_text())
        verification["trusted_key_sha256"] = "0" * 64
        record["signature_verification_sha256"] = save(root, "verification.json", canonical_bytes(verification))
    else:
        contract["signer_identity_and_verification"]["public_key_ref"] = "../outside"
    assert validate(record, contract, data, root)["decision"] == "BLOCKED"
