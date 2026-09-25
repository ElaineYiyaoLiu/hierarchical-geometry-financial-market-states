#!/usr/bin/env python3

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


SCHEMAS = {
    "observable": "observable_dataset.schema.json",
    "branch-b": "branch_b_output.schema.json",
    "manifest": "manifest.schema.json",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_matrix(matrix, name, tolerance):
    if matrix is None:
        return []
    if not isinstance(matrix, list) or any(not isinstance(row, list) for row in matrix):
        return [f"{name} must be a matrix"]

    errors = []
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        return [f"{name} must be square"]

    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                errors.append(f"{name}[{i}][{j}] must be finite")
                continue
            if i == j and abs(value) > tolerance:
                errors.append(f"{name} diagonal must be zero")
            if j > i and abs(value - matrix[j][i]) > tolerance:
                errors.append(f"{name} must be symmetric")
    return errors


def validate_branch_b(record, tolerance):
    errors = []
    if record.get("status") == "complete":
        errors.extend(validate_matrix(record.get("dissimilarity_matrix"), "dissimilarity_matrix", tolerance))
        errors.extend(validate_matrix(record.get("ultrametric_matrix"), "ultrametric_matrix", tolerance))

        sample_order = record.get("sample_order") or []
        n = len(sample_order)
        for name in ("dissimilarity_matrix", "ultrametric_matrix"):
            matrix = record.get(name)
            if matrix is not None and len(matrix) != n:
                errors.append(f"{name} dimension must match sample_order")

        tree = record.get("recovered_tree") or {}
        leaves = tree.get("leaves")
        if leaves is not None and set(leaves) != set(sample_order):
            errors.append("recovered_tree leaves must match sample_order")

    return errors


def validate_observable(record, base_dir):
    if base_dir is None:
        return []

    errors = []
    csv_path = base_dir.resolve() / f"{record['dataset_id']}_{record['split']}.csv"
    if not csv_path.is_file():
        return [f"observable CSV not found: {csv_path.name}"]

    if sha256_file(csv_path).lower() != record["file_checksum"].lower():
        errors.append("observable file_checksum mismatch")

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))

    expected_header = ["sample_id"] + list(record["feature_columns"])
    if not rows or rows[0] != expected_header:
        errors.append("observable CSV header mismatch")
        return errors

    data_rows = rows[1:]
    if len(data_rows) != record["row_count"]:
        errors.append("observable row_count mismatch")
    if any(len(row) != 13 for row in data_rows):
        errors.append("observable CSV must contain sample_id plus 12 features")

    sample_ids = [row[0] for row in data_rows if len(row) == 13]
    canonical = (json.dumps(sample_ids, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
    checksum = hashlib.sha256(canonical).hexdigest()
    if checksum.lower() != record["sample_order_checksum"].lower():
        errors.append("sample_order_checksum mismatch")
    if len(sample_ids) != len(set(sample_ids)):
        errors.append("observable sample IDs must be unique")

    for row in data_rows:
        if len(row) != 13:
            continue
        for value in row[1:]:
            try:
                number = float(value)
            except ValueError:
                errors.append("observable feature values must be numeric")
                continue
            if not math.isfinite(number):
                errors.append("observable feature values must be finite")
    return errors


def validate_manifest(record, base_dir):
    if base_dir is None:
        return []

    errors = []
    root = base_dir.resolve()
    for entry in record.get("files", []):
        path = (root / entry["path"]).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            errors.append(f"manifest path escapes base directory: {entry['path']}")
            continue
        if not path.is_file():
            errors.append(f"manifest file not found: {entry['path']}")
            continue
        if path.stat().st_size != entry["byte_count"]:
            errors.append(f"byte count mismatch: {entry['path']}")
        if sha256_file(path).lower() != entry["sha256"].lower():
            errors.append(f"checksum mismatch: {entry['path']}")
    return errors


def collect_errors(kind, record, schema, matrix_tolerance=1e-12, base_dir=None):
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [error.message for error in validator.iter_errors(record)]
    if kind == "branch-b":
        errors.extend(validate_branch_b(record, matrix_tolerance))
    if kind == "observable":
        errors.extend(validate_observable(record, base_dir))
    if kind == "manifest":
        errors.extend(validate_manifest(record, base_dir))
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate a shared project JSON artifact.")
    parser.add_argument("kind", choices=SCHEMAS)
    parser.add_argument("file", type=Path)
    parser.add_argument("--schema-dir", type=Path, default=Path(__file__).resolve().parents[1] / "interface_package")
    parser.add_argument("--matrix-tolerance", type=float, default=1e-12)
    parser.add_argument("--base-dir", type=Path, default=None, help="Resolve and verify files referenced by a manifest.")
    args = parser.parse_args()

    record = load_json(args.file)
    schema = load_json(args.schema_dir / SCHEMAS[args.kind])
    errors = collect_errors(args.kind, record, schema, args.matrix_tolerance, args.base_dir)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    print(f"OK: {args.file}")


if __name__ == "__main__":
    main()
