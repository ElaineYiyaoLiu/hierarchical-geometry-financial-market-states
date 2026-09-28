from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SupportDecision:
    score: float
    interval_lower: float | None
    interval_upper: float | None
    threshold: float | None
    decision: str
    reason: str


def classify_support(
    *,
    score: float,
    interval_lower: float | None,
    interval_upper: float | None,
    threshold: float | None,
    reliable_interval: bool,
) -> SupportDecision:
    """Apply the protocol-defined interval-based support rule.

    A missing/unreliable interval or missing frozen threshold is indeterminate.
    Equality with the threshold is indeterminate.
    """
    if not np.isfinite(score):
        raise ValueError("support score must be finite")

    if not reliable_interval:
        return SupportDecision(
            score=score,
            interval_lower=interval_lower,
            interval_upper=interval_upper,
            threshold=threshold,
            decision="indeterminate",
            reason="reliable bootstrap interval unavailable",
        )

    if threshold is None:
        return SupportDecision(
            score=score,
            interval_lower=interval_lower,
            interval_upper=interval_upper,
            threshold=None,
            decision="indeterminate",
            reason="frozen geometry-specific threshold unavailable",
        )

    if interval_lower is None or interval_upper is None:
        raise ValueError("reliable_interval=True requires both interval endpoints")
    lower = float(interval_lower)
    upper = float(interval_upper)
    q = float(threshold)
    if not np.isfinite(lower) or not np.isfinite(upper) or not np.isfinite(q):
        raise ValueError("interval endpoints and threshold must be finite")
    if lower > upper:
        raise ValueError("interval lower endpoint cannot exceed upper endpoint")

    if lower > q:
        decision = "supported"
        reason = "lower interval endpoint exceeds frozen threshold"
    elif upper < q:
        decision = "not supported"
        reason = "upper interval endpoint is below frozen threshold"
    else:
        decision = "indeterminate"
        reason = "interval includes or touches frozen threshold"

    return SupportDecision(
        score=score,
        interval_lower=lower,
        interval_upper=upper,
        threshold=q,
        decision=decision,
        reason=reason,
    )
