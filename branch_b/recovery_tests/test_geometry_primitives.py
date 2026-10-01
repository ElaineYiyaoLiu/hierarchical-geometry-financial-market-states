import numpy as np
import pytest

from branch_b.geometries import (
    CORRELATION_ROBUST_SPREAD_LOWER_QUANTILE,
    CORRELATION_ROBUST_SPREAD_UPPER_QUANTILE,
    chebyshev_dissimilarity,
    correlation_profile_admissibility,
    euclidean_dissimilarity,
)


def test_chebyshev_matrix_is_symmetric_zero_diagonal():
    x = np.vstack([np.zeros(12), np.ones(12), np.full(12, 2.0)])
    d = chebyshev_dissimilarity(x)
    assert np.allclose(d, d.T)
    assert np.allclose(np.diag(d), 0.0)
    assert d[0, 2] == 2.0


def test_euclidean_matrix_is_symmetric_zero_diagonal():
    x = np.vstack([np.zeros(12), np.ones(12)])
    d = euclidean_dissimilarity(x)
    assert np.allclose(d, d.T)
    assert np.allclose(np.diag(d), 0.0)
    assert d[0, 1] == np.sqrt(12.0)


def test_correlation_robust_spread_uses_5th_and_95th_quantiles():
    assert CORRELATION_ROBUST_SPREAD_LOWER_QUANTILE == 0.05
    assert CORRELATION_ROBUST_SPREAD_UPPER_QUANTILE == 0.95

    x = np.vstack([
        np.arange(12, dtype=float),
        np.full(12, 5.0),
    ])
    result = correlation_profile_admissibility(
        x,
        tau_nc=0.2,
        tau_deg=0.1,
        s_min=1.0,
        quantile_method="linear",
    )

    expected_spread = np.quantile(x, 0.95, axis=1, method="linear") - np.quantile(
        x, 0.05, axis=1, method="linear"
    )
    assert np.allclose(result["robust_spread"], expected_spread)
    assert result["status"][0] == "ordinary"
    assert result["status"][1] == "near_constant_degeneracy"


def test_relative_spread_denominator_uses_median_abs_floor():
    x = np.vstack([
        np.array([-0.01, 0.01] * 6, dtype=float),
        np.arange(1, 13, dtype=float),
    ])
    result = correlation_profile_admissibility(
        x,
        tau_nc=0.5,
        tau_deg=0.1,
        s_min=2.0,
        quantile_method="linear",
    )
    assert result["denominator"][0] == pytest.approx(2.0)
