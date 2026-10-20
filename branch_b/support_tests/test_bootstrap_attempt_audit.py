"""Synthetic-only bootstrap accounting tests; no scientific threshold selection."""
import numpy as np
import pytest

from branch_b.bootstrap.attempt_audit import audit_bootstrap_attempts
from branch_b.bootstrap.engine import BootstrapReplicate, run_full_pipeline_bootstrap
from branch_b.support.stability import UndefinedRankCorrelation


def _records():
    def evaluate(train, validation, test, seed):
        if seed % 3 == 0:
            raise UndefinedRankCorrelation("synthetic constant ranks")
        if seed % 3 == 1:
            raise ValueError("synthetic failed evaluator")
        return {"synthetic_result": True}

    return run_full_pipeline_bootstrap(
        n_replicates=30, train_size=4, validation_size=4, test_size=4,
        base_seed=36, evaluate_replicate=evaluate,
    )


def test_audit_counts_all_attempts_and_keeps_uncoded_failures():
    records = _records()
    audit = audit_bootstrap_attempts(records)
    assert audit["attempt_count"] == 30
    assert audit["successful_return_count"] + audit["failed_attempt_count"] == 30
    assert audit["inconsistent_record_count"] == 0
    assert audit["duplicate_replicate_index_count"] == 0
    assert audit["noncontiguous_replicate_indices"] is False
    assert audit["missing_replicate_seed_count"] == 0
    assert audit["exception_types"].get("UndefinedRankCorrelation", 0) > 0
    assert audit["exception_types"].get("ValueError", 0) > 0
    assert audit["failure_codes"] == {}
    assert audit["scientific_success_certified"] is False
    assert audit["reliability_decision"] is None
    assert audit == audit_bootstrap_attempts(_records())


def test_audit_flags_inconsistent_attempt_instead_of_counting_success():
    bad = BootstrapReplicate(
        replicate_index=0,
        train_indices=np.array([0]),
        validation_indices=np.array([0]),
        test_indices=np.array([0]),
        result=None,
        failure=None,
        replicate_seed=36,
    )
    audit = audit_bootstrap_attempts([bad])
    assert audit["inconsistent_record_count"] == 1
    assert audit["successful_return_count"] == 0
    assert audit["failed_attempt_count"] == 0


def test_audit_rejects_nonrecords():
    with pytest.raises(TypeError):
        audit_bootstrap_attempts([object()])


def test_audit_exposes_duplicate_attempt_indices_and_missing_seed():
    from dataclasses import replace

    records = _records()[:2]
    duplicate = replace(records[1], replicate_index=records[0].replicate_index,
                        replicate_seed=None)
    audit = audit_bootstrap_attempts([records[0], duplicate])
    assert audit["attempt_count"] == 2
    assert audit["duplicate_replicate_index_count"] == 1
    assert audit["noncontiguous_replicate_indices"] is True
    assert audit["missing_replicate_seed_count"] == 1
    assert audit["scientific_success_certified"] is False


@pytest.mark.parametrize("invalid", [True, -1, 1.0, "1"])
def test_audit_rejects_invalid_attempt_index(invalid):
    from dataclasses import replace

    record = replace(_records()[0], replicate_index=invalid)
    with pytest.raises(TypeError):
        audit_bootstrap_attempts([record])


@pytest.mark.parametrize("override", [
    {"n_replicates": True}, {"n_replicates": 1.5}, {"n_replicates": 0},
    {"train_size": False}, {"validation_size": -1}, {"test_size": 2.0},
    {"base_seed": True}, {"base_seed": -1},
])
def test_bootstrap_engine_rejects_invalid_arguments_before_evaluation(override):
    calls = []

    def evaluator(train, validation, test, seed):
        calls.append(seed)
        return "synthetic"

    kwargs = {
        "n_replicates": 2, "train_size": 3, "validation_size": 3,
        "test_size": 3, "base_seed": 36, "evaluate_replicate": evaluator,
    }
    kwargs.update(override)
    with pytest.raises(ValueError):
        run_full_pipeline_bootstrap(**kwargs)
    assert calls == []


def test_bootstrap_engine_does_not_expose_stored_draws_to_mutating_evaluator():
    def evaluator(train, validation, test, seed):
        train[:] = -1
        validation[:] = -1
        test[:] = -1
        return "synthetic"

    records = run_full_pipeline_bootstrap(
        n_replicates=3, train_size=3, validation_size=3, test_size=3,
        base_seed=36, evaluate_replicate=evaluator,
    )
    assert all((record.train_indices >= 0).all() for record in records)
    assert all((record.validation_indices >= 0).all() for record in records)
    assert all((record.test_indices >= 0).all() for record in records)
