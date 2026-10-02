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
    """Euclidean dissimilarity on an already standardized observable representation."""
    x = as_finite_matrix(standardized_values)
    diff = x[:, None, :] - x[None, :, :]
    d = np.sqrt(np.sum(diff * diff, axis=2))
    return _validate_distance_matrix(d)


def chebyshev_dissimilarity(preprocessed_values: object) -> np.ndarray:
    """Chebyshev dissimilarity on an already standardized observable representation."""
    x = as_finite_matrix(preprocessed_values)
    diff = np.abs(x[:, None, :] - x[None, :, :])
    d = np.max(diff, axis=2)
    return _validate_distance_matrix(d)


def correlation_profile_admissibility(observable_profiles: object) -> dict:
    """Fail closed until Branch B freezes the quantitative correlation-admissibility rule.

    No near-constant statistic, quantile construction, threshold, or deterministic
    handling rule is approved yet. This placeholder prevents an earlier draft rule
    from being treated as frozen scientific methodology.
    """
    as_finite_matrix(observable_profiles)
    raise ConfigurationRequired(
        "correlation admissibility/near-constant rule is pending the explicit Branch B meeting"
    )


def correlation_dissimilarity(observable_profiles: object) -> np.ndarray:
    """Raw Pearson-correlation distance on the released observable profiles.

    Coordinate preprocessing is intentionally absent. This primitive does not claim
    confirmatory admissibility: the separate quantitative near-constant/admissibility
    rule remains unapproved. Exactly constant profiles are mathematically undefined
    for Pearson correlation and therefore fail explicitly.
    """
    x = as_finite_matrix(observable_profiles)

    centered = x - x.mean(axis=1, keepdims=True)
    scales = np.sqrt(np.sum(centered * centered, axis=1))
    if np.any(scales <= 0):
        raise BranchBFailure(
            FailureCode.DEGENERATE_DISTANCE,
            "Pearson correlation is undefined for an exactly constant observable profile",
        )

    corr = (centered @ centered.T) / np.outer(scales, scales)
    corr = np.clip(corr, -1.0, 1.0)
    d = 1.0 - corr
    np.fill_diagonal(d, 0.0)
    return _validate_distance_matrix(d)
