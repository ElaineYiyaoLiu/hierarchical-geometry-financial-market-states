"""Lossless type checks for isolated development reference utilities."""
from __future__ import annotations

import numpy as np


def reject_lossy_reference_input(value: object) -> None:
    """Inspect original containers before NumPy can erase masks or Boolean types."""
    if np.ma.isMaskedArray(value) or np.ma.is_masked(value):
        raise ValueError("masked reference inputs are inadmissible")
    if isinstance(value, (bool, np.bool_)):
        raise ValueError("Boolean reference inputs are inadmissible")
    if isinstance(value, (list, tuple)):
        for item in value:
            reject_lossy_reference_input(item)
    elif isinstance(value, np.ndarray):
        if value.dtype.kind == "b":
            raise ValueError("Boolean reference inputs are inadmissible")
        if value.dtype.kind == "O":
            for item in value.flat:
                reject_lossy_reference_input(item)
