from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from branch_b.failures import ConfigurationRequired
from branch_b.fitters import CommonFitter
from branch_b.normalization import normalize_dissimilarity
from branch_b.preprocessing import Standardizer, as_finite_matrix


@dataclass(frozen=True)
class PipelineConfiguration:
    geometry_id: str
    common_fitter_id: str
    normalization_rule: str | None = None


class RecoveryPipeline:
    """Observable-only train/validation/test orchestration skeleton.

    Geometry-specific hyperparameter selection is injected as a callback so the
    pipeline does not invent a selection rule. Common normalization and fitting are
    explicit dependencies and therefore remain fail-closed while unresolved.
    """

    def __init__(
        self,
        *,
        config: PipelineConfiguration,
        geometry_factory: Callable[[np.ndarray, dict], np.ndarray],
        select_geometry_parameters: Callable[[np.ndarray, np.ndarray], dict],
        fitter: CommonFitter,
    ):
        self.config = config
        self.geometry_factory = geometry_factory
        self.select_geometry_parameters = select_geometry_parameters
        self.fitter = fitter

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

        standardizer = Standardizer.fit(train)
        z_train = standardizer.transform(train)
        z_validation = standardizer.transform(validation)
        z_test = standardizer.transform(test)

        parameters = self.select_geometry_parameters(z_train, z_validation)
        if parameters is None:
            raise ConfigurationRequired("geometry-specific selection callback returned no parameter record")

        test_native = self.geometry_factory(z_test, parameters)
        test_dissimilarity = normalize_dissimilarity(
            test_native,
            rule=self.config.normalization_rule,
        )
        fit = self.fitter.fit(test_dissimilarity, random_seed=random_seed)

        return {
            "geometry_id": self.config.geometry_id,
            "common_fitter_id": self.config.common_fitter_id,
            "preprocessing": standardizer.to_record(),
            "geometry_parameters": parameters,
            "dissimilarity_matrix": test_dissimilarity,
            "ultrametric_matrix": fit.ultrametric_matrix,
            "recovered_tree": fit.tree,
            "diagnostics": fit.diagnostics,
        }
