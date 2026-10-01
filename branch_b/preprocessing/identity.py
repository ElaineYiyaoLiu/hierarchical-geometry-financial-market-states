from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from branch_b.preprocessing.validation import as_finite_matrix


@dataclass(frozen=True)
class IdentityPreprocessor:
    """No-op preprocessor for geometries that use the released profiles directly."""

    def transform(self, values: object) -> np.ndarray:
        return as_finite_matrix(values).copy()

    def to_record(self) -> dict:
        return {"method": "none"}
