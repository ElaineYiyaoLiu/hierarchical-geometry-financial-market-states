import numpy as np

from branch_b.bootstrap import run_full_pipeline_bootstrap


def test_bootstrap_resamples_each_split_and_keeps_failures():
    def evaluate(train_idx, validation_idx, test_idx, seed):
        raise RuntimeError("intentional")

    reps = run_full_pipeline_bootstrap(
        n_replicates=2,
        train_size=3,
        validation_size=4,
        test_size=5,
        base_seed=123,
        evaluate_replicate=evaluate,
    )
    assert len(reps) == 2
    assert all(rep.failure is not None for rep in reps)
    assert all(len(rep.train_indices) == 3 for rep in reps)
    assert all(len(rep.validation_indices) == 4 for rep in reps)
    assert all(len(rep.test_indices) == 5 for rep in reps)


def test_bootstrap_is_reproducible_from_branch_b_owned_seed():
    def evaluate(train_idx, validation_idx, test_idx, seed):
        return seed

    kwargs = dict(
        n_replicates=3,
        train_size=5,
        validation_size=4,
        test_size=3,
        base_seed=987654,
        evaluate_replicate=evaluate,
    )
    left = run_full_pipeline_bootstrap(**kwargs)
    right = run_full_pipeline_bootstrap(**kwargs)

    for a, b in zip(left, right, strict=True):
        assert np.array_equal(a.train_indices, b.train_indices)
        assert np.array_equal(a.validation_indices, b.validation_indices)
        assert np.array_equal(a.test_indices, b.test_indices)
        assert a.result == b.result


def test_duplicate_bootstrap_draws_are_recorded_as_multiplicities():
    from branch_b.bootstrap import distinct_original_indices, draw_multiplicities

    draw = np.array([2, 2, 0, 2, 1, 1])
    assert draw_multiplicities(draw) == {0: 1, 1: 2, 2: 3}
    assert distinct_original_indices(draw) == [0, 1, 2]


def test_full_pipeline_bootstrap_refits_and_reselects_each_replicate():
    from branch_b.bootstrap import run_recovery_pipeline_bootstrap
    from branch_b.fitters import FitResult
    from branch_b.geometries import euclidean_dissimilarity
    from branch_b.preprocessing import Standardizer
    from branch_b.recovery_pipeline import PipelineConfiguration, RecoveryPipeline

    calls = {"preprocess": 0, "select": 0}

    def fit_preprocessor(x):
        calls["preprocess"] += 1
        return Standardizer.fit(x)

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
                diagnostics={"seed": random_seed},
            )

    def selector(candidates):
        calls["select"] += 1
        return 0

    pipeline = RecoveryPipeline(
        config=PipelineConfiguration("standardized_euclidean", "stub"),
        fit_preprocessor=fit_preprocessor,
        geometry_factory=lambda x, params: euclidean_dissimilarity(x),
        geometry_parameter_candidates=lambda train_x: [{}],
        select_validation_candidate=selector,
        fitter=StubFitter(),
    )

    base = np.arange(72, dtype=float).reshape(6, 12)
    # Add coordinate-specific variation so bootstrap standardization is nondegenerate.
    base = base + np.arange(12, dtype=float)[None, :] * np.arange(6, dtype=float)[:, None]

    reps = run_recovery_pipeline_bootstrap(
        pipeline=pipeline,
        train_values=base,
        validation_values=base + 0.5,
        test_values=base + 1.0,
        n_replicates=3,
        base_seed=24680,
    )

    assert calls["preprocess"] == 3
    assert calls["select"] == 3
    assert len(reps) == 3
    assert all(rep.failure is None for rep in reps)
    assert all("test_multiplicity" in rep.result["bootstrap_draws"] for rep in reps)
