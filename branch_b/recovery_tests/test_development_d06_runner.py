"""Synthetic tests for development-only original-ID D06 bootstrap runner."""

import numpy as np

from branch_b.bootstrap.development_d06_runner import run_development_d06_bootstrap
from branch_b.fitters.base import FitResult


IDS = ["A", "B", "C", "D", "E", "F", "G", "H"]


def tree(order):
    return {
        "tree_format_version": "1",
        "root": "ROOT",
        "internal_nodes": ["ROOT"],
        "leaves": list(order),
        "edges": [{"parent": "ROOT", "child": x, "branch_length": 1.0} for x in order],
    }


class IdentityPreprocessor:
    def transform(self, rows):
        return np.asarray(rows, dtype=float).copy()


class RecordingFitter:
    def __init__(self):
        self.calls = []

    def fit_with_original_multiplicities(
        self, dissimilarity, *, original_sample_order, multiplicities, random_seed=None
    ):
        self.calls.append((tuple(original_sample_order), tuple(multiplicities), random_seed))
        return FitResult(np.asarray(dissimilarity).copy(), tree(original_sample_order), {})


def setup(fitter, selector=lambda choices: 0):
    originals = np.repeat(np.arange(1, 9, dtype=float)[:, None], 12, axis=1)

    def geometry(rows, params):
        values = rows[:, 0]
        return abs(values[:, None] - values[None, :])

    return dict(
        train_values=originals,
        validation_values=originals.copy(),
        test_values=originals.copy(),
        train_original_sample_order=IDS,
        validation_original_sample_order=IDS,
        test_original_sample_order=IDS,
        n_replicates=5,
        base_seed=20261117,
        fit_preprocessor=lambda train: IdentityPreprocessor(),
        geometry_factory=geometry,
        geometry_parameter_candidates=lambda train: [{"candidate": 0}],
        select_validation_candidate=selector,
        fitter=fitter,
    )


def test_replays_draws_seeds_and_distinct_original_fits():
    fitter = RecordingFitter()
    opts = setup(fitter)
    first = run_development_d06_bootstrap(**opts)
    second = run_development_d06_bootstrap(**opts)
    assert len(first) == len(second) == 5
    assert any(record.failure is None for record in first)
    for a, b in zip(first, second, strict=True):
        assert a.replicate_seed == b.replicate_seed
        np.testing.assert_array_equal(a.train_indices, b.train_indices)
        np.testing.assert_array_equal(a.validation_indices, b.validation_indices)
        np.testing.assert_array_equal(a.test_indices, b.test_indices)
        assert (a.failure is None) == (b.failure is None)
        if a.failure is None:
            assert a.result["scientific_authorization"] is False
            assert a.result["test_distinct_original_ids"] == [
                IDS[i] for i in sorted(set(map(int, a.test_indices)))
            ]
            assert a.result["bootstrap_identity"]["train_original_ids"] == [
                IDS[int(i)] for i in a.train_indices
            ]
    assert fitter.calls
    assert all(len(order) == len(masses) for order, masses, _ in fitter.calls)


def test_selection_failure_keeps_every_attempt_and_original_draw():
    fitter = RecordingFitter()
    opts = setup(fitter, selector=lambda choices: -1)
    records = run_development_d06_bootstrap(**opts)
    assert len(records) == 5
    for index, record in enumerate(records):
        assert record.replicate_index == index
        assert record.result is None
        assert record.failure is not None
        assert record.replicate_seed is not None
        assert len(record.train_indices) == len(IDS)
        assert len(record.validation_indices) == len(IDS)
        assert len(record.test_indices) == len(IDS)


def test_reference_stability_undefined_is_not_silently_successful():
    # A star tree has constant LCA-depth ranks; Spearman is undefined.
    fitter = RecordingFitter()
    records = run_development_d06_bootstrap(**setup(fitter), full_test_tree=tree(IDS))
    assert len(records) == 5
    assert all(record.result is None and record.failure is not None for record in records)
    assert all(record.failure["exception_type"] in (
        "UndefinedRankCorrelation", "BranchBFailure"
    ) for record in records)


def test_failed_validation_selection_never_reads_test_data():
    class ForbiddenTest:
        def __array__(self, dtype=None, copy=None):
            raise AssertionError("test data accessed before selection")

    fitter = RecordingFitter()
    opts = setup(fitter, selector=lambda choices: -1)
    opts["test_values"] = ForbiddenTest()

    records = run_development_d06_bootstrap(**opts)

    assert len(records) == 5
    assert all(record.result is None for record in records)
    assert all(
        record.failure["exception_type"] == "ConfigurationRequired"
        for record in records
    )