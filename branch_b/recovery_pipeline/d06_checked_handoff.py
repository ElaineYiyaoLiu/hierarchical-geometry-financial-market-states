"""Development-only checked D06 fitting handoff on distinct original identities.

Expects an already approved, normalized distinct-ID dissimilarity matrix and a
validated D06DrawBoundary. Does not modify RecoveryPipeline, preprocess data,
choose validation candidates, choose failure codes, or activate scientific fit.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Protocol

import numpy as np

from branch_b.bootstrap.d06_identity_boundary import D06DrawBoundary
from branch_b.failures import ConfigurationRequired
from branch_b.fitters.base import FitResult
from branch_b.recovery_pipeline.result_validation import (
    checked_sample_order, validate_finite_square, validate_fit_result,
)


class DistinctMultiplicityFitter(Protocol):
    def fit_with_original_multiplicities(
        self, dissimilarity: object, *,
        original_sample_order: list[str],
        multiplicities: list[int],
        random_seed: int | None = None,
    ) -> FitResult: ...


def checked_d06_distinct_fit(
    normalized_distinct_dissimilarity: object,
    *,
    boundary: D06DrawBoundary,
    fitter: DistinctMultiplicityFitter,
    random_seed: int | None = None,
) -> FitResult:
    """Validate ID-aligned distinct fit output with existing structural checks.

    Original ID order is sourced exclusively from the caller's draw binding.
    Exactly one fitted leaf is required per active original identity. The
    occurrence labels remain on boundary, never on the fitted tree. A draw
    with W=0 stays fail-closed without selecting a scientific failure code.
    """
    if not isinstance(boundary, D06DrawBoundary):
        raise TypeError("boundary must be a D06DrawBoundary")
    order = checked_sample_order(list(boundary.distinct_original_ids))
    if boundary.total_pair_weight() == 0:
        raise ConfigurationRequired(
            "D06 low-distinct-observation outcome is not approved"
        )
    if not callable(getattr(fitter, "fit_with_original_multiplicities", None)):
        raise ConfigurationRequired(
            "D06 requires a multiplicity-aware distinct-identity fitter"
        )
    validate_finite_square(normalized_distinct_dissimilarity, size=len(order))
    matrix = np.asarray(normalized_distinct_dissimilarity, dtype=float).copy()
    fit = deepcopy(fitter.fit_with_original_multiplicities(
        matrix, original_sample_order=order.copy(),
        multiplicities=list(boundary.multiplicities),
        random_seed=random_seed,
    ))
    validate_fit_result(fit, sample_order=order)
    return fit
