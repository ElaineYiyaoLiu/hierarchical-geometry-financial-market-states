"""Synthetic integration fixtures only; no bank, method approval, or true hierarchy."""
from copy import deepcopy

import numpy as np
import pytest

from branch_b.bootstrap.checked import (
    bind_bootstrap_draw, bound_lca_stability, run_checked_recovery_pipeline_bootstrap,
)
from branch_b.bootstrap.engine import run_full_pipeline_bootstrap
from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.fitters.base import FitResult
from branch_b.recovery_pipeline.pipeline import PipelineConfiguration, RecoveryPipeline
from branch_b.recovery_pipeline.result_validation import validate_fit_result


VALIDATION = ["V0", "V1", "V2"]
TEST = ["T0", "T1", "T2"]


def _tree(order, resolved=False):
    tree = {
        "tree_format_version": "1", "root": "ROOT", "internal_nodes": ["ROOT"],
        "leaves": list(order),
        "edges": [{"parent": "ROOT", "child": name, "branch_length": 1.0} for name in order],
    }
    if resolved:
        tree["internal_nodes"].append("INNER")
        tree["edges"] = [
            {"parent": "ROOT", "child": "INNER", "branch_length": 1.0},
            {"parent": "ROOT", "child": order[2], "branch_length": 1.0},
            {"parent": "INNER", "child": order[0], "branch_length": 1.0},
            {"parent": "INNER", "child": order[1], "branch_length": 1.0},
        ]
    return tree


def _fit(order, seed=None):
    matrix = np.ones((len(order), len(order)))
    np.fill_diagonal(matrix, 0.0)
    return FitResult(matrix, _tree(order), {"synthetic_seed": seed})


def _corrupt(fit, fault):
    matrix, tree, diagnostics = fit.ultrametric_matrix, fit.tree, fit.diagnostics
    if fault == "not_fit":
        return {}
    if fault == "nan":
        matrix[0, 1] = np.nan
    elif fault == "infinity":
        matrix[0, 1] = np.inf
    elif fault == "dimension":
        matrix = np.zeros((2, 2))
    elif fault == "boolean_matrix":
        matrix = matrix.astype(bool)
    elif fault == "text_matrix":
        matrix = matrix.astype(str)
    elif fault == "complex_matrix":
        matrix = matrix.astype(complex)
    elif fault == "no_matrix":
        matrix = None
    elif fault == "diagnostics":
        diagnostics = []
    elif fault == "leaf_order":
        tree["leaves"].reverse()
    elif fault == "missing_leaf":
        tree["leaves"].pop()
    elif fault == "extra_leaf":
        tree["leaves"].append("EXTRA")
    elif fault == "duplicate_leaf":
        tree["leaves"][1] = tree["leaves"][0]
    elif fault == "extra_tree_field":
        tree["unrecognized"] = True
    elif fault == "empty_version":
        tree["tree_format_version"] = ""
    elif fault == "missing_parent":
        tree["edges"].pop()
    elif fault == "nonfinite_branch":
        tree["edges"][0]["branch_length"] = float("nan")
    return FitResult(matrix, tree, diagnostics)


class Identity:
    def __init__(self, events):
        self.events = events

    def transform(self, values):
        self.events.append("transform")
        return values.copy()

    def to_record(self):
        return {"name": "synthetic_identity"}


class NamedStub:
    fitter_id = "synthetic_named"

    def __init__(self, fault=None, bad_call=1):
        self.fault = fault
        self.bad_call = bad_call
        self.calls = []
        self.unnamed_calls = 0

    def fit(self, dissimilarity, *, random_seed=None):
        self.unnamed_calls += 1
        return _fit([f"S{i}" for i in range(len(dissimilarity))], random_seed)

    def fit_with_sample_order(self, dissimilarity, *, sample_order, random_seed=None):
        self.calls.append((sample_order.copy(), random_seed))
        result = _fit(sample_order, random_seed)
        if self.fault and (self.bad_call is None or len(self.calls) == self.bad_call):
            return _corrupt(result, self.fault)
        return result


