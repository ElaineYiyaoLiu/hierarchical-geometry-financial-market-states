"""Synthetic properties of the isolated min-max ultrametric operator.

Run only in the configured Python 3.14 Branch B CI environment.
"""
import numpy as np
import pytest

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.fitters.minmax_operator import subdominant_ultrametric


def test_three_vertex_bottleneck_path():
    w = np.array([[0.0, 2.0, 5.0], [2.0, 0.0, 3.0], [5.0, 3.0, 0.0]])
    expected = np.array([[0.0, 2.0, 3.0], [2.0, 0.0, 3.0], [3.0, 3.0, 0.0]])
    assert np.array_equal(subdominant_ultrametric(w), expected)


def test_minmax_is_idempotent_and_ultrametric():
    w = np.array([
        [0.0, 4.0, 8.0, 7.0],
        [4.0, 0.0, 3.0, 9.0],
        [8.0, 3.0, 0.0, 2.0],
        [7.0, 9.0, 2.0, 0.0],
    ])
    u = subdominant_ultrametric(w)
    assert np.array_equal(subdominant_ultrametric(u), u)
    assert np.array_equal(u, u.T)
    assert np.all(u <= w)
    for i in range(len(u)):
        for j in range(len(u)):
            for k in range(len(u)):
                assert u[i, j] <= max(u[i, k], u[k, j])


def test_minmax_does_not_mutate_input():
    w = np.array([[0.0, 1.0], [1.0, 0.0]])
    before = w.copy()
    subdominant_ultrametric(w)
    assert np.array_equal(w, before)


@pytest.mark.parametrize("w,code", [
    (np.array([[0.0, np.inf], [np.inf, 0.0]]), FailureCode.NONFINITE_INPUT),
    (np.array([[0.0, 1.0], [2.0, 0.0]]), FailureCode.DEGENERATE_DISTANCE),
    (np.array([[0.0, -1.0], [-1.0, 0.0]]), FailureCode.DEGENERATE_DISTANCE),
    (np.array([[0.0, 1.0, 2.0]]), FailureCode.INPUT_SCHEMA),
])
def test_minmax_rejects_invalid_weights(w, code):
    with pytest.raises(BranchBFailure) as exc:
        subdominant_ultrametric(w)
    assert exc.value.code == code
