import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("project_validator", ROOT / "validator" / "validate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def load(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def errors(kind, schema_name, filename, base_dir=None):
    schema = load(ROOT / "interface_package" / schema_name)
    record = load(ROOT / "golden_cases" / filename)
    return MODULE.collect_errors(kind, record, schema, base_dir=base_dir)


def branch_b_errors(filename):
    return errors("branch-b", "branch_b_output.schema.json", filename)


def observable_errors(filename):
    return errors("observable", "observable_dataset.schema.json", filename)


def test_valid_branch_b_output_passes():
    assert branch_b_errors("valid/branch_b_output.json") == []


def test_failure_output_passes_without_scientific_result():
    assert branch_b_errors("valid/branch_b_failure.json") == []


def test_valid_observable_manifest_passes():
    assert observable_errors("valid/observable_dataset.json") == []


def test_asymmetric_matrix_fails():
    assert any("symmetric" in error for error in branch_b_errors("invalid/asymmetric_matrix.json"))


def test_nonzero_diagonal_fails():
    assert any("diagonal" in error for error in branch_b_errors("invalid/nonzero_diagonal.json"))


def test_nonfinite_matrix_fails():
    assert any("finite" in error for error in branch_b_errors("invalid/nonfinite_matrix.json"))


def test_invalid_tree_leaves_fail():
    assert any("leaves" in error for error in branch_b_errors("invalid/invalid_tree_leaves.json"))


def test_missing_observable_feature_fails():
    assert observable_errors("invalid/observable_missing_feature.json")


def manifest_record(path, byte_count, sha256):
    return {
        "manifest_version": "0.1",
        "dataset_id": "pilot_dataset_001",
        "schema_version": "0.1",
        "sample_order": ["s001", "s002", "s003"],
        "files": [{"path": path, "byte_count": byte_count, "sha256": sha256}],
    }


def manifest_errors(record, base_dir):
    schema = load(ROOT / "interface_package" / "manifest.schema.json")
    return MODULE.collect_errors("manifest", record, schema, base_dir=base_dir)


def test_manifest_file_and_checksum_pass():
    base_dir = ROOT / "golden_cases"
    payload = base_dir / "manifest_payload.txt"
    record = manifest_record("manifest_payload.txt", payload.stat().st_size, MODULE.sha256_file(payload))
    assert manifest_errors(record, base_dir) == []


def test_manifest_missing_file_fails():
    record = manifest_record("missing.txt", 0, "0" * 64)
    assert any("not found" in error for error in manifest_errors(record, ROOT / "golden_cases"))


def test_manifest_bad_checksum_fails():
    base_dir = ROOT / "golden_cases"
    payload = base_dir / "manifest_payload.txt"
    record = manifest_record("manifest_payload.txt", payload.stat().st_size, "0" * 64)
    assert any("checksum mismatch" in error for error in manifest_errors(record, base_dir))


def test_manifest_duplicate_sample_id_fails():
    schema = load(ROOT / "interface_package" / "manifest.schema.json")
    record = manifest_record("manifest_payload.txt", 0, "0" * 64)
    record["sample_order"] = ["s001", "s001"]
    assert MODULE.collect_errors("manifest", record, schema)



def test_observable_csv_consistency_checks(tmp_path):
    dataset_id = "D0123456789ABCDEF"
    sample_ids = ["S00000000000000000001", "S00000000000000000002"]
    header = ["sample_id", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "15Y", "20Y", "30Y", "AUX"]
    lines = [",".join(header)]
    lines.extend(",".join([sid] + ["0.5"] * 12) for sid in sample_ids)
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    csv_path = tmp_path / f"{dataset_id}_train.csv"
    csv_path.write_bytes(payload)

    canonical = (json.dumps(sample_ids, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
    import hashlib
    record = {
        "dataset_id": dataset_id,
        "split": "train",
        "feature_columns": header[1:],
        "aux_feature_type": "liquidity",
        "feature_units": ["unit"] * 12,
        "feature_order_version": "pilot-v1",
        "schema_version": "pilot-v1",
        "row_count": 2,
        "column_count": 12,
        "sample_order_checksum": hashlib.sha256(canonical).hexdigest(),
        "file_checksum": hashlib.sha256(payload).hexdigest(),
    }
    schema = load(ROOT / "interface_package" / "observable_dataset.schema.json")
    assert MODULE.collect_errors("observable", record, schema, base_dir=tmp_path) == []

    record["row_count"] = 3
    assert any("row_count mismatch" in e for e in MODULE.collect_errors("observable", record, schema, base_dir=tmp_path))
