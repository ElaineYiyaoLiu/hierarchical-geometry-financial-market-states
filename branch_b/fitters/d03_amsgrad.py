"""Isolated D03 projected AMSGrad step, Option A (development only).

Approved arithmetic:
    m_t = beta1*m_(t-1) + (1-beta1)*g_t
    v_t = beta2*v_(t-1) + (1-beta2)*g_t**2
    vmax_t = max(vmax_(t-1), v_t)        # raw second moments
    mhat_t = m_t/(1-beta1**t)
    vhatmax_t = vmax_t/(1-beta2**t)
    candidate = w_t - eta*mhat_t/(sqrt(vhatmax_t)+epsilon)
    w_(t+1) = max(0, candidate)

The gradient is not clipped or masked at the projection boundary.
This helper does not activate the Common Fitter, select a timeout, or map
numerical failures to scientific failure codes.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


D03_LEARNING_RATE = 0.01
D03_BETA1 = 0.9
D03_BETA2 = 0.999
D03_EPSILON = 1e-8


@dataclass(frozen=True)
class AMSGradState:
    """Moments after completed step t; arrays are immutable snapshots."""

    t: int
    first_moment: np.ndarray
    second_moment: np.ndarray
    maximum_raw_second_moment: np.ndarray


def _vector(values: object, name: str, *, nonnegative: bool) -> np.ndarray:
    if np.ma.isMaskedArray(values):
        raise ValueError(f"{name} cannot be masked")
    raw = np.asarray(values)
    if raw.ndim != 1 or raw.dtype.kind not in "iuf":
        raise ValueError(f"{name} must be a one-dimensional real vector")
    array = raw.astype(np.float64, copy=True)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    if nonnegative and np.any(array < 0):
        raise ValueError(f"{name} must be nonnegative")
    return array


def _snapshot(values: np.ndarray) -> np.ndarray:
    result = values.copy()
    result.flags.writeable = False
    return result


def initialize_amsgrad(weights: object) -> AMSGradState:
    """Initialize zero moments in the same canonical edge order as weights."""
    w = _vector(weights, "weights", nonnegative=True)
    zero = np.zeros_like(w)
    return AMSGradState(0, _snapshot(zero), _snapshot(zero), _snapshot(zero))


def projected_amsgrad_step(
    weights: object,
    gradient: object,
    state: AMSGradState,
) -> tuple[np.ndarray, AMSGradState]:
    """Return projected next weights and moments for one complete Option A update."""
    w = _vector(weights, "weights", nonnegative=True)
    g = _vector(gradient, "gradient", nonnegative=False)
    if w.size == 0 or g.shape != w.shape:
        raise ValueError("weights and gradient must have matching nonempty shapes")
    if type(state.t) is not int or state.t < 0:
        raise ValueError("AMSGrad step counter must be a nonnegative integer")
    m = _vector(state.first_moment, "first moment", nonnegative=False)
    v = _vector(state.second_moment, "second moment", nonnegative=True)
    vmax = _vector(state.maximum_raw_second_moment, "raw second-moment maximum", nonnegative=True)
    if m.shape != w.shape or v.shape != w.shape or vmax.shape != w.shape:
        raise ValueError("AMSGrad moments must have the weights' shape")
    if np.any(vmax < v):
        raise ValueError("running raw second-moment maximum cannot be below the current second moment")

    t = state.t + 1
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        try:
            new_m = D03_BETA1 * m + (1.0 - D03_BETA1) * g
            new_v = D03_BETA2 * v + (1.0 - D03_BETA2) * (g * g)
            new_vmax = np.maximum(vmax, new_v)
            mhat = new_m / (1.0 - D03_BETA1**t)
            vhatmax = new_vmax / (1.0 - D03_BETA2**t)
            candidate = w - D03_LEARNING_RATE * mhat / (np.sqrt(vhatmax) + D03_EPSILON)
            next_weights = np.maximum(0.0, candidate)
        except FloatingPointError as exc:
            raise ArithmeticError("non-finite AMSGrad arithmetic") from exc
    if not all(np.all(np.isfinite(a)) for a in (new_m, new_v, new_vmax, next_weights)):
        raise ArithmeticError("non-finite AMSGrad result")
    next_weights.flags.writeable = False
    return next_weights, AMSGradState(
        t, _snapshot(new_m), _snapshot(new_v), _snapshot(new_vmax)
    )
