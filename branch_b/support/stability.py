from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from branch_b.failures import BranchBFailure, FailureCode


def average_ranks(values: np.ndarray) -> np.ndarray:
    """Return 1-based average ranks with average ranks assigned to ties."""
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or not np.isfinite(x).all():
        raise BranchBFailure(FailureCode.NONFINITE_INPUT, "rank inputs must be a finite 1D array")

    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=float)
    i = 0
    while i < len(x):
        j = i + 1
        while j < len(x) and x[order[j]] == x[order[i]]:
            j += 1
        avg = (i + 1 + j) / 2.0
        ranks[order[i:j]] = avg
        i = j
    return ranks


def spearman_with_average_ties(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape or x.ndim != 1:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "Spearman inputs must be equal-length 1D arrays")
    if len(x) < 2:
        raise BranchBFailure(FailureCode.INSUFFICIENT_BOOTSTRAP, "at least two ranked relations are required")

    rx = average_ranks(x)
    ry = average_ranks(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denom = float(np.sqrt(np.sum(rx * rx) * np.sum(ry * ry)))
    if denom == 0:
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "LCA-depth ranks are constant")
    return float(np.sum(rx * ry) / denom)


def lca_depth_stability(
    full_depths: Mapping[tuple[str, str], int | float],
    bootstrap_depths: Mapping[tuple[str, str], int | float],
) -> float:
    """Spearman agreement on pairwise LCA depths shared by full and bootstrap trees."""
    common = sorted(set(full_depths) & set(bootstrap_depths))
    if len(common) < 2:
        raise BranchBFailure(
            FailureCode.INSUFFICIENT_BOOTSTRAP,
            "too few common pairwise LCA-depth relations for stability",
        )
    full = np.asarray([full_depths[k] for k in common], dtype=float)
    boot = np.asarray([bootstrap_depths[k] for k in common], dtype=float)
    return spearman_with_average_ties(full, boot)
