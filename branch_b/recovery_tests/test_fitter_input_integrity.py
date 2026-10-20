"""Synthetic input-integrity tests for the non-executable Common Fitter candidate.

These tests exercise validation only; they do not implement or certify a
scientific optimizer, objective, or pilot configuration.
"""
import numpy as np
import pytest

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.fitters.gradient_descent import GradientDescentUltrametricFitter


def _matrix():
    return np.array([[0.0, 2.0, 3.0], [2.0, 0.0, 4.0], [3.0, 4.0, 0.0]])


def test_fitter_accepts_finite_real_symmetric_synthetic_matrix():
    original = _matrix()
    checked = GradientDescentUltrametricFitter().validate_normalized_input(original)
    assert np.array_equal(checked, original)
    assert not np.shares_memory(checked, original)


@pytest.mark.parametrize("invalid", [
    np.array([[False, True], [True, False]]),
    [[0, True], [True, 0]],
    np.array([[0, 2], [2, 0]], dtype=object),
    np.array([["0", "2"], ["2", "0"]]),
    np.array([[0j, 2+0j], [2+0j, 0j]]),
    np.ma.array(_matrix(), mask=[[False, False, False], [False, True, False], [False, False, False]]),
    [[0, 2], [2]],
])
def test_fitter_rejects_lossy_or_non_numeric_input(invalid):
    with pytest.raises(BranchBFailure) as caught:
        GradientDescentUltrametricFitter().validate_normalized_input(invalid)
    assert caught.value.code == FailureCode.INPUT_SCHEMA


def test_fitter_rejects_nested_masked_scalar():
    nested = [[0, np.ma.masked], [np.ma.masked, 0]]
    with pytest.raises(BranchBFailure) as caught:
        GradientDescentUltrametricFitter().validate_normalized_input(nested)
    assert caught.value.code == FailureCode.INPUT_SCHEMA


@pytest.mark.parametrize("field,value", [
    ("convergence_patience", True),
    ("convergence_patience", 2.5),
    ("convergence_patience", 0),
    ("max_iterations", False),
    ("max_iterations", 1.5),
    ("max_iterations", -1),
])
def test_fitter_rejects_invalid_iteration_count_types(field, value):
    from branch_b.fitters.gradient_descent import GradientDescentFitterConfig

    with pytest.raises(ValueError, match="positive integers"):
        GradientDescentUltrametricFitter(
            GradientDescentFitterConfig(**{field: value})
        )
