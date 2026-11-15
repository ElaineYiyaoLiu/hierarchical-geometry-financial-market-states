"""Synthetic-only D03 Option A AMSGrad tests; execute with Python 3.14."""

from math import sqrt

import numpy as np
import pytest

from branch_b.fitters.d03_amsgrad import (
    AMSGradState,
    initialize_amsgrad,
    projected_amsgrad_step,
)


def test_first_step_matches_hand_calculation_and_preserves_inputs():
    weights = np.array([0.4, 0.2])
    gradient = np.array([2.0, -4.0])
    original_weights, original_gradient = weights.copy(), gradient.copy()
    state = initialize_amsgrad(weights)
    updated, next_state = projected_amsgrad_step(weights, gradient, state)
    expected = np.maximum(0, weights - 0.01 * gradient / (np.abs(gradient) + 1e-8))
    np.testing.assert_allclose(updated, expected, rtol=0, atol=1e-14)
    np.testing.assert_allclose(next_state.first_moment, 0.1 * gradient)
    np.testing.assert_allclose(next_state.second_moment, 0.001 * gradient**2)
    np.testing.assert_array_equal(next_state.maximum_raw_second_moment,
                                  next_state.second_moment)
    assert next_state.t == 1 and state.t == 0
    np.testing.assert_array_equal(weights, original_weights)
    np.testing.assert_array_equal(gradient, original_gradient)


def test_running_maximum_is_raw_before_bias_correction():
    w = np.array([1.0])
    state = initialize_amsgrad(w)
    w, state = projected_amsgrad_step(w, [2.0], state)
    m1, v1 = 0.2, 0.004
    assert state.t == 1
    np.testing.assert_allclose(state.second_moment, [v1])
    w2, state2 = projected_amsgrad_step(w, [0.0], state)
    m2 = 0.9 * m1
    v2 = 0.999 * v1
    assert state2.t == 2
    np.testing.assert_allclose(state2.second_moment, [v2])
    np.testing.assert_allclose(state2.maximum_raw_second_moment, [v1])
    denominator = sqrt(v1 / (1.0 - 0.999**2)) + 1e-8
    expected_w2 = w[0] - 0.01 * (m2 / (1.0 - 0.9**2)) / denominator
    assert w2[0] == pytest.approx(expected_w2, abs=1e-14)


def test_projection_after_full_update_does_not_mask_gradient_or_moments():
    weights = [0.001, 0.0]
    gradient = [100.0, -2.0]
    updated, state = projected_amsgrad_step(weights, gradient, initialize_amsgrad(weights))
    assert updated[0] == 0.0
    assert updated[1] > 0.0
    assert state.first_moment[0] > 0
    assert state.first_moment[1] < 0
    assert state.second_moment[0] > 0


def test_zero_gradient_with_zero_moments_is_stable():
    updated, state = projected_amsgrad_step([0.0, 0.5], [0.0, 0.0],
                                            initialize_amsgrad([0.0, 0.5]))
    np.testing.assert_array_equal(updated, [0.0, 0.5])
    np.testing.assert_array_equal(state.second_moment, [0.0, 0.0])


def test_state_and_returned_weights_are_read_only_snapshots():
    state = initialize_amsgrad([0.4])
    updated, next_state = projected_amsgrad_step([0.4], [1.0], state)
    assert not updated.flags.writeable
    assert not next_state.first_moment.flags.writeable
    assert not next_state.second_moment.flags.writeable
    assert not next_state.maximum_raw_second_moment.flags.writeable


@pytest.mark.parametrize("weights,gradient", [
    ([-1.0], [1.0]),
    ([0.5], [float("nan")]),
    ([0.5], [float("inf")]),
    ([0.5], [True]),
    ([0.5], [1.0, 2.0]),
    ([], []),
])
def test_invalid_step_input_rejected(weights, gradient):
    with pytest.raises(ValueError):
        state = initialize_amsgrad(weights)
        projected_amsgrad_step(weights, gradient, state)


def test_invalid_moment_state_rejected():
    state = AMSGradState(1, np.array([0.0]), np.array([0.2]), np.array([0.1]))
    with pytest.raises(ValueError, match="maximum"):
        projected_amsgrad_step([0.5], [1.0], state)
