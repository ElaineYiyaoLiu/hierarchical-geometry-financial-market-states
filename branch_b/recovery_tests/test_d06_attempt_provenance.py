"""Development-only bootstrap provenance and failure-accounting regression.

Synthetic evaluator outcomes only. No scientific failure mapper, deadline
duration, success threshold, or bootstrap decision rule is introduced.
Execute under the required Python 3.14 environment.
"""

import numpy as np
import pytest

from branch_b.bootstrap.engine import run_full_pipeline_bootstrap
from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.fitters.exact_tie_dp import ExactD04DeadlineExpired


def _run(evaluator, *, seed=20261115, n=5):
    return run_full_pipeline_bootstrap(
        n_replicates=n,
        train_size=6,
        validation_size=5,
        test_size=4,
        base_seed=seed,
        evaluate_replicate=evaluator,
    )


def _draw_signature(record):
    return (
        record.replicate_index,
        tuple(record.train_indices),
        tuple(record.validation_indices),
        tuple(record.test_indices),
        record.replicate_seed,
    )


def test_attempts_preserve_original_draw_seed_and_failure_without_success():
    observed = []

    def evaluator(train, validation, test, seed):
        observed.append((
            train.copy(), validation.copy(), test.copy(), seed,
        ))
        # Simulate an evaluator that overwrites its private copies before
        # failing: the engine must keep the actual original draw.
        train[:] = 0
        validation[:] = 0
        test[:] = 0
        raise BranchBFailure(FailureCode.NUMERICAL_FIT, "synthetic numeric fault")

    records = _run(evaluator)
    assert len(records) == len(observed) == 5
    for i, (record, received) in enumerate(zip(records, observed, strict=True)):
        train, validation, test, seed = received
        assert record.replicate_index == i
        assert record.replicate_seed == seed
        np.testing.assert_array_equal(record.train_indices, train)
        np.testing.assert_array_equal(record.validation_indices, validation)
        np.testing.assert_array_equal(record.test_indices, test)
        assert record.result is None
        assert record.failure["failure_code"] == "NUMERICAL_FIT"
        assert record.failure["exception_type"] == "BranchBFailure"
        assert record.failure["message"] == "synthetic numeric fault"


def test_each_exception_kind_is_preserved_without_invented_mapping():
    def evaluator(train, validation, test, seed):
        # Use an observable draw value only to choose a synthetic fixture
        # outcome, without inferring any hidden condition or hierarchy.
        case = int(train[0]) % 4
        if case == 0:
            raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "degenerate synthetic input")
        if case == 1:
            raise ArithmeticError("synthetic arithmetic error")
        if case == 2:
            raise ConfigurationRequired("unapproved synthetic branch")
        raise ExactD04DeadlineExpired(
            processed_weight_levels=2, maximum_stage_states=7
        )

    records = _run(evaluator, n=12)
    expected_types = {
        "BranchBFailure", "ArithmeticError",
        "ConfigurationRequired", "ExactD04DeadlineExpired",
    }
    assert len(records) == 12
    assert all(record.result is None and record.failure is not None for record in records)
    assert all(record.failure["exception_type"] in expected_types for record in records)
    for record in records:
        error = record.failure
        if error["exception_type"] == "BranchBFailure":
            assert error["failure_code"] == "DEGENERATE_DISTANCE"
        else:
            # Existing engine records an unmapped exception; it must not
            # silently invent NUMERICAL_FIT or TIMEOUT.
            assert "failure_code" not in error


def test_identical_owned_seed_replays_attempt_draws_and_evaluator_seeds():
    def evaluator(train, validation, test, seed):
        return {"seed": seed, "development": True}

    first = _run(evaluator)
    second = _run(evaluator)
    assert [_draw_signature(x) for x in first] == [
        _draw_signature(x) for x in second
    ]
    assert all(record.failure is None and record.result is not None for record in first)
    assert all(record.result["seed"] == record.replicate_seed for record in first)


def test_mixed_success_and_failure_attempts_are_both_retained():
    count = 0

    def evaluator(train, validation, test, seed):
        nonlocal count
        count += 1
        if count % 2 == 0:
            raise BranchBFailure(FailureCode.NUMERICAL_FIT, "synthetic even attempt failure")
        return {"synthetic_success": count, "seed": seed}

    records = _run(evaluator)
    assert [record.replicate_index for record in records] == list(range(5))
    assert [record.failure is None for record in records] == [
        True, False, True, False, True
    ]
    for record in records:
        assert record.replicate_seed is not None
        if record.failure is None:
            assert record.result["seed"] == record.replicate_seed
        else:
            assert record.result is None
            assert record.failure["failure_code"] == "NUMERICAL_FIT"


def test_existing_failure_record_does_not_pretend_to_export_structured_diagnostics():
    def evaluator(train, validation, test, seed):
        raise ExactD04DeadlineExpired(
            processed_weight_levels=3, maximum_stage_states=17
        )

    record = _run(evaluator, n=1)[0]
    assert record.result is None
    assert record.failure["exception_type"] == "ExactD04DeadlineExpired"
    assert "failure_code" not in record.failure
    assert "diagnostics" not in record.failure
    # Detailed DP diagnostics currently live on the raised exception object.
    # The engine preserves its message, not a structured exception payload.
    assert isinstance(record.failure["message"], str)
