from __future__ import annotations

import numpy as np

from branch_b.failures import BranchBFailure, FailureCode


COMMON_NORMALIZATION_RULE = "max_offdiagonal"
COMMON_NORMALIZATION_EPSILON = 1e-12


def _validate_dissimilarity(dissimilarity: object) -> np.ndarray:
    d = np.asarray(dissimilarity, dtype=float)
    if d.ndim != 2 or d.shape[0] != d.shape[1] or d.shape[0] < 2:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "dissimilarity must be a square matrix of size at least 2")
    if not np.isfinite(d).all():
        raise BranchBFailure(FailureCode.NONFINITE_INPUT, "dissimilarity contains non-finite values")
    if np.any(d < 0):
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "dissimilarity contains negative values")
    if not np.allclose(d, d.T, rtol=0.0, atol=1e-12):
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "dissimilarity is not symmetric")
    if not np.allclose(np.diag(d), 0.0, rtol=0.0, atol=1e-12):
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "dissimilarity diagonal is not zero")
    return d


def normalize_dissimilarity(
    dissimilarity: object,
    *,
    rule: str = COMMON_NORMALIZATION_RULE,
    epsilon: float = COMMON_NORMALIZATION_EPSILON,
) -> np.ndarray:
    """Apply the frozen common post-geometry max-off-diagonal normalization.

    N(Delta) = Delta / max_{i<j} Delta_ij.

    The same rule is used for every registered geometry. Positive scalar division
    preserves all finite off-diagonal orderings and exact ties.
    """
    if rule != COMMON_NORMALIZATION_RULE:
        raise ValueError(f"unsupported common normalization rule: {rule!r}")
    if not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon must be finite and strictly positive")

    d = _validate_dissimilarity(dissimilarity)
    tri = np.triu_indices(d.shape[0], k=1)
    scale = float(np.max(d[tri]))
    if scale <= epsilon:
        raise BranchBFailure(
            FailureCode.DEGENERATE_DISTANCE,
            "common normalization scale is zero or numerically degenerate",
        )

    normalized = d / scale
    np.fill_diagonal(normalized, 0.0)
    return normalized
