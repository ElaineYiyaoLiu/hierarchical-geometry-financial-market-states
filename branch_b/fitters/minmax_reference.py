"""Reference min-max ultrametric transform for development tests.

This is the forward transform Phi_G for a connected graph; it does not assign
gradients at ties, optimize a loss, or select a scientific failure category.
"""
from __future__ import annotations

import numpy as np

from branch_b.fitters.positive_edge_graph import PositiveEdgeGraph


def minmax_ultrametric(graph: PositiveEdgeGraph, working_weights: object) -> np.ndarray:
    """Return pairwise minimum-bottleneck path distances on a connected graph.

    Uses the recurrence d(i,j) = min(d(i,j), max(d(i,k), d(k,j))).
    Does not edit input arrays, impute missing links, or add infinite roots.
    """
    if not graph.connected:
        raise ValueError("min-max transform requires a connected graph")
    raw = np.asarray(working_weights)
    if raw.dtype.kind not in "iuf" or raw.ndim != 1 or raw.shape != graph.weights.shape:
        raise ValueError("working weights must match retained edge count")
    weight = raw.astype(float, copy=True)
    if not np.isfinite(weight).all() or (weight < 0).any():
        raise ValueError("working weights must be finite and nonnegative")
    n = graph.n_vertices
    distances = np.full((n, n), np.inf, dtype=float)
    np.fill_diagonal(distances, 0.0)
    for (i, j), w in zip(graph.edges, weight, strict=True):
        i, j = int(i), int(j)
        distances[i, j] = w
        distances[j, i] = w
    for k in range(n):
        distances = np.minimum(distances, np.maximum(distances[:, k, None], distances[k, None, :]))
    if not np.isfinite(distances).all():
        raise ValueError("connected graph produced nonfinite min-max distance")
    return distances