def _pipeline(fitter=None, selector=None, events=None, geometry=None):
    fitter = NamedStub() if fitter is None else fitter
    events = [] if events is None else events

    def select(candidates):
        events.append("select")
        return 0 if selector is None else selector(candidates)

    def default_geometry(values, parameters):
        matrix = np.ones((len(values), len(values))) * 2.0
        np.fill_diagonal(matrix, 0.0)
        return matrix

    return RecoveryPipeline(
        config=PipelineConfiguration("synthetic_geometry", fitter.fitter_id),
        fit_preprocessor=lambda values: Identity(events),
        geometry_factory=default_geometry if geometry is None else geometry,
        geometry_parameter_candidates=lambda values: [{"candidate": 0}, {"candidate": 1}],
        select_validation_candidate=select, fitter=fitter,
    )


def _splits():
    values = np.arange(36, dtype=float).reshape(3, 12)
    return values, values + 1.0, values + 2.0


def _run(pipeline, test=None):
    train, validation, default_test = _splits()
    return pipeline.run_checked(
        train, validation, default_test if test is None else test,
        validation_sample_order=VALIDATION, test_sample_order=TEST,
    )


@pytest.mark.parametrize("fault", [
    "not_fit", "nan", "infinity", "dimension", "boolean_matrix", "text_matrix",
    "complex_matrix", "no_matrix", "diagnostics", "leaf_order", "missing_leaf",
    "extra_leaf", "duplicate_leaf", "extra_tree_field", "empty_version", "missing_parent",
    "nonfinite_branch",
])
def test_invalid_fit_is_rejected_before_selection(fault):
    events = []
    fitter = NamedStub(fault)
    with pytest.raises(BranchBFailure) as caught:
        _run(_pipeline(fitter, events=events))
    expected = FailureCode.NUMERICAL_FIT if fault in {"nan", "infinity"} else (
        FailureCode.DEGENERATE_TREE if fault == "missing_parent" else FailureCode.OUTPUT_SCHEMA
    )
    assert caught.value.code == expected
    assert "select" not in events
    assert len(fitter.calls) == 1
    assert fitter.unnamed_calls == 0


def test_checked_success_retains_external_identities_without_claiming_authorization():
    fitter = NamedStub()
    result = _run(_pipeline(fitter))
    assert [row[0] for row in fitter.calls] == [VALIDATION, VALIDATION, TEST]
    assert result["sample_order"] == TEST
    assert result["validation_sample_order"] == VALIDATION
    assert result["result_validation"] == "structural_checks_only"
    assert result["scientific_authorization"] is False
    assert fitter.unnamed_calls == 0


def test_invalid_test_fit_cannot_be_returned_as_checked_success():
    events = []
    fitter = NamedStub("nan", bad_call=3)
    with pytest.raises(BranchBFailure) as caught:
        _run(_pipeline(fitter, events=events))
    assert caught.value.code == FailureCode.NUMERICAL_FIT
    assert events.count("select") == 1
    assert len(fitter.calls) == 3


@pytest.mark.parametrize("order", [None, [], ["V0", "V0", "V2"], ["", "V1", "V2"], ["V0", "V1"]])
def test_invalid_external_order_cannot_reach_fitter(order):
    fitter = NamedStub()
    with pytest.raises(BranchBFailure) as caught:
        _pipeline(fitter).run_checked(*_splits(), validation_sample_order=order, test_sample_order=TEST)
    assert caught.value.code == FailureCode.INPUT_SCHEMA
    assert fitter.calls == []


