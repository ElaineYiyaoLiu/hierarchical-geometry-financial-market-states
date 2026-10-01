from __future__ import annotations

import numpy as np

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.preprocessing import as_finite_matrix


CORRELATION_ROBUST_SPREAD_LOWER_QUANTILE = 0.05
CORRELATION_ROBUST_SPREAD_UPPER_QUANTILE = 0.95


def _validate_distance_matrix(d: np.ndarray) -> np.ndarray:
    if not np.isfinite(d).all():
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "distance matrix contains non-finite values")
    if not np.allclose(d, d.T, rtol=0.0, atol=1e-12):
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "distance matrix is not symmetric")
    if not np.allclose(np.diag(d), 0.0, rtol=0.0, atol=1e-12):
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "distance matrix diagonal is not zero")
    if np.any(d < 0):
        raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "distance matrix contains negative entries")
    return d


def euclidean_dissimilarity(standardized_values: object) -> np.ndarray:
    """Euclidean dissimilarity on an already standardized observable representation.

    Standardization is intentionally not estimated here: train-estimated preprocessing is
    a separate pipeline stage so validation/test data cannot leak into fit parameters.
    """
    x = as_finite_matrix(standardized_values)
    diff = x[:, None, :] - x[None, :, :]
    d = np.sqrt(np.sum(diff * diff, axis=2))
    return _validate_distance_matrix(d)


def chebyshev_dissimilarity(preprocessed_values: object) -> np.ndarray:
    """Chebyshev dissimilarity on an already preprocessed observable representation.

    This implements only the recorded native distance family. The unresolved
    valuation-geometry preprocessing specification remains outside this function.
    """
    x = as_finite_matrix(preprocessed_values)
    diff = np.abs(x[:, None, :] - x[None, :, :])
    d = np.max(diff, axis=2)
    return _validate_distance_matrix(d)


def correlation_profile_admissibility(
    observable_profiles: object,
    *,
    tau_nc: float | None,
    tau_deg: float | None,
    s_min: float | None,
    quantile_method: str | None,
) -> dict:
    """Classify observable profiles by the frozen robust-spread construction.

    Robust spread:
        R(z) = Q_0.95(z) - Q_0.05(z)

    Relative robust spread:
        R_rel(z) = R(z) / max(median(|z|), s_min)

    The quantile levels 0.05 and 0.95 are fixed by the Branch B decision recorded
    on 2026-09-30. The numerical tolerances and quantile interpolation convention
    remain explicit configuration until separately frozen.
    """
    x = as_finite_matrix(observable_profiles)

    if tau_nc is None or tau_deg is None or s_min is None or quantile_method is None:
        raise ConfigurationRequired(
            "correlation admissibility requires frozen tau_nc, tau_deg, s_min, "
            "and quantile interpolation method"
        )

    tau_nc = float(tau_nc)
    tau_deg = float(tau_deg)
    s_min = float(s_min)
    if not np.isfinite(tau_nc) or not np.isfinite(tau_deg) or not np.isfinite(s_min):
        raise ValueError("correlation admissibility parameters must be finite")
    if tau_nc <= 0:
        raise ValueError("tau_nc must be strictly positive")
    if tau_deg < 0 or tau_deg >= tau_nc:
        raise ValueError("tau_deg must satisfy 0 <= tau_deg < tau_nc")
    if s_min <= 0:
        raise ValueError("s_min must be strictly positive")

    try:
        q05 = np.quantile(
            x,
            CORRELATION_ROBUST_SPREAD_LOWER_QUANTILE,
            axis=1,
            method=quantile_method,
        )
        q95 = np.quantile(
            x,
            CORRELATION_ROBUST_SPREAD_UPPER_QUANTILE,
            axis=1,
            method=quantile_method,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid quantile_method: {quantile_method!r}") from exc

    robust_spread = q95 - q05
    median_abs = np.median(np.abs(x), axis=1)
    denominator = np.maximum(median_abs, s_min)
    relative_spread = robust_spread / denominator

    if not np.isfinite(relative_spread).all():
        raise BranchBFailure(
            FailureCode.DEGENERATE_DISTANCE,
            "correlation relative robust spread contains non-finite values",
        )

    status = np.full(x.shape[0], "ordinary", dtype=object)
    status[relative_spread <= tau_nc] = "near_constant"
    status[relative_spread <= tau_deg] = "near_constant_degeneracy"

    return {
        "q05": q05,
        "q95": q95,
        "robust_spread": robust_spread,
        "median_abs": median_abs,
        "denominator": denominator,
        "relative_spread": relative_spread,
        "status": status,
        "quantile_method": quantile_method,
        "tau_nc": tau_nc,
        "tau_deg": tau_deg,
        "s_min": s_min,
    }


def correlation_dissimilarity(
    observable_profiles: object,
    *,
    tau_nc: float | None,
    tau_deg: float | None,
    s_min: float | None,
    quantile_method: str | None,
    degeneracy_handling: str | None = None,
) -> np.ndarray:
    """Pearson-correlation distance under the robust near-constant admissibility rule.

    Ordinary and diagnostic near-constant profiles remain numerically evaluable.
    Profiles classified as near-constant degeneracy require the separately frozen
    degeneracy-handling rule. Until that rule is supplied, execution fails closed.
    """
    x = as_finite_matrix(observable_profiles)
    admissibility = correlation_profile_admissibility(
        x,
        tau_nc=tau_nc,
        tau_deg=tau_deg,
        s_min=s_min,
        quantile_method=quantile_method,
    )
    degenerate = admissibility["status"] == "near_constant_degeneracy"
    if np.any(degenerate):
        if degeneracy_handling is None:
            raise ConfigurationRequired(
                "correlation near-constant degeneracy handling has not yet been frozen"
            )
        if degeneracy_handling == "fail":
            raise BranchBFailure(
                FailureCode.DEGENERATE_DISTANCE,
                "correlation geometry inadmissible: near-constant degeneracy",
            )
        raise ValueError("unsupported correlation degeneracy_handling rule")

    centered = x - x.mean(axis=1, keepdims=True)
    scales = np.sqrt(np.sum(centered * centered, axis=1))
    if np.any(scales <= 0):
        raise BranchBFailure(
            FailureCode.DEGENERATE_DISTANCE,
            "correlation geometry contains an exactly constant observable profile",
        )

    corr = (centered @ centered.T) / np.outer(scales, scales)
    corr = np.clip(corr, -1.0, 1.0)
    d = 1.0 - corr
    np.fill_diagonal(d, 0.0)
    return _validate_distance_matrix(d)
