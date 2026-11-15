"""Synthetic Python 3.14 integration tests for the development-only loop."""

from time import monotonic

import pytest

from branch_b.fitters.development_optimizer import (
    DevelopmentOptimizerDeadlineExpired, run_development_optimizer,
)


def test_two_vertex_composite_converges_and_keeps_last_iterate():
    result = run_development_optimizer(
        (0.8,), (1, 1), deadline_monotonic=monotonic() + 30.0
    )
    assert result.outcome == "CONVERGED"
    assert 5 <= result.completed_updates <= 1000
    assert len(result.objective_history) == result.completed_updates + 1
    assert len(result.relative_change_history) == result.completed_updates
    assert result.weights[0] >= 0
    assert result.ultrametric == result.weights
    assert result.objective_history[-1] <= result.objective_history[0]


def test_weighted_two_vertex_composite_converges():
    result = run_development_optimizer(
        (0.8,), (2, 3), deadline_monotonic=monotonic() + 30.0
    )
    assert result.outcome == "CONVERGED"
    assert result.completed_updates <= 1000
    assert result.weights[0] >= 0


def test_actual_expired_deadline_propagates_unchanged():
    with pytest.raises(DevelopmentOptimizerDeadlineExpired):
        run_development_optimizer(
            (0.8,), (1, 1), deadline_monotonic=monotonic() - 1.0
        )


def test_invalid_fixed_denominator_is_not_floored():
    with pytest.raises(ValueError, match="denominators"):
        run_development_optimizer(
            (0.0,), (1, 1), deadline_monotonic=monotonic() + 30.0
        )


def test_input_identity_and_domain_validation():
    with pytest.raises(ValueError):
        run_development_optimizer(
            (0.8, 0.9), (1, 1), deadline_monotonic=monotonic() + 30.0
        )
    with pytest.raises(ValueError):
        run_development_optimizer(
            (0.8,), (1, 0), deadline_monotonic=monotonic() + 30.0
        )
