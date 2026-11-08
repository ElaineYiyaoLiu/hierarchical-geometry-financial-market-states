"""Independent exact D04 oracle tests; NOT EXECUTED before Python 3.14.

The oracle deliberately does not call the DP's merge/state helpers.
Only small synthetic complete graphs are used.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import combinations, permutations, product

import pytest

from branch_b.fitters.exact_tie_dp import (
    ExactD04DeadlineExpired,
    exact_average_minmax_jacobian,
)


def _oracle(n: int, weights: tuple[float, ...]):
    """Enumerate all orderings, average within labeled trees, then across trees."""
    edges = tuple(combinations(range(n), 2))
    levels = [
        tuple(index for index, weight in enumerate(weights) if weight == level)
        for level in sorted(set(weights))
    ]
    all_orders = product(*(permutations(group) for group in levels))
    # Each full hierarchy owns a list of complete output-to-input controllers.
    by_tree = defaultdict(list)
    count = 0

    for group_order in all_orders:
        strict_order = tuple(index for group in group_order for index in group)
        components = {
            i: (frozenset({i}), (0, i))
            for i in range(n)
        }
        controllers = {}
        for index in strict_order:
            a, b = edges[index]
            group_a = next(obj for obj in components.values() if a in obj[0])
            group_b = next(obj for obj in components.values() if b in obj[0])
            if group_a is group_b:
                continue
            members_a, node_a = group_a
            members_b, node_b = group_b
            for i in members_a:
                for j in members_b:
                    controllers[(min(i, j), max(i, j))] = index
            parent = (1, *sorted((node_a, node_b)))
            merged = (members_a | members_b, parent)
            for i in members_a | members_b:
                components[i] = merged
        hierarchy = components[0][1]
        by_tree[hierarchy].append(tuple(controllers[pair] for pair in edges))
        count += 1

    m = len(edges)
    total_trees = len(by_tree)
    result = [[Fraction(0) for _ in range(m)] for _ in range(m)]
    for assignments in by_tree.values():
        n_assignments = len(assignments)
        for assignment in assignments:
            for row, column in enumerate(assignment):
                result[row][column] += Fraction(1, total_trees * n_assignments)
    return tuple(tuple(row) for row in result), total_trees, count


@pytest.mark.parametrize(
    ("n", "weights"),
    [
        (2, (0.4,)),
        (3, (0.2, 0.5, 0.8)),
        (3, (0.5, 0.5, 0.5)),
        (4, (0.5,) * 6),
        (4, (0.1, 0.1, 0.3, 0.3, 0.4, 0.4)),
        (5, (0.2,) * 4 + (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)),
    ],
)
def test_dp_agrees_with_independent_exact_oracle(n, weights):
    expected, trees, strict_orders = _oracle(n, weights)
    result = exact_average_minmax_jacobian(n, weights)
    assert result.jacobian == expected
    assert result.hierarchy_count == trees
    assert result.strict_order_count == strict_orders
    assert all(sum(row) == 1 for row in result.jacobian)


def test_three_vertex_complete_tie_known_single_row():
    result = exact_average_minmax_jacobian(3, [0.5, 0.5, 0.5])
    # Canonical rows/columns: AB, AC, BC.
    assert result.jacobian[0] == (
        Fraction(2, 3), Fraction(1, 6), Fraction(1, 6)
    )
    assert result.hierarchy_count == 3
    assert result.strict_order_count == 6


def test_actual_deadline_expiry_only():
    with pytest.raises(ExactD04DeadlineExpired):
        exact_average_minmax_jacobian(
            3, [0.2, 0.2, 0.2],
            deadline_monotonic=10.0,
            clock=lambda: 10.0,
        )
    # A nonexpired deadline cannot cause predictive early termination.
    result = exact_average_minmax_jacobian(
        3, [0.2, 0.2, 0.2],
        deadline_monotonic=10.0,
        clock=lambda: 9.0,
    )
    assert result.hierarchy_count == 3


@pytest.mark.parametrize(
    "bad", [(0.1,), (0.0, 0.0), (-0.1, 0.1, 0.2), (float("nan"), 0.1, 0.2)]
)
def test_bad_inputs_rejected(bad):
    with pytest.raises(ValueError):
        exact_average_minmax_jacobian(3, bad)


def test_zero_weights_are_admissible_without_jitter():
    result = exact_average_minmax_jacobian(3, (0.0, 0.0, 0.0))
    assert result.jacobian[0] == (
        Fraction(2, 3), Fraction(1, 6), Fraction(1, 6)
    )
