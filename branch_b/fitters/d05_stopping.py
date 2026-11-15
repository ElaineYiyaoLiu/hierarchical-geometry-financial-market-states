"""Isolated D05 convergence accounting for the approved Common Fitter candidate.

Development-only deterministic helper. No optimizer, deadline, or scientific
failure mapping is activated here. Call only after a *complete* projected update.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

D05_RELATIVE_TOLERANCE = 1e-6
D05_CONSECUTIVE_UPDATES = 5
D05_MAX_COMPLETED_UPDATES = 1000
D05_RELATIVE_FLOOR = 1e-12


@dataclass(frozen=True)
class D05Progress:
    initial_objective: float
    previous_objective: float
    completed_updates: int = 0
    consecutive_small_changes: int = 0


@dataclass(frozen=True)
class D05Update:
    progress: D05Progress
    relative_change: float
    outcome: str


def initialize_d05(initial_objective: float) -> D05Progress:
    if not isfinite(initial_objective):
        raise ValueError("initial objective must be finite")
    return D05Progress(float(initial_objective), float(initial_objective))


def record_completed_d05_update(
    progress: D05Progress,
    current_objective: float,
) -> D05Update:
    """Account for one *completed* projected optimizer update.

    Returns one of CONTINUE, CONVERGED, or ITERATION_CAP. The caller owns
    failure-code mapping and timeout checks; this helper never reports TIMEOUT.
    """
    if not isfinite(current_objective):
        raise ValueError("updated objective must be finite")
    if progress.completed_updates >= D05_MAX_COMPLETED_UPDATES:
        raise ValueError("cannot record beyond the approved completed-update cap")
    previous = progress.previous_objective
    change = abs(float(current_objective) - previous) / max(
        abs(previous), abs(progress.initial_objective), D05_RELATIVE_FLOOR
    )
    consecutive = (
        progress.consecutive_small_changes + 1
        if change < D05_RELATIVE_TOLERANCE
        else 0
    )
    completed = progress.completed_updates + 1
    next_progress = D05Progress(
        progress.initial_objective,
        float(current_objective),
        completed,
        consecutive,
    )
    outcome = (
        "CONVERGED" if consecutive >= D05_CONSECUTIVE_UPDATES
        else "ITERATION_CAP" if completed == D05_MAX_COMPLETED_UPDATES
        else "CONTINUE"
    )
    return D05Update(next_progress, change, outcome)
