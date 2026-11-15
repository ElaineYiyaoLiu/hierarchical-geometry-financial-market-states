"""Development-only read-only audit failure checks, under Python 3.14."""

import json

import pytest

from branch_b.tools.d13_evidence_audit import audit_study
from branch_b.tools import d13_expanded_synthetic_coverage as expanded


def test_missing_original_evidence_is_a_hard_failure(tmp_path):
    with pytest.raises(ValueError, match="missing original evidence file"):
        audit_study("expanded", tmp_path)


def test_unknown_study_type_rejected(tmp_path):
    with pytest.raises(ValueError, match="unknown synthetic evidence type"):
        audit_study("unknown", tmp_path)


def test_incomplete_study_not_mistaken_for_a_complete_one(tmp_path):
    expanded.run(output_dir=tmp_path / "expanded", max_new_trials=0)
    with pytest.raises(ValueError, match="incomplete"):
        audit_study("expanded", tmp_path / "expanded")


def test_corrupted_summary_rejected_without_overwriting_it(tmp_path):
    directory = tmp_path / "expanded"
    expanded.run(output_dir=directory, max_new_trials=1)
    summary = directory / "summary.json"
    altered = json.loads(summary.read_text(encoding="utf-8"))
    altered["completed_trial_records"] = 1000
    summary.write_text(json.dumps(altered), encoding="utf-8")
    original_bytes = summary.read_bytes()
    with pytest.raises(ValueError, match="summary disagrees"):
        audit_study("expanded", directory)
    assert summary.read_bytes() == original_bytes


def test_original_journal_is_not_repaired_when_corrupt(tmp_path):
    directory = tmp_path / "expanded"
    expanded.run(output_dir=directory, max_new_trials=1)
    journal = directory / "attempts.jsonl"
    original = journal.read_bytes() + b'{"truncated":true}'
    journal.write_bytes(original)
    with pytest.raises(ValueError, match="incomplete journal line"):
        audit_study("expanded", directory)
    assert journal.read_bytes() == original
