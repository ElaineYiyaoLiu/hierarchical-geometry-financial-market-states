import numpy as np

from branch_b.fitters import FitResult
from branch_b.geometries import euclidean_dissimilarity
from branch_b.preprocessing import Standardizer
from branch_b.recovery_pipeline import PipelineConfiguration, RecoveryPipeline


class StubFitter:
    fitter_id = "stub"

    def fit(self, dissimilarity, *, random_seed=None):
        d = np.asarray(dissimilarity, dtype=float)
        n = d.shape[0]
        leaves = [f"S{i + 1}" for i in range(n)]
        return FitResult(
            ultrametric_matrix=d.copy(),
            tree={
                "tree_format_version": "1",
                "root": "I000001",
                "internal_nodes": ["I000001"],
                "leaves": leaves,
                "edges": [
                    {
                        "parent": "I000001",
                        "child": leaf,
                        "branch_length": 1.0,
                        "unresolved": n > 2,
                    }
                    for leaf in leaves
                ],
            },
            diagnostics={"stub": True},
        )


def _data():
    train = np.vstack([
        np.arange(12, dtype=float),
        np.arange(12, dtype=float) + 2.0,
        np.arange(12, dtype=float) + 4.0,
    ])
    validation = np.vstack([
        np.arange(12, dtype=float) + 1.0,
        np.arange(12, dtype=float) + 3.0,
    ])
    test = np.vstack([
        np.arange(12, dtype=float) + 5.0,
        np.arange(12, dtype=float) + 7.0,
    ])
    return train, validation, test


def test_pipeline_fits_validation_candidates_then_carries_selection_to_test():
    train, validation, test = _data()

    pipeline = RecoveryPipeline(
        config=PipelineConfiguration(
            geometry_id="standardized_euclidean",
            common_fitter_id="stub",
        ),
        fit_preprocessor=Standardizer.fit,
        geometry_factory=lambda x, params: euclidean_dissimilarity(x) * params["scale"],
        geometry_parameter_candidates=lambda train_x: [{"scale": 1.0}, {"scale": 2.0}],
        select_validation_candidate=lambda candidates: 1,
        fitter=StubFitter(),
    )
    result = pipeline.run(train, validation, test)

    assert result["preprocessing"]["ddof"] == 0
    assert len(result["validation_candidates"]) == 2
    assert result["selected_candidate_index"] == 1
    assert result["geometry_parameters"] == {"scale": 2.0}

    test_d = result["dissimilarity_matrix"]
    assert np.max(test_d[np.triu_indices(2, k=1)]) == 1.0


def test_validation_selector_is_injected_not_hard_coded():
    train, validation, test = _data()
    seen = {}

    def selector(candidates):
        seen["count"] = len(candidates)
        seen["maxima"] = [
            float(np.max(c.dissimilarity_matrix[np.triu_indices(c.dissimilarity_matrix.shape[0], k=1)]))
            for c in candidates
        ]
        return 0

    pipeline = RecoveryPipeline(
        config=PipelineConfiguration("standardized_euclidean", "stub"),
        fit_preprocessor=Standardizer.fit,
        geometry_factory=lambda x, params: euclidean_dissimilarity(x),
        geometry_parameter_candidates=lambda train_x: [{}, {}],
        select_validation_candidate=selector,
        fitter=StubFitter(),
    )
    result = pipeline.run(train, validation, test)

    assert seen["count"] == 2
    assert seen["maxima"] == [1.0, 1.0]
    assert result["selected_candidate_index"] == 0
