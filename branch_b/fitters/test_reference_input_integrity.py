"""Reject input types whose meaning would be lost during NumPy coercion."""
import numpy as np
import pytest

from branch_b.fitters.positive_edge_graph import positive_edge_graph
from branch_b.fitters.minmax_reference import minmax_ultrametric


@pytest.mark.parametrize("bad", [
    [[0.0, True], [True, 0.0]],
    [np.array([False, True]), np.array([True, False])],
    np.ma.array([[0.0, 1.0], [1.0, 0.0]], mask=False),
    [np.ma.array([0.0, 1.0], mask=[False, True]), [1.0, 0.0]],
])
def test_graph_rejects_lossy_inputs_before_coercion(bad):
    with pytest.raises(ValueError, match="Boolean|masked"):
        positive_edge_graph(bad)


@pytest.mark.parametrize("bad", [
    [True, 2.0, 3.0],
    np.ma.array([1.0, 2.0, 3.0], mask=False),
    [np.ma.masked, 2.0, 3.0],
])
def test_minmax_rejects_lossy_working_weights_before_coercion(bad):
    graph = positive_edge_graph([[0.0, 1.0, 2.0], [1.0, 0.0, 3.0], [2.0, 3.0, 0.0]])
    with pytest.raises(ValueError, match="Boolean|masked"):
        minmax_ultrametric(graph, bad)
