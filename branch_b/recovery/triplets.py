from __future__ import annotations

from itertools import combinations

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.serialization import validate_tree_edge_list


def _effective_root_depths(tree: dict) -> dict[str, float]:
    """Cumulative root depth after contracting unresolved and zero-length edges."""
    children: dict[str, list[tuple[str, float]]] = {}
    for edge in tree["edges"]:
        length = float(edge["branch_length"])
        if edge.get("unresolved", False) or length == 0.0:
            effective = 0.0
        else:
            effective = length
        children.setdefault(edge["parent"], []).append((edge["child"], effective))

    root = tree["root"]
    depth = {root: 0.0}
    stack = [root]
    while stack:
        parent = stack.pop()
        for child, increment in children.get(parent, []):
            if child in depth:
                raise BranchBFailure(FailureCode.DEGENERATE_TREE, "tree contains repeated reachability")
            depth[child] = depth[parent] + increment
            stack.append(child)
    return depth


def _parent_map(tree: dict) -> dict[str, str]:
    return {edge["child"]: edge["parent"] for edge in tree["edges"]}


def _ancestor_set(node: str, parent: dict[str, str], root: str) -> set[str]:
    out = {node}
    current = node
    while current != root:
        if current not in parent:
            raise BranchBFailure(FailureCode.DEGENERATE_TREE, "node is disconnected from root")
        current = parent[current]
        if current in out:
            raise BranchBFailure(FailureCode.DEGENERATE_TREE, "cycle detected in tree")
        out.add(current)
    return out


def rooted_triplet_closest_pair(tree: dict, triplet: tuple[str, str, str]) -> tuple[str, str] | None:
    """Return the uniquely deepest pair, or None when the estimated triplet is unresolved.

    Zero-length or explicitly unresolved edges are contracted for this comparison, as
    required by the primary rooted-triplet convention.
    """
    sample_order = tree["leaves"]
    validate_tree_edge_list(tree, sample_order)
    if len(set(triplet)) != 3 or any(leaf not in set(sample_order) for leaf in triplet):
        raise ValueError("triplet must contain three distinct tree leaves")

    parent = _parent_map(tree)
    depth = _effective_root_depths(tree)
    root = tree["root"]
    ancestors = {leaf: _ancestor_set(leaf, parent, root) for leaf in triplet}

    pair_depths: dict[tuple[str, str], float] = {}
    for a, b in combinations(triplet, 2):
        common = ancestors[a] & ancestors[b]
        lca = max(common, key=lambda node: depth[node])
        pair_depths[tuple(sorted((a, b)))] = depth[lca]

    max_depth = max(pair_depths.values())
    winners = [pair for pair, d in pair_depths.items() if np_isclose(d, max_depth)]
    if len(winners) != 1:
        return None

    other_depths = [d for pair, d in pair_depths.items() if pair != winners[0]]
    if any(np_isclose(max_depth, d) for d in other_depths):
        return None
    return winners[0]


def np_isclose(a: float, b: float, *, atol: float = 1e-12) -> bool:
    return abs(a - b) <= atol


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
