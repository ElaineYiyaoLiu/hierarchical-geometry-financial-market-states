"""Development-only chain-rule adapter for the exact D04 min-max Jacobian.

This module does not activate the Common Fitter or select objective, optimizer,
convergence, timeout, or failure rules.  Edge order is combinations(range(n), 2).
The caller owns the deadline and maps the existing deadline exception under
its separately approved failure-handling boundary.
"""

from __future__ import annotations

from math import fsum, isfinite
from typing import Sequence

from branch_b.fitters.exact_tie_dp import (
    ExactD04Result,
    exact_average_minmax_jacobian,
)


def apply_d04_jacobian_transpose(
    jacobian_result: ExactD04Result,
    upstream_gradient: Sequence[float],
) -> tuple[float, ...]:
    """Apply J.T @ grad_U to obtain grad_W in canonical pair order.

    J[output_pair, input_edge] is d(Phi_G(W))[output_pair] / dW[input_edge].
    This operation does not define or modify the objective's upstream gradient.
    """
    jacobian = jacobian_result.jacobian
    m = len(jacobian)
    values = tuple(upstream_gradient)
    if len(values) != m:
        raise ValueError("upstream gradient length does not match D04 Jacobian")
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(value)
        for value in values
    ):
        raise ValueError("upstream gradient must contain finite real numbers")
    if any(len(row) != m for row in jacobian):
        raise ValueError("D04 Jacobian must be square")

    return tuple(
        fsum(float(jacobian[row][col]) * values[row] for row in range(m))
        for col in range(m)
    )


def exact_d04_weight_gradient(
    n: int,
    edge_weights: Sequence[float],
    upstream_gradient: Sequence[float],
    *,
    deadline_monotonic: float | None = None,
) -> tuple[float, ...]:
    """Compute the exact D04 averaged chain-rule gradient for edge weights.

    Existing ExactD04DeadlineExpired is propagated unchanged.
    """
    result = exact_average_minmax_jacobian(
        n, tuple(edge_weights), deadline_monotonic=deadline_monotonic
    )
    return apply_d04_jacobian_transpose(result, upstream_gradient)
