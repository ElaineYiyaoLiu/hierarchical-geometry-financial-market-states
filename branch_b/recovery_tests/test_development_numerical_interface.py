"""Document existing near-symmetry and canonical-upper-triangle behavior.

Synthetic source-conformance characterization only; not a proposal to accept,
reject, average or round additional inputs. Execute with Python 3.14.
"""

from time import monotonic

import numpy as np
import pytest

import branch_b.fitters.development_d06_fitter as dev
from branch_b.failures import BranchBFailure, FailureCode
from branch_b.fitters.gradient_descent import GradientDescentUltrametricFitter


def test_registered_validator_retains_accepted_asymmetry_unchanged():
    matrix = np.array([[0., 0.8], [0.8 + 5e-13, 0.]])
    snapshot = matrix.copy()
    validated = GradientDescentUltrametricFitter().validate_normalized_input(matrix)
    np.testing.assert_array_equal(validated, snapshot)
    assert validated[0, 1] != validated[1, 0]
    np.testing.assert_array_equal(matrix, snapshot)


def test_registered_validator_rejects_asymmetry_above_existing_tolerance():
    matrix = [[0., 0.8], [0.8 + 2e-12, 0.]]
    with pytest.raises(BranchBFailure) as caught:
        GradientDescentUltrametricFitter().validate_normalized_input(matrix)
    assert caught.value.code == FailureCode.DEGENERATE_DISTANCE


def test_registered_validator_retains_accepted_diagonal_residual():
    matrix = [[5e-13, 0.8], [0.8, 0.]]
    checked = GradientDescentUltrametricFitter().validate_normalized_input(matrix)
    assert checked[0, 0] == 5e-13


def test_registered_validator_rejects_diagonal_residual_above_tolerance():
    with pytest.raises(BranchBFailure) as caught:
        GradientDescentUltrametricFitter().validate_normalized_input(
            [[2e-12, 0.8], [0.8, 0.]]
        )
    assert caught.value.code == FailureCode.DEGENERATE_DISTANCE


def test_development_fitter_handoff_uses_canonical_upper_triangle(monkeypatch):
    observed = {}

    def capture(pairs, masses, *, original_sample_order, deadline_monotonic):
        observed["pairs"] = tuple(pairs)
        observed["masses"] = tuple(masses)
        observed["order"] = list(original_sample_order)
        return "synthetic-only-sentinel"

    monkeypatch.setattr(dev, "run_checked_development_tree_fit", capture)
    matrix = np.array([
        [0., 0.4, 0.8],
        [0.4 + 5e-13, 0., 0.6],
        [0.8 - 5e-13, 0.6 + 5e-13, 0.],
    ])
    snapshot = matrix.copy()
    fitter = dev.D06DevelopmentFitter(deadline_monotonic=monotonic() + 30.)
    # This characterization intentionally stops before objective/optimization.
    # The fitter's normal return is replaced by a sentinel to observe the
    # exact validated Delta vector submitted to the optimizer.
    with pytest.raises(AttributeError):
        fitter.fit_with_original_multiplicities(
            matrix, original_sample_order=["A", "B", "C"],
            multiplicities=[2, 1, 3], random_seed=7,
        )
    assert observed == {
        "pairs": (0.4, 0.8, 0.6),
        "masses": (2, 1, 3),
        "order": ["A", "B", "C"],
    }
    np.testing.assert_array_equal(matrix, snapshot)


def test_upper_triangle_reciprocal_guard_is_not_lower_triangle_guard():
    # Both entries are positive, close enough to satisfy the existing
    # symmetry check, but only the upper entry is checked against 1e-12.
    matrix = [[0., 1.5e-12], [0.5e-12, 0.]]
    accepted = GradientDescentUltrametricFitter().validate_normalized_input(matrix)
    assert accepted[0, 1] > 1e-12
    assert accepted[1, 0] <= 1e-12

    reversed_matrix = [[0., 0.5e-12], [1.5e-12, 0.]]
    with pytest.raises(BranchBFailure) as caught:
        GradientDescentUltrametricFitter().validate_normalized_input(reversed_matrix)
    assert caught.value.code == FailureCode.DEGENERATE_DISTANCE
