from __future__ import annotations

from collections.abc import Mapping

import numpy as np


def paired_replicate_contrasts(
    valuation_accuracy: Mapping[str, float],
    comparator_accuracy: Mapping[str, float],
) -> dict[str, float]:
    """Compute valuation-minus-comparator contrasts at the Monte Carlo replicate level."""
    left = set(valuation_accuracy)
    right = set(comparator_accuracy)
    if left != right:
        raise ValueError(
            "paired replicate IDs must match exactly before a paired contrast is computed"
        )

    result: dict[str, float] = {}
    for replicate_id in sorted(left):
        a = float(valuation_accuracy[replicate_id])
        b = float(comparator_accuracy[replicate_id])
        if not np.isfinite(a) or not np.isfinite(b):
            raise ValueError("paired replicate accuracies must be finite")
        result[replicate_id] = a - b
    return result
