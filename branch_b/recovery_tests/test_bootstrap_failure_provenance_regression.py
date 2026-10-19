"""Development-only regression coverage for bootstrap failure provenance.

Synthetic inputs and Branch B-owned test seeds only. This does not define a
bootstrap acceptance threshold, interval method, or pilot configuration.
Run under Python 3.14 using the existing Branch B CI workflow.
"""
import numpy as np

from branch_b.bootstrap import run_full_pipeline_bootstrap
from branch_b.failures import BranchBFailure, FailureCode


def test_mixed_bootstrap_outcomes_are_not_dropped_or_reindexed():
    # The first invocation fails; subsequent invocations succeed.
    def evaluator(train_idx, validation_idx, test_idx, seed):
        index = len(calls)
        calls.append(seed)
        if index == 0:
            raise BranchBFailure(FailureCode.NUMERICAL_FIT, "synthetic fit failure")
        return {"seed": seed}

    calls = []
    reps = run_full_pipeline_bootstrap(
        n_replicates=3,
        train_size=4,
        validation_size=3,
        test_size=2,
        base_seed=12345,
        evaluate_replicate=evaluator,
    )
    assert [rep.replicate_index for rep in reps] == [0, 1, 2]
    assert len(calls) == 3
    assert reps[0].result is None
    assert reps[0].failure["failure_code"] == str(FailureCode.NUMERICAL_FIT)
    assert all(rep.failure is None for rep in reps[1:])
    assert [rep.result["seed"] for rep in reps[1:]] == calls[1:]


def test_bootstrap_split_draws_stay_within_their_own_split():
    def evaluator(train_idx, validation_idx, test_idx, seed):
        assert np.all((train_idx >= 0) & (train_idx < 7))
        assert np.all((validation_idx >= 0) & (validation_idx < 3))
        assert np.all((test_idx >= 0) & (test_idx < 2))
        return seed

    reps = run_full_pipeline_bootstrap(
        n_replicates=5,
        train_size=7,
        validation_size=3,
        test_size=2,
        base_seed=67890,
        evaluate_replicate=evaluator,
    )
    assert len(reps) == 5
    assert all(rep.failure is None for rep in reps)
