"""Exact min-max (subdominant) ultrametric operator on a complete graph.

This is an isolated deterministic mathematical primitive, not the optimizer,
its derivative, or a validated Common Fitter. Only synthetic development inputs
are used by its tests. The existing fitter remains fail-closed.
"""
from __future__ import annotations

import numpy as np

from branch_b.failures import BranchBFailure, FailureCode


def subdominant_ultrametric(weights: object) -> np.ndarray:
    """Return U[i,j] = min over paths i->j of max edge weight on the path.

    The Floyd-Warshall min-max recurrence is exact for finite nonnegative
    symmetric edge weights. It does not select an optimization objective,
    autodifferentiation convention, or tree serialization rule.
    """
    w = np.asarray(weights, dtype=float)
    if w.ndim != 2 or w.shape[0] != w.shape[1] or w.shape[0] < 2:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "weights must be square with at least two vertices")
    if not np.isfinite(w).all():
        raise BranchBFailure(FailureCode.NONFINITE_INPUT, "weights must be finite")
    if np.any(w < 0) or not np.allclose(w, w.T, rtol=0.0, atol=1e-12):
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "weights must be symmetric and nonnegative")
    if not np.allclose(np.diag(w), 0.0, rtol=0.0, atol=1e-12):
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "weights must have a zero diagonal")

    u = w.copy()
    np.fill_diagonal(u, 0.0)
    for k in range(u.shape[0]):
        u = np.minimum(u, np.maximum(u[:, [k]], u[[k], :]))
    np.fill_diagonal(u, 0.0)
    return u
