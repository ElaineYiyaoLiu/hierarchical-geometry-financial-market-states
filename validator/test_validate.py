import hashlib
import json

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("shared_validate", Path(__file__).with_name("validate.py"))
_module = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_module)
collect_errors = _module.collect_errors


def test_manifest_rejects_path_escape(tmp_path):
    schema = {
        "type": "object",
        "properties": {"files": {"type": "array"}},
    }
    record = {
        "files": [{"path": "../outside.bin", "byte_count": 0, "sha256": "0" * 64}]
    }
    errors = collect_errors("manifest", record, schema, base_dir=tmp_path)
    assert any("escapes base directory" in e for e in errors)


def test_branch_b_matrix_dimension_matches_sample_order():
    schema = {"type": "object"}
    record = {
        "status": "complete",
        "sample_order": ["S1", "S2"],
        "dissimilarity_matrix": [[0.0]],
        "recovered_tree": {"leaves": ["S1", "S2"]},
    }
    errors = collect_errors("branch-b", record, schema)
    assert any("dimension must match sample_order" in e for e in errors)
