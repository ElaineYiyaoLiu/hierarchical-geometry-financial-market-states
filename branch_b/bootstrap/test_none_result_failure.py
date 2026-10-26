"""Regression for an evaluator returning no bootstrap result.

Synthetic-only control; does not define scientific bootstrap reliability rules.
"""

from branch_b.bootstrap.attempt_audit import audit_bootstrap_attempts
from branch_b.bootstrap.engine import run_full_pipeline_bootstrap


def test_none_evaluator_result_is_recorded_as_failed_attempt():
    attempts = run_full_pipeline_bootstrap(
        n_replicates=2,
        train_size=4,
        validation_size=3,
        test_size=3,
        base_seed=36,
        evaluate_replicate=lambda train, validation, test, seed: None,
    )
    assert len(attempts) == 2
    for index, attempt in enumerate(attempts):
        assert attempt.replicate_index == index
        assert attempt.replicate_seed is not None
        assert attempt.result is None
        assert attempt.failure is not None
        assert attempt.failure["exception_type"] == "ValueError"
        assert "returned None" in attempt.failure["message"]
        assert "failure_code" not in attempt.failure
    audit = audit_bootstrap_attempts(attempts)
    assert audit["attempt_count"] == 2
    assert audit["failed_attempt_count"] == 2
    assert audit["inconsistent_record_count"] == 0
    assert audit["successful_return_count"] == 0
    assert audit["scientific_success_certified"] is False
