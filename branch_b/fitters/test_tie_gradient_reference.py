"""Small synthetic D04 analysis; not a production tie-gradient policy."""
import numpy as np

from branch_b.fitters.tie_gradient_reference import (
    triangle_tie_resolution_jacobians,
    unresolved_three_way_topology,
)


def test_three_way_tie_stays_multifurcating():
    assert unresolved_three_way_topology() == ((0, 1, 2),)


def test_all_strict_tie_resolutions_have_correct_jacobian():
    resolutions = triangle_tie_resolution_jacobians()
    assert len(resolutions) == 6
    assert {tuple(order) for order, _, _ in resolutions} == {
        (0, 1, 2), (0, 2, 1), (1, 0, 2),
        (1, 2, 0), (2, 0, 1), (2, 1, 0),
    }
    for order, first, jac in resolutions:
        assert first == order[0]
        assert jac.shape == (3, 3)
        assert np.array_equal(jac.sum(axis=1), np.ones(3))


def test_same_binary_tree_can_give_different_limiting_jacobians():
    """Tree topology alone does not select the min-max derivative."""
    resolutions = triangle_tie_resolution_jacobians()
    first_edge_zero = [jac for _, first, jac in resolutions if first == 0]
    assert len(first_edge_zero) == 2
    assert not np.array_equal(first_edge_zero[0], first_edge_zero[1])


def test_limiting_jacobians_agree_with_minmax_forward_operator():
    from branch_b.fitters.positive_edge_graph import positive_edge_graph
    from branch_b.fitters.minmax_reference import minmax_ultrametric

    graph = positive_edge_graph(np.ones((3, 3)) - np.eye(3))
    eps = 1e-6
    delta = 1e-9
    for order, _first, jac in triangle_tie_resolution_jacobians():
        weights = np.empty(3)
        for rank, edge in enumerate(order):
            weights[edge] = 1.0 + rank * eps
        base = minmax_ultrametric(graph, weights)
        pairs = [(0, 1), (0, 2), (1, 2)]
        for edge_index in range(3):
            plus = weights.copy()
            plus[edge_index] += delta
            new = minmax_ultrametric(graph, plus)
            observed = np.array([
                (new[i, j] - base[i, j]) / delta for i, j in pairs
            ])
            np.testing.assert_allclose(observed, jac[:, edge_index], atol=2e-6)


def test_uniform_over_trees_requires_within_tree_gradient_convention():
    resolutions = triangle_tie_resolution_jacobians()
    for first in range(3):
        gradients = [jac for _, merger, jac in resolutions if merger == first]
        assert len(gradients) == 2
        assert not np.array_equal(gradients[0], gradients[1])


def test_uniform_tree_conditional_gradient_matches_order_mean_for_triangle():
    """For the symmetric triangle each binary first-merge tree has two orderings."""
    resolutions = triangle_tie_resolution_jacobians()
    tree_means = [
        np.mean([jac for _, first, jac in resolutions if first == tree], axis=0)
        for tree in range(3)
    ]
    tree_uniform = np.mean(tree_means, axis=0)
    order_uniform = np.mean([jac for _, _, jac in resolutions], axis=0)
    np.testing.assert_allclose(tree_uniform, order_uniform)
    # This value is derived from symmetric triangle perturbations, not a
    # prescribed general D04 rule.
    expected = np.full((3, 3), 1.0 / 3.0)
    np.fill_diagonal(expected, 1.0 / 3.0)
    np.testing.assert_allclose(tree_uniform, expected)


def test_uniform_trees_differs_from_uniform_orderings_for_unequal_fibers():
    """Pure combinatorial counterexample: counts per tree affect weights.

    The toy gradient vectors are arbitrary placeholders, not fitted gradients.
    This proves why tree-average and ordering-average need not coincide.
    """
    gradients_by_tree = {
        "tree_A": [np.array([1., 0.])],
        "tree_B": [np.array([0., 1.]), np.array([0., 1.])],
    }
    tree_mean = np.mean([
        np.mean(g, axis=0) for g in gradients_by_tree.values()
    ], axis=0)
    ordering_mean = np.mean([
        grad for group in gradients_by_tree.values() for grad in group
    ], axis=0)
    np.testing.assert_allclose(tree_mean, [0.5, 0.5])
    np.testing.assert_allclose(ordering_mean, [1. / 3., 2. / 3.])
    assert not np.array_equal(tree_mean, ordering_mean)
