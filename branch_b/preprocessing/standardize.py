from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.preprocessing.validation import as_finite_matrix


@dataclass(frozen=True)
class Standardizer:
    mean_: np.ndarray
    scale_: np.ndarray
    ddof: int

    @classmethod
    def fit(cls, train_values: object, *, ddof: int | None = None) -> "Standardizer":
        """Fit coordinate standardization from training data only.

        The Branch B decision fixes coordinate standardization for Euclidean and
        Chebyshev, but the project record has not yet fixed the standard-deviation
        degrees-of-freedom convention. Execution therefore fails closed when ddof
        is omitted rather than silently choosing population or sample scaling.
        """
        if ddof is None:
            raise ConfigurationRequired(
                "standardization ddof has not yet been explicitly fixed by Branch B"
            )
        if not isinstance(ddof, int) or isinstance(ddof, bool) or ddof < 0:
            raise ValueError("ddof must be a non-negative integer")

        x = as_finite_matrix(train_values)
        if x.shape[0] <= ddof:
            raise BranchBFailure(
                FailureCode.DEGENERATE_DISTANCE,
                "standardization requires more training observations than ddof",
            )

        mean = np.mean(x, axis=0)
        scale = np.std(x, axis=0, ddof=ddof)
        if not np.isfinite(mean).all() or not np.isfinite(scale).all():
            raise BranchBFailure(FailureCode.NONFINITE_INPUT, "non-finite train standardization parameters")
        if np.any(scale <= 0):
            raise BranchBFailure(
                FailureCode.DEGENERATE_DISTANCE,
                "standardization requires strictly positive training feature scales",
            )
        return cls(mean_=mean, scale_=scale, ddof=ddof)

    def transform(self, values: object) -> np.ndarray:
        x = as_finite_matrix(values)
        z = (x - self.mean_) / self.scale_
        if not np.isfinite(z).all():
            raise BranchBFailure(FailureCode.NONFINITE_INPUT, "standardized representation contains non-finite values")
        return z

    def to_record(self) -> dict:
        return {
            "method": "zscore_train_only",
            "mean": self.mean_.tolist(),
            "scale": self.scale_.tolist(),
            "ddof": self.ddof,
        }
