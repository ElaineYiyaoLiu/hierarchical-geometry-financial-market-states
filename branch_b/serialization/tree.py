from __future__ import annotations

from collections import Counter

from branch_b.failures import BranchBFailure, FailureCode


def validate_tree_edge_list(tree: dict, sample_order: list[str]) -> None:
    required = {"tree_format_version", "root", "internal_nodes", "leaves", "edges"}
    if not isinstance(tree, dict) or not required.issubset(tree):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree edge list is missing required fields")

    leaves = tree["leaves"]
    if leaves != sample_order:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree leaves must match canonical sample order exactly")

    root = tree["root"]
    internal = tree["internal_nodes"]
    if root not in internal:
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "tree root must be listed as an internal node")

    nodes = set(internal) | set(leaves)
    if len(nodes) != len(internal) + len(leaves):
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "internal-node and leaf identifiers must be disjoint")

    parent_count: Counter[str] = Counter()
    children: dict[str, list[str]] = {}
    for edge in tree["edges"]:
        if set(edge) - {"parent", "child", "branch_length", "unresolved"}:
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree edge contains unsupported fields")
        parent = edge.get("parent")
        child = edge.get("child")
        length = edge.get("branch_length")
        unresolved = edge.get("unresolved", False)
        if parent not in nodes or child not in nodes:
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree edge references an unknown node")
        if not isinstance(length, (int, float)) or length < 0:
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "branch length must be non-negative")
        if not isinstance(unresolved, bool):
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "unresolved must be boolean when present")
        parent_count[child] += 1
        children.setdefault(parent, []).append(child)

    if parent_count[root] != 0:
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "root cannot have a parent")
    for node in nodes - {root}:
        if parent_count[node] != 1:
            raise BranchBFailure(FailureCode.DEGENERATE_TREE, "every non-root node must have exactly one parent")

    seen: set[str] = set()
    active: set[str] = set()

    def visit(node: str) -> None:
        if node in active:
            raise BranchBFailure(FailureCode.DEGENERATE_TREE, "cycle detected in tree")
        if node in seen:
            return
        active.add(node)
        for child in children.get(node, []):
            visit(child)
        active.remove(node)
        seen.add(node)

    visit(root)
    if seen != nodes:
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "tree contains nodes unreachable from the root")
