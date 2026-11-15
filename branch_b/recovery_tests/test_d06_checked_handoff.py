"""Development-only D06 checked handoff tests on synthetic identities."""

from copy import deepcopy

import numpy as np
import pytest

from branch_b.bootstrap.d06_identity_boundary import build_d06_draw_boundary
from branch_b.failures import BranchBFailure, ConfigurationRequired
from branch_b.fitters.base import FitResult
from branch_b.recovery_pipeline.d06_checked_handoff import checked_d06_distinct_fit


def boundary(indices):
    return build_d06_draw_boundary(
        np.asarray(indices, dtype=int),
        original_sample_order=["A", "B", "C", "D"],
        fit_sample_order=[f"occ{i}" for i in range(len(indices))],
    )


def star_tree(order):
    return {
        "tree_format_version": "1",
        "root": "ROOT",
        "internal_nodes": ["ROOT"],
        "leaves": list(order),
        "edges": [
            {"parent": "ROOT", "child": name, "branch_length": 1.0}
            for name in order
        ],
    }


class RecordingFitter:
    def __init__(self, wrong_leaves=False):
        self.calls = []
        self.wrong_leaves = wrong_leaves

    def fit_with_original_multiplicities(
        self, dissimilarity, *, original_sample_order, multiplicities, random_seed=None
    ):
        self.calls.append((
            np.asarray(dissimilarity).copy(),
            original_sample_order.copy(), multiplicities.copy(), random_seed,
        ))
        order = original_sample_order.copy()
        if self.wrong_leaves:
            order = list(reversed(order))
        n = len(order)
        result = np.ones((n, n), dtype=float)
        np.fill_diagonal(result, 0)
        # Attempted mutation must not affect caller's matrix or boundary.
        dissimilarity[0, 1] = 99.0
        return FitResult(result, star_tree(order), {"development": True})


def test_distinct_fitter_receives_correct_multiplicities_and_ids():
    bound = boundary([2, 1, 2, 0, 1, 0])
    fitter = RecordingFitter()
    matrix = np.array([[0., .2, .4], [.2, 0., .3], [.4, .3, 0.]])
    original = matrix.copy()
    fit = checked_d06_distinct_fit(
        matrix, boundary=bound, fitter=fitter, random_seed=123
    )
    assert len(fitter.calls) == 1
    passed, order, masses, seed = fitter.calls[0]
    np.testing.assert_array_equal(passed, original)
    np.testing.assert_array_equal(matrix, original)
    assert order == ["A", "B", "C"]
    assert masses == [2, 2, 2]
    assert seed == 123
    assert fit.tree["leaves"] == ["A", "B", "C"]
    assert bound.fit_sample_order == tuple(f"occ{i}" for i in range(6))


def test_fitter_result_with_occurrence_leaves_is_rejected():
    bound = boundary([0, 0, 1])
    class OccurrenceFitter(RecordingFitter):
        def fit_with_original_multiplicities(self, dissimilarity, *, original_sample_order,
                                             multiplicities, random_seed=None):
            return FitResult(
                np.zeros((2, 2)), star_tree(["occ0", "occ1"]), {}
            )
    with pytest.raises(BranchBFailure):
        checked_d06_distinct_fit(
            np.array([[0., 0.5], [0.5, 0.]]),
            boundary=bound, fitter=OccurrenceFitter()
        )


def test_zero_pair_weight_remains_fail_closed_without_fitter_invocation():
    bound = boundary([1, 1, 1])
    fitter = RecordingFitter()
    with pytest.raises(ConfigurationRequired, match="low-distinct"):
        checked_d06_distinct_fit(
            np.zeros((1, 1)), boundary=bound, fitter=fitter
        )
    assert fitter.calls == []


def test_missing_multiplicity_interface_does_not_fall_back():
    class Legacy:
        def fit_with_sample_order(self, *args, **kwargs):
            raise AssertionError("must not be called")
    with pytest.raises(ConfigurationRequired, match="multiplicity-aware"):
        checked_d06_distinct_fit(
            np.array([[0., 0.5], [0.5, 0.]]),
            boundary=boundary([0, 1]), fitter=Legacy()
        )


def test_wrong_shape_is_rejected_before_fitter():
    fitter = RecordingFitter()
    with pytest.raises(BranchBFailure):
        checked_d06_distinct_fit(
            np.zeros((3, 3)), boundary=boundary([0, 1]), fitter=fitter
        )
    assert fitter.calls == []


def test_invalid_leaf_order_is_rejected():
    fitter = RecordingFitter(wrong_leaves=True)
    with pytest.raises(BranchBFailure):
        checked_d06_distinct_fit(
            np.array([[0., 0.5, 1.], [0.5, 0., 0.6], [1., 0.6, 0.]]),
            boundary=boundary([0, 1, 2]), fitter=fitter
        )
