from branch_b.output import build_complete_result, build_failure_result


def _common_kwargs():
    return {
        "dataset_id": "D",
        "split": "test",
        "geometry_id": "g",
        "common_fitter_id": "f",
        "schema_version": "1",
        "parameters": {"geometry": {}, "common_fitter": {}, "preprocessing": {}},
        "diagnostics": {},
        "runtime_seconds": 0.1,
        "peak_memory_bytes": 1,
        "software_environment": {"python": "3.14"},
        "random_seeds": {},
    }


def test_complete_record_has_complete_status():
    record = build_complete_result(
        **_common_kwargs(),
        sample_order=["A", "B"],
        dissimilarity_matrix=[[0.0, 1.0], [1.0, 0.0]],
        ultrametric_matrix=[[0.0, 1.0], [1.0, 0.0]],
        recovered_tree={
            "tree_format_version": "1",
            "root": "R",
            "internal_nodes": ["R"],
            "leaves": ["A", "B"],
            "edges": [
                {"parent": "R", "child": "A", "branch_length": 1.0},
                {"parent": "R", "child": "B", "branch_length": 1.0},
            ],
        },
        hierarchy_support={"score": 0.0, "decision": "indeterminate"},
        bootstrap_stability=None,
    )
    assert record["status"] == "complete"
    assert record["failure_code"] is None


def test_failure_record_keeps_failure_separate_from_support_decision():
    record = build_failure_result(
        **_common_kwargs(),
        failure_code="NUMERICAL_FIT",
    )
    assert record["status"] == "failure"
    assert record["failure_code"] == "NUMERICAL_FIT"
    assert "hierarchy_support" not in record
