import numpy as np

from branch_b.bootstrap import run_full_pipeline_bootstrap


def test_bootstrap_resamples_each_split_and_keeps_failures():
    def evaluate(train_idx, validation_idx, test_idx, seed):
        raise RuntimeError("intentional")

    reps = run_full_pipeline_bootstrap(
        n_replicates=2,
        train_size=3,
        validation_size=4,
        test_size=5,
        base_seed=123,
        evaluate_replicate=evaluate,
    )
    assert len(reps) == 2
    assert all(rep.failure is not None for rep in reps)
    assert all(len(rep.train_indices) == 3 for rep in reps)
    assert all(len(rep.validation_indices) == 4 for rep in reps)
    assert all(len(rep.test_indices) == 5 for rep in reps)


def test_bootstrap_is_reproducible_from_branch_b_owned_seed():
    def evaluate(train_idx, validation_idx, test_idx, seed):
        return seed

    kwargs = dict(
        n_replicates=3,
        train_size=5,
        validation_size=4,
        test_size=3,
        base_seed=987654,
        evaluate_replicate=evaluate,
    )
    left = run_full_pipeline_bootstrap(**kwargs)
    right = run_full_pipeline_bootstrap(**kwargs)

    for a, b in zip(left, right, strict=True):
        assert np.array_equal(a.train_indices, b.train_indices)
        assert np.array_equal(a.validation_indices, b.validation_indices)
        assert np.array_equal(a.test_indices, b.test_indices)
        assert a.result == b.result
