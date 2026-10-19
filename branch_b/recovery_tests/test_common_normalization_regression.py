"""Development regression tests for the registered common normalization.

These use synthetic matrices only and do not change any frozen scientific rule.
Execute with the repository's Python 3.14 CI workflow.
"""
import numpy as np
import pytest

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.normalization import normalize_dissimilarity


def test_common_normalization_preserves_order_and_ties():
    d = np.array([
        [0.0, 2.0, 2.0],
        [2.0, 0.0, 4.0],
        [2.0, 4.0, 0.0],
    ])
    result = normalize_dissimilarity(d)
    assert np.array_equal(result, d / 4.0)
    assert result[0, 1] == result[0, 2]
    assert np.max(result[np.triu_indices(3, 1)]) == 1.0


@pytest.mark.parametrize("scale", [0.0, 1e-12])
def test_common_normalization_rejects_registered_degenerate_scales(scale):
    d = np.array([[0.0, scale], [scale, 0.0]])
    with pytest.raises(BranchBFailure) as exc:
        normalize_dissimilarity(d)
    assert exc.value.code == FailureCode.DEGENERATE_DISTANCE


def test_common_normalization_rejects_nonfinite_input():
    d = np.array([[0.0, np.nan], [np.nan, 0.0]])
    with pytest.raises(BranchBFailure) as exc:
        normalize_dissimilarity(d)
    assert exc.value.code == FailureCode.NONFINITE_INPUT


def test_common_normalization_rejects_asymmetry():
    d = np.array([[0.0, 1.0], [2.0, 0.0]])
    with pytest.raises(BranchBFailure) as exc:
        normalize_dissimilarity(d)
    assert exc.value.code == FailureCode.DEGENERATE_DISTANCE
