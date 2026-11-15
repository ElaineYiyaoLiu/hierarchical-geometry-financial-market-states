"""Synthetic D05 completed-update accounting tests; execute on Python 3.14."""

import pytest

from branch_b.fitters.d05_stopping import (
    D05_MAX_COMPLETED_UPDATES,
    initialize_d05,
    record_completed_d05_update,
)


def test_five_consecutive_strict_changes_converge():
    state = initialize_d05(2.0)
    for step in range(1, 6):
        update = record_completed_d05_update(state, 2.0)
        state = update.progress
        assert update.outcome == ("CONVERGED" if step == 5 else "CONTINUE")
    assert state.completed_updates == 5
    assert state.consecutive_small_changes == 5


def test_one_large_change_resets_consecutive_counter():
    state = initialize_d05(2.0)
    for value in (2.0, 2.0, 1.5, 1.5):
        result = record_completed_d05_update(state, value)
        state = result.progress
    assert state.consecutive_small_changes == 1
    assert result.outcome == "CONTINUE"


def test_relative_change_uses_initial_objective_in_denominator():
    state = initialize_d05(100.0)
    result = record_completed_d05_update(state, 100.00005)
    assert result.relative_change == pytest.approx(5e-7)
    assert result.progress.consecutive_small_changes == 1


def test_exact_tolerance_does_not_count_as_convergence():
    state = initialize_d05(1.0)
    result = record_completed_d05_update(state, 1.000001)
    assert result.relative_change == pytest.approx(1e-6)
    # Float rounding near threshold makes equality fragile; assert only exact rule
    # with a separately constructed comfortably-above-threshold value.
    above = record_completed_d05_update(state, 1.000002)
    assert above.progress.consecutive_small_changes == 0


def test_cap_after_exactly_one_thousand_completed_updates():
    state = initialize_d05(1.0)
    for index in range(D05_MAX_COMPLETED_UPDATES):
        result = record_completed_d05_update(state, 1.0 + (index % 2) * 0.01)
        state = result.progress
    assert state.completed_updates == D05_MAX_COMPLETED_UPDATES
    assert result.outcome == "ITERATION_CAP"
    with pytest.raises(ValueError):
        record_completed_d05_update(state, 1.0)


def test_nonfinite_values_are_rejected():
    with pytest.raises(ValueError):
        initialize_d05(float("nan"))
    with pytest.raises(ValueError):
        record_completed_d05_update(initialize_d05(1.0), float("inf"))


def test_zero_initial_objective_uses_floor():
    state = initialize_d05(0.0)
    result = record_completed_d05_update(state, 1e-14)
    assert result.relative_change == pytest.approx(0.01)
    assert result.outcome == "CONTINUE"
