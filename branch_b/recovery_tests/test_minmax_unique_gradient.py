"""Synthetic derivative checks for the isolated tie-free min-max reference.

Execute only in the project's Python 3.14 test environment.
"""
import numpy as np
import pytest

from branch_b.failures import ConfigurationRequired
from branch_b.fitters.minmax_operator import subdominant_ultrametric
from branch_b.fitters.minmax_unique_gradient import unique_bottleneck_jacobian


def test_three_vertex_jacobian_matches_unique_bottlenecks():
    w = np.array([
        [0.0, 2.0, 5.0],
        [2.0, 0.0, 3.0],
        [5.0, 3.0, 0.0],
    ])
    pairs, jacobian = unique_bottleneck_jacobian(w)
    np.testing.assert_array_equal(pairs, [[0, 1], [0, 2], [1, 2]])
    np.testing.assert_array_equal(jacobian, [
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
    ])


def test_jacobian_matches_all_pairwise_central_differences():
    w = np.array([
        [0.0, 4.0, 8.0, 7.0],
        [4.0, 0.0, 3.0, 9.0],
        [8.0, 3.0, 0.0, 2.0],
        [7.0, 9.0, 2.0, 0.0],
    ])
    original = w.copy()
    pairs, jacobian = unique_bottleneck_jacobian(w)
    epsilon = 1e-5
    for column, (i, j) in enumerate(pairs):
        positive, negative = w.copy(), w.copy()
        positive[i, j] += epsilon
        positive[j, i] += epsilon
        negative[i, j] -= epsilon
        negative[j, i] -= epsilon
        upper = subdominant_ultrametric(positive)
        lower = subdominant_ultrametric(negative)
        observed = np.array([
            (upper[a, b] - lower[a, b]) / (2 * epsilon)
            for a, b in pairs
        ])
        np.testing.assert_allclose(observed, jacobian[:, column], atol=1e-9)
    np.testing.assert_array_equal(w, original)


def test_tied_weights_are_not_assigned_an_unapproved_derivative():
    w = np.array([
        [0.0, 2.0, 2.0],
        [2.0, 0.0, 3.0],
        [2.0, 3.0, 0.0],
    ])
    with pytest.raises(ConfigurationRequired, match="tied weights"):
        unique_bottleneck_jacobian(w)


def test_jacobian_is_equivariant_under_vertex_relabeling():
    """The derivative reference must not depend on sample identifiers/order."""
    w = np.array([
        [0.0, 4.0, 8.0, 7.0],
        [4.0, 0.0, 3.0, 9.0],
        [8.0, 3.0, 0.0, 2.0],
        [7.0, 9.0, 2.0, 0.0],
    ])
    order = [3, 1, 0, 2]
    pairs, jacobian = unique_bottleneck_jacobian(w)
    permuted_pairs, permuted_jacobian = unique_bottleneck_jacobian(
        w[np.ix_(order, order)]
    )
    original_edge_ids = {
        tuple(pair): index for index, pair in enumerate(pairs.tolist())
    }
    edge_reindex = [
        original_edge_ids[tuple(sorted((order[i], order[j])))]
        for i, j in permuted_pairs
    ]
    np.testing.assert_array_equal(
        permuted_jacobian,
        jacobian[np.ix_(edge_reindex, edge_reindex)],
    )


def test_jacobian_is_invariant_under_positive_weight_rescaling():
    """Away from ties, scaling weights preserves the controlling edge."""
    w = np.array([
        [0.0, 2.0, 5.0],
        [2.0, 0.0, 3.0],
        [5.0, 3.0, 0.0],
    ])
    pairs, jacobian = unique_bottleneck_jacobian(w)
    scaled_pairs, scaled_jacobian = unique_bottleneck_jacobian(4.0 * w)
    np.testing.assert_array_equal(scaled_pairs, pairs)
    np.testing.assert_array_equal(scaled_jacobian, jacobian)
