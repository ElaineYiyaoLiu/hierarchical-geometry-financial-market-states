"""Synthetic recovery-pipeline orchestration regressions (Python 3.14).

A stub fitter and selector test plumbing only; neither is a scientific
candidate, an approved selection rule, or evidence of pilot readiness.
"""
import numpy as np
import pytest

from branch_b.failures import ConfigurationRequired
from branch_b.fitters import FitResult
from branch_b.preprocessing import Standardizer
from branch_b.recovery_pipeline import PipelineConfiguration, RecoveryPipeline


class StubFitter:
    fitter_id = "test_stub"

    def fit(self, dissimilarity, *, random_seed=None):
        d = np.asarray(dissimilarity, dtype=float)
        return FitResult(
            ultrametric_matrix=d.copy(),
            tree={"synthetic_stub": True},
            diagnostics={"seed": random_seed},
        )


def make_pipeline(candidates, selector, geometry):
    return RecoveryPipeline(
        config=PipelineConfiguration("synthetic_geometry", "test_stub"),
        fit_preprocessor=Standardizer.fit,
        geometry_factory=geometry,
        geometry_parameter_candidates=lambda train: candidates,
        select_validation_candidate=selector,
        fitter=StubFitter(),
    )


def test_validation_selection_is_applied_unchanged_to_test():
    seen = []

    def geometry(values, params):
        seen.append((values.copy(), params["multiplier"]))
        d = np.abs(values[:, None, 0] - values[None, :, 0])
        return d * params["multiplier"]

    pipeline = make_pipeline(
        [{"multiplier": 1}, {"multiplier": 2}],
        lambda candidates: 1,
        geometry,
    )
    train = np.vstack([np.zeros(12), np.full(12, 2.0)])
    validation = np.vstack([np.full(12, 4.0), np.full(12, 6.0)])
    test = np.vstack([np.full(12, 10.0), np.full(12, 14.0)])
    result = pipeline.run(train, validation, test, random_seed=123)

    assert result["selected_candidate_index"] == 1
    assert result["geometry_parameters"] == {"multiplier": 2}
    assert [multiplier for _, multiplier in seen] == [1, 2, 2]
    assert np.array_equal(seen[0][0][:, 0], [3.0, 5.0])
    assert np.array_equal(seen[-1][0][:, 0], [9.0, 13.0])
    assert np.array_equal(result["dissimilarity_matrix"], [[0.0, 1.0], [1.0, 0.0]])


@pytest.mark.parametrize("selector", [lambda candidates: -1, lambda candidates: 9, lambda candidates: True])
def test_invalid_validation_selection_fails_closed(selector):
    pipeline = make_pipeline(
        [{}],
        selector,
        lambda values, params: np.array([[0.0, 1.0], [1.0, 0.0]]),
    )
    train = np.vstack([np.zeros(12), np.full(12, 2.0)])
    with pytest.raises(ConfigurationRequired):
        pipeline.run(train, train, train)


def test_empty_candidate_registry_fails_before_validation_or_test_fit():
    geometry_calls = []

    def geometry(values, params):
        geometry_calls.append(True)
        return np.array([[0.0, 1.0], [1.0, 0.0]])

    pipeline = make_pipeline([], lambda candidates: 0, geometry)
    train = np.vstack([np.zeros(12), np.full(12, 2.0)])
    with pytest.raises(ConfigurationRequired, match="no prespecified"):
        pipeline.run(train, train, train)
    assert geometry_calls == []


def test_nonfinite_test_input_fails_before_geometry_fitting():
    geometry_calls = []

    def geometry(values, params):
        geometry_calls.append(True)
        return np.array([[0.0, 1.0], [1.0, 0.0]])

    pipeline = make_pipeline([{}], lambda candidates: 0, geometry)
    train = np.vstack([np.zeros(12), np.full(12, 2.0)])
    test = train.copy()
    test[0, 0] = np.nan
    with pytest.raises(Exception, match="non-finite"):
        pipeline.run(train, train, test)
    assert geometry_calls == []
