from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Protocol

import numpy as np

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.fitters import CommonFitter, FitResult
from branch_b.normalization import normalize_dissimilarity
from branch_b.preprocessing import as_finite_matrix
from .result_validation import (
    IdentityAwareFitter, checked_sample_order, validate_finite_square, validate_fit_result,
)


class FittedPreprocessor(Protocol):
    def transform(self, values: object) -> np.ndarray:
        ...

    def to_record(self) -> dict:
        ...


@dataclass(frozen=True)
class PipelineConfiguration:
    geometry_id: str
    common_fitter_id: str
    normalization_rule: str = "max_offdiagonal"


@dataclass(frozen=True)
class ValidationCandidate:
    parameters: dict
    dissimilarity_matrix: np.ndarray
    fit: FitResult


class RecoveryPipeline:
    """Observable-only validation-selection-to-test orchestration.

    Preprocessing is fit on training only. Prespecified candidates are evaluated
    on validation, then a caller-supplied selector returns their selected index.
    Test conversion, transformation, geometry, and fitting follow valid selection.

    Callback outputs are snapshotted before their buffers can be reused. run()
    retains the generic development/stub contract; run_checked() additionally
    requires externally supplied sample identities and structural fit checks.
    Neither entry point defines or authorizes a scientific selection criterion.
    """

    def __init__(
        self,
        *,
        config: PipelineConfiguration,
        fit_preprocessor: Callable[[np.ndarray], FittedPreprocessor],
        geometry_factory: Callable[[np.ndarray, dict], np.ndarray],
        geometry_parameter_candidates: Callable[[np.ndarray], list[dict]],
        select_validation_candidate: Callable[[list[ValidationCandidate]], int],
        fitter: CommonFitter | IdentityAwareFitter,
    ):
        self.config = config
        self.fit_preprocessor = fit_preprocessor
        self.geometry_factory = geometry_factory
        self.geometry_parameter_candidates = geometry_parameter_candidates
        self.select_validation_candidate = select_validation_candidate
        self.fitter = fitter

    def _fit_split(
        self, values: np.ndarray, parameters: dict, *,
        random_seed: int | None, sample_order: list[str] | None = None,
    ) -> tuple[np.ndarray, FitResult]:
        if sample_order is not None:
            if values.ndim != 2 or len(values) != len(sample_order):
                raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "transformed rows must match canonical sample order")
        native = self.geometry_factory(values.copy(), deepcopy(parameters))
        normalized = normalize_dissimilarity(native, rule=self.config.normalization_rule)
        if sample_order is None:
            fit = deepcopy(self.fitter.fit(normalized.copy(), random_seed=random_seed))
        else:
            validate_finite_square(normalized, size=len(sample_order))
            fit = deepcopy(self.fitter.fit_with_sample_order(
                normalized.copy(), sample_order=sample_order.copy(), random_seed=random_seed,
            ))
            # Mandatory in the checked path, before selection sees this fit.
            validate_fit_result(fit, sample_order=sample_order)
        return normalized, fit

    def run(
        self, train_values: object, validation_values: object, test_values: object,
        *, random_seed: int | None = None,
    ) -> dict:
        """Generic development orchestration; not scientific result validation."""
        return self._run(train_values, validation_values, test_values, random_seed=random_seed)

    def run_checked(
        self, train_values: object, validation_values: object, test_values: object,
        *, validation_sample_order: list[str], test_sample_order: list[str],
        random_seed: int | None = None,
    ) -> dict:
        """Require named fits and structural checks, without approving a method.

        Orders must come from the caller's canonical input/manifest, not from a
        returned tree. No automatic relabeling, sorting, or reindexing occurs.
        The fitter must implement fit_with_sample_order; no unchecked fallback.
        Numerical conformance and scientific authorization remain separate gates.
        """
        validation_order = checked_sample_order(validation_sample_order)
        test_order = checked_sample_order(test_sample_order)
        if not callable(getattr(self.fitter, "fit_with_sample_order", None)):
            raise ConfigurationRequired("checked processing requires an identity-aware fitter")
        if self.fitter.fitter_id != self.config.common_fitter_id:
            raise ConfigurationRequired("configured and actual fitter identifiers differ")
        return self._run(
            train_values, validation_values, test_values, random_seed=random_seed,
            validation_sample_order=validation_order, test_sample_order=test_order,
        )

    def _run(
        self, train_values: object, validation_values: object, test_values: object,
        *, random_seed: int | None,
        validation_sample_order: list[str] | None = None,
        test_sample_order: list[str] | None = None,
    ) -> dict:
        train = as_finite_matrix(train_values)
        validation = as_finite_matrix(validation_values)
        if validation_sample_order is not None:
            checked_sample_order(validation_sample_order, size=len(validation))

        preprocessor = self.fit_preprocessor(train.copy())
        x_train = preprocessor.transform(train.copy()).copy()
        x_validation = preprocessor.transform(validation.copy()).copy()

        parameter_records = self.geometry_parameter_candidates(x_train.copy())
        if not isinstance(parameter_records, list) or not parameter_records:
            raise ConfigurationRequired("geometry-parameter candidates must be a non-empty list")
        if not all(isinstance(parameters, dict) for parameters in parameter_records):
            raise ConfigurationRequired("each geometry-parameter candidate must be a dictionary")

        parameter_records = deepcopy(parameter_records)
        validation_candidates: list[ValidationCandidate] = []
        for parameters in parameter_records:
            d_validation, fit_validation = self._fit_split(
                x_validation, parameters, random_seed=random_seed,
                sample_order=validation_sample_order,
            )
            validation_candidates.append(ValidationCandidate(
                parameters=deepcopy(parameters), dissimilarity_matrix=d_validation,
                fit=fit_validation,
            ))

        selected_index = self.select_validation_candidate(deepcopy(validation_candidates))
        if not isinstance(selected_index, int) or isinstance(selected_index, bool):
            raise ConfigurationRequired("validation selector must return an integer candidate index")
        if selected_index < 0 or selected_index >= len(validation_candidates):
            raise ConfigurationRequired("validation selector returned an out-of-range candidate index")

        # Test data cannot affect candidate construction or selection via a
        # conversion/transform callback invoked before the index is validated.
        selected = validation_candidates[selected_index]
        test = as_finite_matrix(test_values)
        if test_sample_order is not None:
            checked_sample_order(test_sample_order, size=len(test))
        x_test = preprocessor.transform(test.copy()).copy()
        d_test, fit_test = self._fit_split(
            x_test, selected.parameters, random_seed=random_seed, sample_order=test_sample_order,
        )

        result = {
            "geometry_id": self.config.geometry_id,
            "common_fitter_id": self.config.common_fitter_id,
            "preprocessing": deepcopy(preprocessor.to_record()),
            "selected_candidate_index": selected_index,
            "geometry_parameters": deepcopy(selected.parameters),
            "validation_candidates": validation_candidates,
            "dissimilarity_matrix": d_test,
            "ultrametric_matrix": fit_test.ultrametric_matrix,
            "recovered_tree": fit_test.tree,
            "diagnostics": fit_test.diagnostics,
        }
        if test_sample_order is not None:
            # Internal metadata, not additional fields for a frozen exchange schema.
            result["sample_order"] = test_sample_order.copy()
            result["validation_sample_order"] = validation_sample_order.copy()
            result["result_validation"] = "structural_checks_only"
            result["scientific_authorization"] = False
        return result
