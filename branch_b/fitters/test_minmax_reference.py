"""Synthetic forward min-max operator tests; optimizer not executed."""
import numpy as np
import pytest

from branch_b.fitters.positive_edge_graph import positive_edge_graph
from branch_b.fitters.minmax_reference import minmax_ultrametric


def test_minmax_paths_choose_smallest_bottleneck():
    graph = positive_edge_graph(np.array([
        [0., 1., 4.],
        [1., 0., 2.],
        [4., 2., 0.],
    ]))
    values = minmax_ultrametric(graph, graph.weights)
    np.testing.assert_array_equal(values, np.array([
        [0., 1., 2.],
        [1., 0., 2.],
        [2., 2., 0.],
    ]))


def test_transform_accepts_zero_working_weights_without_input_mutation():
    graph = positive_edge_graph(np.array([[0., 2., 3.], [2., 0., 4.], [3., 4., 0.]]))
    working = np.array([0., 1., 3.])
    before = working.copy()
    values = minmax_ultrametric(graph, working)
    np.testing.assert_array_equal(values, np.array([[0., 0., 1.], [0., 0., 1.], [1., 1., 0.]]))
    np.testing.assert_array_equal(working, before)


def test_disconnected_graph_is_not_filled_with_infinities():
    graph = positive_edge_graph(np.zeros((3, 3)))
    with pytest.raises(ValueError, match="connected"):
        minmax_ultrametric(graph, graph.weights)


@pytest.mark.parametrize("weight", [[-1., 2., 3.], [float("inf"), 2., 3.], [1., 2.]])
def test_invalid_working_weights_rejected(weight):
    graph = positive_edge_graph(np.array([[0., 1., 2.], [1., 0., 3.], [2., 3., 0.]]))
    with pytest.raises(ValueError):
        minmax_ultrametric(graph, weight)
