import pytest

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.serialization import validate_tree_edge_list


def test_tree_rejects_unreachable_cycle():
    tree = {
        "tree_format_version": "1",
        "root": "R",
        "internal_nodes": ["R", "I", "J"],
        "leaves": ["A"],
        "edges": [
            {"parent": "R", "child": "A", "branch_length": 1.0},
            {"parent": "I", "child": "J", "branch_length": 0.0},
            {"parent": "J", "child": "I", "branch_length": 0.0},
        ],
    }
    with pytest.raises(BranchBFailure) as exc:
        validate_tree_edge_list(tree, ["A"])
    assert exc.value.code == FailureCode.DEGENERATE_TREE
