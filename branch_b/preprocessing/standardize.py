from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.preprocessing.validation import as_finite_matrix


@dataclass(frozen=True)
class Standardizer:
    mean_: np.ndarray
    scale_: np.ndarray
    ddof: int = 0

    @classmethod
    def fit(cls, train_values: object) -> "Standardizer":
        """Fit the registered train-only coordinate z-score transformation.

        Branch B fixes ddof=0. Validation/test values never influence the fitted
        mean or scale, and the registered implementation does not expose an alternate
        ddof through this scientific preprocessing class.
        """
        x = as_finite_matrix(train_values)
        mean = np.mean(x, axis=0)
        scale = np.std(x, axis=0, ddof=0)
        if not np.isfinite(mean).all() or not np.isfinite(scale).all():
            raise BranchBFailure(FailureCode.NONFINITE_INPUT, "non-finite train standardization parameters")
        if np.any(scale <= 0):
            raise BranchBFailure(
                FailureCode.DEGENERATE_DISTANCE,
                "standardization requires strictly positive training feature scales",
            )
        return cls(mean_=mean, scale_=scale)

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
            "ddof": 0,
        }
