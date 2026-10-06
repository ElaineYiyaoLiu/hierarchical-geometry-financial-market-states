import hashlib
import importlib.util
from pathlib import Path

import pytest


def module(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


queue = module("prepare_a_pl_queue")
provenance = module("check_minimum_effect_provenance")


def fixture(tmp_path):
    p = tmp_path / "original.json"
    p.write_text('{"dummy_fixture_only":true}\n')
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    record = {"minimum_effect_value": .1, "effect_orientation_and_units": "fixture",
              "approval_authority": "fixture", "freeze_id": "fixture",
              "frozen_at_utc": "2026-09-01T00:00:00Z",
              "earliest_relevant_development_contrast_inspection_at_utc": "2026-09-02T00:00:00Z"}
    for key in provenance.REFERENCES:
        record[key + "_ref"] = p.name
        record[key + "_sha256"] = digest
    return record


def test_complete_fixture_is_only_reviewable(tmp_path):
    result = provenance.check(fixture(tmp_path), tmp_path)
    assert result["status"] == "REVIEWABLE" and result["recorded_chronology_consistent"]
    assert not result["approval_granted"] and not result["historical_chronology_independently_verified"]


@pytest.mark.parametrize("date", ["2026-09-01T00:00:00Z", "2026-08-31T23:00:00Z",
                                 "2026-09-02T00:00:00", "2026-09-02T00:00:00-04:00", None])
def test_missing_non_utc_equal_and_late_freeze_block(tmp_path, date):
    record = fixture(tmp_path)
    record["earliest_relevant_development_contrast_inspection_at_utc"] = date
    record["chronology_verified"] = True  # Never trust a self-declared flag.
    assert provenance.check(record, tmp_path)["status"] == "BLOCKED"


@pytest.mark.parametrize("value", [True, 0, -1, float("nan"), float("inf"), None])
def test_effect_value_cannot_be_fabricated_from_invalid_fields(tmp_path, value):
    record = fixture(tmp_path)
    record["minimum_effect_value"] = value
    assert provenance.check(record, tmp_path)["status"] == "BLOCKED"


@pytest.mark.parametrize("ref", ["../outside", "/outside", "missing.json"])
def test_missing_escaped_and_tampered_evidence_block(tmp_path, ref):
    record = fixture(tmp_path)
    record["original_decision_ref"] = ref
    assert provenance.check(record, tmp_path)["status"] == "BLOCKED"
    record = fixture(tmp_path)
    record["original_decision_sha256"] = "0" * 64
    assert provenance.check(record, tmp_path)["status"] == "BLOCKED"


def test_queue_keeps_all_gates_and_never_changes_input_or_authorizes(tmp_path):
    rows = [{"gate_id": gate, "status": "PENDING"} for gate in sorted(queue.audit.__globals__["REQUIRED_GATES"])]
    before = [r.copy() for r in rows]
    result = queue.prepare(rows, tmp_path)
    assert rows == before and len(result["work_items"]) == 8
    assert not result["formal_generation_authorized"] and not result["pilot_exchange_authorized"]
    assert not any(r["gate_id"].startswith(("B_", "FACULTY")) for r in result["work_items"])
    assert result["other_gate_count"] == 12
