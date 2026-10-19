"""Synthetic output-ownership checks; no scientific fitter or bank is used.

Run under Python 3.14. Counter-valued fitter outputs are diagnostic stubs, not
recovered hierarchies or a scientific candidate/selection procedure.
"""
from copy import deepcopy

import numpy as np
import pytest

from branch_b.bootstrap import run_recovery_pipeline_bootstrap
from branch_b.fitters import FitResult
from branch_b.recovery_pipeline import PipelineConfiguration, RecoveryPipeline


class IdentityPreprocessor:
    def __init__(self):
        self.record = {"synthetic": {"version": 0}}

    def transform(self, values):
        return values.copy()

    def to_record(self):
        return self.record


class ReusingFitter:
    """Return the same buffers, optionally inside a new outer FitResult."""

    fitter_id = "synthetic_reusing_fitter"

    def __init__(self, reuse_outer=True):
        self.calls = 0
        self.fail_next = False
        self.reuse_outer = reuse_outer
        self.matrix = np.zeros((2, 2))
        self.tree = {"synthetic": {"call": 0}}
        self.diagnostics = {"synthetic": {"call": 0, "seed": None}}
        self.shared = FitResult(self.matrix, self.tree, self.diagnostics)

    def fit(self, dissimilarity, *, random_seed=None):
        self.calls += 1
        self.matrix[:] = [[0.0, self.calls], [self.calls, 0.0]]
        self.tree["synthetic"]["call"] = self.calls
        self.diagnostics["synthetic"].update(call=self.calls, seed=random_seed)
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("synthetic failure after reusing result buffers")
        if self.reuse_outer:
            return self.shared
        return FitResult(self.matrix.view(), self.tree, self.diagnostics)


def _geometry(values, parameters):
    return np.array([[0.0, 2.0], [2.0, 0.0]])


def _candidates(values):
    return [{"synthetic_candidate": 0}, {"synthetic_candidate": 1}]


def _pipeline(fitter, *, preprocessor=None, geometry=_geometry,
              candidates=_candidates, selector=None):
    preprocessor = IdentityPreprocessor() if preprocessor is None else preprocessor
    selector = (lambda records: 1) if selector is None else selector
    return RecoveryPipeline(
        config=PipelineConfiguration("synthetic_geometry", fitter.fitter_id),
        fit_preprocessor=lambda train: preprocessor,
        geometry_factory=geometry,
        geometry_parameter_candidates=candidates,
        select_validation_candidate=selector,
        fitter=fitter,
    )


def _splits():
    return tuple(np.full((2, 12), value) for value in (7.0, 13.0, 29.0))


def _fit_markers(fit):
    return (
        fit.ultrametric_matrix[0, 1],
        fit.tree["synthetic"]["call"],
        fit.diagnostics["synthetic"]["call"],
    )


def _assert_same_record(actual, expected):
    for key in ("geometry_id", "common_fitter_id", "preprocessing",
                "selected_candidate_index", "geometry_parameters",
                "recovered_tree", "diagnostics"):
        assert actual[key] == expected[key]
    for key in ("dissimilarity_matrix", "ultrametric_matrix"):
        np.testing.assert_array_equal(actual[key], expected[key])
    assert len(actual["validation_candidates"]) == len(expected["validation_candidates"])
    for left, right in zip(actual["validation_candidates"],
                           expected["validation_candidates"], strict=True):
        assert left.parameters == right.parameters
        np.testing.assert_array_equal(left.dissimilarity_matrix, right.dissimilarity_matrix)
        np.testing.assert_array_equal(left.fit.ultrametric_matrix, right.fit.ultrametric_matrix)
        assert left.fit.tree == right.fit.tree
        assert left.fit.diagnostics == right.fit.diagnostics


@pytest.mark.parametrize("return_view", [False, True])
def test_reused_transform_buffer_cannot_mix_train_validation_and_test(return_view):
    class BufferPreprocessor(IdentityPreprocessor):
        def __init__(self):
            super().__init__()
            self.buffer = np.empty((2, 12))

        def transform(self, values):
            self.buffer[:] = values
            return self.buffer.view() if return_view else self.buffer

    training_seen = []
    geometry_seen = []

    def candidates(values):
        training_seen.append(values.copy())
        return _candidates(values)

    def geometry(values, parameters):
        geometry_seen.append(values.copy())
        return _geometry(values, parameters)

    splits = _splits()
    before = tuple(values.copy() for values in splits)
    pipeline = _pipeline(ReusingFitter(), preprocessor=BufferPreprocessor(),
                         geometry=geometry, candidates=candidates)
    pipeline.run(*splits)

    np.testing.assert_array_equal(training_seen[0], before[0])
    assert len(geometry_seen) == 3
    for observed, expected in zip(geometry_seen, (before[1], before[1], before[2]), strict=True):
        np.testing.assert_array_equal(observed, expected)
    for actual, expected in zip(splits, before, strict=True):
        np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize("reuse_outer", [False, True])
