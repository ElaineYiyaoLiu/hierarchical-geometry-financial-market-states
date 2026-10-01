from __future__ import annotations

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.serialization import validate_tree_edge_list


def _parent_map(tree: dict) -> dict[str, str]:
    return {edge["child"]: edge["parent"] for edge in tree["edges"]}


def _effective_topological_depths(tree: dict) -> dict[str, int]:
    """Resolved topological depth after contracting zero-length/unresolved edges.

    Every positive, resolved parent-child edge contributes one level. A zero-length
    edge or an edge explicitly marked unresolved contributes zero levels. Positive
    branch-length magnitudes otherwise have no effect on hierarchical depth.
    """
    children: dict[str, list[tuple[str, int]]] = {}
    for edge in tree["edges"]:
        increment = 0 if edge.get("unresolved", False) or float(edge["branch_length"]) == 0.0 else 1
        children.setdefault(edge["parent"], []).append((edge["child"], increment))

    root = tree["root"]
    out = {root: 0}
    stack = [root]
    while stack:
        node = stack.pop()
        for child, increment in children.get(node, []):
            if child in out:
                raise BranchBFailure(
                    FailureCode.DEGENERATE_TREE,
                    "cycle or duplicate reachability detected",
                )
            out[child] = out[node] + increment
            stack.append(child)
    return out


def _ancestors(node: str, parent: dict[str, str], root: str) -> list[str]:
    result = [node]
    seen = {node}
    while result[-1] != root:
        cur = result[-1]
        if cur not in parent:
            raise BranchBFailure(FailureCode.DEGENERATE_TREE, "node is not connected to root")
        nxt = parent[cur]
        if nxt in seen:
            raise BranchBFailure(FailureCode.DEGENERATE_TREE, "cycle detected in tree")
        seen.add(nxt)
        result.append(nxt)
    return result


def lca_depths(tree: dict, sample_order: list[str]) -> dict[tuple[str, str], int]:
    """Pairwise LCA depths on the contracted resolved topology."""
    validate_tree_edge_list(tree, sample_order)
    parent = _parent_map(tree)
    depth = _effective_topological_depths(tree)
    root = tree["root"]
    result: dict[tuple[str, str], int] = {}
    ancestors = {leaf: _ancestors(leaf, parent, root) for leaf in sample_order}
    ancestor_sets = {leaf: set(path) for leaf, path in ancestors.items()}

    for i, a in enumerate(sample_order):
        for b in sample_order[i + 1 :]:
            common = ancestor_sets[a] & ancestor_sets[b]
            if not common:
                raise BranchBFailure(FailureCode.DEGENERATE_TREE, "pair has no common ancestor")
            lca_depth = max(depth[node] for node in common)
            result[(a, b)] = lca_depth
    return result
