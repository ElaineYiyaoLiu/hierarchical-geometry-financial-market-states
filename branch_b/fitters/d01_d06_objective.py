"""Isolated D01/D06 soft-cardinality objective and symmetric gradient.

Development-only numerical kernel. This does not enable scientific fitting,
choose a timeout, define low-distinct-count failure mapping, or alter any
Common Fitter configuration. Inputs are canonical upper-triangle pair vectors.
"""

from __future__ import annotations

from itertools import combinations
from math import exp, fsum, isfinite
from numbers import Integral, Real
from typing import Sequence


def _sigmoid(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + exp(-x))
    t = exp(x)
    return t / (1.0 + t)


def soft_cardinality_objective_gradient(
    ultrametric_pairs: Sequence[float],
    input_dissimilarity_pairs: Sequence[float],
    multiplicities: Sequence[int],
) -> tuple[float, tuple[float, ...]]:
    """Return (J, dJ/du) in lexicographic undirected pair order.

    The diagonal u_ii=0 is constant. The gradient coordinate u_ab changes
    both symmetric off-diagonal matrix entries. Fixed input Delta is the
    denominator, never fitted u; beta=5 is the approved sigmoid scale.

    The domain requires at least two active distinct identities, all positive
    integer multiplicities, and positive finite input denominators. Mapping
    domain errors to scientific failure codes belongs to the full fitter.
    """
    masses = tuple(multiplicities)
    n = len(masses)
    if n < 2 or any(
        isinstance(m, bool) or not isinstance(m, Integral) or m <= 0
        for m in masses
    ):
        raise ValueError("at least two active distinct identities with positive integer multiplicities required")

    pairs = tuple(combinations(range(n), 2))
    u_values = tuple(ultrametric_pairs)
    delta_values = tuple(input_dissimilarity_pairs)
    if len(u_values) != len(pairs) or len(delta_values) != len(pairs):
        raise ValueError("upper triangle vectors must match the distinct-identity pairs")

    def checked(values, *, positive):
        output = []
        for value in values:
            if isinstance(value, bool) or not isinstance(value, Real):
                raise ValueError("pair values must be finite real numbers")
            converted = float(value)
            if not isfinite(converted) or (converted <= 0 if positive else converted < 0):
                raise ValueError("pair values violate finite nonnegative/positive domain")
            output.append(converted)
        return tuple(output)

    u_values = checked(u_values, positive=False)
    delta_values = checked(delta_values, positive=True)
    u = [[0.0] * n for _ in range(n)]
    for (i, j), value in zip(pairs, u_values, strict=True):
        u[i][j] = u[j][i] = value

    w = sum(masses[i] * masses[j] for i, j in pairs)
    objective_terms = []
    gradient_terms = [[] for _ in pairs]

    def indicator(a, b, i, j):
        return int(i != j and ((i == a and j == b) or (i == b and j == a)))

    for (i, j), delta in zip(pairs, delta_values, strict=True):
        h = u[i][j]
        scale = masses[i] * masses[j] / (2.0 * delta * w)
        endpoint_terms = []
        for k in range(n):
            for endpoint in (i, j):
                s = _sigmoid(5.0 * (h - u[endpoint][k]))
                endpoint_terms.append(masses[k] * s)
                ds = s * (1.0 - s)
                for col, (a, b) in enumerate(pairs):
                    gradient_terms[col].append(
                        scale * 5.0 * masses[k] * ds *
                        (indicator(a, b, i, j) - indicator(a, b, endpoint, k))
                    )
        objective_terms.append(scale * fsum(endpoint_terms))

    objective = fsum(objective_terms)
    gradient = tuple(fsum(terms) for terms in gradient_terms)
    if not isfinite(objective) or any(not isfinite(x) for x in gradient):
        raise ArithmeticError("non-finite objective or gradient")
    return objective, gradient
