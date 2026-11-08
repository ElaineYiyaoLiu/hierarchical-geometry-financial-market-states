"""Exact D04 min-max Jacobian averaging for a complete weighted graph.

UNVERIFIED DEVELOPMENT IMPLEMENTATION. Do not use for scientific/pilot fitting
until reviewed and tested under the project's required Python 3.14 environment.

Equal total weight is assigned to each distinct labeled binary hierarchy
realizable by strict edge orderings within exactly tied input-weight levels.
Within each hierarchy, its strict edge orderings have equal weight.

No stochastic tie breaking, sampling, premature complexity cutoff, or
fabricated timeout is used. This module is standalone: it does not change the
existing unimplemented scientific fitter or failure-code registry.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import isfinite
from time import monotonic
from typing import Callable, TypeAlias

# Every leaf and internal node is tagged, permitting unambiguous total-order
# comparison and preserving original labeled hierarchy structure.
Node: TypeAlias = tuple
Forest: TypeAlias = tuple[Node, ...]
StateKey: TypeAlias = tuple[int, Forest]
SparseJacobian: TypeAlias = dict[tuple[int, int], int]


@dataclass
class _Accumulator:
    count: int
    jacobian_sum: SparseJacobian


@dataclass(frozen=True)
class ExactD04Result:
    """All rows/columns use lexicographic canonical pairs (i,j), i<j."""

    jacobian: tuple[tuple[Fraction, ...], ...]
    hierarchy_count: int
    strict_order_count: int
    maximum_stage_states: int
    processed_weight_levels: int


class ExactD04DeadlineExpired(TimeoutError):
    """Raised ONLY when the supplied actual monotonic deadline has elapsed."""

    def __init__(self, *, processed_weight_levels: int, maximum_stage_states: int):
        self.processed_weight_levels = processed_weight_levels
        self.maximum_stage_states = maximum_stage_states
        super().__init__("exact D04 computation reached the actual monotonic deadline")


def _leaves(node: Node) -> tuple[int, ...]:
    if node[0] == 0:
        return (node[1],)
    return _leaves(node[1]) + _leaves(node[2])


def _merge(forest: Forest, a: int, b: int) -> tuple[Forest, tuple[int, ...], tuple[int, ...]] | None:
    """Merge components containing a,b; return None for a redundant edge."""
    positions: dict[int, int] = {}
    component_leaves: list[tuple[int, ...]] = []
    for index, node in enumerate(forest):
        members = _leaves(node)
        component_leaves.append(members)
        for member in members:
            positions[member] = index

    ia, ib = positions[a], positions[b]
    if ia == ib:
        return None

    left, right = sorted((forest[ia], forest[ib]))
    parent: Node = (1, left, right)
    next_forest = tuple(sorted(
        [node for i, node in enumerate(forest) if i != ia and i != ib] + [parent]
    ))
    return next_forest, component_leaves[ia], component_leaves[ib]


def _check_input(n: int, weights: tuple[float, ...]) -> tuple[tuple[int, int], ...]:
    if type(n) is not int or n < 2:
        raise ValueError("n must be an integer >= 2")
    edges = tuple(combinations(range(n), 2))
    if len(weights) != len(edges):
        raise ValueError("weights must align with every canonical complete-graph edge")
    if any(
        isinstance(weight, bool)
        or not isinstance(weight, (int, float))
        or not isfinite(weight)
        or weight < 0
        for weight in weights
    ):
        raise ValueError("edge weights must be finite nonnegative real numbers")
    return edges


def exact_average_minmax_jacobian(
    n: int,
    edge_weights: tuple[float, ...] | list[float],
    *,
    deadline_monotonic: float | None = None,
    clock: Callable[[], float] = monotonic,
) -> ExactD04Result:
    """Compute the exact hierarchy-balanced D04 min-max Jacobian.

    Input edges are canonical lexicographic pairs from combinations(range(n),2).
    Each distinct exact edge-weight level is processed separately; the ordering
    between different weight levels is never permuted.

    The state (processed-edge mask, labeled rooted forest) is sufficient:
    future Kruskal merges and their Jacobian increments depend only on it.
    Counts and summed prefix Jacobians of all paths reaching a state may thus
    be aggregated *without* altering the conditional within-hierarchy average.

    The returned Jacobian contains exact rational entries. The caller is
    responsible for applying its transpose to the approved smooth J gradient,
    respecting the method-card failure registry and actual runtime deadline.
    """
    weights = tuple(edge_weights)
    edges = _check_input(n, weights)
    if deadline_monotonic is not None and not isfinite(deadline_monotonic):
        raise ValueError("deadline_monotonic must be finite or None")

    pair_to_row = {pair: index for index, pair in enumerate(edges)}
    levels: dict[float, list[int]] = defaultdict(list)
    for edge_index, weight in enumerate(weights):
        levels[weight].append(edge_index)

    initial_forest: Forest = tuple((0, index) for index in range(n))
    # A completed level always has a zero local mask, because each tied group
    # receives its own mask and is exhausted before the next group.
    frontier: dict[Forest, _Accumulator] = {
        initial_forest: _Accumulator(count=1, jacobian_sum={})
    }
    maximum_stage_states = 1
    processed_levels = 0

    def check_deadline() -> None:
        if deadline_monotonic is not None and clock() >= deadline_monotonic:
            raise ExactD04DeadlineExpired(
                processed_weight_levels=processed_levels,
                maximum_stage_states=maximum_stage_states,
            )

    check_deadline()
    for level in sorted(levels):
        tied_indices = levels[level]
        complete_mask = (1 << len(tied_indices)) - 1
        states: dict[StateKey, _Accumulator] = {
            (0, forest): _Accumulator(acc.count, acc.jacobian_sum.copy())
            for forest, acc in frontier.items()
        }
        maximum_stage_states = max(maximum_stage_states, len(states))

        for depth in range(len(tied_indices)):
            next_states: dict[StateKey, _Accumulator] = {}
            for (mask, forest), acc in states.items():
                check_deadline()
                for local_index, original_edge_index in enumerate(tied_indices):
                    if mask & (1 << local_index):
                        continue
                    check_deadline()
                    a, b = edges[original_edge_index]
                    merged = _merge(forest, a, b)
                    if merged is None:
                        new_forest = forest
                        increments: tuple[tuple[int, int], ...] = ()
                    else:
                        new_forest, component_a, component_b = merged
                        increments = tuple(
                            (pair_to_row[(min(i, j), max(i, j))], original_edge_index)
                            for i in component_a for j in component_b
                        )

                    key = (mask | (1 << local_index), new_forest)
                    target = next_states.get(key)
                    if target is None:
                        target = _Accumulator(count=0, jacobian_sum={})
                        next_states[key] = target
                    target.count += acc.count
                    for location, value in acc.jacobian_sum.items():
                        target.jacobian_sum[location] = (
                            target.jacobian_sum.get(location, 0) + value
                        )
                    for location in increments:
                        target.jacobian_sum[location] = (
                            target.jacobian_sum.get(location, 0) + acc.count
                        )
            states = next_states
            maximum_stage_states = max(maximum_stage_states, len(states))

        # Exact mask exhaustion is an invariant, not an early-stop heuristic.
        if any(mask != complete_mask for mask, _forest in states):
            raise AssertionError("incomplete tied-edge permutation")
        frontier = {}
        for (_mask, forest), acc in states.items():
            previous = frontier.get(forest)
            if previous is None:
                frontier[forest] = acc
            else:
                previous.count += acc.count
                for location, value in acc.jacobian_sum.items():
                    previous.jacobian_sum[location] = (
                        previous.jacobian_sum.get(location, 0) + value
                    )
        processed_levels += 1
        check_deadline()

    # The complete graph is connected; final forest nodes are full labeled trees.
    if any(len(forest) != 1 for forest in frontier):
        raise AssertionError("complete-graph Kruskal forest was not connected")

    total_hierarchies = len(frontier)
    if total_hierarchies == 0:
        raise AssertionError("no realizable strict edge ordering")
    total_orderings = sum(acc.count for acc in frontier.values())
    m = len(edges)
    # Average once within each full hierarchy, then once across hierarchies.
    result = [[Fraction(0) for _ in range(m)] for _ in range(m)]
    for acc in frontier.values():
        check_deadline()
        for (row, col), integer_sum in acc.jacobian_sum.items():
            result[row][col] += Fraction(
                integer_sum, acc.count * total_hierarchies
            )

    return ExactD04Result(
        jacobian=tuple(tuple(row) for row in result),
        hierarchy_count=total_hierarchies,
        strict_order_count=total_orderings,
        maximum_stage_states=maximum_stage_states,
        processed_weight_levels=processed_levels,
    )
