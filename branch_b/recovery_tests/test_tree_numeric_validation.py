"""Synthetic regression tests for finite tree branch lengths (Python 3.14 CI)."""
from copy import deepcopy

import pytest

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.serialization.tree import validate_tree_edge_list


def two_leaf_tree():
    return {
        "tree_format_version": "1",
        "root": "I000001",
        "internal_nodes": ["I000001"],
        "leaves": ["S1", "S2"],
        "edges": [
            {"parent": "I000001", "child": "S1", "branch_length": 0.0},
            {"parent": "I000001", "child": "S2", "branch_length": 1.0},
        ],
    }


def test_zero_length_branch_remains_valid():
    validate_tree_edge_list(two_leaf_tree(), ["S1", "S2"])


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -float("inf"), True, -1.0])
def test_invalid_branch_length_rejected(invalid):
    tree = deepcopy(two_leaf_tree())
    tree["edges"][0]["branch_length"] = invalid
    with pytest.raises(BranchBFailure) as exc:
        validate_tree_edge_list(tree, ["S1", "S2"])
    assert exc.value.code == FailureCode.OUTPUT_SCHEMA


def test_leaf_cannot_parent_another_leaf():
    tree = {
        "tree_format_version": "1",
        "root": "I000001",
        "internal_nodes": ["I000001"],
        "leaves": ["S1", "S2"],
        "edges": [
            {"parent": "I000001", "child": "S1", "branch_length": 0.0},
            {"parent": "S1", "child": "S2", "branch_length": 1.0},
        ],
    }
    with pytest.raises(BranchBFailure) as exc:
        validate_tree_edge_list(tree, ["S1", "S2"])
    assert exc.value.code == FailureCode.DEGENERATE_TREE


def test_unresolved_multifurcation_with_zero_branches_is_valid():
    tree = {
        "tree_format_version": "1",
        "root": "I000001",
        "internal_nodes": ["I000001"],
        "leaves": ["S1", "S2", "S3"],
        "edges": [
            {"parent": "I000001", "child": "S1", "branch_length": 0.0, "unresolved": True},
            {"parent": "I000001", "child": "S2", "branch_length": 0.0, "unresolved": True},
            {"parent": "I000001", "child": "S3", "branch_length": 0.0, "unresolved": True},
        ],
    }
    validate_tree_edge_list(tree, ["S1", "S2", "S3"])


def test_duplicate_parent_edges_are_structurally_invalid():
    tree = two_leaf_tree()
    tree["edges"].append(dict(tree["edges"][0]))
    with pytest.raises(BranchBFailure) as exc:
        validate_tree_edge_list(tree, ["S1", "S2"])
    assert exc.value.code == FailureCode.DEGENERATE_TREE


@pytest.mark.parametrize("invalid_edges", [None, "not-an-edge-list", {"parent": "I000001"}])
def test_invalid_edge_collection_reports_schema_failure(invalid_edges):
    tree = two_leaf_tree()
    tree["edges"] = invalid_edges
    with pytest.raises(BranchBFailure) as exc:
        validate_tree_edge_list(tree, ["S1", "S2"])
    assert exc.value.code == FailureCode.OUTPUT_SCHEMA


@pytest.mark.parametrize("invalid_edge", [None, "edge", 42, ["I000001", "S1"]])
def test_invalid_edge_item_reports_schema_failure(invalid_edge):
    tree = two_leaf_tree()
    tree["edges"][0] = invalid_edge
    with pytest.raises(BranchBFailure) as exc:
        validate_tree_edge_list(tree, ["S1", "S2"])
    assert exc.value.code == FailureCode.OUTPUT_SCHEMA


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("leaves", None),
        ("leaves", "S1"),
        ("leaves", ["S1", {"id": "S2"}]),
        ("internal_nodes", None),
        ("internal_nodes", "I000001"),
        ("internal_nodes", [None]),
        ("root", {"id": "I000001"}),
    ],
)
def test_invalid_tree_node_container_types_report_schema_failure(field, invalid):
    tree = two_leaf_tree()
    tree[field] = invalid
    with pytest.raises(BranchBFailure) as exc:
        validate_tree_edge_list(tree, ["S1", "S2"])
    assert exc.value.code == FailureCode.OUTPUT_SCHEMA


@pytest.mark.parametrize(
    ("endpoint", "invalid"),
    [
        ("parent", None),
        ("parent", ["I000001"]),
        ("parent", {"id": "I000001"}),
        ("child", None),
        ("child", ["S1"]),
        ("child", {"id": "S1"}),
    ],
)
def test_invalid_edge_endpoint_types_report_schema_failure(endpoint, invalid):
    tree = two_leaf_tree()
    tree["edges"][0][endpoint] = invalid
    with pytest.raises(BranchBFailure) as exc:
        validate_tree_edge_list(tree, ["S1", "S2"])
    assert exc.value.code == FailureCode.OUTPUT_SCHEMA
