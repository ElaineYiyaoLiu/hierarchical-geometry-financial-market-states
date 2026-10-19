"""Safety regressions for the registered but non-executable Common Fitter.

The optimizer kernel is not yet validated. These tests deliberately avoid
pretending that a configured candidate constitutes an executable fitter.
Synthetic matrices only; run with Python 3.14.
"""
import numpy as np
import pytest

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.fitters.gradient_descent import GradientDescentUltrametricFitter


def test_registered_fitter_is_not_mistaken_for_executable_kernel():
    fitter = GradientDescentUltrametricFitter()
    d = np.array([[0.0, 1.0], [1.0, 0.0]])
    with pytest.raises(ConfigurationRequired, match="kernel"):
        fitter.fit(d)


def test_registered_fitter_rejects_zero_weight_before_kernel():
    fitter = GradientDescentUltrametricFitter()
    d = np.array([[0.0, 0.0], [0.0, 0.0]])
    with pytest.raises(BranchBFailure) as exc:
        fitter.fit(d)
    assert exc.value.code == FailureCode.DEGENERATE_DISTANCE


def test_complete_graph_edge_weights_match_input():
    fitter = GradientDescentUltrametricFitter()
    d = np.array([
        [0.0, 0.25, 1.0],
        [0.25, 0.0, 0.5],
        [1.0, 0.5, 0.0],
    ])
    edges, weights = fitter.complete_graph_edges(d)
    assert edges.tolist() == [[0, 1], [0, 2], [1, 2]]
    assert np.array_equal(weights, [0.25, 1.0, 0.5])
