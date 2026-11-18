"""Independent synthetic D04/D06 numerical oracles; development only.

Run with project Python 3.14. This test module does not authorize scientific
fitting, choose numeric policy, alter production code, or use hidden data.
"""

from fractions import Fraction
from math import exp

import pytest

from branch_b.fitters.d01_d06_objective import soft_cardinality_objective_gradient
from branch_b.fitters.exact_tie_dp import exact_average_minmax_jacobian


def test_d04_three_vertex_full_tie_has_explicit_hierarchy_balanced_jacobian():
    # Canonical edges are (0,1), (0,2), (1,2).
    # Each edge is equally likely to form the first (cherry) merge.
    # Given the cherry, either of the two remaining edges is equally likely
    # to complete the hierarchy, while the final redundant edge changes nothing.
    result = exact_average_minmax_jacobian(3, (0.4, 0.4, 0.4))
    expected = (
        (Fraction(2, 3), Fraction(1, 6), Fraction(1, 6)),
        (Fraction(1, 6), Fraction(2, 3), Fraction(1, 6)),
        (Fraction(1, 6), Fraction(1, 6), Fraction(2, 3)),
    )
    assert result.jacobian == expected
    assert result.hierarchy_count == 3
    assert result.strict_order_count == 6


def test_d06_two_originals_matches_independent_closed_form():
    # Multiplicities affect soft self-mass; no duplicate leaves/edges exist.
    # For two originals with fitted separation h:
    # S_A(h) = m_A * sigmoid(5h) + m_B/2
    # S_B(h) = m_B * sigmoid(5h) + m_A/2
    # W = m_A*m_B, so the pair weight cancels the normalization.
    m_a, m_b = 2, 3
    h, delta = 0.4, 0.8
    sigmoid = 1.0 / (1.0 + exp(-5.0 * h))
    expected_j = (m_a + m_b) * (sigmoid + 0.5) / (2.0 * delta)
    expected_derivative = (
        (m_a + m_b) * 5.0 * sigmoid * (1.0 - sigmoid) / (2.0 * delta)
    )
    observed_j, observed_gradient = soft_cardinality_objective_gradient(
        (h,), (delta,), (m_a, m_b)
    )
    assert observed_j == pytest.approx(expected_j, rel=1e-13, abs=1e-13)
    assert observed_gradient == pytest.approx((expected_derivative,), rel=1e-13, abs=1e-13)


@pytest.mark.parametrize("masses", [(1, 1, 1), (2, 1, 3), (3, 2, 1)])
def test_d06_smooth_gradient_matches_central_difference(masses):
    # A strictly positive synthetic input and an admissible ultrametric for 3
    # originals (two equal large distances). The soft objective is smooth in
    # its supplied pair coordinates even when their values tie.
    delta = (0.35, 0.85, 0.75)
    u = (0.25, 0.65, 0.65)
    _, gradient = soft_cardinality_objective_gradient(u, delta, masses)
    step = 1e-6
    for index, derivative in enumerate(gradient):
        plus = list(u)
        minus = list(u)
        plus[index] += step
        minus[index] -= step
        jp, _ = soft_cardinality_objective_gradient(plus, delta, masses)
        jm, _ = soft_cardinality_objective_gradient(minus, delta, masses)
        finite_difference = (jp - jm) / (2.0 * step)
        assert derivative == pytest.approx(finite_difference, rel=2e-6, abs=2e-7)
