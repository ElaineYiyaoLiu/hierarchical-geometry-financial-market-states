from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class FitResult:
    ultrametric_matrix: np.ndarray
    tree: dict
    diagnostics: dict


class CommonFitter(Protocol):
    fitter_id: str

    def fit(self, dissimilarity: object, *, random_seed: int | None = None) -> FitResult:
        ...
