import numpy as np

from branch_b.bootstrap import run_full_pipeline_bootstrap
from branch_b.failures import BranchBFailure, FailureCode


def test_bootstrap_preserves_protocol_failure_code():
    def evaluate(train_idx, validation_idx, test_idx, seed):
        raise BranchBFailure(FailureCode.NUMERICAL_FIT, "intentional numerical failure")

    reps = run_full_pipeline_bootstrap(
        n_replicates=1,
        train_size=2,
        validation_size=2,
        test_size=2,
        base_seed=1,
        evaluate_replicate=evaluate,
    )
    assert reps[0].failure["failure_code"] == "NUMERICAL_FIT"
