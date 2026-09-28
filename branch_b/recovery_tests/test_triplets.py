from branch_b.recovery import rooted_triplet_accuracy, rooted_triplet_closest_pair


def _tree():
    return {
        "tree_format_version": "1",
        "root": "R",
        "internal_nodes": ["R", "I"],
        "leaves": ["A", "B", "C"],
        "edges": [
            {"parent": "R", "child": "I", "branch_length": 1.0},
            {"parent": "R", "child": "C", "branch_length": 1.0},
            {"parent": "I", "child": "A", "branch_length": 1.0},
            {"parent": "I", "child": "B", "branch_length": 1.0},
        ],
    }


def test_rooted_triplet_closest_pair():
    assert rooted_triplet_closest_pair(_tree(), ("A", "B", "C")) == ("A", "B")


def test_rooted_triplet_accuracy_exact_match():
    tree = _tree()
    assert rooted_triplet_accuracy(tree, tree, tree["leaves"]) == 1.0
