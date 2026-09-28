from __future__ import annotations

from itertools import combinations

from branch_b.recovery.lca import lca_depths


def rooted_triplet_closest_pair(tree: dict, triplet: tuple[str, str, str]) -> tuple[str, str] | None:
    leaves = list(triplet)
    depths = lca_depths(tree, tree["leaves"])
    pair_depths = {}
    for a, b in combinations(leaves, 2):
        key = (a, b) if (a, b) in depths else (b, a)
        pair_depths[tuple(sorted((a, b)))] = depths[key]

    max_depth = max(pair_depths.values())
    winners = [pair for pair, d in pair_depths.items() if d == max_depth]
    if len(winners) != 1:
        return None
    return winners[0]


def rooted_triplet_accuracy(reference_tree: dict, estimated_tree: dict, sample_order: list[str]) -> float:
    total = 0
    correct = 0
    for triplet in combinations(sample_order, 3):
        reference = rooted_triplet_closest_pair(reference_tree, triplet)
        estimated = rooted_triplet_closest_pair(estimated_tree, triplet)
        total += 1
        if reference is not None and estimated == reference:
            correct += 1
    if total == 0:
        raise ValueError("at least three leaves are required for rooted-triplet accuracy")
    return correct / total
