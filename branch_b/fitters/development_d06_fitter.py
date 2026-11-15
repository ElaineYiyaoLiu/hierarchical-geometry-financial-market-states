"""Development-only D06 multiplicity-aware optimizer-to-tree fitter.

For synthetic integration under Python 3.14. A caller supplies an absolute
monotonic deadline; this class never selects a timeout duration or invokes
production GradientDescentUltrametricFitter.fit. No scientific failure mapping,
pilot approval, or frozen tree-height convention is implied.
"""

from __future__ import annotations

from itertools import combinations
from math import isfinite

import numpy as np

from branch_b.failures import ConfigurationRequired
from branch_b.fitters.development_tree_fit import run_checked_development_tree_fit
from branch_b.fitters.gradient_descent import GradientDescentUltrametricFitter
from branch_b.recovery_pipeline.result_validation import checked_sample_order


class D06DevelopmentFitter:
    """Explicitly deadline-bound implementation of the existing D06 handoff."""

    fitter_id = "development_d06_gradient_descent_not_scientific"

    def __init__(self, *, deadline_monotonic: float):
        if (
            isinstance(deadline_monotonic, bool)
            or not isinstance(deadline_monotonic, (int, float))
            or not isfinite(deadline_monotonic)
        ):
            raise ValueError("an actual finite monotonic deadline is required")
        self.deadline_monotonic = float(deadline_monotonic)

    def fit_with_original_multiplicities(
        self,
        dissimilarity: object,
        *,
        original_sample_order: list[str],
        multiplicities: list[int],
        random_seed: int | None = None,
    ):
        """Run D01-D06 with the specified distinct identities and multiplicities.

        The supplied seed is metadata only: approved primary optimization uses
        no stochastic restarts. No success is returned for ITERATION_CAP.
        """
        order = checked_sample_order(original_sample_order)
        if len(order) < 2:
            raise ConfigurationRequired(
                "D06 low-distinct-observation outcome is not approved"
            )
        if not isinstance(multiplicities, list) or len(multiplicities) != len(order):
            raise ValueError("multiplicities must align with original identities")
        if any(type(m) is not int or m <= 0 for m in multiplicities):
            raise ValueError("active multiplicities must be positive integers")
        if random_seed is not None and (type(random_seed) is not int or random_seed < 0):
            raise ValueError("Branch B-owned seed must be a nonnegative integer")

        # Reuse existing registered input checks rather than inventing a new
        # admissibility/tie/near-zero convention. Do not invoke its fit stub.
        matrix = GradientDescentUltrametricFitter().validate_normalized_input(
            dissimilarity
        )
        if matrix.shape != (len(order), len(order)):
            raise ValueError("dissimilarity must align with distinct identities")
        delta = tuple(
            float(matrix[i, j])
            for i, j in combinations(range(len(order)), 2)
        )
        fit = run_checked_development_tree_fit(
            delta, tuple(multiplicities),
            original_sample_order=order,
            deadline_monotonic=self.deadline_monotonic,
        )
        # Mutate only a fresh local result; FitResult is frozen, diagnostics is
        # a normal dict allocated by the development exporter.
        fit.diagnostics["branch_b_seed"] = random_seed
        return fit
