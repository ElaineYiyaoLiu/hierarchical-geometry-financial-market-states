"""Development-only exact-height ultrametric to unresolved rooted-tree conversion.

This isolated candidate uses differences between exact merge heights as branch
lengths. The height-to-branch-length interpretation still requires project
review before scientific use. No numerical tie tolerance is selected here.
No production fitter is registered or activated.
"""

from __future__ import annotations

import numpy as np

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.recovery_pipeline.result_validation import (
    checked_sample_order, validate_bound_tree,
)


def extract_exact_ultrametric_tree(ultrametric: object, *, sample_order: list[str]) -> dict:
    """Build one multifurcating cluster node per distinct exact merge cluster.

    Exact equal heights coalesce into a single unresolved multifurcation, not
    an arbitrary chain of binary merges. Input must be an exact finite symmetric
    nonnegative ultrametric. A tiny unequal difference is NOT rounded to a tie.
    Leaf heights are zero. Equal parent/child heights retain zero-length edges.
    """
    order = checked_sample_order(sample_order)
    if np.ma.isMaskedArray(ultrametric):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "masked ultrametric")
    raw = np.asarray(ultrametric)
    if raw.ndim != 2 or raw.shape != (len(order), len(order)) or raw.dtype.kind not in "iuf":
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "ultrametric shape or scalar type is invalid")
    u = raw.astype(float, copy=True)
    if not np.isfinite(u).all() or np.any(u < 0):
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "ultrametric must be finite and nonnegative")
    if not np.array_equal(u, u.T) or np.any(np.diag(u) != 0):
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "ultrametric must have exact symmetry and zero diagonal")
    n = len(order)
    if n < 2:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "at least two original identities required")
    for k in range(n):
        if np.any(u > np.maximum(u[:, [k]], u[[k], :])):
            raise BranchBFailure(FailureCode.DEGENERATE_TREE, "matrix violates ultrametric inequality")

    # At every distinct merge height, equivalence classes of u_ij <= height
    # define the clusters. Using each class once avoids artificial binary
    # refinement at ties, including at the zero merge height.
    heights = sorted({float(u[i, j]) for i in range(n) for j in range(i + 1, n)})
    named: dict[frozenset[int], str] = {
        frozenset((i,)): order[i] for i in range(n)
    }
    node_heights: dict[frozenset[int], float] = {
        frozenset((i,)): 0.0 for i in range(n)
    }
    occupied = set(order)
    internal: list[str] = []
    new_clusters: list[frozenset[int]] = []
    counter = 0

    for h in heights:
        unvisited = set(range(n))
        components = []
        while unvisited:
            seed = min(unvisited)
            component = frozenset(j for j in range(n) if u[seed, j] <= h)
            # A validated ultrametric guarantees transitivity of this relation.
            unvisited.difference_update(component)
            if len(component) > 1 and component not in named:
                components.append(component)
        for component in sorted(components, key=lambda c: tuple(sorted(c))):
            while True:
                candidate = f"__d06_internal_{counter}"
                counter += 1
                if candidate not in occupied:
                    break
            occupied.add(candidate)
            named[component] = candidate
            node_heights[component] = h
            internal.append(candidate)
            new_clusters.append(component)

    root_cluster = frozenset(range(n))
    if root_cluster not in named:
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "root cluster is absent")
    root = named[root_cluster]
    edges = []
    for parent_cluster in new_clusters:
        # Its direct children are the maximal previously-created proper
        # subclusters (including singleton leaves).
        smaller = [c for c in named if c < parent_cluster]
        children = [
            c for c in smaller
            if not any(c < other < parent_cluster for other in smaller)
        ]
        children.sort(key=lambda c: tuple(sorted(c)))
        for child in children:
            length = node_heights[parent_cluster] - node_heights[child]
            if length < 0:
                raise BranchBFailure(FailureCode.DEGENERATE_TREE, "negative tree branch")
            edges.append({
                "parent": named[parent_cluster],
                "child": named[child],
                "branch_length": float(length),
                "unresolved": bool(length == 0 or len(children) > 2),
            })

    tree = {
        "tree_format_version": "1",
        "root": root,
        "internal_nodes": internal,
        "leaves": order,
        "edges": edges,
    }
    validate_bound_tree(tree, sample_order=order)
    return tree
