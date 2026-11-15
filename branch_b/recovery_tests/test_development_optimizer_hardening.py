"""Development-only integration hardening using synthetic inputs (Python 3.14).

The 1000-update test deliberately stubs the *objective* to force persistent
nonconvergence; it tests optimizer-loop accounting, not convergence on data.
No hidden data, scientific timeout value, or production failure mapping is used.
"""

from time import monotonic

import pytest

import branch_b.fitters.development_optimizer as loop
from branch_b.fitters.exact_tie_dp import ExactD04DeadlineExpired


def test_real_two_vertex_repeatability_excluding_elapsed_clock():
    first = loop.run_development_optimizer(
        (0.8,), (2, 3), deadline_monotonic=monotonic() + 30.0
    )
    second = loop.run_development_optimizer(
        (0.8,), (2, 3), deadline_monotonic=monotonic() + 30.0
    )
    assert first.outcome == second.outcome == "CONVERGED"
    assert first.completed_updates == second.completed_updates
    assert first.weights == second.weights
    assert first.ultrametric == second.ultrametric
    assert first.objective_history == second.objective_history
    assert first.relative_change_history == second.relative_change_history


def test_full_1000_completed_updates_produce_iteration_cap(monkeypatch):
    calls = {"objective": 0, "gradient": 0}

    def deliberately_nonconvergent_objective(ultrametric, delta, masses):
        # First call is J0. Subsequent completed-update objectives alternate
        # between 1 and 2 so the five-small-change stopping rule never fires.
        calls["objective"] += 1
        value = 1.0 if calls["objective"] % 2 else 2.0
        return value, (0.0,)

    def zero_gradient(n, weights, upstream, *, deadline_monotonic):
        calls["gradient"] += 1
        return (0.0,)

    monkeypatch.setattr(
        loop, "soft_cardinality_objective_gradient",
        deliberately_nonconvergent_objective,
    )
    monkeypatch.setattr(loop, "exact_d04_weight_gradient", zero_gradient)

    result = loop.run_development_optimizer(
        (0.8,), (1, 1), deadline_monotonic=monotonic() + 30.0
    )
    assert result.outcome == "ITERATION_CAP"
    assert result.completed_updates == 1000
    assert len(result.objective_history) == 1001
    assert len(result.relative_change_history) == 1000
    assert calls == {"objective": 2001, "gradient": 1000}
    assert result.weights == (0.8,)
    assert set(result.objective_history) == {1.0, 2.0}
    assert all(change > 1e-6 for change in result.relative_change_history)


def test_expired_deadline_is_not_iteration_cap():
    with pytest.raises(ExactD04DeadlineExpired):
        loop.run_development_optimizer(
            (0.8,), (1, 1), deadline_monotonic=monotonic() - 1.0
        )


def test_numerical_error_is_not_reclassified_as_timeout(monkeypatch):
    def arithmetic_failure(n, weights, upstream, *, deadline_monotonic):
        raise ArithmeticError("synthetic optimizer arithmetic failure")

    monkeypatch.setattr(loop, "exact_d04_weight_gradient", arithmetic_failure)
    with pytest.raises(ArithmeticError, match="synthetic optimizer arithmetic failure"):
        loop.run_development_optimizer(
            (0.8,), (1, 1), deadline_monotonic=monotonic() + 30.0
        )


def test_deadline_expiration_inside_d04_is_propagated(monkeypatch):
    def deadline_failure(n, weights, upstream, *, deadline_monotonic):
        raise ExactD04DeadlineExpired(
            processed_weight_levels=0, maximum_stage_states=7
        )

    monkeypatch.setattr(loop, "exact_d04_weight_gradient", deadline_failure)
    with pytest.raises(ExactD04DeadlineExpired) as captured:
        loop.run_development_optimizer(
            (0.8,), (1, 1), deadline_monotonic=monotonic() + 30.0
        )
    assert captured.value.maximum_stage_states == 7
