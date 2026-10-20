from __future__ import annotations

from collections import Counter
from math import isfinite

from branch_b.failures import BranchBFailure, FailureCode


def validate_tree_edge_list(tree: dict, sample_order: list[str]) -> None:
    required = {"tree_format_version", "root", "internal_nodes", "leaves", "edges"}
    if not isinstance(tree, dict) or not required.issubset(tree):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree edge list is missing required fields")

    leaves = tree["leaves"]
    internal = tree["internal_nodes"]
    if not isinstance(leaves, list) or not all(isinstance(node, str) for node in leaves):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree leaves must be a list of identifiers")
    if not isinstance(internal, list) or not all(isinstance(node, str) for node in internal):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree internal nodes must be a list of identifiers")
    if not isinstance(tree["root"], str):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree root must be an identifier")
    if leaves != sample_order:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree leaves must match canonical sample order exactly")

    root = tree["root"]
    if root not in internal:
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "tree root must be listed as an internal node")

    nodes = set(internal) | set(leaves)
    if len(nodes) != len(internal) + len(leaves):
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "internal-node and leaf identifiers must be disjoint")

    if not isinstance(tree["edges"], list):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree edges must be a list")

    parent_count: Counter[str] = Counter()
    children: dict[str, list[str]] = {}
    for edge in tree["edges"]:
        if not isinstance(edge, dict):
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "each tree edge must be an object")
        if set(edge) - {"parent", "child", "branch_length", "unresolved"}:
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree edge contains unsupported fields")
        parent = edge.get("parent")
        child = edge.get("child")
        length = edge.get("branch_length")
        unresolved = edge.get("unresolved", False)
        if not isinstance(parent, str) or not isinstance(child, str):
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree edge endpoints must be identifiers")
        if parent not in nodes or child not in nodes:
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "tree edge references an unknown node")
        if parent in leaves:
            raise BranchBFailure(FailureCode.DEGENERATE_TREE, "a leaf cannot be the parent of a tree edge")
        if isinstance(length, bool) or not isinstance(length, (int, float)) or not isfinite(length) or length < 0:
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "branch length must be finite and non-negative")
        if not isinstance(unresolved, bool):
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "unresolved must be boolean when present")
        parent_count[child] += 1
        children.setdefault(parent, []).append(child)

    # An internal node with no outgoing edge would create an undeclared leaf.
    # Multifurcations remain valid; only terminal-node identity is checked.
    if any(not children.get(node) for node in internal):
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "internal node has no children")

    if parent_count[root] != 0:
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "root cannot have a parent")
    for node in nodes - {root}:
        if parent_count[node] != 1:
            raise BranchBFailure(FailureCode.DEGENERATE_TREE, "every non-root node must have exactly one parent")

    # Iterative depth-first traversal avoids Python recursion limits on deep trees.
    seen: set[str] = set()
    active: set[str] = set()
    stack: list[tuple[str, bool]] = [(root, False)]
    while stack:
        node, exiting = stack.pop()
        if exiting:
            active.remove(node)
            seen.add(node)
            continue
        if node in active:
            raise BranchBFailure(FailureCode.DEGENERATE_TREE, "cycle detected in tree")
        if node in seen:
            continue
        active.add(node)
        stack.append((node, True))
        stack.extend((child, False) for child in reversed(children.get(node, [])))
    if seen != nodes:
        raise BranchBFailure(FailureCode.DEGENERATE_TREE, "tree contains nodes unreachable from the root")
