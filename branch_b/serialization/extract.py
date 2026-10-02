from __future__ import annotations

from collections import defaultdict

import numpy as np

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.serialization.tree import validate_tree_edge_list


def _validate_ultrametric(u: object, *, atol: float = 1e-12) -> np.ndarray:
    d = np.asarray(u, dtype=float)
    if d.ndim != 2 or d.shape[0] != d.shape[1] or d.shape[0] < 2:
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "ultrametric must be square with at least two leaves")
    if not np.isfinite(d).all() or np.any(d < 0):
        raise BranchBFailure(FailureCode.NUMERICAL_FIT, "ultrametric contains invalid values")
    if not np.allclose(d, d.T, rtol=0.0, atol=atol):
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "ultrametric is not symmetric")
    if not np.allclose(np.diag(d), 0.0, rtol=0.0, atol=atol):
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "ultrametric diagonal is not zero")

    n = d.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                a, b, c = d[i, j], d[i, k], d[j, k]
                if a > max(b, c) + atol or b > max(a, c) + atol or c > max(a, b) + atol:
                    raise BranchBFailure(FailureCode.DEGENERATE_TREE, "matrix violates the ultrametric inequality")
    return d


def ultrametric_to_tree(
    ultrametric: object,
    sample_order: list[str],
    *,
    tree_format_version: str = "1",
) -> dict:
    """Convert an ultrametric to a deterministic rooted edge-list without binary tie breaking."""
    d = _validate_ultrametric(ultrametric)
    n = d.shape[0]
    if len(sample_order) != n or len(set(sample_order)) != n:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "sample_order must uniquely match ultrametric size")

    positive_or_zero = sorted(set(float(d[i, j]) for i in range(n) for j in range(i + 1, n)))
    active = {frozenset([i]): sample_order[i] for i in range(n)}
    altitude = {sample_order[i]: 0.0 for i in range(n)}
    internal_nodes: list[str] = []
    edges: list[dict] = []
    next_internal = 1

    for height in positive_or_zero:
        groups: dict[frozenset[int], list[frozenset[int]]] = defaultdict(list)

        # At an ultrametric threshold, d <= height defines equivalence classes.
        for cluster in active:
            representative = min(cluster)
            eq = frozenset(j for j in range(n) if d[representative, j] <= height + 1e-12)
            groups[eq].append(cluster)

        changed = False
        new_active = dict(active)
        for eq, children_clusters in sorted(groups.items(), key=lambda item: min(item[0])):
            unique_children = []
            seen = set()
            for c in children_clusters:
                if c not in seen:
                    seen.add(c)
                    unique_children.append(c)
            if len(unique_children) <= 1:
                continue
            if frozenset().union(*unique_children) != eq:
                continue

            node_id = f"I{next_internal:06d}"
            next_internal += 1
            internal_nodes.append(node_id)
            altitude[node_id] = height
            unresolved_node = len(unique_children) > 2

            for child_cluster in sorted(unique_children, key=lambda c: min(c)):
                child_id = active[child_cluster]
                branch_length = max(0.0, height - altitude[child_id])
                edges.append({
                    "parent": node_id,
                    "child": child_id,
                    "branch_length": branch_length,
                    "unresolved": bool(unresolved_node or branch_length == 0.0),
                })
                new_active.pop(child_cluster, None)

            new_active[eq] = node_id
            changed = True

        if changed:
            active = new_active

    if len(active) != 1:
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "ultrametric did not yield one rooted hierarchy")

    root = next(iter(active.values()))
    if root in sample_order:
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "ultrametric collapsed to a single leaf")

    tree = {
        "tree_format_version": tree_format_version,
        "root": root,
        "internal_nodes": internal_nodes,
        "leaves": list(sample_order),
        "edges": edges,
    }
    validate_tree_edge_list(tree, sample_order)
    return tree