def test_each_fit_is_snapshotted_before_selection_and_test(reuse_outer):
    fitter = ReusingFitter(reuse_outer=reuse_outer)
    seen_by_selector = []

    def selector(candidates):
        seen_by_selector.extend(_fit_markers(candidate.fit) for candidate in candidates)
        return 1

    result = _pipeline(fitter, selector=selector).run(*_splits())

    assert seen_by_selector == [(1.0, 1, 1), (2.0, 2, 2)]
    assert [_fit_markers(candidate.fit) for candidate in result["validation_candidates"]] == seen_by_selector
    assert result["ultrametric_matrix"][0, 1] == 3.0
    assert result["recovered_tree"]["synthetic"]["call"] == 3
    assert result["diagnostics"]["synthetic"]["call"] == 3
    for candidate in result["validation_candidates"]:
        assert not np.shares_memory(candidate.fit.ultrametric_matrix, fitter.matrix)
    assert not np.shares_memory(result["ultrametric_matrix"], fitter.matrix)


@pytest.mark.parametrize("later_action", ["cache_mutation", "second_run", "failing_run"])
def test_later_fitter_activity_cannot_rewrite_a_completed_record(later_action):
    fitter = ReusingFitter()
    pipeline = _pipeline(fitter)
    result = pipeline.run(*_splits())
    saved = deepcopy(result)

    if later_action == "cache_mutation":
        fitter.matrix.fill(999.0)
        fitter.tree["synthetic"]["call"] = 999
        fitter.diagnostics["synthetic"]["call"] = 999
    elif later_action == "second_run":
        pipeline.run(*_splits())
    else:
        fitter.fail_next = True
        with pytest.raises(RuntimeError, match="synthetic failure"):
            pipeline.run(*_splits())

    _assert_same_record(result, saved)


def test_preprocessing_record_is_detached_from_callback_storage():
    preprocessor = IdentityPreprocessor()
    result = _pipeline(ReusingFitter(), preprocessor=preprocessor).run(*_splits())
    preprocessor.record["synthetic"]["version"] = 999
    assert result["preprocessing"] == {"synthetic": {"version": 0}}


def test_returned_record_mutation_does_not_write_back_to_component_caches():
    preprocessor = IdentityPreprocessor()
    fitter = ReusingFitter()
    result = _pipeline(fitter, preprocessor=preprocessor).run(*_splits())
    result["preprocessing"]["synthetic"]["version"] = 999
    result["ultrametric_matrix"].fill(999.0)
    result["recovered_tree"]["synthetic"]["call"] = 999
    result["diagnostics"]["synthetic"]["call"] = 999

    assert preprocessor.record == {"synthetic": {"version": 0}}
    assert _fit_markers(fitter.shared) == (3.0, 3, 3)
    assert [_fit_markers(candidate.fit) for candidate in result["validation_candidates"]] == [
        (1.0, 1, 1), (2.0, 2, 2),
    ]


def test_reused_fitter_does_not_overwrite_earlier_bootstrap_results():
    fitter = ReusingFitter()
    train, validation, test = _splits()
    records = run_recovery_pipeline_bootstrap(
        pipeline=_pipeline(fitter),
        train_values=train,
        validation_values=validation,
        test_values=test,
        n_replicates=3,
        base_seed=20261019,  # Branch B implementation-test seed, not production.
    )
    assert fitter.calls == 9
    assert len(records) == 3
    assert all(record.failure is None for record in records)
    for index, record in enumerate(records):
        expected_call = 3 * (index + 1)
        assert record.result["ultrametric_matrix"][0, 1] == expected_call
        assert record.result["recovered_tree"]["synthetic"]["call"] == expected_call
        assert record.result["diagnostics"]["synthetic"]["call"] == expected_call
        assert record.result["diagnostics"]["synthetic"]["seed"] == record.replicate_seed
        assert not np.shares_memory(record.result["ultrametric_matrix"], fitter.matrix)
