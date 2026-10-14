import hashlib
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "freeze_reconciliation", Path(__file__).with_name("check_freeze_reconciliation.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture(tmp_path):
    evidence = tmp_path / "evidence.json"
    approval = tmp_path / "approval.json"
    evidence.write_bytes(b'{"dummy":true}\n')
    approval.write_bytes(b'{"dummy_approval":true}\n')
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    gates = [{"gate_id": name, "owner": "fixture", "status": "PASS",
              "evidence_ref": evidence.name, "evidence_sha256": digest,
              "approval_authority": "fixture", "approval_ref": approval.name,
              "approval_sha256": hashlib.sha256(approval.read_bytes()).hexdigest(),
              "freeze_id": "fixture-freeze"} for name in sorted(mod.audit.__globals__["REQUIRED_GATES"])]
    freezes = [{"freeze_id": "fixture-freeze", "artifact": evidence.name,
                "checksum": digest, "owner": "fixture", "approved_by": "fixture",
                "version": "fixture-v1", "status": "frozen",
                "frozen_at_utc": "2026-01-01T00:00:00Z"}]
    return gates, freezes


def test_consistent_fixture_is_reviewable_without_authorizing(tmp_path):
    gates, freezes = fixture(tmp_path)
    result = mod.reconcile(gates, freezes, tmp_path)
    assert result["decision"] == "REVIEWABLE"
    assert not result["approval_granted"] and not result["pilot_exchange_authorized"]
    assert not result["formal_generation_authorized"]


@pytest.mark.parametrize("field,value", [
    ("status", "pending"), ("artifact", "other.json"), ("checksum", "0" * 64),
    ("frozen_at_utc", None), ("frozen_at_utc", "2026-01-01T00:00:00"),
    ("frozen_at_utc", "2026-01-01T00:00:00-04:00"),
    ("version", "pending"), ("approved_by", ""), ("owner", ""),
])
def test_placeholder_mismatch_and_missing_freeze_evidence_block(tmp_path, field, value):
    gates, freezes = fixture(tmp_path)
    freezes[0][field] = value
    assert mod.reconcile(gates, freezes, tmp_path)["decision"] == "BLOCKED"


def test_missing_duplicate_and_tampered_freeze_block(tmp_path):
    gates, freezes = fixture(tmp_path)
    assert mod.reconcile(gates, [], tmp_path)["decision"] == "BLOCKED"
    assert mod.reconcile(gates, freezes * 2, tmp_path)["structural_blockers"]
    (tmp_path / "evidence.json").write_bytes(b"changed")
    assert mod.reconcile(gates, freezes, tmp_path)["decision"] == "BLOCKED"


def test_matching_freeze_does_not_upgrade_scoped_gate(tmp_path):
    gates, freezes = fixture(tmp_path)
    gates[0]["status"] = "PASS_SCOPED"
    result = mod.reconcile(gates, freezes, tmp_path)
    assert result["gates"][0]["freeze_reference_consistent"]
    assert result["decision"] == "BLOCKED"


def test_freeze_can_bind_actual_approval_bytes(tmp_path):
    gates, freezes = fixture(tmp_path)
    freezes[0]["artifact"] = gates[0]["approval_ref"]
    freezes[0]["checksum"] = gates[0]["approval_sha256"]
    assert mod.reconcile(gates, freezes, tmp_path)["decision"] == "REVIEWABLE"
