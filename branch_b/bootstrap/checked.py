"""Identity-bound development bootstrap integration, not a scientific certificate.

Repeated rows remain repeated rows. This does not resolve the reciprocal-weight
conflict, change pair weights, or choose common-observation or interval rules.
"""
from __future__ import annotations

from copy import deepcopy

import numpy as np

from branch_b.bootstrap.engine import BootstrapReplicate, run_full_pipeline_bootstrap
from branch_b.bootstrap.pipeline import (
    bootstrap_lca_stability_against_full_test, draw_multiplicities,
)
from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.preprocessing import as_finite_matrix
from branch_b.recovery_pipeline.pipeline import RecoveryPipeline
from branch_b.recovery_pipeline.result_validation import checked_sample_order, validate_bound_tree


def bind_bootstrap_draw(
    indices: object, *, original_sample_order: list[str], fit_sample_order: list[str],
) -> list[dict[str, str]]:
    """Bind independent fit-row labels to original identities, keeping duplicates.

    fit_sample_order labels draw occurrences, not new original observations.
    Both orders must be supplied independently of any returned fitted tree.
    """
    originals = checked_sample_order(original_sample_order)
    labels = checked_sample_order(fit_sample_order)
    if np.ma.isMaskedArray(indices):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "masked bootstrap identity indices are not admissible")
    try:
        draw = np.asarray(indices)
    except (TypeError, ValueError, OverflowError) as exc:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "bootstrap identity indices must form a regular array") from exc
    if draw.ndim != 1 or draw.dtype.kind not in "iu" or len(draw) != len(labels):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "bootstrap indices must be integers matching the fit row count")
    if np.any(draw < 0) or np.any(draw >= len(originals)):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "bootstrap index is outside the canonical original sample order")
    return [{"fit_sample_id": label, "original_sample_id": originals[int(index)]}
            for label, index in zip(labels, draw, strict=True)]


def bound_lca_stability(
    *, full_test_tree: dict, original_sample_order: list[str],
    bootstrap_tree: dict, bootstrap_sample_order: list[str], bootstrap_test_indices: object,
) -> float:
    """Validate both external order bindings before using the existing statistic."""
    originals = checked_sample_order(original_sample_order)
    labels = checked_sample_order(bootstrap_sample_order)
    bind_bootstrap_draw(bootstrap_test_indices, original_sample_order=originals, fit_sample_order=labels)
    validate_bound_tree(full_test_tree, sample_order=originals)
    validate_bound_tree(bootstrap_tree, sample_order=labels)
    return bootstrap_lca_stability_against_full_test(
        full_test_tree=full_test_tree, bootstrap_tree=bootstrap_tree,
        bootstrap_test_indices=np.asarray(bootstrap_test_indices).copy(),
    )


def run_checked_recovery_pipeline_bootstrap(
    *, pipeline: RecoveryPipeline,
    train_values: object, validation_values: object, test_values: object,
    train_sample_order: list[str], validation_sample_order: list[str], test_sample_order: list[str],
    validation_fit_sample_order: list[str], test_fit_sample_order: list[str],
    n_replicates: int, base_seed: int, full_test_tree: dict | None = None,
) -> list[BootstrapReplicate]:
    """Route every attempt through run_checked, without falling back to run.

    Original orders identify input rows. Independent fit orders identify the
    positions in each resampled split and are passed explicitly to the fitter.
    The returned mapping preserves their association with original identities.
    A successful return means structural checks passed, not a protocol-valid
    scientific success: numerical conformance and all approval gates remain open.
    """
    if not isinstance(pipeline, RecoveryPipeline):
        raise ConfigurationRequired("checked bootstrap requires RecoveryPipeline")
    if not callable(getattr(pipeline.fitter, "fit_with_sample_order", None)):
        raise ConfigurationRequired("checked bootstrap requires an identity-aware fitter")

    train = as_finite_matrix(train_values).copy()
    validation = as_finite_matrix(validation_values).copy()
    test = as_finite_matrix(test_values).copy()
    train_order = checked_sample_order(train_sample_order, size=len(train))
    validation_order = checked_sample_order(validation_sample_order, size=len(validation))
    test_order = checked_sample_order(test_sample_order, size=len(test))
    validation_labels = checked_sample_order(validation_fit_sample_order, size=len(validation))
    test_labels = checked_sample_order(test_fit_sample_order, size=len(test))
    reference_tree = deepcopy(full_test_tree)
    if reference_tree is not None:
        validate_bound_tree(reference_tree, sample_order=test_order)

    def evaluate(train_idx, validation_idx, test_idx, seed):
        validation_binding = bind_bootstrap_draw(
            validation_idx, original_sample_order=validation_order, fit_sample_order=validation_labels,
        )
        test_binding = bind_bootstrap_draw(
            test_idx, original_sample_order=test_order, fit_sample_order=test_labels,
        )
        result = pipeline.run_checked(
            train[train_idx], validation[validation_idx], test[test_idx],
            validation_sample_order=validation_labels, test_sample_order=test_labels, random_seed=seed,
        )
        result["bootstrap_draws"] = {
            "train_multiplicity": draw_multiplicities(train_idx),
            "validation_multiplicity": draw_multiplicities(validation_idx),
            "test_multiplicity": draw_multiplicities(test_idx),
            "test_distinct_original_indices": sorted(draw_multiplicities(test_idx)),
        }
        result["bootstrap_identity"] = {
            "train_original_ids": [train_order[int(i)] for i in train_idx],
            "validation": validation_binding, "test": test_binding,
        }
        if reference_tree is not None:
            result["lca_depth_stability"] = bound_lca_stability(
                full_test_tree=reference_tree, original_sample_order=test_order,
                bootstrap_tree=result["recovered_tree"], bootstrap_sample_order=test_labels,
                bootstrap_test_indices=test_idx,
            )
        return result

    return run_full_pipeline_bootstrap(
        n_replicates=n_replicates, train_size=len(train), validation_size=len(validation),
        test_size=len(test), base_seed=base_seed, evaluate_replicate=evaluate,
    )
