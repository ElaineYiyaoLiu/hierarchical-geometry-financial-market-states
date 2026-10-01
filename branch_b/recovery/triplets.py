from __future__ import annotations

from itertools import combinations

from branch_b.recovery.lca import lca_depths
from branch_b.serialization import validate_tree_edge_list


def rooted_triplet_closest_pair(tree: dict, triplet: tuple[str, str, str]) -> tuple[str, str] | None:
    """Return the uniquely deepest pair, or None when the triplet is unresolved.

    Depth is resolved topological depth after zero-length and explicitly unresolved
    edges are contracted. Positive branch-length magnitudes do not affect the
    rooted-triplet relationship.
    """
    sample_order = tree["leaves"]
    validate_tree_edge_list(tree, sample_order)
    leaf_set = set(sample_order)
    if len(set(triplet)) != 3 or any(leaf not in leaf_set for leaf in triplet):
        raise ValueError("triplet must contain three distinct tree leaves")

    depths = lca_depths(tree, sample_order)
    pair_depths: dict[tuple[str, str], int] = {}
    for a, b in combinations(triplet, 2):
        key = (a, b) if (a, b) in depths else (b, a)
        pair_depths[tuple(sorted((a, b)))] = depths[key]

    max_depth = max(pair_depths.values())
    winners = [pair for pair, value in pair_depths.items() if value == max_depth]
    if len(winners) != 1:
        return None
    return winners[0]


def rooted_triplet_accuracy(reference_tree: dict, estimated_tree: dict, sample_order: list[str]) -> float:
    total = 0
    correct = 0
    for triplet in combinations(sample_order, 3):
        reference = rooted_triplet_closest_pair(reference_tree, triplet)
        if reference is None:
            continue
        estimated = rooted_triplet_closest_pair(estimated_tree, triplet)
        total += 1
        if estimated == reference:
            correct += 1
    if total == 0:
        raise ValueError("no reference-resolved triplets are available")
    return correct / total
