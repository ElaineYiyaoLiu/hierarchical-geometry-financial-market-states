"""Development-only LCA stability for D06 distinct-original-ID trees.

This adapts the existing LCA-depth and average-rank Spearman statistic to
D06 trees with one leaf per active original identity. No support threshold,
bootstrap reliability decision, new failure mapping, or scientific approval
is introduced.
"""

from __future__ import annotations

from branch_b.bootstrap.d06_identity_boundary import D06DrawBoundary
from branch_b.failures import BranchBFailure, FailureCode
from branch_b.recovery import lca_depths
from branch_b.recovery_pipeline.result_validation import (
    checked_sample_order,
    validate_bound_tree,
)
from branch_b.support import lca_depth_stability


def development_distinct_original_lca_stability(
    *,
    full_test_tree: dict,
    full_original_sample_order: list[str],
    bootstrap_tree: dict,
    test_boundary: D06DrawBoundary,
) -> float:
    """Compare LCA depths on shared original IDs, never draw-occurrence labels.

    The external canonical full-test order is authoritative. The bootstrap
    tree must have precisely the active original IDs from the validated draw
    boundary, in canonical order; duplicate occurrences affect D06 fitting
    via multiplicities, not the number of LCA relations.

    Undefined/too-small Spearman comparisons propagate their existing errors;
    this helper does not create a new scientific failure code.
    """
    if not isinstance(test_boundary, D06DrawBoundary):
        raise TypeError("test_boundary must be D06DrawBoundary")
    full_order = checked_sample_order(full_original_sample_order)
    if tuple(full_order) != test_boundary.original_sample_order:
        raise BranchBFailure(
            FailureCode.INPUT_SCHEMA,
            "full-test original IDs do not match the bootstrap draw binding",
        )
    active_order = checked_sample_order(list(test_boundary.distinct_original_ids))
    validate_bound_tree(full_test_tree, sample_order=full_order)
    validate_bound_tree(bootstrap_tree, sample_order=active_order)
    full_depths = lca_depths(full_test_tree, full_order)
    bootstrap_depths = lca_depths(bootstrap_tree, active_order)
    return lca_depth_stability(full_depths, bootstrap_depths)
