from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from branch_b.failures import BranchBFailure, FailureCode


@dataclass(frozen=True)
class BootstrapSupportSummary:
    q_hat: float | None
    stability_mean: float | None
    successful_fits: int
    failed_fits: int
    failure_rate: float
    reliable_for_interval: bool


def summarize_successful_support(
    *,
    q_values: list[float],
    stability_values: list[float],
    failed_fits: int,
    minimum_successful_fits: int | None,
) -> BootstrapSupportSummary:
    """Summarize successful bootstrap fits without choosing pilot-fixed CI rules."""
    if len(q_values) != len(stability_values):
        raise ValueError("q_values and stability_values must correspond one-to-one")
    if failed_fits < 0:
        raise ValueError("failed_fits must be non-negative")

    total = len(q_values) + failed_fits
    failure_rate = float(failed_fits / total) if total else 0.0

    if not q_values:
        return BootstrapSupportSummary(
            q_hat=None,
            stability_mean=None,
            successful_fits=0,
            failed_fits=failed_fits,
            failure_rate=failure_rate,
            reliable_for_interval=False,
        )

    q = np.asarray(q_values, dtype=float)
    s = np.asarray(stability_values, dtype=float)
    if not np.isfinite(q).all() or not np.isfinite(s).all():
        raise BranchBFailure(FailureCode.NONFINITE_INPUT, "bootstrap support values must be finite")

    reliable = (
        minimum_successful_fits is not None
        and len(q_values) >= minimum_successful_fits
    )
    return BootstrapSupportSummary(
        q_hat=float(np.mean(q)),
        stability_mean=float(np.mean(s)),
        successful_fits=len(q_values),
        failed_fits=failed_fits,
        failure_rate=failure_rate,
        reliable_for_interval=reliable,
    )
