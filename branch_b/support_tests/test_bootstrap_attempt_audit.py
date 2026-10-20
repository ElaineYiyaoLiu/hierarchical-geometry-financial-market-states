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
