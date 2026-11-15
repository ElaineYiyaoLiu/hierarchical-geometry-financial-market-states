"""Development-only composite D01/D03/D04/D05/D06 optimizer exercise.

Uses approved isolated mathematical components with canonical upper-triangle
ordering. Does NOT register or activate the production Common Fitter, map
exceptions to scientific failure codes, choose a pilot deadline, produce a
validated tree, or alter the frozen pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from time import monotonic
from typing import Sequence

import numpy as np

from branch_b.fitters.d01_d06_objective import soft_cardinality_objective_gradient
from branch_b.fitters.d03_amsgrad import initialize_amsgrad, projected_amsgrad_step
from branch_b.fitters.d04_gradient_adapter import exact_d04_weight_gradient
from branch_b.fitters.d05_stopping import (
    D05_MAX_COMPLETED_UPDATES, initialize_d05, record_completed_d05_update,
)
from branch_b.fitters.exact_tie_dp import ExactD04DeadlineExpired
from branch_b.fitters.minmax_operator import subdominant_ultrametric


@dataclass(frozen=True)
class DevelopmentOptimizerResult:
    outcome: str  # CONVERGED or ITERATION_CAP; no scientific failure mapping
    completed_updates: int
    weights: tuple[float, ...]
    ultrametric: tuple[float, ...]
    objective_history: tuple[float, ...]
    relative_change_history: tuple[float, ...]
    elapsed_seconds: float


def _ultrametric_vector(n: int, weights: Sequence[float]) -> tuple[float, ...]:
    matrix = np.zeros((n, n), dtype=float)
    for (i, j), value in zip(combinations(range(n), 2), weights, strict=True):
        matrix[i, j] = matrix[j, i] = value
    u = subdominant_ultrametric(matrix)
    return tuple(float(u[i, j]) for i, j in combinations(range(n), 2))


def run_development_optimizer(
    input_dissimilarity_pairs: Sequence[float],
    multiplicities: Sequence[int],
    *,
    deadline_monotonic: float,
) -> DevelopmentOptimizerResult:
    """Optimize from Delta using approved components, until convergence/cap/deadline.

    The caller provides an actual monotonic deadline. An expired deadline raises
    ExactD04DeadlineExpired, never a synthetic TIMEOUT result. No approximate
    D04 fallback, early state-count guard, best-so-far replacement, or
    iteration-count override is introduced.

    The project-facing failure mapper must later distinguish numerical errors,
    D04 deadline expiry, and cap exhaustion.
    """
    if isinstance(deadline_monotonic, bool) or not isinstance(
        deadline_monotonic, (int, float)
    ) or not isfinite(deadline_monotonic):
        raise ValueError("a finite monotonic deadline is required")
    started = monotonic()
    masses = tuple(multiplicities)
    n = len(masses)
    delta = tuple(input_dissimilarity_pairs)
    if len(delta) != n * (n - 1) // 2:
        raise ValueError("input pair vector does not match active identities")
    # The source-registered input reciprocal tolerance applies to distinct
    # input Delta only; projected optimizer weights may reach zero.
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float))
        or not isfinite(value) or value <= 1e-12
        for value in delta
    ):
        raise ValueError("fixed normalized input denominators must exceed 1e-12")
    weights = np.asarray(delta, dtype=np.float64).copy()
    # Preflight the multiplicities and objective domain even if deadline expired.
    ultrametric = _ultrametric_vector(n, weights)
    initial, _ = soft_cardinality_objective_gradient(ultrametric, delta, masses)
    progress = initialize_d05(initial)
    states = initialize_amsgrad(weights)
    objectives = [initial]
    changes: list[float] = []

    def check_deadline() -> None:
        if monotonic() >= deadline_monotonic:
            raise ExactD04DeadlineExpired(
                processed_weight_levels=0, maximum_stage_states=0
            )

    while progress.completed_updates < D05_MAX_COMPLETED_UPDATES:
        check_deadline()
        ultrametric = _ultrametric_vector(n, weights)
        _, upstream = soft_cardinality_objective_gradient(
            ultrametric, delta, masses
        )
        gradient = exact_d04_weight_gradient(
            n, tuple(float(w) for w in weights), upstream,
            deadline_monotonic=deadline_monotonic,
        )
        check_deadline()
        next_weights, next_states = projected_amsgrad_step(
            weights, gradient, states
        )
        next_ultrametric = _ultrametric_vector(n, next_weights)
        current, _ = soft_cardinality_objective_gradient(
            next_ultrametric, delta, masses
        )
        # Count only completed projected steps with a finite evaluated J.
        update = record_completed_d05_update(progress, current)
        weights, states, progress = next_weights, next_states, update.progress
        objectives.append(current)
        changes.append(update.relative_change)
        if update.outcome != "CONTINUE":
            return DevelopmentOptimizerResult(
                outcome=update.outcome,
                completed_updates=progress.completed_updates,
                weights=tuple(float(w) for w in weights),
                ultrametric=next_ultrametric,
                objective_history=tuple(objectives),
                relative_change_history=tuple(changes),
                elapsed_seconds=monotonic() - started,
            )
    raise AssertionError("approved D05 cap should produce a terminal outcome")
