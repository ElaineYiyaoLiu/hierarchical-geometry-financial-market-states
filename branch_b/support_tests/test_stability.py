import numpy as np
import pytest

from branch_b.support import average_ranks, lca_depth_stability, spearman_with_average_ties


def test_average_ranks_uses_average_for_ties():
    ranks = average_ranks(np.array([10.0, 20.0, 20.0, 30.0]))
    assert np.allclose(ranks, [1.0, 2.5, 2.5, 4.0])


def test_spearman_identical_rank_pattern_is_one():
    assert spearman_with_average_ties(
        np.array([1.0, 2.0, 2.0, 4.0]),
        np.array([10.0, 20.0, 20.0, 40.0]),
    ) == pytest.approx(1.0)


def test_lca_depth_stability_uses_common_relations_only():
    full = {("A", "B"): 3, ("A", "C"): 1, ("B", "C"): 1}
    boot = {("A", "B"): 4, ("A", "C"): 2, ("X", "Y"): 9}
    assert lca_depth_stability(full, boot) == pytest.approx(1.0)
