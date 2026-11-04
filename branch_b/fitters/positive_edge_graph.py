"""Observable-only graph preparation for the proposed zero-edge D01 convention.

Development utility only. It does not change the registered Common Fitter,
choose a scientific failure code, or construct an infinite-root tree.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from branch_b.fitters._reference_input import reject_lossy_reference_input


@dataclass(frozen=True)
class PositiveEdgeGraph:
    n_vertices: int
    edges: np.ndarray
    weights: np.ndarray
    components: tuple[tuple[int, ...], ...]

    @property
    def connected(self) -> bool:
        return len(self.components) == 1


def positive_edge_graph(dissimilarity: object) -> PositiveEdgeGraph:
    """Keep edges strictly above the fixed tolerance, retaining all vertices.

    Off-diagonal weights at or below 1e-12 are removed. No diagonal repair,
    edge insertion, or failure-code assignment is performed.
    """
    reject_lossy_reference_input(dissimilarity)
    raw = np.asarray(dissimilarity)
    if np.ma.isMaskedArray(dissimilarity) or raw.dtype.kind not in "iuf":
        raise ValueError("expected an unmasked real numeric dissimilarity matrix")
    if raw.ndim != 2 or raw.shape[0] != raw.shape[1] or raw.shape[0] < 2:
        raise ValueError("expected a square matrix with at least two vertices")
    d = raw.astype(float, copy=True)
    if not np.isfinite(d).all() or np.any(d < 0):
        raise ValueError("dissimilarities must be finite and nonnegative")
    if not np.array_equal(d, d.T) or not np.array_equal(np.diag(d), np.zeros(d.shape[0])):
        raise ValueError("expected exactly symmetric matrix with zero diagonal")
    n = d.shape[0]
    i, j = np.triu_indices(n, k=1)
    keep = d[i, j] > 1e-12
    edges = np.column_stack((i[keep], j[keep]))
    weights = d[i[keep], j[keep]].copy()
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        a, b = int(u), int(v)
        adjacency[a].append(b)
        adjacency[b].append(a)
    seen = set()
    components = []
    for vertex in range(n):
        if vertex in seen:
            continue
        queue = [vertex]
        seen.add(vertex)
        component = []
        for u in queue:
            component.append(u)
            for v in adjacency[u]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        components.append(tuple(sorted(component)))
    return PositiveEdgeGraph(n, edges, weights, tuple(components))
