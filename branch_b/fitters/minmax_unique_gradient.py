"""Synthetic-development derivative reference for tie-free min-max ultrametrics.

This diagnostic is deliberately not wired into the Common Fitter. It provides
a unique-bottleneck Jacobian reference only when *all* undirected edge weights
are distinct. It refuses tied inputs instead of choosing a scientific tie rule.
"""
from __future__ import annotations

import numpy as np

from branch_b.failures import ConfigurationRequired
from branch_b.fitters.minmax_operator import subdominant_ultrametric


def unique_bottleneck_jacobian(weights: object) -> tuple[np.ndarray, np.ndarray]:
    """Return (undirected edge pairs, Jacobian) for tie-free complete graphs.

    Jacobian[a, b] is d Phi(W)[i,j] / d W[p,q], where a indexes
    the lexicographically ordered pair (i,j), b indexes (p,q), i<j, p<q.
    A minimum-spanning-tree path has a unique maximum-weight edge when
    all input edge weights are distinct. This is a diagnostic, not a
    differentiable optimizer kernel or a tie/subgradient policy.
    """
    u = subdominant_ultrametric(weights)
    w = np.asarray(weights, dtype=float)
    n = w.shape[0]
    i, j = np.triu_indices(n, k=1)
    pairs = np.column_stack((i, j))
    values = w[i, j]
    if np.unique(values).size != values.size:
        raise ConfigurationRequired(
            "unique-bottleneck diagnostic cannot select derivatives at tied weights"
        )

    order = np.argsort(values)
    parent = list(range(n))

    def find(vertex: int) -> int:
        while parent[vertex] != vertex:
            vertex = parent[vertex]
        return vertex

    adjacency: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for edge_id in order:
        a, b = map(int, pairs[edge_id])
        ra, rb = find(a), find(b)
        if ra == rb:
            continue
        parent[ra] = rb
        adjacency[a].append((b, int(edge_id)))
        adjacency[b].append((a, int(edge_id)))

    jacobian = np.zeros((len(pairs), len(pairs)), dtype=float)
    for row, (source, target) in enumerate(pairs):
        stack = [(int(source), -1, ())]
        while stack:
            node, previous, path = stack.pop()
            if node == target:
                bottleneck = max(path, key=lambda edge_id: values[edge_id])
                jacobian[row, bottleneck] = 1.0
                if u[source, target] != values[bottleneck]:
                    raise AssertionError("min-max and spanning-tree bottlenecks disagree")
                break
            for neighbor, edge_id in adjacency[node]:
                if neighbor != previous:
                    stack.append((neighbor, node, (*path, edge_id)))
        else:
            raise AssertionError("complete-graph spanning tree is disconnected")
    return pairs, jacobian
