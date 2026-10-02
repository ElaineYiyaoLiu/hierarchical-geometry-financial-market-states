import numpy as np

from branch_b.fitters import FitResult
from branch_b.geometries import euclidean_dissimilarity
from branch_b.preprocessing import Standardizer
from branch_b.recovery_pipeline import PipelineConfiguration, RecoveryPipeline


class StubFitter:
    fitter_id = "stub"

    def fit(self, dissimilarity, *, random_seed=None):
        d = np.asarray(dissimilarity, dtype=float)
        return FitResult(
            ultrametric_matrix=d.copy(),
            tree={
                "tree_format_version": "1",
                "root": "I000001",
                "internal_nodes": ["I000001"],
                "leaves": ["S1", "S2"],
                "edges": [
                    {"parent": "I000001", "child": "S1", "branch_length": 1.0},
                    {"parent": "I000001", "child": "S2", "branch_length": 1.0},
                ],
            },
            diagnostics={"stub": True},
        )


def test_pipeline_uses_registered_preprocessing_and_common_normalization():
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

    pipeline = RecoveryPipeline(
        config=PipelineConfiguration(
            geometry_id="standardized_euclidean",
            common_fitter_id="stub",
        ),
        fit_preprocessor=lambda x: Standardizer.fit(x),
        geometry_factory=lambda x, params: euclidean_dissimilarity(x),
        select_geometry_parameters=lambda train_x, validation_x: {},
        fitter=StubFitter(),
    )
    result = pipeline.run(train, validation, test)

    assert result["preprocessing"]["ddof"] == 0
    d = result["dissimilarity_matrix"]
    assert np.max(d[np.triu_indices(2, k=1)]) == 1.0
