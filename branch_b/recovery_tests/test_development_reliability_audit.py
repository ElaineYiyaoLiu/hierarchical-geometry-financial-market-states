"""Synthetic-only D12/D14 attempt ledger audits; Python 3.14 required."""

from dataclasses import replace

import numpy as np
import pytest

from branch_b.bootstrap.engine import run_full_pipeline_bootstrap
from branch_b.bootstrap.development_reliability_audit import audit_development_attempts
from branch_b.failures import BranchBFailure, FailureCode


def _synthetic_records():
    count = 0

    def evaluate(train, validation, test, seed):
        nonlocal count
        count += 1
        if count == 2:
            raise BranchBFailure(FailureCode.NUMERICAL_FIT, "synthetic fit failure")
        if count == 4:
            raise ArithmeticError("synthetic unclassified error")
        return {"synthetic_score": count}

    return run_full_pipeline_bootstrap(
        n_replicates=5, train_size=7, validation_size=6, test_size=5,
        base_seed=20261115, evaluate_replicate=evaluate,
    )


def test_all_attempts_and_failure_types_retained_without_cutoff():
    records = _synthetic_records()
    audited = audit_development_attempts(
        records, train_size=7, validation_size=6, test_size=5
    )
    assert audited.attempted == 5
    assert audited.succeeded == 3
    assert audited.failed == 2
    assert audited.failure_fraction == 2 / 5
    assert dict(audited.failure_codes) == {
        "NUMERICAL_FIT": 1, "EXCEPTION:ArithmeticError": 1
    }
    assert audited.distinct_recorded_seeds == 5
    assert 1 <= audited.minimum_distinct_train_positions <= 7


def test_engine_seed_and_sample_positions_replay_exactly():
    def evaluate(train, validation, test, seed):
        return {"seed": seed}

    opts = dict(n_replicates=5, train_size=7, validation_size=6,
                test_size=5, base_seed=36, evaluate_replicate=evaluate)
    first = run_full_pipeline_bootstrap(**opts)
    second = run_full_pipeline_bootstrap(**opts)
    for a, b in zip(first, second, strict=True):
        assert a.replicate_seed == b.replicate_seed
        np.testing.assert_array_equal(a.train_indices, b.train_indices)
        np.testing.assert_array_equal(a.validation_indices, b.validation_indices)
        np.testing.assert_array_equal(a.test_indices, b.test_indices)
    assert audit_development_attempts(
        first, train_size=7, validation_size=6, test_size=5
    ) == audit_development_attempts(
        second, train_size=7, validation_size=6, test_size=5
    )


def test_missing_seed_fails_closed():
    records = _synthetic_records()
    records[0] = replace(records[0], replicate_seed=None)
    with pytest.raises(ValueError, match="seed"):
        audit_development_attempts(records, train_size=7, validation_size=6, test_size=5)


def test_duplicate_seed_fails_closed():
    records = _synthetic_records()
    records[1] = replace(records[1], replicate_seed=records[0].replicate_seed)
    with pytest.raises(ValueError, match="duplicate recorded"):
        audit_development_attempts(records, train_size=7, validation_size=6, test_size=5)


def test_missing_attempt_index_fails_closed():
    records = _synthetic_records()
    records[1] = replace(records[1], replicate_index=10)
    with pytest.raises(ValueError, match="attempt index"):
        audit_development_attempts(records, train_size=7, validation_size=6, test_size=5)


def test_out_of_range_original_position_fails_closed():
    records = _synthetic_records()
    indices = records[0].train_indices.copy()
    indices[0] = 7
    records[0] = replace(records[0], train_indices=indices)
    with pytest.raises(ValueError, match="bounds"):
        audit_development_attempts(records, train_size=7, validation_size=6, test_size=5)


def test_failure_without_code_or_exception_type_is_rejected():
    records = _synthetic_records()
    records[1] = replace(records[1], failure={"message": "lost failure"})
    with pytest.raises(ValueError, match="both code and exception type"):
        audit_development_attempts(records, train_size=7, validation_size=6, test_size=5)


def test_failed_attempt_with_successful_result_rejected():
    records = _synthetic_records()
    records[1] = replace(records[1], result={"unexpected": "success"})
    with pytest.raises(ValueError, match="failed attempt"):
        audit_development_attempts(records, train_size=7, validation_size=6, test_size=5)


def test_empty_ledger_and_invalid_split_size_fail_closed():
    with pytest.raises(ValueError, match="nonempty"):
        audit_development_attempts([], train_size=7, validation_size=6, test_size=5)
    with pytest.raises(ValueError, match="positive integer"):
        audit_development_attempts(_synthetic_records(), train_size=True, validation_size=6, test_size=5)
