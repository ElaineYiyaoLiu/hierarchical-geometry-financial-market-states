"""Isolated D13 proposed resampled-mean interval arithmetic (development only).

No protocol success/reliability threshold, seed derivation, failure mapping,
coverage guarantee, calibration, or production support decision is defined here.
Caller supplies an explicit NumPy Generator and **already identified successful**
Q values. Run synthetic development tests only under Python 3.14.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import fsum, isfinite
from numbers import Real
from typing import Sequence

import numpy as np


SECONDARY_RESAMPLES = 10_000
LOWER_ONE_BASED_RANK = 250
UPPER_ONE_BASED_RANK = 9750


@dataclass(frozen=True)
class DevelopmentD13Interval:
    point_estimate: float
    lower_endpoint: float
    upper_endpoint: float
    successful_score_count: int
    secondary_resample_count: int
    lower_one_based_rank: int
    upper_one_based_rank: int


def development_d13_resampled_mean_interval(
    successful_q_scores: Sequence[float], *, rng: np.random.Generator
) -> DevelopmentD13Interval:
    """Compute team-selected candidate arithmetic from pre-screened successes.

    This *does not* determine if enough successes/common identities exist.
    The attempt ledger and failures must be retained by the caller separately.
    A returned interval is not a scientifically approved support statement.
    """
    if not isinstance(rng, np.random.Generator):
        raise TypeError("caller must provide an explicit NumPy Generator")
    if isinstance(successful_q_scores, (str, bytes)):
        raise TypeError("successful scores must be finite real scalars")
    scores = tuple(successful_q_scores)
    if not scores:
        raise ValueError("no successful Q scores; reliability outcome not decided here")
    checked = []
    for score in scores:
        if isinstance(score, (bool, np.bool_)) or not isinstance(score, Real):
            raise ValueError("all successful scores must be finite real scalars")
        value = float(score)
        if not isfinite(value):
            raise ValueError("all successful scores must be finite real scalars")
        checked.append(value)
    count = len(checked)
    point_estimate = fsum(checked) / count
    if not isfinite(point_estimate):
        raise ArithmeticError("nonfinite successful-score mean")
    means = np.empty(SECONDARY_RESAMPLES, dtype=np.float64)
    for resample in range(SECONDARY_RESAMPLES):
        positions = rng.integers(0, count, size=count, endpoint=False)
        mean = fsum(checked[int(index)] for index in positions) / count
        if not isfinite(mean):
            raise ArithmeticError("nonfinite secondary-resample mean")
        means[resample] = mean
    means.sort()
    return DevelopmentD13Interval(
        point_estimate=point_estimate,
        lower_endpoint=float(means[LOWER_ONE_BASED_RANK - 1]),
        upper_endpoint=float(means[UPPER_ONE_BASED_RANK - 1]),
        successful_score_count=count,
        secondary_resample_count=SECONDARY_RESAMPLES,
        lower_one_based_rank=LOWER_ONE_BASED_RANK,
        upper_one_based_rank=UPPER_ONE_BASED_RANK,
    )
