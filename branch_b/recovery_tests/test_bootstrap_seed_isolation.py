"""Synthetic bootstrap seed-isolation checks (Python 3.14 CI only).

A failing replicate must not change later replicate draws or owned seeds.
"""
import numpy as np

from branch_b.bootstrap.engine import run_full_pipeline_bootstrap


def _run(failing):
    def evaluate(train, validation, test, seed):
        if failing and len(train) and train[0] >= 0:
            raise RuntimeError("synthetic evaluation failure")
        return {"seed": seed}
    return run_full_pipeline_bootstrap(
        n_replicates=4,
        train_size=5,
        validation_size=3,
        test_size=2,
        base_seed=2026,
        evaluate_replicate=evaluate,
    )


def test_replicate_draws_do_not_depend_on_evaluation_failures():
    successful = _run(False)
    failed = _run(True)
    assert len(successful) == len(failed) == 4
    for ok, bad in zip(successful, failed, strict=True):
        assert ok.replicate_index == bad.replicate_index
        assert np.array_equal(ok.train_indices, bad.train_indices)
        assert np.array_equal(ok.validation_indices, bad.validation_indices)
        assert np.array_equal(ok.test_indices, bad.test_indices)
        assert ok.failure is None
        assert bad.result is None
        assert bad.failure["exception_type"] == "RuntimeError"


def test_repeated_bootstrap_has_identical_owned_seeds():
    first = _run(False)
    second = _run(False)
    assert [rep.result["seed"] for rep in first] == [
        rep.result["seed"] for rep in second
    ]


def test_one_failed_replicate_does_not_shift_later_owned_seeds():
    baseline = _run(False)

    def evaluate(train, validation, test, seed):
        if seed == baseline[1].result["seed"]:
            raise RuntimeError("single synthetic replicate failure")
        return {"seed": seed}

    with_failure = run_full_pipeline_bootstrap(
        n_replicates=4,
        train_size=5,
        validation_size=3,
        test_size=2,
        base_seed=2026,
        evaluate_replicate=evaluate,
    )
    assert with_failure[1].failure["exception_type"] == "RuntimeError"
    assert with_failure[1].result is None
    for index in (0, 2, 3):
        assert with_failure[index].failure is None
        assert with_failure[index].result["seed"] == baseline[index].result["seed"]
        assert np.array_equal(with_failure[index].train_indices, baseline[index].train_indices)
        assert np.array_equal(with_failure[index].validation_indices, baseline[index].validation_indices)
        assert np.array_equal(with_failure[index].test_indices, baseline[index].test_indices)
