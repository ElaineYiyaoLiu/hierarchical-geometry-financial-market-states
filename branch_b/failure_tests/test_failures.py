import numpy as np
import pytest

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.geometries import correlation_dissimilarity
from branch_b.preprocessing import as_finite_matrix


def test_nonfinite_observable_is_explicit_failure():
    x = np.zeros((2, 12))
    x[0, 0] = np.nan
    with pytest.raises(BranchBFailure) as exc:
        as_finite_matrix(x)
    assert exc.value.code == FailureCode.NONFINITE_INPUT


def test_correlation_threshold_fails_closed_when_unset():
    x = np.arange(36, dtype=float).reshape(3, 12)
    with pytest.raises(ConfigurationRequired):
        correlation_dissimilarity(x, near_constant_scale_threshold=None)
