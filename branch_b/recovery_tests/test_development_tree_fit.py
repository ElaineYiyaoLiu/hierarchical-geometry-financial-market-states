"""Synthetic optimizer-to-tree integration tests. Python 3.14 required."""

from dataclasses import replace
from time import monotonic

import numpy as np
import pytest

from branch_b.failures import ConfigurationRequired
from branch_b.fitters.development_optimizer import run_development_optimizer
from branch_b.fitters.development_tree_fit import (
    development_fit_from_converged_optimizer,
    run_checked_development_tree_fit,
)
from branch_b.recovery_pipeline.result_validation import validate_fit_result


def test_real_two_identity_optimizer_result_exports_valid_tree_and_matrix():
    fit = run_checked_development_tree_fit(
        (0.8,), (2, 3),
        original_sample_order=["A", "B"],
        deadline_monotonic=monotonic() + 30,
    )
    validate_fit_result(fit, sample_order=["A", "B"])
    assert fit.tree["leaves"] == ["A", "B"]
    assert fit.diagnostics["outcome"] == "CONVERGED"
    assert fit.diagnostics["scientific_authorization"] is False
    np.testing.assert_array_equal(
        fit.ultrametric_matrix, fit.ultrametric_matrix.T
    )
    assert len(fit.tree["edges"]) == 2
    assert all(edge["branch_length"] >= 0 for edge in fit.tree["edges"])
    assert fit.tree["edges"][0]["branch_length"] == fit.ultrametric_matrix[0, 1]


def test_converged_synthetic_tied_final_ultrametric_stays_unresolved():
    baseline = run_development_optimizer(
        (0.8,), (1, 1), deadline_monotonic=monotonic() + 30
    )
    synthetic = replace(
        baseline, ultrametric=(0.6, 0.6, 0.6)
    )
    fit = development_fit_from_converged_optimizer(
        synthetic, original_sample_order=["A", "B", "C"]
    )
    assert len(fit.tree["internal_nodes"]) == 1
    assert len(fit.tree["edges"]) == 3
    assert all(edge["unresolved"] for edge in fit.tree["edges"])
    np.testing.assert_array_equal(
        fit.ultrametric_matrix,
        [[0, .6, .6], [.6, 0, .6], [.6, .6, 0]],
    )


def test_nonconverged_optimizer_result_is_not_exported():
    baseline = run_development_optimizer(
        (0.8,), (1, 1), deadline_monotonic=monotonic() + 30
    )
    with pytest.raises(ConfigurationRequired, match="requires convergence"):
        development_fit_from_converged_optimizer(
            replace(baseline, outcome="ITERATION_CAP"),
            original_sample_order=["A", "B"],
        )


def test_original_identity_count_must_match_optimizer_matrix():
    baseline = run_development_optimizer(
        (0.8,), (1, 1), deadline_monotonic=monotonic() + 30
    )
    with pytest.raises(ValueError, match="counts differ"):
        development_fit_from_converged_optimizer(
            baseline, original_sample_order=["A", "B", "C"],
        )
