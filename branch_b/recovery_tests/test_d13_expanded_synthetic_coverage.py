"""Synthetic-only expanded D13 study journal and resume checks (Python 3.14)."""

import json

import pytest

from branch_b.tools.d13_expanded_synthetic_coverage import OUTER_TRIALS, run


def test_one_trial_then_resume_does_not_duplicate_or_change_result(tmp_path):
    first = run(output_dir=tmp_path / "study", max_new_trials=1)
    assert first["completed_trial_records"] == 1
    assert first["all_cells_complete"] is False
    saved = (tmp_path / "study" / "attempts.jsonl").read_bytes()
    repeat = run(output_dir=tmp_path / "study", max_new_trials=0)
    assert repeat == first
    assert (tmp_path / "study" / "attempts.jsonl").read_bytes() == saved
    second = run(output_dir=tmp_path / "study", max_new_trials=1)
    assert second["completed_trial_records"] == 2
    lines = (tmp_path / "study" / "attempts.jsonl").read_text().splitlines()
    assert len(lines) == 2
    rows = [json.loads(line)["result"] for line in lines]
    assert [row["trial_index"] for row in rows] == [0, 1]
    assert second["total_planned_trial_records"] == 3 * 2 * OUTER_TRIALS


def test_design_mismatch_is_not_silently_accepted(tmp_path):
    location = tmp_path / "study"
    run(output_dir=location, max_new_trials=0)
    altered = json.loads((location / "design.json").read_text())
    altered["outer_trials_per_cell"] = 1
    (location / "design.json").write_text(json.dumps(altered))
    with pytest.raises(ValueError, match="design manifest"):
        run(output_dir=location, max_new_trials=0)


def test_incomplete_journal_line_is_explicitly_rejected(tmp_path):
    location = tmp_path / "study"
    run(output_dir=location, max_new_trials=0)
    (location / "attempts.jsonl").write_text('{"incomplete":true}', encoding="utf-8")
    with pytest.raises(ValueError, match="incomplete journal line"):
        run(output_dir=location, max_new_trials=0)


def test_invalid_trial_limit_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="max_new_trials"):
        run(output_dir=tmp_path / "study", max_new_trials=-1)
