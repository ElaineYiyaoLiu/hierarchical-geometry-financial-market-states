"""Analytic checks for approved Week 9 formulas, not a production fitter.

Run only under project Python 3.14. All examples are synthetic mathematics.
"""

from itertools import combinations, permutations
from math import exp, factorial, isclose

import pytest

from branch_b.fitters.exact_tie_dp import exact_average_minmax_jacobian


def _sigma(x):
    return 1 / (1 + exp(-x))


def _matrix(n, vector):
    result = [[0.0] * n for _ in range(n)]
    for (i, j), value in zip(combinations(range(n), 2), vector, strict=True):
        result[i][j] = result[j][i] = value
    return result


def _closure(n, vector):
    result = _matrix(n, vector)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                result[i][j] = min(result[i][j], max(result[i][k], result[k][j]))
    return [result[i][j] for i, j in combinations(range(n), 2)]


def _objective(u_vector, delta, masses):
    n = len(masses)
    pairs = tuple(combinations(range(n), 2))
    u = _matrix(n, u_vector)
    total = sum(masses[i] * masses[j] for i, j in pairs)
    value = 0.0
    for (i, j), distance in zip(pairs, delta, strict=True):
        endpoint_mass = sum(
            masses[k] * (_sigma(5 * (u[i][j] - u[i][k]))
                         + _sigma(5 * (u[i][j] - u[j][k])))
            for k in range(n)
        )
        value += masses[i] * masses[j] * endpoint_mass / (2 * distance)
    return value / total


def _smooth_gradient(u_vector, delta, masses):
    n = len(masses)
    pairs = tuple(combinations(range(n), 2))
    u = _matrix(n, u_vector)
    total = sum(masses[i] * masses[j] for i, j in pairs)
    gradient = []
    for a, b in pairs:
        def indicator(i, j):
            return int(i != j and {i, j} == {a, b})

        value = 0.0
        for (i, j), distance in zip(pairs, delta, strict=True):
            for k in range(n):
                for endpoint in (i, j):
                    s = _sigma(5 * (u[i][j] - u[endpoint][k]))
                    value += (masses[i] * masses[j] * masses[k] / distance
                              * s * (1 - s)
                              * (indicator(i, j) - indicator(endpoint, k)))
        gradient.append(5 * value / (2 * total))
    return gradient


def _difference(function, vector, coordinate, step=1e-6):
    above, below = list(vector), list(vector)
    above[coordinate] += step
    below[coordinate] -= step
    return (function(above) - function(below)) / (2 * step)


@pytest.mark.parametrize('masses', [(1, 1), (2, 3)])
@pytest.mark.parametrize('x', [0.0, 0.2, 0.7])
def test_g1_closed_form_and_feasible_derivative(masses, x):
    distance = 0.8
    expected = sum(masses) / (2 * distance) * (_sigma(5 * x) + 0.5)
    derivative = 5 * sum(masses) / (2 * distance) * _sigma(5 * x) * (1 - _sigma(5 * x))
    assert _objective([x], [distance], masses) == pytest.approx(expected)
    assert _smooth_gradient([x], [distance], masses)[0] == pytest.approx(derivative)
    f = lambda v: _objective(v, [distance], masses)
    numerical = ((f([1e-7]) - f([0])) / 1e-7 if x == 0 else _difference(f, [x], 0))
    assert numerical == pytest.approx(derivative, rel=1e-6)


@pytest.mark.parametrize('masses', [(1, 1, 1), (2, 3, 1)])
def test_g2_full_composite_gradient_in_strict_chamber(masses):
    weights, delta = [0.2, 0.5, 0.8], [0.3, 0.7, 1.0]
    u = _closure(3, weights)
    assert u == [0.2, 0.5, 0.5]
    h = _smooth_gradient(u, delta, masses)
    for i in range(3):
        assert h[i] == pytest.approx(_difference(lambda v: _objective(v, delta, masses), u, i), abs=1e-8)
    g = [h[0], h[1] + h[2], 0.0]
    for i in range(3):
        numerical = _difference(lambda v: _objective(_closure(3, v), delta, masses), weights, i)
        assert g[i] == pytest.approx(numerical, abs=1e-8)


def test_g3_full_gradient_matches_mean_limiting_chamber_gradients():
    delta, masses, tied = [0.4, 0.7, 1.0], (2, 3, 1), [0.5] * 3
    h = _smooth_gradient(tied, delta, masses)
    p = exact_average_minmax_jacobian(3, tied).jacobian
    actual = [sum(float(p[row][col]) * h[row] for row in range(3)) for col in range(3)]
    gradients = []
    # For K3, every hierarchy owns two of the six orders, so this average
    # equals the approved two-level average. Do not generalize to K4.
    for order in permutations(range(3)):
        weights = [0.5] * 3
        for rank, edge in enumerate(order):
            weights[edge] += (rank - 1) * 1e-5
        gradients.append([
            _difference(lambda v: _objective(_closure(3, v), delta, masses), weights, col, step=1e-7)
            for col in range(3)
        ])
    expected = [sum(g[col] for g in gradients) / 6 for col in range(3)]
    assert actual == pytest.approx(expected, abs=1e-4)


def test_g4_weighted_self_mass_and_all_one_reduction():
    masses = (2, 3, 1)
    pairs = tuple(combinations(range(3), 2))
    assert [masses[i] * masses[j] for i, j in pairs] == [6, 2, 3]
    assert sum(masses[i] * masses[j] for i, j in pairs) == 11
    # At u=0 every sigmoid is 1/2, including self-mass. With Delta=1
    # the weighted edge mean is exactly half the total active mass.
    assert _objective([0.0] * 3, [1.0] * 3, masses) == 3.0
    assert _objective([0.0] * 3, [1.0] * 3, (1, 1, 1)) == 1.5
    vector, delta = [0.2, 0.5, 0.5], [0.3, 0.7, 1.0]
    u = _matrix(3, vector)
    ordinary = sum(sum(_sigma(5 * (u[i][j] - u[e][k])) for e in (i, j) for k in range(3))
                   / (2 * d) for (i, j), d in zip(pairs, delta, strict=True)) / 3
    assert _objective(vector, delta, (1, 1, 1)) == ordinary
    # Changing fixed admissible input denominators changes J even at fixed u.
    assert not isclose(_objective(vector, delta, masses), _objective(vector, [1.0] * 3, masses))


@pytest.mark.parametrize('weights', [(0.5,) * 6, (0.0, 0.0, 0.4, 0.2, 0.4, 0.4)])
def test_d04_exact_relabeling_equivariance(weights):
    pairs = tuple(combinations(range(4), 2))
    index = {pair: k for k, pair in enumerate(pairs)}
    baseline = exact_average_minmax_jacobian(4, weights)
    for permutation in permutations(range(4)):
        mapped = [index[tuple(sorted((permutation[i], permutation[j])))] for i, j in pairs]
        candidate = exact_average_minmax_jacobian(4, [weights[k] for k in mapped])
        assert candidate.hierarchy_count == baseline.hierarchy_count
        assert candidate.strict_order_count == baseline.strict_order_count
        for row, old_row in enumerate(mapped):
            for col, old_col in enumerate(mapped):
                assert candidate.jacobian[row][col] == baseline.jacobian[old_row][old_col]
    if len(set(weights)) == 1:
        assert baseline.strict_order_count == factorial(6)
