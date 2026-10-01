import numpy as np
import pytest

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.geometries import correlation_dissimilarity, correlation_profile_admissibility
from branch_b.preprocessing import as_finite_matrix


def test_nonfinite_observable_is_explicit_failure():
    x = np.zeros((2, 12))
    x[0, 0] = np.nan
    with pytest.raises(BranchBFailure) as exc:
        as_finite_matrix(x)
    assert exc.value.code == FailureCode.NONFINITE_INPUT


def test_correlation_admissibility_fails_closed_when_parameters_unset():
    x = np.arange(36, dtype=float).reshape(3, 12)
    with pytest.raises(ConfigurationRequired):
        correlation_profile_admissibility(
            x,
            tau_nc=None,
            tau_deg=None,
            s_min=None,
            quantile_method=None,
        )


def test_correlation_degeneracy_handling_fails_closed_when_needed():
    x = np.vstack([
        np.ones(12),
        np.arange(12, dtype=float),
    ])
    with pytest.raises(ConfigurationRequired):
        correlation_dissimilarity(
            x,
            tau_nc=0.2,
            tau_deg=0.1,
            s_min=1.0,
            quantile_method="linear",
            degeneracy_handling=None,
        )
