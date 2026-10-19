"""Synthetic properties of the isolated min-max ultrametric operator.

Run only in the configured Python 3.14 Branch B CI environment.
"""
import numpy as np
import pytest

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.fitters.minmax_operator import subdominant_ultrametric


def test_three_vertex_bottleneck_path():
    w = np.array([[0.0, 2.0, 5.0], [2.0, 0.0, 3.0], [5.0, 3.0, 0.0]])
    expected = np.array([[0.0, 2.0, 3.0], [2.0, 0.0, 3.0], [3.0, 3.0, 0.0]])
    assert np.array_equal(subdominant_ultrametric(w), expected)


def test_minmax_is_idempotent_and_ultrametric():
    w = np.array([
        [0.0, 4.0, 8.0, 7.0],
        [4.0, 0.0, 3.0, 9.0],
        [8.0, 3.0, 0.0, 2.0],
        [7.0, 9.0, 2.0, 0.0],
    ])
    u = subdominant_ultrametric(w)
    assert np.array_equal(subdominant_ultrametric(u), u)
    assert np.array_equal(u, u.T)
    assert np.all(u <= w)
    for i in range(len(u)):
        for j in range(len(u)):
            for k in range(len(u)):
                assert u[i, j] <= max(u[i, k], u[k, j])


def test_minmax_does_not_mutate_input():
    w = np.array([[0.0, 1.0], [1.0, 0.0]])
    before = w.copy()
    subdominant_ultrametric(w)
    assert np.array_equal(w, before)


@pytest.mark.parametrize("w,code", [
    (np.array([[0.0, np.inf], [np.inf, 0.0]]), FailureCode.NONFINITE_INPUT),
    (np.array([[0.0, 1.0], [2.0, 0.0]]), FailureCode.DEGENERATE_DISTANCE),
    (np.array([[0.0, -1.0], [-1.0, 0.0]]), FailureCode.DEGENERATE_DISTANCE),
    (np.array([[0.0, 1.0, 2.0]]), FailureCode.INPUT_SCHEMA),
])
def test_minmax_rejects_invalid_weights(w, code):
    with pytest.raises(BranchBFailure) as exc:
        subdominant_ultrametric(w)
    assert exc.value.code == code


def test_minmax_agrees_with_independent_spanning_tree_bottlenecks():
    """Compare the recurrence against a separate Kruskal path construction."""
    w = np.array([
        [0.0, 7.0, 4.0, 9.0, 6.0],
        [7.0, 0.0, 5.0, 8.0, 3.0],
        [4.0, 5.0, 0.0, 2.0, 7.0],
        [9.0, 8.0, 2.0, 0.0, 1.0],
        [6.0, 3.0, 7.0, 1.0, 0.0],
    ])
    n = len(w)
    parent = list(range(n))

    def root(i):
        while parent[i] != i:
            i = parent[i]
        return i

    adjacency = [[] for _ in range(n)]
    edges = sorted((w[i, j], i, j) for i in range(n) for j in range(i + 1, n))
    for weight, i, j in edges:
        ri, rj = root(i), root(j)
        if ri == rj:
            continue
        parent[ri] = rj
        adjacency[i].append((j, weight))
        adjacency[j].append((i, weight))

    expected = np.zeros_like(w)
    for source in range(n):
        stack = [(source, -1, 0.0)]
        while stack:
            node, previous, bottleneck = stack.pop()
            expected[source, node] = bottleneck
            for neighbor, weight in adjacency[node]:
                if neighbor != previous:
                    stack.append((neighbor, node, max(bottleneck, weight)))
    assert np.array_equal(subdominant_ultrametric(w), expected)


def test_minmax_is_permutation_equivariant_and_scale_equivariant():
    """Relabeling vertices and positive rescaling preserve bottleneck paths."""
    w = np.array([
        [0.0, 2.0, 8.0, 6.0],
        [2.0, 0.0, 5.0, 7.0],
        [8.0, 5.0, 0.0, 3.0],
        [6.0, 7.0, 3.0, 0.0],
    ])
    order = [3, 1, 0, 2]
    expected = subdominant_ultrametric(w)
    permuted = subdominant_ultrametric(w[np.ix_(order, order)])
    assert np.array_equal(permuted, expected[np.ix_(order, order)])
    assert np.array_equal(subdominant_ultrametric(4.0 * w), 4.0 * expected)


def test_minmax_preserves_equal_height_unresolved_structure():
    """Equal bottleneck heights remain equal; this primitive never resolves ties."""
    w = np.array([
        [0.0, 2.0, 2.0],
        [2.0, 0.0, 2.0],
        [2.0, 2.0, 0.0],
    ])
    assert np.array_equal(subdominant_ultrametric(w), w)


def test_zero_weight_path_collapses_only_its_connected_component():
    """Equation (5): zero-weight paths have zero bottleneck distance."""
    w = np.array([
        [0.0, 0.0, 9.0, 8.0],
        [0.0, 0.0, 0.0, 7.0],
        [9.0, 0.0, 0.0, 3.0],
        [8.0, 7.0, 3.0, 0.0],
    ])
    expected = np.array([
        [0.0, 0.0, 0.0, 3.0],
        [0.0, 0.0, 0.0, 3.0],
        [0.0, 0.0, 0.0, 3.0],
        [3.0, 3.0, 3.0, 0.0],
    ])
    assert np.array_equal(subdominant_ultrametric(w), expected)
