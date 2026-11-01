"""Development-only tied-gradient enumeration for a three-leaf triangle.

This module does NOT define the approved D04 admissibility measure or the
gradient for the full Dasgupta-plus-size objective. A binary refinement alone
does not generally identify a unique limiting min-max gradient.
"""
from __future__ import annotations

from itertools import permutations

import numpy as np


EDGES = ((0, 1), (0, 2), (1, 2))


def triangle_tie_resolution_jacobians() -> tuple[tuple[tuple[int, ...], int, np.ndarray], ...]:
    """All six strict edge orderings of an equal-weight three-leaf triangle.

    Each tuple contains the edge ordering, the first (binary) merger, and
    Jacobian of (u_01, u_02, u_12) with respect to (w_01, w_02, w_12).
    With distinct weights the two smallest edges form the MST; the first
    merger is the smallest edge, and the other two ultrametric pair
    distances equal the second-smallest edge weight.
    """
    results = []
    for order in permutations(range(3)):
        first, second, _last = order
        jac = np.zeros((3, 3), dtype=float)
        jac[first, first] = 1.0
        for pair in range(3):
            if pair != first:
                jac[pair, second] = 1.0
        results.append((order, first, jac))
    return tuple(results)


def unresolved_three_way_topology() -> tuple[tuple[int, ...], ...]:
    """Return the single root's children, without inventing binary mergers."""
    return ((0, 1, 2),)