def test_wrong_geometry_dimension_rejected_before_fitter():
    fitter = NamedStub()
    geometry = lambda values, parameters: np.array([[0.0, 2.0], [2.0, 0.0]])
    with pytest.raises(BranchBFailure) as caught:
        _run(_pipeline(fitter, geometry=geometry))
    assert caught.value.code == FailureCode.OUTPUT_SCHEMA
    assert fitter.calls == []


def test_unnamed_fitter_has_no_checked_fallback():
    class Legacy:
        fitter_id = "legacy_stub"

        def fit(self, *args, **kwargs):
            raise AssertionError("unchecked fallback must not run")

    with pytest.raises(ConfigurationRequired, match="identity-aware"):
        _run(_pipeline(Legacy()))


def test_supplied_identity_list_is_isolated_from_fitter_mutation():
    class Mutator(NamedStub):
        def fit_with_sample_order(self, dissimilarity, *, sample_order, random_seed=None):
            result = _fit(sample_order)
            sample_order.reverse()
            return result

    original_validation, original_test = VALIDATION.copy(), TEST.copy()
    result = _run(_pipeline(Mutator()))
    assert VALIDATION == original_validation and TEST == original_test
    assert result["sample_order"] == original_test


@pytest.mark.parametrize("checked", [False, True])
@pytest.mark.parametrize("index", [None, True, False, 1.0, "0", -1, 2])
def test_invalid_selection_never_converts_or_transforms_test(checked, index):
    class UnreadableTest:
        def __array__(self, dtype=None, copy=None):
            raise AssertionError("test input was accessed before valid selection")

    events = []
    pipeline = _pipeline(selector=lambda candidates: index, events=events)
    with pytest.raises(ConfigurationRequired):
        if checked:
            _run(pipeline, test=UnreadableTest())
        else:
            train, validation, _ = _splits()
            pipeline.run(train, validation, UnreadableTest())
    assert events == ["transform", "transform", "select"]


def test_valid_selection_precedes_test_conversion_and_transform():
    events = []

    class RecordedTest:
        def __array__(self, dtype=None, copy=None):
            events.append("test_read")
            return np.arange(36, dtype=float).reshape(3, 12)

    _run(_pipeline(events=events), test=RecordedTest())
    assert events == ["transform", "transform", "select", "test_read", "transform"]


def test_structural_validator_does_not_invent_a_numerical_comparison_rule():
    fit = _fit(TEST)
    fit.ultrametric_matrix[0, 1] = 0.25
    # This deliberately asymmetric fixture is structurally numeric. Passing here
    # is not an ultrametric/symmetry certificate; approved numerical checks remain required.
    validate_fit_result(fit, sample_order=TEST)


def test_bootstrap_identity_mapping_keeps_repeated_original_ids():
    result = bind_bootstrap_draw(
        np.array([2, 0, 2]), original_sample_order=TEST,
        fit_sample_order=["B0", "B1", "B2"],
    )
    assert result == [
        {"fit_sample_id": "B0", "original_sample_id": "T2"},
        {"fit_sample_id": "B1", "original_sample_id": "T0"},
        {"fit_sample_id": "B2", "original_sample_id": "T2"},
    ]


@pytest.mark.parametrize("draw", [[0, 1, 3], [-1, 1, 2], [0.0, 1.0, 2.0], [True, False, True], [[0, 1, 2]], [0, 1]])
def test_bad_draw_binding_is_rejected(draw):
    with pytest.raises(BranchBFailure) as caught:
        bind_bootstrap_draw(draw, original_sample_order=TEST, fit_sample_order=["B0", "B1", "B2"])
    assert caught.value.code == FailureCode.INPUT_SCHEMA


@pytest.mark.parametrize("which", ["full", "bootstrap"])
def test_named_topology_with_reordered_leaf_list_is_rejected(which):
    full = _tree(TEST, resolved=True)
    labels = ["B0", "B1", "B2"]
    bootstrap = _tree(labels, resolved=True)
    (full if which == "full" else bootstrap)["leaves"].reverse()
    with pytest.raises(BranchBFailure) as caught:
        bound_lca_stability(
            full_test_tree=full, original_sample_order=TEST,
            bootstrap_tree=bootstrap, bootstrap_sample_order=labels,
            bootstrap_test_indices=np.array([0, 1, 2]),
        )
    assert caught.value.code == FailureCode.OUTPUT_SCHEMA


