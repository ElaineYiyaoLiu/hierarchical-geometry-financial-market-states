"""Synthetic-development D06 checked split orchestration.

Does not alter RecoveryPipeline or bootstrap execution. Retains every resampled
training row for fitted preprocessing, then uses separately bound distinct
original identities for validation/test geometry and checked fitting. Candidate
selection is caller-supplied; no criterion is selected here. Not approved for
scientific/pilot or locked-test use.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable

import numpy as np

from branch_b.bootstrap.d06_identity_boundary import (
    D06DrawBoundary, aligned_distinct_rows,
)
from branch_b.failures import ConfigurationRequired
from branch_b.normalization import normalize_dissimilarity
from branch_b.preprocessing import as_finite_matrix
from branch_b.recovery_pipeline.d06_checked_handoff import checked_d06_distinct_fit


@dataclass(frozen=True)
class D06DevelopmentCandidate:
    parameters: dict
    dissimilarity_matrix: np.ndarray
    fit: object


def run_d06_development_splits(
    train_occurrences: object,
    validation_occurrences: object,
    test_occurrences: object,
    *,
    validation_boundary: D06DrawBoundary,
    test_boundary: D06DrawBoundary,
    fit_preprocessor: Callable,
    geometry_factory: Callable,
    geometry_parameter_candidates: Callable,
    select_validation_candidate: Callable,
    fitter: object,
    random_seed: int | None = None,
) -> dict:
    """Validate selection on distinct validation IDs before reading test rows.

    Caller supplies already-resampled split rows in draw order and their own
    canonical-index identity bindings. No re-estimation on distinct train rows.
    Disagreement between same-ID transformed rows fails closed. A returned
    result is structural development evidence, not scientific authorization.
    """
    train = as_finite_matrix(train_occurrences).copy()
    validation = as_finite_matrix(validation_occurrences).copy()
    if len(validation) != len(validation_boundary.draw_indices):
        raise ValueError("validation occurrence count differs from bound draw")
    fitted = fit_preprocessor(train.copy())
    x_train = np.asarray(fitted.transform(train.copy())).copy()
    x_validation = np.asarray(fitted.transform(validation.copy())).copy()
    validation_distinct = aligned_distinct_rows(x_validation, validation_boundary)
    parameters = geometry_parameter_candidates(x_train.copy())
    if not isinstance(parameters, list) or not parameters or not all(
        isinstance(p, dict) for p in parameters
    ):
        raise ConfigurationRequired("parameter candidates must be nonempty dictionaries")

    def fit_split(rows: np.ndarray, boundary: D06DrawBoundary, params: dict):
        native = geometry_factory(rows.copy(), deepcopy(params))
        normalized = normalize_dissimilarity(native)
        fit = checked_d06_distinct_fit(
            normalized, boundary=boundary, fitter=fitter, random_seed=random_seed
        )
        return normalized.copy(), fit

    candidates = []
    for params in deepcopy(parameters):
        normalized, fit = fit_split(validation_distinct, validation_boundary, params)
        candidates.append(D06DevelopmentCandidate(deepcopy(params), normalized, fit))
    index = select_validation_candidate(deepcopy(candidates))
    if type(index) is not int or not 0 <= index < len(candidates):
        raise ConfigurationRequired("validation selector must return a valid integer index")

    # Critical gate: do not convert or transform test until selection succeeds.
    test = as_finite_matrix(test_occurrences).copy()
    if len(test) != len(test_boundary.draw_indices):
        raise ValueError("test occurrence count differs from bound draw")
    x_test = np.asarray(fitted.transform(test.copy())).copy()
    test_distinct = aligned_distinct_rows(x_test, test_boundary)
    selected = candidates[index]
    normalized_test, fit_test = fit_split(
        test_distinct, test_boundary, selected.parameters
    )
    return {
        "selected_candidate_index": index,
        "geometry_parameters": deepcopy(selected.parameters),
        "validation_candidates": deepcopy(candidates),
        "dissimilarity_matrix": normalized_test.copy(),
        "ultrametric_matrix": fit_test.ultrametric_matrix.copy(),
        "recovered_tree": deepcopy(fit_test.tree),
        "diagnostics": deepcopy(fit_test.diagnostics),
        "validation_distinct_original_ids": list(validation_boundary.distinct_original_ids),
        "test_distinct_original_ids": list(test_boundary.distinct_original_ids),
        "validation_multiplicities": list(validation_boundary.multiplicities),
        "test_multiplicities": list(test_boundary.multiplicities),
        "result_validation": "structural_checks_only",
        "scientific_authorization": False,
    }
