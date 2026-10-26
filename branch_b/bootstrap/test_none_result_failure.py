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


def test_none_failure_replays_deterministically():
    kwargs = dict(
        n_replicates=3,
        train_size=5,
        validation_size=4,
        test_size=4,
        base_seed=1024,
        evaluate_replicate=lambda train, validation, test, seed: None,
    )
    first = run_full_pipeline_bootstrap(**kwargs)
    second = run_full_pipeline_bootstrap(**kwargs)
    assert len(first) == len(second) == 3
    for a, b in zip(first, second, strict=True):
        assert a.replicate_seed == b.replicate_seed
        assert a.train_indices.tolist() == b.train_indices.tolist()
        assert a.validation_indices.tolist() == b.validation_indices.tolist()
        assert a.test_indices.tolist() == b.test_indices.tolist()
        assert a.failure == b.failure


def test_evaluator_exception_preserves_attempt_metadata():
    def evaluator(train, validation, test, seed):
        train[:] = -1  # Mutate only the evaluator's copy.
        raise RuntimeError("synthetic evaluator failure")

    attempts = run_full_pipeline_bootstrap(
        n_replicates=1,
        train_size=5,
        validation_size=4,
        test_size=3,
        base_seed=105,
        evaluate_replicate=evaluator,
    )
    assert len(attempts) == 1
    attempt = attempts[0]
    assert attempt.result is None
    assert attempt.failure == {
        "exception_type": "RuntimeError",
        "message": "synthetic evaluator failure",
    }
    assert attempt.replicate_seed is not None
    assert all(0 <= int(i) < 5 for i in attempt.train_indices)
    assert len(attempt.train_indices) == 5
    audit = audit_bootstrap_attempts(attempts)
    assert audit["failed_attempt_count"] == 1
    assert audit["inconsistent_record_count"] == 0
