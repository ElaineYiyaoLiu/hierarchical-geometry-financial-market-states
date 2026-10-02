import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_pilot_exit import validate_matrix, checked_evidence
from validate_escalation import validate
from resource_projection import project


def test_incomplete_matrix_never_passes(tmp_path):
    assert validate_matrix([], tmp_path)["decision"] == "BLOCKED"
    rows = [{"criterion_id": f"J.{i}", "status": "PENDING"} for i in range(1, 19)]
    assert len(validate_matrix(rows, tmp_path)["blockers"]) == 18


def test_digest_and_path_escape_fail(tmp_path):
    p = tmp_path / "receipt"; p.write_bytes(b"receipt")
    with pytest.raises(ValueError):
        checked_evidence(tmp_path, "receipt", "0" * 64)
    with pytest.raises(ValueError):
        checked_evidence(tmp_path, "../outside", "a" * 64)


def test_reviewable_matrix_grants_no_authorization(tmp_path):
    p = tmp_path / "receipt"; p.write_bytes(b"receipt")
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    rows = [{"criterion_id": f"J.{i}", "status": "PASS", "approver": "PL",
             "freeze_id": "reviewed-entry", "approval_date_utc": "2026-10-02T00:00:00Z",
             "evidence_ref": "receipt", "evidence_sha256": sha} for i in range(1, 19)]
    result = validate_matrix(rows, tmp_path)
    assert result["evidence_complete"]
    assert not result["generation_authorized"] and not result["pilot_exit_approval_granted"]
    rows[-1]["criterion_id"] = "J.1"
    assert validate_matrix(rows, tmp_path)["decision"] == "BLOCKED"


def test_blank_escalation_and_resource_templates_are_not_evidence(tmp_path):
    assert validate({}, {"status": "DRAFT_PENDING_APPROVAL"}, b"draft", tmp_path)["decision"] == "BLOCKED"
    assert project([])["status"] == "UNMEASURED"


def test_resource_calculation_counts_failed_attempts_in_planned_total():
    result = project([{"stage": "fit", "benchmark_ref": "measured", "planned_attempts": "10",
                       "core_hours_per_attempt": "2", "bytes_per_attempt": str(2 ** 30),
                       "wall_seconds_per_attempt": "3600"}])
    assert result["total_core_hours"] == "20"
    assert result["total_storage_gib"] == "10"
    assert result["stages"][0]["serial_elapsed_hours"] == "10"
    assert not result["feasibility_approved"]
