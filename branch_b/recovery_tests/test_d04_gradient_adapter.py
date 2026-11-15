"""Synthetic-only D04 Jacobian-to-gradient adapter tests for Python 3.14."""

from fractions import Fraction
from itertools import combinations

import numpy as np
import pytest

from branch_b.fitters.d04_gradient_adapter import (
    apply_d04_jacobian_transpose,
    exact_d04_weight_gradient,
)
from branch_b.fitters.exact_tie_dp import (
    ExactD04DeadlineExpired,
    exact_average_minmax_jacobian,
)
from branch_b.fitters.minmax_unique_gradient import unique_bottleneck_jacobian


def test_complete_tie_chain_rule_orientation():
    result = exact_average_minmax_jacobian(3, (0.5, 0.5, 0.5))
    upstream = (2.0, 3.0, 5.0)
    expected = tuple(
        float(sum(result.jacobian[row][col] * Fraction(upstream[row])
                  for row in range(3)))
        for col in range(3)
    )
    assert apply_d04_jacobian_transpose(result, upstream) == pytest.approx(expected)
    assert exact_d04_weight_gradient(3, (0.5,) * 3, upstream) == pytest.approx(expected)


def test_tie_free_matches_independent_unique_bottleneck_reference():
    n = 4
    weights = (0.1, 0.25, 0.6, 0.35, 0.8, 0.9)
    matrix = np.zeros((n, n), dtype=float)
    edges = tuple(combinations(range(n), 2))
    for (i, j), weight in zip(edges, weights, strict=True):
        matrix[i, j] = matrix[j, i] = weight
    reference_pairs, reference_jacobian = unique_bottleneck_jacobian(matrix)
    assert tuple(map(tuple, reference_pairs.tolist())) == edges

    upstream = np.array((1.0, -0.5, 2.0, 0.25, 1.5, -1.0))
    expected = reference_jacobian.T @ upstream
    actual = exact_d04_weight_gradient(n, weights, tuple(upstream))
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)


def test_upstream_validation():
    result = exact_average_minmax_jacobian(3, (0.5,) * 3)
    with pytest.raises(ValueError):
        apply_d04_jacobian_transpose(result, (1.0,))
    with pytest.raises(ValueError):
        apply_d04_jacobian_transpose(result, (1.0, float("nan"), 2.0))
    with pytest.raises(ValueError):
        apply_d04_jacobian_transpose(result, (1.0, True, 2.0))


def test_deadline_propagates_without_remapping():
    with pytest.raises(ExactD04DeadlineExpired):
        exact_d04_weight_gradient(
            3, (0.5,) * 3, (1.0,) * 3, deadline_monotonic=0.0
        )
