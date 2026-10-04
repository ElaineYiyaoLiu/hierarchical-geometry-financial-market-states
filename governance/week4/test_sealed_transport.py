import copy
import sys
from pathlib import Path
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sealed_transport import sign, verify
from run_sealed_rehearsal import rehearse


@pytest.fixture
def release():
    key = Ed25519PrivateKey.generate()
    payload = {"scope": "DUMMY_REHEARSAL_ONLY", "signer_id": "DUMMY",
        "contract_sha256": "a" * 64, "initial_output_manifest_sha256": "b" * 64,
        "issued_at_utc": "2026-10-04T00:00:00Z", "trigger": False,
        "uniform_total_per_sentinel": 5, "released_fields": {"dummy": 1}}
    kwargs = {"trusted_public_key": key.public_key().public_bytes_raw(),
        "expected_signer": "DUMMY", "expected_scope": "DUMMY_REHEARSAL_ONLY",
        "expected_contract_sha256": "a" * 64,
        "expected_initial_manifest_sha256": "b" * 64,
        "allowed_release_fields": ["dummy"]}
    return key, payload, kwargs


def test_signature_verifies_without_granting_authority(release):
    key, payload, kwargs = release
    result = verify(sign(payload, key), **kwargs)
    assert result["signature_valid"]
    assert result["operational_authorization_granted"] is False


def test_signed_payload_tamper_is_detected(release):
    key, payload, kwargs = release
    envelope = sign(payload, key)
    envelope["payload"]["released_fields"]["dummy"] = 999
    with pytest.raises(ValueError, match="signature"):
        verify(envelope, **kwargs)


@pytest.mark.parametrize("field,value", [
    ("trigger", "false"), ("uniform_total_per_sentinel", True),
    ("uniform_total_per_sentinel", 10), ("released_fields", {}),
    ("released_fields", {"dummy": 1, "extra": 2}),
    ("issued_at_utc", "2026-10-04T00:00:00"), ("scope", "PRODUCTION"),
    ("signer_id", "OTHER"), ("contract_sha256", "c" * 64),
    ("initial_output_manifest_sha256", "c" * 64),
])
def test_valid_signature_does_not_bypass_contract_checks(release, field, value):
    key, payload, kwargs = release
    payload[field] = value
    with pytest.raises(ValueError):
        verify(sign(payload, key), **kwargs)


def test_dummy_rehearsal_never_claims_custodian_availability(tmp_path):
    report = rehearse(tmp_path / "demo")
    assert all(report["checks"].values())
    assert report["custodian_operational_availability_verified"] is False
    assert report["pilot_generation_authorized"] is False
    assert report["approved_precision_contract"] is False
