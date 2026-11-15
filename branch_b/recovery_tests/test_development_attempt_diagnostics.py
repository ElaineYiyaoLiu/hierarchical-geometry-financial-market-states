"""Synthetic bootstrap diagnostic sidecar tests (Python 3.14 only)."""

import numpy as np

from branch_b.bootstrap.development_attempt_diagnostics import (
    run_development_bootstrap_with_diagnostics,
)
from branch_b.failures import BranchBFailure, FailureCode
from branch_b.fitters.development_optimizer import DevelopmentOptimizerDeadlineExpired
from branch_b.fitters.exact_tie_dp import ExactD04DeadlineExpired


def run(evaluate, n=4):
    return run_development_bootstrap_with_diagnostics(
        n_replicates=n,
        train_size=5,
        validation_size=4,
        test_size=3,
        base_seed=20261115,
        evaluate_replicate=evaluate,
    )


def test_sidecar_preserves_d04_work_counters_and_original_failure():
    def evaluator(train, validation, test, seed):
        raise ExactD04DeadlineExpired(
            processed_weight_levels=3, maximum_stage_states=17
        )

    records, details = run(evaluator, n=2)
    assert len(records) == len(details) == 2
    for record, item in zip(records, details, strict=True):
        assert record.result is None
        assert record.failure["exception_type"] == "ExactD04DeadlineExpired"
        assert "failure_code" not in record.failure
        assert "diagnostics" not in record.failure
        assert item.replicate_seed == record.replicate_seed
        assert item.existing_failure_code is None
        assert item.detail == {
            "deadline_source": "d04",
            "processed_weight_levels": 3,
            "maximum_stage_states": 17,
        }


def test_optimizer_deadline_does_not_claim_d04_counters():
    def evaluator(train, validation, test, seed):
        raise DevelopmentOptimizerDeadlineExpired("actual test deadline")

    records, details = run(evaluator, n=1)
    assert records[0].failure["exception_type"] == "DevelopmentOptimizerDeadlineExpired"
    assert details[0].detail == {"deadline_source": "optimizer"}
    assert details[0].existing_failure_code is None


def test_existing_failure_code_is_preserved_without_remapping():
    def evaluator(train, validation, test, seed):
        raise BranchBFailure(FailureCode.NUMERICAL_FIT, "synthetic numerical failure")

    records, details = run(evaluator, n=1)
    assert records[0].failure["failure_code"] == "NUMERICAL_FIT"
    assert details[0].existing_failure_code == "NUMERICAL_FIT"
    assert details[0].detail == {}


def test_mixed_attempts_preserve_original_indices_seeds_and_results():
    count = 0
    original_inputs = []

    def evaluator(train, validation, test, seed):
        nonlocal count
        count += 1
        original_inputs.append((train.copy(), validation.copy(), test.copy(), seed))
        train[:] = 0
        if count % 2 == 0:
            raise ArithmeticError("synthetic arithmetic failure")
        return {"seed": seed, "attempt": count}

    records, details = run(evaluator, n=4)
    assert [x.outcome for x in details] == [
        "SUCCEEDED", "FAILED", "SUCCEEDED", "FAILED"
    ]
    for record, item, input_record in zip(records, details, original_inputs, strict=True):
        train, validation, test, seed = input_record
        np.testing.assert_array_equal(record.train_indices, train)
        np.testing.assert_array_equal(record.validation_indices, validation)
        np.testing.assert_array_equal(record.test_indices, test)
        assert item.replicate_seed == record.replicate_seed == seed
        if item.outcome == "SUCCEEDED":
            assert record.failure is None and record.result["seed"] == seed
        else:
            assert record.result is None and record.failure["exception_type"] == "ArithmeticError"
            assert item.exception_type == "ArithmeticError"
            assert item.detail == {}


def test_deterministic_replay_keeps_attempt_alignment():
    def evaluator(train, validation, test, seed):
        return {"seed": seed}

    first, first_details = run(evaluator)
    second, second_details = run(evaluator)
    assert first_details == second_details
    for x, y in zip(first, second, strict=True):
        assert x.replicate_seed == y.replicate_seed
        np.testing.assert_array_equal(x.train_indices, y.train_indices)
        np.testing.assert_array_equal(x.validation_indices, y.validation_indices)
        np.testing.assert_array_equal(x.test_indices, y.test_indices)
