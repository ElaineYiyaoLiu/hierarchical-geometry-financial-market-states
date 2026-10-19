"""Synthetic mutation-isolation regression for observable geometry parameters."""

import numpy as np

from branch_b.fitters.base import FitResult
from branch_b.recovery_pipeline.pipeline import PipelineConfiguration, RecoveryPipeline


class IdentityPreprocessor:
    def transform(self, values):
        return values.copy()

    def to_record(self):
        return {"name": "synthetic_identity"}


class SyntheticFitter:
    fitter_id = "synthetic_stub"

    def fit(self, dissimilarity, *, random_seed=None):
        d = np.asarray(dissimilarity)
        return FitResult(ultrametric_matrix=d.copy(), tree={}, diagnostics={})


def test_factory_mutation_does_not_change_selected_nested_parameters():
    original = {"nested": {"scale": 1.0}}
    factory_calls = []

    def geometry_factory(values, parameters):
        factory_calls.append(parameters["nested"]["scale"])
        parameters["nested"]["scale"] = 999.0
        return np.array([[0.0, 2.0], [2.0, 0.0]])

    pipeline = RecoveryPipeline(
        config=PipelineConfiguration(
            geometry_id="synthetic_geometry",
            common_fitter_id="synthetic_stub",
        ),
        fit_preprocessor=lambda train: IdentityPreprocessor(),
        geometry_factory=geometry_factory,
        geometry_parameter_candidates=lambda train: [original],
        select_validation_candidate=lambda candidates: 0,
        fitter=SyntheticFitter(),
    )
    x = np.zeros((2, 12))
    result = pipeline.run(x, x.copy(), x.copy())

    assert factory_calls == [1.0, 1.0]
    assert original == {"nested": {"scale": 1.0}}
    assert result["geometry_parameters"] == original
    assert result["validation_candidates"][0].parameters == original
    assert result["geometry_parameters"] is not original
    assert result["geometry_parameters"]["nested"] is not original["nested"]
