from __future__ import annotations

from collections import Counter

import numpy as np

from branch_b.bootstrap.engine import BootstrapReplicate, run_full_pipeline_bootstrap
from branch_b.failures import BranchBFailure, FailureCode
from branch_b.recovery import lca_depths
from branch_b.recovery_pipeline import RecoveryPipeline
from branch_b.support import lca_depth_stability


def draw_multiplicities(indices: np.ndarray) -> dict[int, int]:
    """Return original-row multiplicities; duplicate draws do not become new identities."""
    return dict(sorted(Counter(int(i) for i in np.asarray(indices, dtype=int)).items()))


def distinct_original_indices(indices: np.ndarray) -> list[int]:
    """Original observations represented at least once in a bootstrap draw."""
    return sorted(draw_multiplicities(indices))


def _pair_depth(
    depths: dict[tuple[str, str], int],
    order: dict[str, int],
    left: str,
    right: str,
) -> int:
    if order[left] < order[right]:
        return depths[(left, right)]
    return depths[(right, left)]


def bootstrap_lca_depths_by_original(
    *,
    bootstrap_tree: dict,
    bootstrap_test_indices: np.ndarray,
) -> dict[tuple[int, int], int]:
    """Project bootstrap-tree LCA depths onto distinct original test identities.

    Bootstrap rows may contain repeated draws of one original observation. Repeated
    copies remain multiplicities, not distinct identities. A projected original pair
    is accepted only when every cross-copy LCA-depth relation agrees; otherwise the
    bootstrap tree does not define one unambiguous relation for that original pair.
    """
    draw = np.asarray(bootstrap_test_indices, dtype=int)
    sample_order = list(bootstrap_tree.get("leaves", []))
    if len(sample_order) != len(draw):
        raise BranchBFailure(
            FailureCode.INPUT_SCHEMA,
            "bootstrap tree leaf count must match bootstrap test draw count",
        )

    position = {leaf: i for i, leaf in enumerate(sample_order)}
    if len(position) != len(sample_order):
        raise BranchBFailure(
            FailureCode.OUTPUT_SCHEMA,
            "bootstrap tree leaf identifiers must be unique",
        )

    raw_depths = lca_depths(bootstrap_tree, sample_order)
    groups: dict[int, list[str]] = {}
    for leaf, original_index in zip(sample_order, draw, strict=True):
        groups.setdefault(int(original_index), []).append(leaf)

    originals = sorted(groups)
    projected: dict[tuple[int, int], int] = {}
    for i, left_original in enumerate(originals):
        for right_original in originals[i + 1 :]:
            values = {
                _pair_depth(raw_depths, position, left_leaf, right_leaf)
                for left_leaf in groups[left_original]
                for right_leaf in groups[right_original]
            }
            if len(values) != 1:
                raise BranchBFailure(
                    FailureCode.DEGENERATE_TREE,
                    "duplicate bootstrap copies imply inconsistent LCA-depth relation "
                    "for the same original-observation pair",
                )
            projected[(left_original, right_original)] = next(iter(values))
    return projected


def full_test_lca_depths_by_index(full_test_tree: dict) -> dict[tuple[int, int], int]:
    """Index full-test LCA relations by canonical original row position."""
    sample_order = list(full_test_tree.get("leaves", []))
    raw_depths = lca_depths(full_test_tree, sample_order)
    position = {leaf: i for i, leaf in enumerate(sample_order)}
    return {
        (position[left], position[right]): depth
        for (left, right), depth in raw_depths.items()
    }


def bootstrap_lca_stability_against_full_test(
    *,
    full_test_tree: dict,
    bootstrap_tree: dict,
    bootstrap_test_indices: np.ndarray,
) -> float:
    """LCA-depth rank agreement on distinct original observations shared by both fits."""
    full_depths = full_test_lca_depths_by_index(full_test_tree)
    bootstrap_depths = bootstrap_lca_depths_by_original(
        bootstrap_tree=bootstrap_tree,
        bootstrap_test_indices=bootstrap_test_indices,
    )
    return lca_depth_stability(full_depths, bootstrap_depths)


def run_recovery_pipeline_bootstrap(
    *,
    pipeline: RecoveryPipeline,
    train_values: object,
    validation_values: object,
    test_values: object,
    n_replicates: int,
    base_seed: int,
    full_test_tree: dict | None = None,
) -> list[BootstrapReplicate]:
    """Run the full recovery pipeline inside each independently resampled split.

    Preprocessing is refit on bootstrap training, validation selection is rerun on
    bootstrap validation, and the selected parameters are applied to bootstrap test
    within every replicate. When the full-test tree is supplied, each successful
    replicate also records LCA-depth stability after projecting duplicate bootstrap
    draws back to distinct original test-observation identities.
    """
    train = np.asarray(train_values, dtype=float)
    validation = np.asarray(validation_values, dtype=float)
    test = np.asarray(test_values, dtype=float)

    def evaluate(train_idx, validation_idx, test_idx, seed):
        result = pipeline.run(
            train[train_idx],
            validation[validation_idx],
            test[test_idx],
            random_seed=seed,
        )
        result["bootstrap_draws"] = {
            "train_multiplicity": draw_multiplicities(train_idx),
            "validation_multiplicity": draw_multiplicities(validation_idx),
            "test_multiplicity": draw_multiplicities(test_idx),
            "test_distinct_original_indices": distinct_original_indices(test_idx),
        }
        if full_test_tree is not None:
            result["lca_depth_stability"] = bootstrap_lca_stability_against_full_test(
                full_test_tree=full_test_tree,
                bootstrap_tree=result["recovered_tree"],
                bootstrap_test_indices=test_idx,
            )
        return result

    return run_full_pipeline_bootstrap(
        n_replicates=n_replicates,
        train_size=len(train),
        validation_size=len(validation),
        test_size=len(test),
        base_seed=base_seed,
        evaluate_replicate=evaluate,
    )
