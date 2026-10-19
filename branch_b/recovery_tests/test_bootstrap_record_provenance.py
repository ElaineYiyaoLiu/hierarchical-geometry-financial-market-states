"""Synthetic bootstrap provenance checks; execute under Python 3.14.

The literal seeds below are Branch B development fixtures, not production seeds.
No fitter, scientific interval, experimental bank, or automatic retry is used.
"""
from __future__ import annotations

import numpy as np
import pytest

from branch_b.bootstrap import BootstrapReplicate, run_full_pipeline_bootstrap
from branch_b.bootstrap.pipeline import run_recovery_pipeline_bootstrap
from branch_b.failures import BranchBFailure, FailureCode


BASE_SEED = 12345
SIZES = (5, 3, 2)
REPLICATES = 4


def _run(evaluate, *, base_seed=BASE_SEED):
    return run_full_pipeline_bootstrap(
        n_replicates=REPLICATES,
        train_size=SIZES[0],
        validation_size=SIZES[1],
        test_size=SIZES[2],
        base_seed=base_seed,
        evaluate_replicate=evaluate,
    )


def _draws(record):
    return record.train_indices, record.validation_indices, record.test_indices


@pytest.mark.parametrize("outcome", ["success", "none", "structured_failure", "unexpected_failure"])
def test_every_attempt_records_the_exact_seed_passed_to_the_evaluator(outcome):
    supplied_seeds = []

    def evaluate(train, validation, test, seed):
        supplied_seeds.append(seed)
        if outcome == "structured_failure":
            raise BranchBFailure(FailureCode.NUMERICAL_FIT, "synthetic failure")
        if outcome == "unexpected_failure":
            raise RuntimeError("synthetic unexpected failure")
        return None if outcome == "none" else {"completed": True}

    records = _run(evaluate)
    assert len(records) == REPLICATES
    assert [record.replicate_index for record in records] == list(range(REPLICATES))
    assert [record.replicate_seed for record in records] == supplied_seeds
    assert all(type(record.replicate_seed) is int for record in records)
    for record in records:
        if outcome == "structured_failure":
            assert record.result is None
            assert record.failure == {
                "exception_type": "BranchBFailure",
                "message": "synthetic failure",
                "failure_code": "NUMERICAL_FIT",
            }
        elif outcome == "unexpected_failure":
            assert record.result is None
            assert record.failure == {
                "exception_type": "RuntimeError",
                "message": "synthetic unexpected failure",
            }
        else:
            assert record.failure is None
            assert record.result == (None if outcome == "none" else {"completed": True})


@pytest.mark.parametrize("fail_after_mutation", [False, True])
def test_evaluator_mutation_cannot_rewrite_original_draw_evidence(fail_after_mutation):
    original_draws = []
    callback_arrays = []
    supplied_seeds = []

    def evaluate(train, validation, test, seed):
        arrays = (train, validation, test)
        original_draws.append(tuple(array.copy() for array in arrays))
        callback_arrays.append(arrays)
        supplied_seeds.append(seed)
        for array in arrays:
            array[:] = -1
        if fail_after_mutation:
            raise BranchBFailure(FailureCode.NUMERICAL_FIT, "synthetic mutation failure")
        return {"completed": True}

    records = _run(evaluate)
    for record, expected, supplied in zip(records, original_draws, callback_arrays, strict=True):
        for actual, before, callback_array in zip(_draws(record), expected, supplied, strict=True):
            np.testing.assert_array_equal(actual, before)
            assert not np.shares_memory(actual, callback_array)
            # A retained callback reference must not alter the returned evidence later.
            callback_array[:] = -2
            np.testing.assert_array_equal(actual, before)
        assert (record.failure is not None) is fail_after_mutation
    assert [record.replicate_seed for record in records] == supplied_seeds


