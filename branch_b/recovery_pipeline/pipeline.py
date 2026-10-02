from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

import numpy as np

from branch_b.failures import ConfigurationRequired
from branch_b.fitters import CommonFitter, FitResult
from branch_b.normalization import normalize_dissimilarity
from branch_b.preprocessing import as_finite_matrix


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

    Preprocessing is fit on training only. Every prespecified geometry-parameter
    candidate is evaluated on validation using the same common normalization and
    Common Fitter. A caller-supplied, ground-truth-free selector chooses among those
    validation candidates. The selected parameter record is then applied unchanged
    to the test split.

    This class intentionally does not define the scientific validation criterion.
    """

    def __init__(
        self,
        *,
        config: PipelineConfiguration,
        fit_preprocessor: Callable[[np.ndarray], FittedPreprocessor],
        geometry_factory: Callable[[np.ndarray, dict], np.ndarray],
        geometry_parameter_candidates: Callable[[np.ndarray], list[dict]],
        select_validation_candidate: Callable[[list[ValidationCandidate]], int],
        fitter: CommonFitter,
    ):
        self.config = config
        self.fit_preprocessor = fit_preprocessor
        self.geometry_factory = geometry_factory
        self.geometry_parameter_candidates = geometry_parameter_candidates
        self.select_validation_candidate = select_validation_candidate
        self.fitter = fitter

    def _fit_split(
        self,
        values: np.ndarray,
        parameters: dict,
        *,
        random_seed: int | None,
    ) -> tuple[np.ndarray, FitResult]:
        native = self.geometry_factory(values, parameters)
        normalized = normalize_dissimilarity(
            native,
            rule=self.config.normalization_rule,
        )
        fit = self.fitter.fit(normalized, random_seed=random_seed)
        return normalized, fit

    def run(
        self,
        train_values: object,
        validation_values: object,
        test_values: object,
        *,
        random_seed: int | None = None,
    ) -> dict:
        train = as_finite_matrix(train_values)
        validation = as_finite_matrix(validation_values)
        test = as_finite_matrix(test_values)

        preprocessor = self.fit_preprocessor(train)
        x_train = preprocessor.transform(train)
        x_validation = preprocessor.transform(validation)
        x_test = preprocessor.transform(test)

        parameter_records = self.geometry_parameter_candidates(x_train)
        if not parameter_records:
            raise ConfigurationRequired("no prespecified geometry-parameter candidates were supplied")

        validation_candidates: list[ValidationCandidate] = []
        for parameters in parameter_records:
            d_validation, fit_validation = self._fit_split(
                x_validation,
                parameters,
                random_seed=random_seed,
            )
            validation_candidates.append(
                ValidationCandidate(
                    parameters=dict(parameters),
                    dissimilarity_matrix=d_validation,
                    fit=fit_validation,
                )
            )

        selected_index = self.select_validation_candidate(validation_candidates)
        if not isinstance(selected_index, int) or isinstance(selected_index, bool):
            raise ConfigurationRequired("validation selector must return an integer candidate index")
        if selected_index < 0 or selected_index >= len(validation_candidates):
            raise ConfigurationRequired("validation selector returned an out-of-range candidate index")

        selected = validation_candidates[selected_index]
        d_test, fit_test = self._fit_split(
            x_test,
            selected.parameters,
            random_seed=random_seed,
        )

        return {
            "geometry_id": self.config.geometry_id,
            "common_fitter_id": self.config.common_fitter_id,
            "preprocessing": preprocessor.to_record(),
            "selected_candidate_index": selected_index,
            "geometry_parameters": dict(selected.parameters),
            "validation_candidates": validation_candidates,
            "dissimilarity_matrix": d_test,
            "ultrametric_matrix": fit_test.ultrametric_matrix,
            "recovered_tree": fit_test.tree,
            "diagnostics": fit_test.diagnostics,
        }
