import numpy as np
import pytest

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.fitters import GradientDescentUltrametricFitter
from branch_b.normalization import normalize_dissimilarity


def test_common_normalization_uses_max_offdiagonal_and_preserves_order():
    d = np.array([
        [0.0, 2.0, 4.0],
        [2.0, 0.0, 8.0],
        [4.0, 8.0, 0.0],
    ])
    n = normalize_dissimilarity(d)
    assert np.allclose(n, d / 8.0)
    assert n[0, 1] < n[0, 2] < n[1, 2]
    assert n[1, 2] == pytest.approx(1.0)


def test_common_normalization_rejects_degenerate_scale():
    d = np.zeros((3, 3))
    with pytest.raises(BranchBFailure) as exc:
        normalize_dissimilarity(d)
    assert exc.value.code == FailureCode.DEGENERATE_DISTANCE


def test_candidate_fitter_has_registered_project_settings_but_kernel_remains_guarded():
    fitter = GradientDescentUltrametricFitter()
    spec = fitter.project_specification()
    assert spec["graph_rule"] == "complete_graph"
    assert spec["optimizer"] == "AMSGrad"
    assert spec["learning_rate"] == pytest.approx(0.01)
    assert spec["convergence_rule"]["relative_objective_improvement_below"] == pytest.approx(1e-8)
    assert spec["convergence_rule"]["consecutive_iterations"] == 10
    assert spec["max_iterations"] == 1000
    assert spec["near_zero_weight_tolerance"] == pytest.approx(1e-12)
    assert spec["random_restarts"] == 0

    d = np.array([
        [0.0, 0.25, 0.5],
        [0.25, 0.0, 1.0],
        [0.5, 1.0, 0.0],
    ])
    with pytest.raises(ConfigurationRequired):
        fitter.fit(d)


def test_candidate_fitter_rejects_near_zero_reciprocal_weight():
    fitter = GradientDescentUltrametricFitter()
    d = np.array([
        [0.0, 1e-13, 1.0],
        [1e-13, 0.0, 0.5],
        [1.0, 0.5, 0.0],
    ])
    with pytest.raises(BranchBFailure) as exc:
        fitter.validate_normalized_input(d)
    assert exc.value.code == FailureCode.DEGENERATE_DISTANCE


def test_relative_objective_improvement_rule():
    fitter = GradientDescentUltrametricFitter()
    assert fitter.relative_objective_improvement(100.0, 99.0) == pytest.approx(0.01)
