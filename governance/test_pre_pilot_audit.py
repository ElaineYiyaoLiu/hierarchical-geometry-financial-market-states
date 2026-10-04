import hashlib
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("pre_pilot_audit", Path(__file__).with_name("audit_pre_pilot.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def records(tmp_path):
    evidence = tmp_path / "evidence.json"
    approval = tmp_path / "approval.json"
    evidence.write_text('{"fixture": true}\n')
    approval.write_text('{"fixture_approval": true}\n')
    return [{
        "gate_id": gate, "owner": "fixture", "status": "PASS",
        "evidence_ref": evidence.name,
        "evidence_sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
        "approval_authority": "fixture reviewer",
        "approval_ref": approval.name,
        "approval_sha256": hashlib.sha256(approval.read_bytes()).hexdigest(),
        "freeze_id": "fixture-freeze",
    } for gate in sorted(module.REQUIRED_GATES)]


def test_complete_fixture_is_reviewable_and_never_authorizes(tmp_path):
    result = module.audit(records(tmp_path), tmp_path)
    assert result["evidence_complete"] and result["decision"] == "REVIEWABLE"
    assert result["pilot_exchange_authorized"] is False
    assert result["formal_generation_authorized"] is False


@pytest.mark.parametrize("change", ["missing", "duplicate", "unknown"])
def test_invalid_gate_set_blocks(tmp_path, change):
    rows = records(tmp_path)
    if change == "missing":
        rows.pop()
    elif change == "duplicate":
        rows.append(rows[0].copy())
    else:
        rows.append({**rows[0], "gate_id": "unrecognized"})
    assert module.audit(rows, tmp_path)["structural_blockers"]


@pytest.mark.parametrize("status", ["PASS_SCOPED", "RECORDED_REVERIFY", "PENDING", "WAIVED"])
def test_partial_and_waived_status_never_closes_gate(tmp_path, status):
    rows = records(tmp_path)
    rows[0]["status"] = status
    result = module.audit(rows, tmp_path)
    assert result["gates"][0]["evidence_checksum_verified"]
    assert result["gates"][0]["status"] == "BLOCKED"


def test_primary_and_approval_checksum_mismatches_block(tmp_path):
    rows = records(tmp_path)
    rows[0]["evidence_sha256"] = "0" * 64
    rows[1]["approval_sha256"] = "0" * 64
    result = module.audit(rows, tmp_path)
    assert result["gates"][0]["status"] == result["gates"][1]["status"] == "BLOCKED"


@pytest.mark.parametrize("ref", ["../outside", "/outside"])
def test_evidence_path_escape_blocks(tmp_path, ref):
    rows = records(tmp_path)
    rows[0]["evidence_ref"] = ref
    assert module.audit(rows, tmp_path)["gates"][0]["status"] == "BLOCKED"


def test_blank_approval_does_not_pass(tmp_path):
    rows = records(tmp_path)
    rows[0]["approval_ref"] = ""
    assert module.audit(rows, tmp_path)["gates"][0]["status"] == "BLOCKED"
