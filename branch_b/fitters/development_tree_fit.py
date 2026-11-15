"""Development-only conversion of a converged optimizer run to a checked FitResult.

No production registration, pilot timeout, failure-code mapping, tree-height
freeze, or scientific authorization. The exact-height tree serializer is a
candidate convention awaiting review before scientific use.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np

from branch_b.failures import ConfigurationRequired
from branch_b.fitters.base import FitResult
from branch_b.fitters.development_optimizer import (
    DevelopmentOptimizerResult, run_development_optimizer,
)
from branch_b.fitters.development_tree_extraction import extract_exact_ultrametric_tree
from branch_b.recovery_pipeline.result_validation import (
    checked_sample_order, validate_fit_result,
)


def development_fit_from_converged_optimizer(
    result: DevelopmentOptimizerResult,
    *,
    original_sample_order: list[str],
) -> FitResult:
    """Make a checked tree/matrix from the final converged iterate only.

    Cap exhaustion must remain unsuccessful; this helper does not assign a
    scientific failure code. It cannot be used as a fallback for nonconvergence.
    """
    if not isinstance(result, DevelopmentOptimizerResult):
        raise TypeError("expected a development optimizer result")
    if result.outcome != "CONVERGED":
        raise ConfigurationRequired(
            "development fit export requires convergence; cap failure mapping is separate"
        )
    order = checked_sample_order(original_sample_order)
    n = len(order)
    if len(result.ultrametric) != n * (n - 1) // 2:
        raise ValueError("optimizer ultrametric and original identity counts differ")
    matrix = np.zeros((n, n), dtype=float)
    for (i, j), value in zip(
        combinations(range(n), 2), result.ultrametric, strict=True
    ):
        matrix[i, j] = matrix[j, i] = value
    tree = extract_exact_ultrametric_tree(matrix, sample_order=order)
    fit = FitResult(
        ultrametric_matrix=matrix,
        tree=tree,
        diagnostics={
            "development_only": True,
            "scientific_authorization": False,
            "outcome": result.outcome,
            "completed_updates": result.completed_updates,
            "objective_history": list(result.objective_history),
            "relative_change_history": list(result.relative_change_history),
            "elapsed_seconds": result.elapsed_seconds,
        },
    )
    validate_fit_result(fit, sample_order=order)
    return fit


def run_checked_development_tree_fit(
    input_dissimilarity_pairs,
    multiplicities,
    *,
    original_sample_order: list[str],
    deadline_monotonic: float,
) -> FitResult:
    """Exercise the standalone optimizer and serialize only its converged result."""
    order = checked_sample_order(original_sample_order)
    if len(multiplicities) != len(order):
        raise ValueError("multiplicities must align with original identities")
    result = run_development_optimizer(
        input_dissimilarity_pairs, multiplicities,
        deadline_monotonic=deadline_monotonic,
    )
    return development_fit_from_converged_optimizer(
        result, original_sample_order=order,
    )
