"""Development-only D06 bootstrap orchestration on original identities.

All resampled rows remain available to the split preprocessor. The existing
bootstrap engine owns draws, evaluator seeds, and unsuccessful-attempt records.
No scientific threshold, seed-namespace freeze, or production activation.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Callable

from branch_b.bootstrap.d06_identity_boundary import build_d06_draw_boundary
from branch_b.bootstrap.development_distinct_stability import (
    development_distinct_original_lca_stability,
)
from branch_b.bootstrap.engine import BootstrapReplicate, run_full_pipeline_bootstrap
from branch_b.preprocessing import as_finite_matrix
from branch_b.recovery_pipeline.d06_development_splits import run_d06_development_splits
from branch_b.recovery_pipeline.result_validation import checked_sample_order, validate_bound_tree


class _DeferredTestDraw:
    """Expose test rows only when the split runner requests them."""

    def __init__(self, values, indices, expected_size):
        self.values = values
        self.indices = indices.copy()
        self.expected_size = expected_size

    def __array__(self, dtype=None, copy=None):
        rows = as_finite_matrix(self.values)
        if len(rows) != self.expected_size:
            raise ValueError("test rows do not match original identity count")

        selected = rows[self.indices].copy()
        if dtype is not None:
            selected = selected.astype(dtype, copy=False)
        return selected

def run_development_d06_bootstrap(
    *,
    train_values: object,
    validation_values: object,
    test_values: object,
    train_original_sample_order: list[str],
    validation_original_sample_order: list[str],
    test_original_sample_order: list[str],
    n_replicates: int,
    base_seed: int,
    fit_preprocessor: Callable,
    geometry_factory: Callable,
    geometry_parameter_candidates: Callable,
    select_validation_candidate: Callable,
    fitter: object,
    full_test_tree: dict | None = None,
) -> list[BootstrapReplicate]:
    """Run the checked development split path for each bootstrap attempt.

    The full-test reference is supplied by the caller, not inferred from a
    bootstrap result. A failed fit or undefined stability is an unsuccessful
    attempt retained by the existing bootstrap engine, never silently dropped.
    """
    train = as_finite_matrix(train_values).copy()
    validation = as_finite_matrix(validation_values).copy()
    train_ids = checked_sample_order(train_original_sample_order, size=len(train))
    validation_ids = checked_sample_order(validation_original_sample_order, size=len(validation))
    test_ids = checked_sample_order(test_original_sample_order)
    reference = deepcopy(full_test_tree)
    if reference is not None:
        validate_bound_tree(reference, sample_order=test_ids)

    def evaluate(train_idx, validation_idx, test_idx, seed):
        validation_boundary = build_d06_draw_boundary(
            validation_idx,
            original_sample_order=validation_ids,
            fit_sample_order=[f"validation_occ_{i}" for i in range(len(validation_idx))],
        )
        test_boundary = build_d06_draw_boundary(
            test_idx,
            original_sample_order=test_ids,
            fit_sample_order=[f"test_occ_{i}" for i in range(len(test_idx))],
        )
        result = run_d06_development_splits(
            train[train_idx],validation[validation_idx],_DeferredTestDraw(test_values, test_idx, len(test_ids)),
            validation_boundary=validation_boundary,
            test_boundary=test_boundary,
            fit_preprocessor=fit_preprocessor,
            geometry_factory=geometry_factory,
            geometry_parameter_candidates=geometry_parameter_candidates,
            select_validation_candidate=select_validation_candidate,
            fitter=fitter,
            random_seed=seed,
        )
        result["bootstrap_identity"] = {
            "train_original_ids": [train_ids[int(i)] for i in train_idx],
            "validation_original_ids": list(validation_boundary.occurrence_original_ids),
            "test_original_ids": list(test_boundary.occurrence_original_ids),
        }
        if reference is not None:
            result["lca_depth_stability"] = development_distinct_original_lca_stability(
                full_test_tree=reference,
                full_original_sample_order=test_ids,
                bootstrap_tree=result["recovered_tree"],
                test_boundary=test_boundary,
            )
        return result

    return run_full_pipeline_bootstrap(
        n_replicates=n_replicates,
        train_size=len(train),
        validation_size=len(validation),
        test_size=len(test_ids),
        base_seed=base_seed,
        evaluate_replicate=evaluate,
    )
