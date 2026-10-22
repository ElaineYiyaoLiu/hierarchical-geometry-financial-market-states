import copy

from test_a_pl_preparation import queue
from test_freeze_reconciliation import fixture


def test_evidence_complete_queue_still_requires_actual_freeze_entries(tmp_path):
    rows, freezes = fixture(tmp_path)
    before = copy.deepcopy((rows, freezes))
    blocked = queue.prepare(rows, tmp_path)
    assert blocked["evidence_only_audit_decision"] == "REVIEWABLE"
    assert blocked["overall_gate_audit_decision"] == "BLOCKED"
    assert all(r["status"] == "BLOCKED" for r in blocked["work_items"])
    assert all("referenced freeze entry missing" in r["missing_evidence"]
               for r in blocked["work_items"])
    complete = queue.prepare(rows, tmp_path, freezes)
    assert complete["overall_gate_audit_decision"] == "REVIEWABLE"
    assert all(r["status"] == "REVIEWABLE" for r in complete["work_items"])
    assert not complete["pilot_exchange_authorized"]
    assert not complete["formal_generation_authorized"]
    assert (rows, freezes) == before


def test_duplicate_freeze_records_block_each_queue_item(tmp_path):
    rows, freezes = fixture(tmp_path)
    result = queue.prepare(rows, tmp_path, freezes * 2)
    assert result["structural_blockers"]
    assert all(r["status"] == "BLOCKED" and r["missing_evidence"]
               for r in result["work_items"])
