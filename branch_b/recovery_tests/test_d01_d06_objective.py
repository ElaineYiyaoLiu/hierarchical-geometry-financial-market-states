"""Python 3.14 synthetic checks for the isolated D01/D06 objective kernel."""

import pytest

from branch_b.fitters.d01_d06_objective import soft_cardinality_objective_gradient
from branch_b.fitters.d04_gradient_adapter import exact_d04_weight_gradient
from branch_b.recovery_tests.test_week9_objective_reference import (
    _closure, _objective, _smooth_gradient,
)


@pytest.mark.parametrize(
    "masses,u,delta",
    [
        ((1, 1), (0.2,), (0.8,)),
        ((2, 3), (0.0,), (0.8,)),
        ((1, 1, 1), (0.2, 0.5, 0.5), (0.3, 0.7, 1.0)),
        ((2, 3, 1), (0.2, 0.5, 0.5), (0.3, 0.7, 1.0)),
        ((2, 3, 1), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
    ],
)
def test_kernel_agrees_with_independent_week9_reference(masses, u, delta):
    objective, gradient = soft_cardinality_objective_gradient(u, delta, masses)
    assert objective == pytest.approx(_objective(u, delta, masses), rel=1e-12)
    assert gradient == pytest.approx(_smooth_gradient(u, delta, masses), rel=1e-12, abs=1e-12)


def test_full_composite_gradient_in_strict_chamber():
    weights = (0.2, 0.5, 0.8)
    delta = (0.3, 0.7, 1.0)
    masses = (2, 3, 1)
    u = _closure(3, weights)
    _, upstream = soft_cardinality_objective_gradient(u, delta, masses)
    actual = exact_d04_weight_gradient(3, weights, upstream)

    step = 1e-6
    for coordinate in range(3):
        plus, minus = list(weights), list(weights)
        plus[coordinate] += step
        minus[coordinate] -= step
        jp = soft_cardinality_objective_gradient(_closure(3, plus), delta, masses)[0]
        jm = soft_cardinality_objective_gradient(_closure(3, minus), delta, masses)[0]
        assert actual[coordinate] == pytest.approx(
            (jp - jm) / (2 * step), abs=1e-8
        )


@pytest.mark.parametrize(
    "u,delta,masses",
    [
        ((0.0,), (0.8,), (1,)),
        ((0.0,), (0.8,), (1, 0)),
        ((0.0,), (0.0,), (1, 1)),
        ((-0.1,), (0.8,), (1, 1)),
        ((0.1,), (0.8,), (True, 1)),
        ((0.1, 0.2), (0.8,), (1, 1)),
    ],
)
def test_invalid_objective_domain_does_not_choose_failure_code(u, delta, masses):
    with pytest.raises(ValueError):
        soft_cardinality_objective_gradient(u, delta, masses)