@pytest.mark.parametrize("base_seed", [12345, 67890])
def test_provenance_change_preserves_the_existing_random_stream(base_seed):
    """Reference the draw order in the pre-change engine, without calling its helpers."""
    expected = []
    sequences = np.random.SeedSequence(base_seed).spawn(REPLICATES)
    for sequence in sequences:
        rng = np.random.default_rng(sequence)
        draws = tuple(rng.integers(0, size, size=size, endpoint=False) for size in SIZES)
        seed = int(rng.integers(0, 2**63 - 1))
        expected.append((draws, seed))

    def evaluate(train, validation, test, seed):
        return tuple(tuple(array.tolist()) for array in (train, validation, test)), seed

    records = _run(evaluate, base_seed=base_seed)
    for record, (draws, seed) in zip(records, expected, strict=True):
        for actual, reference in zip(_draws(record), draws, strict=True):
            np.testing.assert_array_equal(actual, reference)
        assert record.replicate_seed == seed
        assert record.result == (tuple(tuple(array.tolist()) for array in draws), seed)
        assert record.failure is None


def test_failed_record_has_enough_arguments_to_replay_synthetic_randomness():
    """Manual test-only replay: the engine itself must still invoke each attempt once."""
    observed = []

    def fingerprint(train, validation, test, seed):
        random_values = tuple(np.random.default_rng(seed).integers(0, 1000, size=3).tolist())
        return tuple(tuple(array.tolist()) for array in (train, validation, test)), random_values

    def evaluate(train, validation, test, seed):
        value = fingerprint(train, validation, test, seed)
        observed.append(value)
        if len(observed) == 2:
            raise RuntimeError("synthetic single failure")
        return value

    records = _run(evaluate)
    assert len(observed) == REPLICATES  # No retry or replacement of the failed slot.
    failed = records[1]
    assert failed.result is None
    assert failed.failure["exception_type"] == "RuntimeError"
    assert failed.replicate_seed is not None
    assert fingerprint(*_draws(failed), failed.replicate_seed) == observed[1]
    for index in (0, 2, 3):
        assert records[index].result == observed[index]
        assert records[index].failure is None


def test_legacy_manual_record_marks_seed_as_unrecorded_not_invented():
    record = BootstrapReplicate(
        0,
        np.array([0, 1]),
        np.array([1, 0]),
        np.array([0, 0]),
        None,
        {"exception_type": "RuntimeError", "message": "synthetic legacy record"},
    )
    assert record.replicate_seed is None


def test_pipeline_bootstrap_preserves_seed_on_success_and_failure():
    calls = []

    class RecordingPipeline:
        def run(self, train, validation, test, *, random_seed):
            calls.append((random_seed, train.copy(), validation.copy(), test.copy()))
            if len(calls) == 2:
                raise BranchBFailure(FailureCode.NUMERICAL_FIT, "synthetic pipeline failure")
            return {"observed_seed": random_seed}

    train = np.arange(60, dtype=float).reshape(5, 12)
    validation = np.arange(36, dtype=float).reshape(3, 12) + 100.0
    test = np.arange(24, dtype=float).reshape(2, 12) + 200.0
    records = run_recovery_pipeline_bootstrap(
        pipeline=RecordingPipeline(),
        train_values=train,
        validation_values=validation,
        test_values=test,
        n_replicates=REPLICATES,
        base_seed=BASE_SEED,
    )
    assert len(calls) == len(records) == REPLICATES
    for index, (record, call) in enumerate(zip(records, calls, strict=True)):
        seed, received_train, received_validation, received_test = call
        assert record.replicate_seed == seed
        np.testing.assert_array_equal(received_train, train[record.train_indices])
        np.testing.assert_array_equal(received_validation, validation[record.validation_indices])
        np.testing.assert_array_equal(received_test, test[record.test_indices])
        if index == 1:
            assert record.result is None
            assert record.failure["failure_code"] == "NUMERICAL_FIT"
        else:
            assert record.failure is None
            assert record.result["observed_seed"] == seed
            assert "bootstrap_draws" in record.result
