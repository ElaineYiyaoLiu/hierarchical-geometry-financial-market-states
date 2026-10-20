"""Synthetic rank-comparison failure tests; no hidden hierarchy or official data."""
import numpy as np
import pytest

from branch_b.bootstrap.engine import run_full_pipeline_bootstrap
from branch_b.support.stability import (
    UndefinedRankCorrelation, lca_depth_stability, spearman_with_average_ties,
)


@pytest.mark.parametrize("which_constant", ["left", "right", "both"])
def test_constant_ranks_are_undefined_not_structurally_invalid(which_constant):
    varied = np.array([1.0, 2.0, 3.0])
    constant = np.array([1.0, 1.0, 1.0])
    left = constant if which_constant in ("left", "both") else varied
    right = constant if which_constant in ("right", "both") else varied
    with pytest.raises(UndefinedRankCorrelation, match="undefined"):
        spearman_with_average_ties(left, right)


def test_valid_star_comparison_is_unsuccessful_without_invalid_tree_code():
    """Equal LCA depths are allowed; rank correlation itself is undefined."""
    full = {("a", "b"): 1, ("a", "c"): 1, ("b", "c"): 1}
    other = {("a", "b"): 2, ("a", "c"): 2, ("b", "c"): 2}
    with pytest.raises(UndefinedRankCorrelation):
        lca_depth_stability(full, other)

    def evaluator(train, validation, test, seed):
        return lca_depth_stability(full, other)

    records = run_full_pipeline_bootstrap(
        n_replicates=2, train_size=3, validation_size=3,
        test_size=3, base_seed=36, evaluate_replicate=evaluator,
    )
    assert len(records) == 2
    assert all(record.result is None for record in records)
    assert all(record.failure["exception_type"] == "UndefinedRankCorrelation" for record in records)
    assert all("failure_code" not in record.failure for record in records)
    assert all(record.replicate_seed is not None for record in records)


def test_nonconstant_rank_agreement_remains_defined():
    x = np.array([1.0, 2.0, 2.0, 4.0])
    assert spearman_with_average_ties(x, x) == pytest.approx(1.0)
