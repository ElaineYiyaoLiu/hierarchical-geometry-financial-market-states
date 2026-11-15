"""Synthetic D06 dual-representation tests for actual Python 3.14."""

import numpy as np
import pytest

from branch_b.bootstrap.d06_identity_boundary import (
    aligned_distinct_rows,
    build_d06_draw_boundary,
)
from branch_b.failures import BranchBFailure


def _make(indices, labels=None):
    if labels is None:
        labels = [f"occ-{i}" for i in range(len(indices))]
    return build_d06_draw_boundary(
        np.array(indices, dtype=int),
        original_sample_order=["A", "B", "C", "D"],
        fit_sample_order=labels,
    )


def test_occurrences_and_distinct_identities_are_both_preserved():
    boundary = _make([0, 0, 1, 1, 1, 2])
    assert boundary.occurrence_original_ids == ("A", "A", "B", "B", "B", "C")
    assert boundary.distinct_original_ids == ("A", "B", "C")
    assert boundary.multiplicities == (2, 3, 1)
    assert boundary.pair_weights() == (6, 2, 3)
    assert boundary.total_pair_weight() == 11
    assert boundary.first_occurrence_positions == (0, 2, 5)
    assert len(boundary.fit_sample_order) == 6
    assert "D" not in boundary.distinct_original_ids


def test_canonical_identity_order_is_not_draw_order():
    boundary = _make([2, 1, 2, 0, 1, 0])
    assert boundary.distinct_original_ids == ("A", "B", "C")
    assert boundary.multiplicities == (2, 2, 2)
    assert boundary.first_occurrence_positions == (3, 1, 0)


def test_renaming_occurrence_labels_does_not_change_distinct_mapping():
    baseline = _make([0, 0, 1, 1, 1, 2])
    renamed = _make([0, 0, 1, 1, 1, 2], [f"d-{i}" for i in range(6)])
    assert baseline.occurrence_original_ids == renamed.occurrence_original_ids
    assert baseline.distinct_original_ids == renamed.distinct_original_ids
    assert baseline.multiplicities == renamed.multiplicities
    assert baseline.pair_weights() == renamed.pair_weights()


def test_project_transformed_rows_preserves_occurrences_upstream():
    boundary = _make([2, 1, 2, 0, 1, 0])
    rows = np.array([[30., 3.], [20., 2.], [30., 3.],
                     [10., 1.], [20., 2.], [10., 1.]])
    original = rows.copy()
    aligned = aligned_distinct_rows(rows, boundary)
    np.testing.assert_array_equal(aligned, [[10., 1.], [20., 2.], [30., 3.]])
    np.testing.assert_array_equal(rows, original)
    aligned[0, 0] = 999
    np.testing.assert_array_equal(rows, original)


def test_disagreeing_same_original_rows_refuse_collapse():
    boundary = _make([0, 0, 1])
    with pytest.raises(ValueError, match="disagree"):
        aligned_distinct_rows([[1., 2.], [1., 3.], [4., 5.]], boundary)


def test_single_distinct_identity_is_retained_without_inventing_outcome():
    boundary = _make([1, 1, 1])
    assert boundary.distinct_original_ids == ("B",)
    assert boundary.multiplicities == (3,)
    assert boundary.pair_weights() == ()
    assert boundary.total_pair_weight() == 0


@pytest.mark.parametrize(
    "indices,labels",
    [
        ([0, 4], ["r0", "r1"]),
        ([-1, 0], ["r0", "r1"]),
        ([0, 1], ["duplicate", "duplicate"]),
    ],
)
def test_invalid_identity_bindings_fail_closed(indices, labels):
    with pytest.raises(BranchBFailure):
        _make(indices, labels)
