"""Synthetic exact-height tree extraction checks (Python 3.14 only)."""

import numpy as np
import pytest

from branch_b.failures import BranchBFailure
from branch_b.fitters.development_tree_extraction import extract_exact_ultrametric_tree
from branch_b.recovery_pipeline.result_validation import validate_bound_tree


def test_fully_tied_three_vertex_star_is_not_binary_refined():
    matrix = np.full((3, 3), 0.75)
    np.fill_diagonal(matrix, 0.0)
    tree = extract_exact_ultrametric_tree(matrix, sample_order=["A", "B", "C"])
    assert len(tree["internal_nodes"]) == 1
    assert len(tree["edges"]) == 3
    assert sorted(edge["child"] for edge in tree["edges"]) == ["A", "B", "C"]
    assert all(edge["branch_length"] == 0.75 for edge in tree["edges"])
    assert all(edge["unresolved"] for edge in tree["edges"])
    validate_bound_tree(tree, sample_order=["A", "B", "C"])


def test_nested_exact_heights_preserve_cluster_and_branch_differences():
    matrix = np.array([
        [0., .25, .9], [.25, 0., .9], [.9, .9, 0.]
    ])
    tree = extract_exact_ultrametric_tree(matrix, sample_order=["A", "B", "C"])
    assert len(tree["internal_nodes"]) == 2
    root_edges = [edge for edge in tree["edges"] if edge["parent"] == tree["root"]]
    assert sorted(edge["branch_length"] for edge in root_edges) == pytest.approx([0.65, 0.9])
    assert all(edge["branch_length"] >= 0 for edge in tree["edges"])
    assert not any(edge["unresolved"] for edge in tree["edges"])


def test_zero_height_cluster_retains_zero_length_unresolved_edges():
    matrix = np.array([
        [0., 0., .8], [0., 0., .8], [.8, .8, 0.]
    ])
    tree = extract_exact_ultrametric_tree(matrix, sample_order=["A", "B", "C"])
    zero_edges = [e for e in tree["edges"] if e["branch_length"] == 0]
    assert len(zero_edges) == 2
    assert all(e["unresolved"] for e in zero_edges)
    validate_bound_tree(tree, sample_order=["A", "B", "C"])


def test_canonical_order_and_generated_internal_ids_do_not_collide():
    order = ["__d06_internal_0", "C", "B"]
    matrix = np.full((3, 3), 1.0)
    np.fill_diagonal(matrix, 0.0)
    tree = extract_exact_ultrametric_tree(matrix, sample_order=order)
    assert tree["leaves"] == order
    assert not (set(tree["internal_nodes"]) & set(order))
    validate_bound_tree(tree, sample_order=order)


@pytest.mark.parametrize("matrix", [
    [[0., 1., 2.], [1., 0., 3.], [2., 3., 0.]],
    [[0., 1.], [2., 0.]],
    [[0., -1.], [-1., 0.]],
    [[0., float("nan")], [float("nan"), 0.]],
])
def test_invalid_exact_ultrametric_fails_closed(matrix):
    with pytest.raises(BranchBFailure):
        extract_exact_ultrametric_tree(matrix, sample_order=["A", "B"] if len(matrix) == 2 else ["A", "B", "C"])
