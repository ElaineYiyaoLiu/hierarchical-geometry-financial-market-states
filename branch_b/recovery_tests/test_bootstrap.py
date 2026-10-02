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


def _three_leaf_tree(prefix=""):
    return {
        "tree_format_version": "1",
        "root": f"{prefix}R",
        "internal_nodes": [f"{prefix}R", f"{prefix}I"],
        "leaves": [f"{prefix}L0", f"{prefix}L1", f"{prefix}L2"],
        "edges": [
            {"parent": f"{prefix}R", "child": f"{prefix}I", "branch_length": 1.0},
            {"parent": f"{prefix}R", "child": f"{prefix}L2", "branch_length": 1.0},
            {"parent": f"{prefix}I", "child": f"{prefix}L0", "branch_length": 1.0},
            {"parent": f"{prefix}I", "child": f"{prefix}L1", "branch_length": 1.0},
        ],
    }


def test_bootstrap_lca_depths_collapse_duplicate_copies_to_original_pairs():
    from branch_b.bootstrap import bootstrap_lca_depths_by_original

    tree = {
        "tree_format_version": "1",
        "root": "R",
        "internal_nodes": ["R", "I", "J"],
        "leaves": ["B0", "B1", "B2", "B3"],
        "edges": [
            {"parent": "R", "child": "I", "branch_length": 1.0},
            {"parent": "R", "child": "B3", "branch_length": 1.0},
            {"parent": "I", "child": "J", "branch_length": 1.0},
            {"parent": "I", "child": "B2", "branch_length": 1.0},
            {"parent": "J", "child": "B0", "branch_length": 1.0},
            {"parent": "J", "child": "B1", "branch_length": 1.0},
        ],
    }
    # B0/B1 are two bootstrap copies of original observation 0.
    projected = bootstrap_lca_depths_by_original(
        bootstrap_tree=tree,
        bootstrap_test_indices=np.array([0, 0, 1, 2]),
    )
    assert projected == {(0, 1): 1, (0, 2): 0, (1, 2): 0}


def test_bootstrap_lca_projection_rejects_inconsistent_duplicate_copy_relations():
    import pytest

    from branch_b.bootstrap import bootstrap_lca_depths_by_original
    from branch_b.failures import BranchBFailure, FailureCode

    tree = {
        "tree_format_version": "1",
        "root": "R",
        "internal_nodes": ["R", "I", "J"],
        "leaves": ["B0", "B1", "B2", "B3"],
        "edges": [
            {"parent": "R", "child": "I", "branch_length": 1.0},
            {"parent": "R", "child": "B1", "branch_length": 1.0},
            {"parent": "I", "child": "J", "branch_length": 1.0},
            {"parent": "I", "child": "B3", "branch_length": 1.0},
            {"parent": "J", "child": "B0", "branch_length": 1.0},
            {"parent": "J", "child": "B2", "branch_length": 1.0},
        ],
    }
    # B0/B1 are copies of original 0, but they imply different depths to original 1.
    with pytest.raises(BranchBFailure) as exc:
        bootstrap_lca_depths_by_original(
            bootstrap_tree=tree,
            bootstrap_test_indices=np.array([0, 0, 1, 2]),
        )
    assert exc.value.code == FailureCode.DEGENERATE_TREE


def test_bootstrap_lca_stability_matches_distinct_original_relations():
    import pytest

    from branch_b.bootstrap import bootstrap_lca_stability_against_full_test

    full_tree = _three_leaf_tree("F")
    boot_tree = {
        "tree_format_version": "1",
        "root": "R",
        "internal_nodes": ["R", "I", "J"],
        "leaves": ["B0", "B1", "B2", "B3"],
        "edges": [
            {"parent": "R", "child": "I", "branch_length": 1.0},
            {"parent": "R", "child": "B3", "branch_length": 1.0},
            {"parent": "I", "child": "J", "branch_length": 1.0},
            {"parent": "I", "child": "B2", "branch_length": 1.0},
            {"parent": "J", "child": "B0", "branch_length": 1.0},
            {"parent": "J", "child": "B1", "branch_length": 1.0},
        ],
    }
    value = bootstrap_lca_stability_against_full_test(
        full_test_tree=full_tree,
        bootstrap_tree=boot_tree,
        bootstrap_test_indices=np.array([0, 0, 1, 2]),
    )
    assert value == pytest.approx(1.0)
