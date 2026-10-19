"""Observable-only development input validation over explicitly supplied bytes.

No filenames, directories, banks, or manifest paths are opened. Hash matches
establish byte bindings, not release authorization or scientific eligibility.
The caller must obtain permitted input and trusted expectations independently.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from hashlib import sha256
import io
import json
from pathlib import Path

import numpy as np
from jsonschema import Draft202012Validator

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.output.checked import _checked_bytes, _json_bytes, _require_python314
from branch_b.recovery_pipeline.result_validation import checked_sample_order

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "interface_package" / "observable_dataset.schema.json"


@dataclass(frozen=True)
class LoadedDevelopmentObservable:
    """Detached values and immutable identity/provenance fields.

    The array is read-only against accidental writes, not a security sandbox.
    Use copies for callbacks; do not mutate values separately from their IDs.
    """

    values: np.ndarray
    sample_order: tuple[str, ...]
    manifest_bytes: bytes
    manifest_sha256: str
    csv_sha256: str
    schema_sha256: str
    validation_scope: str = "observable_schema_identity_finiteness_only"
    scientific_authorization: bool = False

    def manifest_record(self) -> dict:
        return json.loads(self.manifest_bytes)


def _manifest(content: bytes) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise BranchBFailure(FailureCode.INPUT_SCHEMA, "observable manifest contains a duplicate field")
            result[key] = value
        return result

    def constant(value):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "observable manifest contains a nonfinite literal")

    try:
        record = json.loads(content.decode("utf-8"), object_pairs_hook=pairs,
                            parse_constant=constant)
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "observable manifest is not valid UTF-8 JSON") from exc
    if type(record) is not dict:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "observable manifest must be an object")
    return record


def load_development_observable(
    *, csv_bytes: bytes, manifest_bytes: bytes,
    expected_csv_sha256: str, expected_manifest_sha256: str,
    expected_dataset_id: str, expected_split: str, expected_schema_version: str,
) -> LoadedDevelopmentObservable:
    """Verify manifest/CSV hashes, exact header, identities, dimensions and values.

    Rows are not sorted, deduplicated, standardized, repaired, or filtered.
    The sample-order hash uses the shared validator's existing JSON recipe.
    This loader does not decide correlation admissibility or any method gate.
    """
    _require_python314()
    manifest_hash = _checked_bytes(manifest_bytes, expected_manifest_sha256)
    csv_hash = _checked_bytes(csv_bytes, expected_csv_sha256)
    record = _manifest(manifest_bytes)
    schema_bytes = _SCHEMA_PATH.read_bytes()
    schema = json.loads(schema_bytes)
    if next(Draft202012Validator(schema).iter_errors(record), None) is not None:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "observable manifest violates the shared schema")
    expected = {"dataset_id": expected_dataset_id, "split": expected_split,
                "schema_version": expected_schema_version}
    if not all(isinstance(value, str) and value for value in expected.values()):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "expected observable identity fields are required")
    if any(record[key] != value for key, value in expected.items()):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "observable identity differs from external expectations")
    if record["file_checksum"] != csv_hash:
        raise BranchBFailure(FailureCode.CHECKSUM_MISMATCH, "CSV checksum differs from the bound observable manifest")
    try:
        text = csv_bytes.decode("utf-8")
        rows = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    except (UnicodeError, csv.Error) as exc:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "observable CSV is malformed UTF-8 data") from exc
    if not rows or rows[0] != ["sample_id", *record["feature_columns"]]:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "observable CSV header differs from the manifest")
    data = rows[1:]
    if len(data) != record["row_count"] or any(len(row) != 13 for row in data):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "observable CSV dimensions differ from the manifest")
    order = checked_sample_order([row[0] for row in data], size=len(data))
    if sha256(_json_bytes(order)).hexdigest() != record["sample_order_checksum"]:
        raise BranchBFailure(FailureCode.CHECKSUM_MISMATCH, "observable row identities differ from the sample-order checksum")
    try:
        values = np.array([[float(value) for value in row[1:]] for row in data], dtype=float)
    except (ValueError, TypeError, OverflowError) as exc:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "observable feature values must be numeric") from exc
    if not np.isfinite(values).all():
        raise BranchBFailure(FailureCode.NONFINITE_INPUT, "observable feature values must be finite")
    values.setflags(write=False)
    return LoadedDevelopmentObservable(
        values=values, sample_order=tuple(order), manifest_bytes=manifest_bytes,
        manifest_sha256=manifest_hash, csv_sha256=csv_hash,
        schema_sha256=sha256(schema_bytes).hexdigest(),
    )
