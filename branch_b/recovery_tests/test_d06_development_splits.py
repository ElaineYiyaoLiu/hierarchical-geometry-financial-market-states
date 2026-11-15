"""Synthetic D06 split-orchestration tests; execute under Python 3.14."""

import numpy as np
import pytest

from branch_b.bootstrap.d06_identity_boundary import build_d06_draw_boundary
from branch_b.failures import ConfigurationRequired
from branch_b.fitters.base import FitResult
from branch_b.recovery_pipeline.d06_development_splits import run_d06_development_splits


def bound(indices, prefix):
    return build_d06_draw_boundary(
        np.asarray(indices, dtype=int),
        original_sample_order=["A", "B", "C", "D"],
        fit_sample_order=[f"{prefix}{i}" for i in range(len(indices))],
    )


def tree(order):
    return {
        "tree_format_version": "1", "root": "ROOT",
        "internal_nodes": ["ROOT"], "leaves": list(order),
        "edges": [
            {"parent": "ROOT", "child": x, "branch_length": 1.0}
            for x in order
        ],
    }


class Fitter:
    def __init__(self, events):
        self.events = events

    def fit_with_original_multiplicities(
        self, dissimilarity, *, original_sample_order, multiplicities, random_seed=None
    ):
        self.events.append(("fit", tuple(original_sample_order), tuple(multiplicities)))
        n = len(original_sample_order)
        return FitResult(
            np.asarray(dissimilarity).copy(),
            tree(original_sample_order),
            {"seed": random_seed},
        )


class Preprocessor:
    def __init__(self, events):
        self.events = events

    def transform(self, x):
        self.events.append(("transform", len(x)))
        return np.asarray(x, dtype=float).copy()


def configure(events, selector=None, geometry=None):
    def preprocessor(rows):
        events.append(("fit_preprocessor", len(rows), tuple(rows[:, 0])))
        return Preprocessor(events)

    def default_geometry(rows, params):
        events.append(("geometry", len(rows), params["candidate"]))
        differences = rows[:, [0]] - rows[:, [0]].T
        return abs(differences)

    def candidates(rows):
        events.append(("candidates", len(rows)))
        return [{"candidate": 0}, {"candidate": 1}]

    def select(values):
        events.append(("select", len(values)))
        return 0 if selector is None else selector(values)

    return dict(
        fit_preprocessor=preprocessor,
        geometry_factory=default_geometry if geometry is None else geometry,
        geometry_parameter_candidates=candidates,
        select_validation_candidate=select,
        fitter=Fitter(events),
        random_seed=42,
    )


def inputs():
    # Original A=1, B=2, C=4, D=8. Training includes repeated B.
    train = np.array([[1.], [2.], [2.], [4.], [2.]])
    validation_idx = [2, 1, 2, 0, 1, 0]
    test_idx = [0, 0, 2, 1, 2, 1]
    originals = np.array([[1.], [2.], [4.], [8.]])
    return (
        train, originals[validation_idx], originals[test_idx],
        bound(validation_idx, "V"), bound(test_idx, "T"),
    )


def test_multiset_preprocessing_then_distinct_validation_and_test():
    events = []
    train, validation, test, vb, tb = inputs()
    result = run_d06_development_splits(
        train, validation, test,
        validation_boundary=vb, test_boundary=tb, **configure(events),
    )
    assert ("fit_preprocessor", 5, (1.0, 2.0, 2.0, 4.0, 2.0)) in events
    assert result["validation_distinct_original_ids"] == ["A", "B", "C"]
    assert result["test_distinct_original_ids"] == ["A", "B", "C"]
    assert result["validation_multiplicities"] == [2, 2, 2]
    assert result["test_multiplicities"] == [2, 2, 2]
    assert result["recovered_tree"]["leaves"] == ["A", "B", "C"]
    assert result["scientific_authorization"] is False
    assert [entry[2] for entry in events if entry[0] == "fit"] == [
        (2, 2, 2), (2, 2, 2), (2, 2, 2)
    ]
    assert events.index(("select", 2)) < events.index(("transform", len(test)))


def test_invalid_validation_selection_does_not_read_test():
    class ForbiddenTest:
        def __array__(self, dtype=None, copy=None):
            raise AssertionError("test data read before valid validation selection")

    events = []
    train, validation, _, vb, tb = inputs()
    with pytest.raises(ConfigurationRequired, match="selector"):
        run_d06_development_splits(
            train, validation, ForbiddenTest(), validation_boundary=vb,
            test_boundary=tb, **configure(events, selector=lambda values: -1),
        )
    assert events.count(("select", 2)) == 1
    assert len([x for x in events if x[0] == "fit"]) == 2


def test_validation_fit_failure_does_not_read_test():
    class ForbiddenTest:
        def __array__(self, dtype=None, copy=None):
            raise AssertionError("test read after failed validation fit")

    events = []
    train, validation, _, vb, tb = inputs()

    def bad_geometry(rows, params):
        raise ArithmeticError("synthetic validation failure")

    with pytest.raises(ArithmeticError, match="synthetic validation failure"):
        run_d06_development_splits(
            train, validation, ForbiddenTest(), validation_boundary=vb,
            test_boundary=tb, **configure(events, geometry=bad_geometry),
        )
    assert not any(x[0] == "select" for x in events)