def test_correct_bindings_preserve_existing_lca_statistic():
    labels = ["B0", "B1", "B2"]
    score = bound_lca_stability(
        full_test_tree=_tree(TEST, resolved=True), original_sample_order=TEST,
        bootstrap_tree=_tree(labels, resolved=True), bootstrap_sample_order=labels,
        bootstrap_test_indices=np.array([0, 1, 2]),
    )
    assert score == pytest.approx(1.0)


def _bootstrap_kwargs(pipeline):
    train, validation, test = _splits()
    return dict(
        pipeline=pipeline, train_values=train, validation_values=validation, test_values=test,
        train_sample_order=["R0", "R1", "R2"], validation_sample_order=VALIDATION,
        test_sample_order=TEST, validation_fit_sample_order=["BV0", "BV1", "BV2"],
        test_fit_sample_order=["BT0", "BT1", "BT2"], n_replicates=4,
        base_seed=20261019,  # Branch B implementation-test seed only.
    )


@pytest.mark.parametrize("fault", ["nan", "leaf_order"])
def test_checked_bootstrap_keeps_every_invalid_fit_as_failure(fault):
    fitter = NamedStub(fault, bad_call=None)
    records = run_checked_recovery_pipeline_bootstrap(**_bootstrap_kwargs(_pipeline(fitter)))
    assert len(records) == len(fitter.calls) == 4
    expected = "NUMERICAL_FIT" if fault == "nan" else "OUTPUT_SCHEMA"
    assert all(record.failure["failure_code"] == expected and record.result is None for record in records)
    assert all(isinstance(record.replicate_seed, int) for record in records)
    assert fitter.unnamed_calls == 0


def test_checked_bootstrap_retains_original_draw_sequence_and_identity_bindings():
    records = run_checked_recovery_pipeline_bootstrap(**_bootstrap_kwargs(_pipeline()))
    reference = run_full_pipeline_bootstrap(
        n_replicates=4, train_size=3, validation_size=3, test_size=3, base_seed=20261019,
        evaluate_replicate=lambda train, validation, test, seed: seed,
    )
    for record, before in zip(records, reference, strict=True):
        assert record.failure is None
        assert record.replicate_seed == before.replicate_seed
        for attribute in ("train_indices", "validation_indices", "test_indices"):
            np.testing.assert_array_equal(getattr(record, attribute), getattr(before, attribute))
        identities = record.result["bootstrap_identity"]["test"]
        assert [row["original_sample_id"] for row in identities] == [TEST[int(i)] for i in record.test_indices]
        assert [row["fit_sample_id"] for row in identities] == ["BT0", "BT1", "BT2"]
        assert record.result["scientific_authorization"] is False


@pytest.mark.parametrize("geometry_name", ["euclidean_dissimilarity", "chebyshev_dissimilarity"])
def test_duplicate_row_conflict_is_demonstrated_without_selecting_a_repair(geometry_name):
    from branch_b import geometries
    from branch_b.fitters.gradient_descent import GradientDescentUltrametricFitter
    from branch_b.normalization import normalize_dissimilarity

    original = np.arange(36, dtype=float).reshape(3, 12)
    repeated = original[[0, 0, 2]]
    distance = normalize_dissimilarity(getattr(geometries, geometry_name)(repeated))
    assert distance[0, 1] == 0.0
    with pytest.raises(BranchBFailure) as caught:
        GradientDescentUltrametricFitter().validate_normalized_input(distance)
    assert caught.value.code == FailureCode.DEGENERATE_DISTANCE
