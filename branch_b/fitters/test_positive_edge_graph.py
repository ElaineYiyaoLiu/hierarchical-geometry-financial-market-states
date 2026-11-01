"""Synthetic graph-construction checks; no scientific fitter is executed."""
import numpy as np
import pytest

from branch_b.fitters.positive_edge_graph import positive_edge_graph


def test_duplicate_points_keep_vertices_and_positive_paths():
    d = np.array([[0., 0., 2., 4.],
                  [0., 0., 2., 4.],
                  [2., 2., 0., 3.],
                  [4., 4., 3., 0.]])
    graph = positive_edge_graph(d)
    assert graph.n_vertices == 4
    assert graph.connected
    assert graph.components == ((0, 1, 2, 3),)
    assert graph.edges.tolist() == [[0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
    assert graph.weights.tolist() == [2., 4., 2., 4., 3.]


def test_threshold_boundary_and_input_immutability():
    d = np.array([[0., 1e-13, 1e-12, 2e-12],
                  [1e-13, 0., 0., 3.],
                  [1e-12, 0., 0., 0.],
                  [2e-12, 3., 0., 0.]])
    before = d.copy()
    graph = positive_edge_graph(d)
    assert graph.edges.tolist() == [[0, 3], [1, 3]]
    assert graph.weights.tolist() == [2e-12, 3.]
    assert graph.components == ((0, 1, 3), (2,))
    np.testing.assert_array_equal(d, before)


def test_all_zero_distances_leave_all_vertices_isolated():
    graph = positive_edge_graph(np.zeros((3, 3)))
    assert graph.edges.shape == (0, 2)
    assert graph.components == ((0,), (1,), (2,))
    assert not graph.connected


def test_arbitrary_dissimilarity_can_yield_two_components():
    d = np.array([[0., 3., 0., 0.],
                  [3., 0., 0., 0.],
                  [0., 0., 0., 2.],
                  [0., 0., 2., 0.]])
    graph = positive_edge_graph(d)
    assert graph.components == ((0, 1), (2, 3))
    assert not graph.connected


def test_positive_complete_graph_remains_connected():
    graph = positive_edge_graph(np.array([[0., 1., 2.], [1., 0., 3.], [2., 3., 0.]]))
    assert graph.connected
    assert len(graph.weights) == 3


@pytest.mark.parametrize("bad", [
    [[0., 1.], [2., 0.]],
    [[0., -1.], [-1., 0.]],
    [[1., 2.], [2., 0.]],
    [[0., float("inf")], [float("inf"), 0.]],
    np.array([[False, True], [True, False]]),
])
def test_invalid_inputs_rejected(bad):
    with pytest.raises(ValueError):
        positive_edge_graph(bad)


def test_d02_beta_fixed_without_calibration():
    from branch_b.fitters.gradient_descent import (
        GradientDescentFitterConfig, GradientDescentUltrametricFitter,
    )
    fitter = GradientDescentUltrametricFitter()
    assert fitter.config.sigmoid_beta == 5.0
    assert fitter.project_specification()["sigmoid_beta_calibration"] == "none"
    with pytest.raises(ValueError, match="D02"):
        GradientDescentUltrametricFitter(GradientDescentFitterConfig(sigmoid_beta=4.0))
