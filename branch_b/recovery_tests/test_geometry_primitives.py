import numpy as np

from branch_b.geometries import (
    chebyshev_dissimilarity,
    correlation_dissimilarity,
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


def test_raw_correlation_distance_uses_unstandardized_profiles():
    x = np.vstack([
        np.arange(12, dtype=float),
        np.arange(12, dtype=float)[::-1],
        np.arange(12, dtype=float) * 2.0 + 5.0,
    ])
    d = correlation_dissimilarity(x)
    assert np.allclose(np.diag(d), 0.0)
    assert d[0, 1] == np.float64(2.0)
    assert d[0, 2] == np.float64(0.0)
