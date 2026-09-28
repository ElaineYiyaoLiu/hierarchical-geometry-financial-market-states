from __future__ import annotations

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.serialization import validate_tree_edge_list


def _parent_map(tree: dict) -> dict[str, str]:
    return {edge["child"]: edge["parent"] for edge in tree["edges"]}


def _depths(tree: dict) -> dict[str, int]:
    children: dict[str, list[str]] = {}
    for edge in tree["edges"]:
        children.setdefault(edge["parent"], []).append(edge["child"])
    root = tree["root"]
    out = {root: 0}
    stack = [root]
    while stack:
        node = stack.pop()
        for child in children.get(node, []):
            if child in out:
                raise BranchBFailure(FailureCode.DEGENERATE_TREE, "cycle or duplicate reachability detected")
            out[child] = out[node] + 1
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
    validate_tree_edge_list(tree, sample_order)
    parent = _parent_map(tree)
    depth = _depths(tree)
    root = tree["root"]
    result: dict[tuple[str, str], int] = {}
    ancestors = {leaf: _ancestors(leaf, parent, root) for leaf in sample_order}
    ancestor_sets = {leaf: set(path) for leaf, path in ancestors.items()}

    for i, a in enumerate(sample_order):
        for b in sample_order[i + 1 :]:
            common = ancestor_sets[a] & ancestor_sets[b]
            if not common:
                raise BranchBFailure(FailureCode.DEGENERATE_TREE, "pair has no common ancestor")
            lca = max(common, key=lambda node: depth[node])
            result[(a, b)] = depth[lca]
    return result
