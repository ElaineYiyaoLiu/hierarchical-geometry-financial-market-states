"""Synthetic D06 full optimizer/tree checked handoff (Python 3.14)."""

from time import monotonic

import numpy as np
import pytest

from branch_b.bootstrap.d06_identity_boundary import build_d06_draw_boundary
from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.fitters.development_d06_fitter import D06DevelopmentFitter
from branch_b.fitters.exact_tie_dp import ExactD04DeadlineExpired
from branch_b.recovery_pipeline.d06_checked_handoff import checked_d06_distinct_fit


def boundary(draw):
    return build_d06_draw_boundary(
        np.asarray(draw, dtype=int),
        original_sample_order=["A", "B", "C"],
        fit_sample_order=[f"occ{i}" for i in range(len(draw))],
    )


def test_two_identity_weighted_development_fit_is_structurally_checked():
    b = boundary([0, 0, 1, 1, 1])
    normalized = np.array([[0., 1.], [1., 0.]])
    before = normalized.copy()
    fit = checked_d06_distinct_fit(
        normalized, boundary=b,
        fitter=D06DevelopmentFitter(deadline_monotonic=monotonic() + 30.0),
        random_seed=42,
    )
    np.testing.assert_array_equal(normalized, before)
    assert b.multiplicities == (2, 3)
    assert fit.tree["leaves"] == ["A", "B"]
    assert fit.diagnostics["outcome"] == "CONVERGED"
    assert fit.diagnostics["branch_b_seed"] == 42
    assert fit.diagnostics["scientific_authorization"] is False
    assert fit.ultrametric_matrix.shape == (2, 2)
    assert len(fit.diagnostics["objective_history"]) == fit.diagnostics["completed_updates"] + 1


def test_actual_expired_deadline_is_propagated():
    with pytest.raises(ExactD04DeadlineExpired):
        checked_d06_distinct_fit(
            [[0., 1.], [1., 0.]],
            boundary=boundary([0, 1]),
            fitter=D06DevelopmentFitter(deadline_monotonic=monotonic() - 1.0),
        )


def test_distinct_zero_denominator_remains_registered_failure():
    with pytest.raises(BranchBFailure) as error:
        checked_d06_distinct_fit(
            [[0., 0.], [0., 0.]], boundary=boundary([0, 1]),
            fitter=D06DevelopmentFitter(deadline_monotonic=monotonic() + 30.0),
        )
    assert error.value.code == FailureCode.DEGENERATE_DISTANCE


def test_one_distinct_original_is_unapproved_and_never_optimized():
    with pytest.raises(ConfigurationRequired, match="low-distinct"):
        checked_d06_distinct_fit(
            [[0.]], boundary=boundary([1, 1, 1]),
            fitter=D06DevelopmentFitter(deadline_monotonic=monotonic() + 30.0),
        )


def test_multiplicity_alignment_is_strict():
    fitter = D06DevelopmentFitter(deadline_monotonic=monotonic() + 30.0)
    with pytest.raises(ValueError, match="multiplicities"):
        fitter.fit_with_original_multiplicities(
            [[0., 1.], [1., 0.]], original_sample_order=["A", "B"],
            multiplicities=[1, 0],
        )
    with pytest.raises(ValueError, match="align"):
        fitter.fit_with_original_multiplicities(
            [[0., 1.], [1., 0.]], original_sample_order=["A", "B"],
            multiplicities=[2],
        )


def test_no_implicit_deadline_or_invalid_clock_value():
    with pytest.raises(TypeError):
        D06DevelopmentFitter()
    with pytest.raises(ValueError):
        D06DevelopmentFitter(deadline_monotonic=float("inf"))
