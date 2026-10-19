"""Synthetic mutation-isolation regression for observable geometry parameters."""

import numpy as np
import pytest

from branch_b.failures import ConfigurationRequired

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


def test_selector_mutation_cannot_rewrite_selected_candidate_or_validation_fit():
    original = {"nested": {"scale": 1.0}}
    factory_calls = []

    def geometry_factory(values, parameters):
        factory_calls.append(parameters["nested"]["scale"])
        return np.array([[0.0, 2.0], [2.0, 0.0]])

    def mutating_selector(candidates):
        candidates[0].parameters["nested"]["scale"] = 999.0
        candidates[0].dissimilarity_matrix[0, 1] = 999.0
        candidates[0].fit.ultrametric_matrix[0, 1] = 999.0
        return 0

    pipeline = RecoveryPipeline(
        config=PipelineConfiguration(
            geometry_id="synthetic_geometry",
            common_fitter_id="synthetic_stub",
        ),
        fit_preprocessor=lambda train: IdentityPreprocessor(),
        geometry_factory=geometry_factory,
        geometry_parameter_candidates=lambda train: [original],
        select_validation_candidate=mutating_selector,
        fitter=SyntheticFitter(),
    )
    x = np.zeros((2, 12))
    result = pipeline.run(x, x.copy(), x.copy())

    assert factory_calls == [1.0, 1.0]
    assert result["geometry_parameters"] == original
    candidate = result["validation_candidates"][0]
    assert candidate.parameters == original
    assert candidate.dissimilarity_matrix[0, 1] == 1.0
    assert candidate.fit.ultrametric_matrix[0, 1] == 1.0


def test_mutating_geometry_and_fitter_cannot_corrupt_pipeline_matrices():
    observed_geometry_inputs = []

    def mutating_geometry(values, parameters):
        observed_geometry_inputs.append(values[0, 0])
        values[0, 0] = 999.0
        return np.array([[0.0, 2.0], [2.0, 0.0]])

    class MutatingFitter:
        fitter_id = "synthetic_mutator"

        def fit(self, dissimilarity, *, random_seed=None):
            dissimilarity[0, 1] = 999.0
            return FitResult(
                ultrametric_matrix=np.zeros((2, 2)),
                tree={},
                diagnostics={},
            )

    pipeline = RecoveryPipeline(
        config=PipelineConfiguration(
            geometry_id="synthetic_geometry",
            common_fitter_id="synthetic_mutator",
        ),
        fit_preprocessor=lambda train: IdentityPreprocessor(),
        geometry_factory=mutating_geometry,
        geometry_parameter_candidates=lambda train: [{"scale": 1.0}, {"scale": 2.0}],
        select_validation_candidate=lambda candidates: 0,
        fitter=MutatingFitter(),
    )
    x = np.zeros((2, 12))
    result = pipeline.run(x, x.copy(), x.copy())

    assert observed_geometry_inputs == [0.0, 0.0, 0.0]
    assert x[0, 0] == 0.0
    assert all(
        candidate.dissimilarity_matrix[0, 1] == 1.0
        for candidate in result["validation_candidates"]
    )
    assert result["dissimilarity_matrix"][0, 1] == 1.0


def test_mutating_preprocessing_callbacks_do_not_change_split_inputs():
    observed = []

    class MutatingPreprocessor:
        def transform(self, values):
            observed.append(values[0, 0])
            values[0, 0] = 999.0
            return np.zeros_like(values)

        def to_record(self):
            return {"name": "synthetic_mutating_preprocessor"}

    def fit_preprocessor(train):
        observed.append(train[0, 0])
        train[0, 0] = 999.0
        return MutatingPreprocessor()

    def parameter_candidates(train):
        observed.append(train[0, 0])
        train[0, 0] = 999.0
        return [{"scale": 1.0}]

    pipeline = RecoveryPipeline(
        config=PipelineConfiguration(
            geometry_id="synthetic_geometry",
            common_fitter_id="synthetic_stub",
        ),
        fit_preprocessor=fit_preprocessor,
        geometry_factory=lambda values, parameters: np.array(
            [[0.0, 2.0], [2.0, 0.0]]
        ),
        geometry_parameter_candidates=parameter_candidates,
        select_validation_candidate=lambda candidates: 0,
        fitter=SyntheticFitter(),
    )
    train = np.zeros((2, 12))
    validation = np.zeros((2, 12))
    test = np.zeros((2, 12))
    result = pipeline.run(train, validation, test)

    assert observed == [0.0, 0.0, 0.0, 0.0, 0.0]
    assert np.all(train == 0.0)
    assert np.all(validation == 0.0)
    assert np.all(test == 0.0)
    assert result["geometry_parameters"] == {"scale": 1.0}


@pytest.mark.parametrize(
    "invalid_candidates",
    [None, [], {}, "candidate", [{"scale": 1.0}, None], [1]],
)
def test_malformed_geometry_candidate_collection_fails_before_fitting(invalid_candidates):
    fitter_calls = []

    class RecordingFitter:
        fitter_id = "synthetic_recording"

        def fit(self, dissimilarity, *, random_seed=None):
            fitter_calls.append(True)
            return FitResult(ultrametric_matrix=np.zeros((2, 2)), tree={}, diagnostics={})

    pipeline = RecoveryPipeline(
        config=PipelineConfiguration(
            geometry_id="synthetic_geometry",
            common_fitter_id="synthetic_recording",
        ),
        fit_preprocessor=lambda train: IdentityPreprocessor(),
        geometry_factory=lambda values, parameters: np.array(
            [[0.0, 2.0], [2.0, 0.0]]
        ),
        geometry_parameter_candidates=lambda train: invalid_candidates,
        select_validation_candidate=lambda candidates: 0,
        fitter=RecordingFitter(),
    )
    x = np.zeros((2, 12))
    with pytest.raises(ConfigurationRequired):
        pipeline.run(x, x.copy(), x.copy())
    assert not fitter_calls


def test_candidate_snapshot_survives_factory_mutating_future_candidate():
    original_candidates = [
        {"nested": {"scale": 1.0}},
        {"nested": {"scale": 2.0}},
    ]
    observed = []

    def geometry_factory(values, parameters):
        observed.append(parameters["nested"]["scale"])
        original_candidates[1]["nested"]["scale"] = 999.0
        return np.array([[0.0, 2.0], [2.0, 0.0]])

    pipeline = RecoveryPipeline(
        config=PipelineConfiguration(
            geometry_id="synthetic_geometry",
            common_fitter_id="synthetic_stub",
        ),
        fit_preprocessor=lambda train: IdentityPreprocessor(),
        geometry_factory=geometry_factory,
        geometry_parameter_candidates=lambda train: original_candidates,
        select_validation_candidate=lambda candidates: 1,
        fitter=SyntheticFitter(),
    )
    x = np.zeros((2, 12))
    result = pipeline.run(x, x.copy(), x.copy())

    assert observed == [1.0, 2.0, 2.0]
    assert result["geometry_parameters"] == {"nested": {"scale": 2.0}}
    assert [candidate.parameters["nested"]["scale"] for candidate in result["validation_candidates"]] == [1.0, 2.0]
