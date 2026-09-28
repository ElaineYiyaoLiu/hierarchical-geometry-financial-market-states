from __future__ import annotations

import numpy as np

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.preprocessing import as_finite_matrix


def _validate_distance_matrix(d: np.ndarray) -> np.ndarray:
    if not np.isfinite(d).all():
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "distance matrix contains non-finite values")
    if not np.allclose(d, d.T, rtol=0.0, atol=1e-12):
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "distance matrix is not symmetric")
    if not np.allclose(np.diag(d), 0.0, rtol=0.0, atol=1e-12):
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "distance matrix diagonal is not zero")
    if np.any(d < 0):
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "distance matrix contains negative entries")
    return d


def euclidean_dissimilarity(standardized_values: object) -> np.ndarray:
    """Euclidean dissimilarity on an already standardized observable representation.

    Standardization is intentionally not estimated here: train-estimated preprocessing is
    a separate pipeline stage so validation/test data cannot leak into fit parameters.
    """
    x = as_finite_matrix(standardized_values)
    diff = x[:, None, :] - x[None, :, :]
    d = np.sqrt(np.sum(diff * diff, axis=2))
    return _validate_distance_matrix(d)


def chebyshev_dissimilarity(preprocessed_values: object) -> np.ndarray:
    """Chebyshev dissimilarity on an already preprocessed observable representation.

    This implements only the recorded native distance family. The unresolved
    valuation-geometry preprocessing specification remains outside this function.
    """
    x = as_finite_matrix(preprocessed_values)
    diff = np.abs(x[:, None, :] - x[None, :, :])
    d = np.max(diff, axis=2)
    return _validate_distance_matrix(d)


def correlation_dissimilarity(
    observable_profiles: object,
    *,
    near_constant_scale_threshold: float | None,
) -> np.ndarray:
    """Pearson-correlation distance with an explicit unresolved admissibility parameter.

    The project has not yet frozen the quantitative near-constant threshold. Passing
    None therefore fails closed rather than inventing a value.
    """
    x = as_finite_matrix(observable_profiles)
    if near_constant_scale_threshold is None:
        raise ConfigurationRequired(
            "correlation near-constant admissibility threshold has not yet been frozen"
        )
    if not np.isfinite(near_constant_scale_threshold) or near_constant_scale_threshold < 0:
        raise ValueError("near_constant_scale_threshold must be finite and non-negative")

    centered = x - x.mean(axis=1, keepdims=True)
    scales = np.sqrt(np.sum(centered * centered, axis=1))
    if np.any(scales <= near_constant_scale_threshold):
        raise BranchBFailure(
            FailureCode.DEGENERATE_DISTANCE,
            "correlation geometry inadmissible: constant/near-constant observable profile",
        )

    corr = (centered @ centered.T) / np.outer(scales, scales)
    corr = np.clip(corr, -1.0, 1.0)
    d = 1.0 - corr
    np.fill_diagonal(d, 0.0)
    return _validate_distance_matrix(d)
