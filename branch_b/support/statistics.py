from __future__ import annotations

import numpy as np

from branch_b.failures import BranchBFailure, FailureCode


def normalized_ultrametric_distortion(dissimilarity: object, ultrametric: object) -> float:
    delta = np.asarray(dissimilarity, dtype=float)
    u = np.asarray(ultrametric, dtype=float)
    if delta.ndim != 2 or delta.shape[0] != delta.shape[1] or u.shape != delta.shape:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "dissimilarity and ultrametric must be same-size square matrices")
    if not np.isfinite(delta).all() or not np.isfinite(u).all():
        raise BranchBFailure(FailureCode.NONFINITE_INPUT, "support matrices contain non-finite values")
    tri = np.triu_indices(delta.shape[0], k=1)
    denom = float(np.sum(delta[tri]))
    if denom <= 0:
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "dissimilarity has zero off-diagonal mass")
    return float(np.sum(np.abs(u[tri] - delta[tri])) / denom)


def q_statistic(stability: float, distortion: float) -> float:
    if not np.isfinite(stability) or not np.isfinite(distortion):
        raise BranchBFailure(FailureCode.NONFINITE_INPUT, "support statistic inputs must be finite")
    if distortion < 0:
        raise ValueError("distortion must be non-negative")
    return float(stability - min(distortion, 1.0))
