import hashlib
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "revision_audit", Path(__file__).with_name("audit_revision_preparation.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture(tmp_path):
    file = tmp_path / "dummy.json"
    file.write_bytes(b'{"dummy_fixture_only":true}\n')
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    record = {"status": "APPROVED_FROZEN", "calibration_seed_release_authorized": False,
              "locked_test_authorized": False, "changes": [{"change_id": "fixture", "field": "timeout"}],
              "prohibited_scientific_changes": [], "allowed_evidence_refs": [file.name],
              "pilot_exit_approval_ref": file.name, "pilot_exit_approval_sha256": digest,
              "checksum_freeze_ref": file.name, "checksum_freeze_sha256": digest,
              "approvals": {"PL": file.name, "Faculty": file.name},
              "approvals_sha256": {"PL": digest, "Faculty": digest}}
    row = {"change_id": "fixture", "field": "timeout", "before_value": "fixture-before",
           "proposed_value": "fixture-after", "protocol_basis": "fixture-G4",
           "scientific_effect": "fixture", "freeze_id": "fixture", "status": "APPROVED_FROZEN",
           "permitted_evidence_ref": file.name, "evidence_sha256": digest,
           "artifact_ref": file.name, "artifact_sha256": digest,
           "PL_approval_ref": file.name, "PL_approval_sha256": digest,
           "Faculty_approval_ref": file.name, "Faculty_approval_sha256": digest}
    return record, [row]


def test_consistent_fixture_never_approves_revision_or_release(tmp_path):
    record, rows = fixture(tmp_path)
    result = mod.audit_revision(record, rows, tmp_path)
    assert result["decision"] == "REVIEWABLE"
    for flag in ("revision_approved", "calibration_seed_release_authorized",
                 "locked_test_authorized", "scientific_scope_independently_verified",
                 "before_inspection_chronology_verified"):
        assert result[flag] is False


@pytest.mark.parametrize("field", ["primary_generator_grid", "minimum_effect_size",
                                   "geometry_set", "interface_correction"])
def test_unknown_and_scientific_changes_require_separate_review(tmp_path, field):
    record, rows = fixture(tmp_path)
    rows[0]["field"] = record["changes"][0]["field"] = field
    assert mod.audit_revision(record, rows, tmp_path)["decision"] == "BLOCKED"


@pytest.mark.parametrize("change", ["missing_approval", "tamper", "duplicate",
                                   "missing_change", "unauthorized_seed_release"])
def test_missing_bytes_and_invalid_change_binding_block(tmp_path, change):
    record, rows = fixture(tmp_path)
    if change == "missing_approval":
        record["approvals"]["Faculty"] = None
    elif change == "tamper":
        (tmp_path / "dummy.json").write_bytes(b"changed")
    elif change == "duplicate":
        rows *= 2
    elif change == "missing_change":
        record["changes"] = []
    else:
        record["calibration_seed_release_authorized"] = True
    assert mod.audit_revision(record, rows, tmp_path)["decision"] == "BLOCKED"


def test_real_blank_template_returns_actionable_blockers(tmp_path):
    assert mod.audit_revision({"status": "NOT_PROPOSED"}, [], tmp_path)["decision"] == "BLOCKED"
