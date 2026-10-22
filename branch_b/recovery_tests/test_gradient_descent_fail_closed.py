"""Synthetic interface checks for the not-yet-executable Common Fitter.

These tests do not exercise or substitute for the scientific optimizer.
"""

import numpy as np
import pytest

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.fitters.gradient_descent import (
    GradientDescentFitterConfig,
    GradientDescentUltrametricFitter,
)


def test_valid_synthetic_input_fails_closed_without_optimizer_kernel():
    fitter = GradientDescentUltrametricFitter()
    d = np.array([[0.0, 0.5, 1.0], [0.5, 0.0, 0.75], [1.0, 0.75, 0.0]])
    original = d.copy()

    with pytest.raises(ConfigurationRequired, match="optimizer kernel"):
        fitter.fit(d)

    np.testing.assert_array_equal(d, original)


@pytest.mark.parametrize(
    "matrix, failure_code",
    [
        (np.zeros((2, 3)), FailureCode.INPUT_SCHEMA),
        (np.array([[0.0, np.nan], [np.nan, 0.0]]), FailureCode.NONFINITE_INPUT),
        (np.array([[0.0, 0.5], [0.6, 0.0]]), FailureCode.DEGENERATE_DISTANCE),
        (np.array([[0.0, 0.0], [0.0, 0.0]]), FailureCode.DEGENERATE_DISTANCE),
        (np.array([[0.0, -0.5], [-0.5, 0.0]]), FailureCode.DEGENERATE_DISTANCE),
    ],
)
def test_invalid_synthetic_input_is_rejected_before_kernel(matrix, failure_code):
    fitter = GradientDescentUltrametricFitter()
    with pytest.raises(BranchBFailure) as caught:
        fitter.fit(matrix)
    assert caught.value.code == failure_code


def test_pilot_timeout_setting_does_not_enable_unimplemented_kernel():
    fitter = GradientDescentUltrametricFitter(
        GradientDescentFitterConfig(timeout_seconds=10.0)
    )
    d = np.array([[0.0, 1.0], [1.0, 0.0]])
    with pytest.raises(ConfigurationRequired, match="optimizer kernel"):
        fitter.fit(d)


@pytest.mark.parametrize(
    "malformed_input, failure_code",
    [
        (
            [["not-a-number", "also-not-a-number"], ["x", "y"]],
            FailureCode.INPUT_SCHEMA,
        ),
        # Original-value validation rejects None before floating-point coercion.
        ([[0.0, None], [None, 0.0]], FailureCode.INPUT_SCHEMA),
        (object(), FailureCode.INPUT_SCHEMA),
    ],
)
def test_malformed_input_has_structured_failure(malformed_input, failure_code):
    fitter = GradientDescentUltrametricFitter()
    with pytest.raises(BranchBFailure) as caught:
        fitter.fit(malformed_input)
    assert caught.value.code == failure_code
