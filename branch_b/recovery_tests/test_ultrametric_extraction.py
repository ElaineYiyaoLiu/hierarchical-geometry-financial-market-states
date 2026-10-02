from branch_b.serialization import ultrametric_to_tree


def test_equal_height_tie_stays_multifurcating():
    u = [
        [0.0, 1.0, 1.0],
        [1.0, 0.0, 1.0],
        [1.0, 1.0, 0.0],
    ]
    tree = ultrametric_to_tree(u, ["A", "B", "C"])
    root_edges = [e for e in tree["edges"] if e["parent"] == tree["root"]]
    assert len(root_edges) == 3
    assert all(e["unresolved"] for e in root_edges)


def test_zero_distance_pair_preserves_zero_length_unresolved_branches():
    u = [
        [0.0, 0.0, 2.0],
        [0.0, 0.0, 2.0],
        [2.0, 2.0, 0.0],
    ]
    tree = ultrametric_to_tree(u, ["A", "B", "C"])
    zero_edges = [e for e in tree["edges"] if e["branch_length"] == 0.0]
    assert len(zero_edges) >= 2
    assert all(e["unresolved"] for e in zero_edges)
