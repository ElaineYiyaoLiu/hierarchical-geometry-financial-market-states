"""Synthetic development-only tests for D06 original-ID LCA stability."""

import numpy as np
import pytest

from branch_b.bootstrap.d06_identity_boundary import build_d06_draw_boundary
from branch_b.bootstrap.development_distinct_stability import (
    development_distinct_original_lca_stability,
)
from branch_b.failures import BranchBFailure, FailureCode


ORIGINALS = ["A", "B", "C", "D"]


def boundary(indices, label_prefix="occ"):
    return build_d06_draw_boundary(
        np.asarray(indices, dtype=int),
        original_sample_order=ORIGINALS,
        fit_sample_order=[f"{label_prefix}{i}" for i in range(len(indices))],
    )


def tree(leaves):
    # A and B share a resolved non-root ancestor; other leaves join at root.
    assert "A" in leaves and "B" in leaves
    return {
        "tree_format_version": "1",
        "root": "ROOT",
        "internal_nodes": ["ROOT", "AB"],
        "leaves": list(leaves),
        "edges": [
            {"parent": "ROOT", "child": "AB", "branch_length": 1.0},
            {"parent": "AB", "child": "A", "branch_length": 1.0},
            {"parent": "AB", "child": "B", "branch_length": 1.0},
            *(
                {"parent": "ROOT", "child": name, "branch_length": 1.0}
                for name in leaves if name not in ("A", "B")
            ),
        ],
    }


def measure(bound, *, sample_order=None, boot_tree=None):
    return development_distinct_original_lca_stability(
        full_test_tree=tree(ORIGINALS),
        full_original_sample_order=ORIGINALS if sample_order is None else sample_order,
        bootstrap_tree=tree(["A", "B", "C"]) if boot_tree is None else boot_tree,
        test_boundary=bound,
    )


def test_duplicate_draw_fits_distinct_tree_and_preserves_rank_statistic():
    draw = boundary([2, 0, 1, 0, 1, 0])
    assert draw.distinct_original_ids == ("A", "B", "C")
    assert draw.multiplicities == (3, 2, 1)
    assert measure(draw) == pytest.approx(1.0)


def test_renaming_occurrences_does_not_change_stability():
    first = boundary([2, 0, 1, 0, 1, 0], "v")
    second = boundary([1, 0, 2, 1, 0, 0], "renamed")
    assert measure(first) == pytest.approx(measure(second))


def test_mismatched_original_binding_rejected():
    with pytest.raises(BranchBFailure) as err:
        measure(boundary([0, 1, 2]), sample_order=["B", "A", "C", "D"])
    assert err.value.code == FailureCode.INPUT_SCHEMA


def test_occurrence_labeled_bootstrap_tree_rejected():
    with pytest.raises(BranchBFailure):
        measure(boundary([0, 0, 1, 2]), boot_tree=tree(["A", "B", "C", "D"]))


def test_two_originals_retain_existing_insufficient_relations_behavior():
    draw = boundary([0, 0, 1, 1])
    with pytest.raises(BranchBFailure) as err:
        measure(draw, boot_tree=tree(["A", "B"]))
    assert err.value.code == FailureCode.INSUFFICIENT_BOOTSTRAP
