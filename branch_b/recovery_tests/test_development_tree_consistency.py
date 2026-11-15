"""Independent tree-to-ultrametric checks on synthetic binary-exact heights."""

from copy import deepcopy
from time import monotonic

import numpy as np
import pytest

from branch_b.failures import BranchBFailure
from branch_b.fitters.development_tree_extraction import extract_exact_ultrametric_tree
from branch_b.fitters.development_tree_fit import run_checked_development_tree_fit
from branch_b.fitters.development_tree_consistency import (
    candidate_tree_exactly_matches_matrix,
    reconstruct_candidate_ultrametric,
)


@pytest.mark.parametrize("u", [
    np.array([[0., .75], [.75, 0.]]),
    np.array([[0., .25, .75], [.25, 0., .75], [.75, .75, 0.]]),
    np.array([[0., 0., .75], [0., 0., .75], [.75, .75, 0.]]),
    np.array([[0., .75, .75], [.75, 0., .75], [.75, .75, 0.]]),
])
def test_reconstruction_matches_ultrametric_exactly_on_binary_heights(u):
    order = [f"X{i}" for i in range(len(u))]
    tree = extract_exact_ultrametric_tree(u, sample_order=order)
    reconstructed = reconstruct_candidate_ultrametric(tree, sample_order=order)
    np.testing.assert_array_equal(reconstructed, u)
    assert candidate_tree_exactly_matches_matrix(tree, u, sample_order=order)


def test_independent_check_detects_branch_length_mismatch():
    u = np.array([[0., .25, .75], [.25, 0., .75], [.75, .75, 0.]])
    order = ["A", "B", "C"]
    tree = extract_exact_ultrametric_tree(u, sample_order=order)
    changed = deepcopy(tree)
    # Modifying the root->C length alone breaks root-to-leaf equality.
    edge = next(e for e in changed["edges"] if e["child"] == "C")
    edge["branch_length"] += 0.125
    with pytest.raises(BranchBFailure, match="unequal root-to-leaf"):
        reconstruct_candidate_ultrametric(changed, sample_order=order)


def test_independent_check_detects_structurally_valid_wrong_height():
    u = np.array([[0., .5], [.5, 0.]])
    tree = extract_exact_ultrametric_tree(u, sample_order=["A", "B"])
    changed = deepcopy(tree)
    for edge in changed["edges"]:
        edge["branch_length"] = 0.75
    # Both leaves still have equal heights, and the tree is structurally valid.
    assert not candidate_tree_exactly_matches_matrix(
        changed, u, sample_order=["A", "B"]
    )


def test_actual_two_vertex_optimizer_export_matches_candidate_reconstruction():
    fit = run_checked_development_tree_fit(
        (0.8,), (2, 3),
        original_sample_order=["A", "B"],
        deadline_monotonic=monotonic() + 30.0,
    )
    assert candidate_tree_exactly_matches_matrix(
        fit.tree, fit.ultrametric_matrix, sample_order=["A", "B"]
    )
