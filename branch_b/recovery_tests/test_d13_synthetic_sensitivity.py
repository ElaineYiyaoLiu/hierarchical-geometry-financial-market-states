"""Synthetic-only D13 sensitivity journal tests; run under Python 3.14."""

import json

import pytest

from branch_b.tools.d13_synthetic_sensitivity import _trial, run


def test_independent_failure_ledger_is_complete():
    row = _trial(0, 0)
    assert row["attempted"] == 60
    assert row["succeeded"] + row["failed"] == row["attempted"]
    assert row["statuses"].count("FAILED") == row["failed"]
    assert row["statuses"].count("SUCCEEDED") == row["succeeded"]


def test_score_dependent_target_is_different_from_all_attempt_target():
    row = _trial(1, 0)
    assert row["calculable"]
    assert row["conditional_target"] == pytest.approx(1.0 / 3.0)
    assert row["all_attempt_target"] == 0.0


def test_shared_shift_scenario_has_explicit_unconditional_target():
    row = _trial(2, 0)
    assert row["calculable"]
    assert row["failed"] == 0
    assert row["succeeded"] == 60
    assert row["conditional_target"] == 0.0


def test_resume_does_not_duplicate_journal_rows(tmp_path):
    output = tmp_path / "sensitivity"
    first = run(output, max_new_trials=1)
    assert first["completed_records"] == 1
    journal = (output / "attempts.jsonl").read_bytes()
    assert run(output, max_new_trials=0) == first
    assert journal == (output / "attempts.jsonl").read_bytes()
    second = run(output, max_new_trials=1)
    assert second["completed_records"] == 2
    rows = [json.loads(line) for line in (output / "attempts.jsonl").read_text().splitlines()]
    assert len(rows) == 2
    assert [x["result"]["trial_index"] for x in rows] == [0, 1]


def test_corrupted_design_fails_closed(tmp_path):
    output = tmp_path / "sensitivity"
    run(output, max_new_trials=0)
    config = json.loads((output / "design.json").read_text())
    config["outer_trials"] = 1
    (output / "design.json").write_text(json.dumps(config))
    with pytest.raises(ValueError, match="design differs"):
        run(output, max_new_trials=0)


def test_duplicate_attempt_fails_closed(tmp_path):
    output = tmp_path / "sensitivity"
    run(output, max_new_trials=1)
    file = output / "attempts.jsonl"
    file.write_bytes(file.read_bytes() * 2)
    with pytest.raises(ValueError, match="duplicate"):
        run(output, max_new_trials=0)


def test_invalid_batch_limit_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="max_new_trials"):
        run(tmp_path / "sensitivity", max_new_trials=-1)
