"""Synthetic-only regression tests for observable matrix conversion boundaries."""
import numpy as np
import pytest

from branch_b.bootstrap.pipeline import run_recovery_pipeline_bootstrap
from branch_b.failures import BranchBFailure, FailureCode
from branch_b.normalization.common import normalize_dissimilarity
from branch_b.preprocessing.validation import as_finite_matrix


def _observations():
    return np.arange(36.0).reshape(3, 12)


def _distances():
    return np.array([[0., 2., 3.], [2., 0., 4.], [3., 4., 0.]])


@pytest.mark.parametrize("invalid", [
    np.ones((3, 12), dtype=bool),
    np.ones((3, 12), dtype=object),
    np.ones((3, 12), dtype=str),
    np.ma.array(_observations(), mask=np.eye(3, 12, dtype=bool)),
    [[False] + [1.] * 11] + [[1.] * 12] * 2,
    [[1.] * 12, [2.] * 11],
])
def test_observable_boundary_rejects_lossy_input(invalid):
    with pytest.raises(BranchBFailure) as caught:
        as_finite_matrix(invalid)
    assert caught.value.code == FailureCode.INPUT_SCHEMA


@pytest.mark.parametrize("invalid", [
    np.array([[False, True], [True, False]]),
    np.array([[0, 2], [2, 0]], dtype=object),
    np.array([["0", "2"], ["2", "0"]]),
    np.ma.array(_distances(), mask=np.eye(3, dtype=bool)),
    [[0, True], [True, 0]],
    [[0, 2], [2]],
])
def test_normalization_rejects_lossy_input(invalid):
    with pytest.raises(BranchBFailure) as caught:
        normalize_dissimilarity(invalid)
    assert caught.value.code == FailureCode.INPUT_SCHEMA


def test_valid_observations_are_copied_without_reordering():
    original = _observations()
    converted = as_finite_matrix(original)
    assert np.array_equal(converted, original)
    assert not np.shares_memory(converted, original)


def test_valid_normalization_retains_frozen_formula():
    d = _distances()
    normalized = normalize_dissimilarity(d)
    assert np.array_equal(normalized, d / 4.0)
    assert np.array_equal(d, _distances())


def test_unchecked_bootstrap_rejects_bad_input_before_pipeline_call():
    class NeverCalled:
        def run(self, *args, **kwargs):
            raise AssertionError("malformed input must never reach the pipeline")

    with pytest.raises(BranchBFailure) as caught:
        run_recovery_pipeline_bootstrap(
            pipeline=NeverCalled(),
            train_values=np.ones((3, 12), dtype=bool),
            validation_values=_observations(),
            test_values=_observations(),
            n_replicates=2,
            base_seed=36,
        )
    assert caught.value.code == FailureCode.INPUT_SCHEMA
