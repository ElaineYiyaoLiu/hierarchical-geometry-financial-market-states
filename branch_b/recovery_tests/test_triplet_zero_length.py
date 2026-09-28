from branch_b.recovery import rooted_triplet_closest_pair


def test_zero_length_internal_edge_makes_triplet_unresolved():
    tree = {
        "tree_format_version": "1",
        "root": "R",
        "internal_nodes": ["R", "I"],
        "leaves": ["A", "B", "C"],
        "edges": [
            {"parent": "R", "child": "I", "branch_length": 0.0},
            {"parent": "R", "child": "C", "branch_length": 1.0},
            {"parent": "I", "child": "A", "branch_length": 1.0},
            {"parent": "I", "child": "B", "branch_length": 1.0},
        ],
    }
    assert rooted_triplet_closest_pair(tree, ("A", "B", "C")) is None


def test_explicit_unresolved_internal_edge_makes_triplet_unresolved():
    tree = {
        "tree_format_version": "1",
        "root": "R",
        "internal_nodes": ["R", "I"],
        "leaves": ["A", "B", "C"],
        "edges": [
            {"parent": "R", "child": "I", "branch_length": 2.0, "unresolved": True},
            {"parent": "R", "child": "C", "branch_length": 1.0},
            {"parent": "I", "child": "A", "branch_length": 1.0},
            {"parent": "I", "child": "B", "branch_length": 1.0},
        ],
    }
    assert rooted_triplet_closest_pair(tree, ("A", "B", "C")) is None
