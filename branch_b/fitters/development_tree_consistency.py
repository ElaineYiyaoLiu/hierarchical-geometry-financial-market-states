"""Independent development-only reconstruction of tree cophenetic heights.

This checks the current *candidate* convention: root-to-leaf path lengths
represent a common root height, and the height of each pair's LCA gives
the ultrametric entry. Floating-point comparison policy is NOT frozen.
Strict equality here is for exact representable synthetic fixtures only;
do not use as the production numerical acceptance gate.
"""

from __future__ import annotations

from math import fsum

import numpy as np

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.recovery_pipeline.result_validation import (
    checked_sample_order, validate_bound_tree, validate_finite_square,
)


def reconstruct_candidate_ultrametric(tree: dict, *, sample_order: list[str]) -> np.ndarray:
    """Independently reconstruct pair cophenetic heights from a valid tree.

    Does not consult the ultrametric used to create the tree. Refuses unequal
    root-to-leaf distances, since that would not encode the candidate
    height-difference convention. Does not silently round unequal heights.
    """
    order = checked_sample_order(sample_order)
    validate_bound_tree(tree, sample_order=order)
    parent = {}
    length = {}
    for edge in tree["edges"]:
        child = edge["child"]
        parent[child] = edge["parent"]
        length[child] = float(edge["branch_length"])
    root = tree["root"]
    ancestry: dict[str, tuple[str, ...]] = {}
    heights: dict[str, float] = {}
    for leaf in order:
        nodes = [leaf]
        weights = []
        node = leaf
        while node != root:
            weights.append(length[node])
            node = parent[node]
            nodes.append(node)
        ancestry[leaf] = tuple(nodes)
        heights[leaf] = fsum(weights)
    if len(set(heights.values())) != 1:
        raise BranchBFailure(
            FailureCode.DEGENERATE_TREE,
            "candidate tree has unequal root-to-leaf heights",
        )
    result = np.zeros((len(order), len(order)), dtype=float)
    for i, left in enumerate(order):
        left_ancestors = set(ancestry[left])
        for j in range(i + 1, len(order)):
            right = order[j]
            ancestor = next(
                node for node in ancestry[right] if node in left_ancestors
            )
            # Walk from one leaf to the LCA. fsum improves arithmetic stability
            # but introduces no floating-point tolerance.
            path = []
            node = left
            while node != ancestor:
                path.append(length[node])
                node = parent[node]
            value = fsum(path)
            result[i, j] = result[j, i] = value
    return result


def candidate_tree_exactly_matches_matrix(
    tree: dict, ultrametric: object, *, sample_order: list[str]
) -> bool:
    """Exact equality for synthetic tests, not a scientific comparison rule."""
    order = checked_sample_order(sample_order)
    validate_finite_square(ultrametric, size=len(order))
    reconstructed = reconstruct_candidate_ultrametric(
        tree, sample_order=order
    )
    return bool(np.array_equal(reconstructed, np.asarray(ultrametric)))
