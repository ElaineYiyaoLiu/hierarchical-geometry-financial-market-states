from __future__ import annotations

import numpy as np

from branch_b.failures import ConfigurationRequired


def normalize_dissimilarity(dissimilarity: object, *, rule: str | None = None) -> np.ndarray:
    """Project-level post-geometry normalization entry point.

    The exact common normalization formula is not present in the approved records
    reviewed so far. This function therefore fails closed until that rule is frozen.
    """
    _ = np.asarray(dissimilarity, dtype=float)
    if rule is None:
        raise ConfigurationRequired("common post-geometry normalization rule is not yet frozen")
    raise ConfigurationRequired(f"normalization rule {rule!r} is not implemented or approved")
