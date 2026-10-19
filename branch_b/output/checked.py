"""Checked development output transport, without scientific certification.

No files are written and no data sources are opened except the shared schema.
Support values and failure codes must be supplied, never inferred here. The
separate receipt binds bytes; it is not a freeze or permission to disclose them.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from importlib.metadata import version
import json
import math
from pathlib import Path
import platform
import re
import sys

import numpy as np
from jsonschema import Draft202012Validator, FormatChecker

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.recovery_pipeline.result_validation import (
    checked_sample_order, validate_bound_tree, validate_finite_square,
)

IDENTITY_FIELDS = ("dataset_id", "split", "geometry_id", "common_fitter_id", "schema_version")
_CONTEXT_FIELDS = {
    "runtime_seconds", "peak_memory_bytes", "software_environment", "random_seeds",
    "configuration_file", "creation_timestamp",
}
_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "interface_package" / "branch_b_output.schema.json"
_SCOPE = "schema_structure_finiteness_only"


@dataclass(frozen=True)
class PreparedDevelopmentOutput:
    """Immutable payload and detached receipt; neither authorizes submission."""

    record_bytes: bytes
    receipt_bytes: bytes


def _require_python314() -> None:
    if sys.version_info[:2] != (3, 14):
        raise ConfigurationRequired("development output processing requires Python 3.14")


def _schema() -> tuple[dict, str]:
    content = _SCHEMA_PATH.read_bytes()
    return json.loads(content), sha256(content).hexdigest()


def _required_format_checker() -> FormatChecker:
    checker = FormatChecker()
    # jsonschema silently skips formats whose optional dependencies are absent.
    if "date-time" not in checker.checkers:
        raise ConfigurationRequired(
            "date-time validation is unavailable; install branch_b/requirements-output-dev.txt under Python 3.14"
        )
    return checker


def _json_value(value: object, active: set[int]) -> None:
    """Reject lossy key/string conversions, nonfinite values, and cycles."""
    if value is None or isinstance(value, (str, bool)):
        return
    if type(value) is int:
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "output JSON must contain only finite numbers")
        return
    if type(value) not in (dict, list):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "output must contain JSON-native values")
    identity = id(value)
    if identity in active:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "output JSON contains a cycle")
    active.add(identity)
    try:
        if isinstance(value, dict):
            if not all(isinstance(key, str) for key in value):
                raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "output JSON keys must be strings")
            children = value.values()
        else:
            children = value
        for child in children:
            _json_value(child, active)
    finally:
        active.remove(identity)


def _json_bytes(value: object) -> bytes:
    try:
        _json_value(value, set())
        return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
    except (RecursionError, ValueError, TypeError, OverflowError) as exc:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "output is not lossless finite JSON") from exc


def _decode_canonical(content: bytes) -> object:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "duplicate JSON object key")
            result[key] = value
        return result

    def constant(value):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "nonfinite JSON literal")

    try:
        value = json.loads(content.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=constant)
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "invalid output JSON bytes") from exc
    if _json_bytes(value) != content:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "development output bytes are not canonical")
    return value


def _digest(value: object) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-fA-F]{64}", value) is None:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "expected checksum must be SHA-256 hexadecimal")
    return value.lower()


def _revision(value: object) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "source revision must be a full Git commit identifier")
    return value


def _checked_bytes(content: object, expected: str) -> str:
    if type(content) is not bytes:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "artifact content must be immutable bytes")
    actual = sha256(content).hexdigest()
    if actual != _digest(expected):
        raise BranchBFailure(FailureCode.CHECKSUM_MISMATCH, "artifact bytes do not match the external checksum")
    return actual


def _identity(expected: object) -> dict:
    if not isinstance(expected, dict) or set(expected) != set(IDENTITY_FIELDS):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "expected output identity must specify all five identifiers")
    if not all(isinstance(value, str) and value for value in expected.values()):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "expected output identifiers must be non-empty strings")
    if expected["split"] not in {"train", "validation", "test"}:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "invalid expected output split")
    return expected.copy()


def validate_development_output(
    record: object, *, expected_identity: dict,
    expected_sample_order: list[str] | None, expected_configuration_file: str,
) -> None:
    """Apply the unchanged shared schema and exact external bindings.

    This intentionally does not choose matrix or tree numerical tolerances,
    evaluate support decisions, or establish configuration approval.
    """
    expected = _identity(expected_identity)
    if not isinstance(expected_configuration_file, str) or not expected_configuration_file:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "expected configuration reference is required")
    if type(record) is not dict:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "output record must be an object")
    _json_bytes(record)
    schema, _ = _schema()
    validator = Draft202012Validator(schema, format_checker=_required_format_checker())
    if next(validator.iter_errors(record), None) is not None:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "output violates the shared Branch B schema")
    if any(record[key] != value for key, value in expected.items()):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "output identifiers disagree with expected identity")
    if record.get("configuration_file") != expected_configuration_file or "creation_timestamp" not in record:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "output requires its bound configuration reference and timestamp")
    if "checksum" in record:
        raise ConfigurationRequired("use a detached exact-byte checksum; no self-checksum convention is selected here")
    if record["status"] == "complete":
        order = checked_sample_order(expected_sample_order)
        if record["sample_order"] != order:
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "output sample order disagrees with external canonical order")
        validate_finite_square(record["dissimilarity_matrix"], size=len(order))
        if record.get("ultrametric_matrix") is not None:
            validate_finite_square(record["ultrametric_matrix"], size=len(order))
        validate_bound_tree(record["recovered_tree"], sample_order=order)
    elif any(key in record for key in ("hierarchy_support", "bootstrap_stability")):
        # A failed fit is not automatically a support decision, even when the
        # generic shared schema can represent additional partial quantities.
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "failure transport must not imply a support result")


def _base(context: dict, expected_identity: dict) -> dict:
    if not isinstance(context, dict) or set(context) != _CONTEXT_FIELDS:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "context must supply exactly the required runtime and provenance fields")
    return {**_identity(expected_identity), **deepcopy(context)}


def complete_record_from_checked_pipeline(
    result: dict, *, context: dict, expected_identity: dict,
    expected_sample_order: list[str], expected_configuration_file: str,
    common_fitter_parameters: dict, hierarchy_support: dict,
    bootstrap_stability: float | None,
) -> dict:
    """Adapt a full-test checked result; do not manufacture scientific summaries.

    Supply support, stability, fitter configuration, seeds, and execution
    environment from their actual provenance. Development fixtures may supply
    synthetic values. Structural markers are checked but are not certificates.
    """
    record = _base(context, expected_identity)
    if record["split"] != "test":
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "the recovery pipeline returns a test-split result")
    source = deepcopy(result)
    required = {"sample_order", "geometry_id", "common_fitter_id", "geometry_parameters",
                "preprocessing", "diagnostics", "dissimilarity_matrix", "ultrametric_matrix",
                "recovered_tree", "result_validation", "scientific_authorization"}
    if not isinstance(source, dict) or not required.issubset(source):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "checked pipeline result is incomplete")
    if source["result_validation"] != "structural_checks_only" or source["scientific_authorization"] is not False:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "expected a structural-only development result")
    if "bootstrap_identity" in source or "bootstrap_draws" in source:
        raise ConfigurationRequired("individual bootstrap attempts are not final dataset support outputs")
    for key in ("geometry_id", "common_fitter_id"):
        if source[key] != record[key]:
            raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "checked result identity differs from output context")
    order = checked_sample_order(expected_sample_order)
    if source["sample_order"] != order:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "checked result sample order differs from output context")
    for key in ("dissimilarity_matrix", "ultrametric_matrix"):
        validate_finite_square(source[key], size=len(order))
        record[key] = np.asarray(source[key]).tolist()
    record.update({
        "sample_order": order, "recovered_tree": source["recovered_tree"],
        "diagnostics": source["diagnostics"],
        "parameters": {"geometry": source["geometry_parameters"],
                       "preprocessing": source["preprocessing"],
                       "common_fitter": deepcopy(common_fitter_parameters)},
        "hierarchy_support": deepcopy(hierarchy_support),
        "bootstrap_stability": bootstrap_stability,
        "status": "complete", "failure_code": None,
    })
    validate_development_output(record, expected_identity=expected_identity,
                                expected_sample_order=order,
                                expected_configuration_file=expected_configuration_file)
    return record


def failure_record_for_development(
    *, context: dict, expected_identity: dict, expected_configuration_file: str,
    parameters: dict, diagnostics: dict, failure_code: str,
) -> dict:
    """Preserve an explicitly supplied failure; never assign a support decision."""
    record = _base(context, expected_identity)
    record.update({"parameters": deepcopy(parameters), "diagnostics": deepcopy(diagnostics),
                   "status": "failure", "failure_code": failure_code})
    validate_development_output(record, expected_identity=expected_identity,
                                expected_sample_order=None,
                                expected_configuration_file=expected_configuration_file)
    return record


def prepare_development_output(
    record: dict, *, expected_identity: dict, expected_sample_order: list[str] | None,
    expected_configuration_file: str, source_revision: str,
    configuration_bytes: bytes, expected_configuration_sha256: str,
    input_manifest_bytes: bytes, expected_input_manifest_sha256: str,
) -> PreparedDevelopmentOutput:
    """Freeze development transport bytes and their independently checkable receipt.

    Input/configuration hashes verify the supplied external bindings, not that
    their contents are authorized or scientifically consistent. No filesystem
    path supplied in the record or those bytes is followed.
    """
    _require_python314()
    config_hash = _checked_bytes(configuration_bytes, expected_configuration_sha256)
    input_hash = _checked_bytes(input_manifest_bytes, expected_input_manifest_sha256)
    source = _revision(source_revision)
    snapshot = deepcopy(record)
    validate_development_output(snapshot, expected_identity=expected_identity,
                                expected_sample_order=expected_sample_order,
                                expected_configuration_file=expected_configuration_file)
    payload = _json_bytes(snapshot)
    _, schema_hash = _schema()
    receipt = {
        "receipt_version": "branch-b-development-output-v1",
        "scope": _SCOPE, "scientific_authorization": False,
        "identity": _identity(expected_identity), "source_revision": source,
        "configuration_file": expected_configuration_file,
        "configuration_sha256": config_hash, "input_manifest_sha256": input_hash,
        "output_schema_sha256": schema_hash,
        "record_sha256": sha256(payload).hexdigest(), "record_byte_count": len(payload),
        "record_creation_timestamp": snapshot["creation_timestamp"],
        "producer_environment": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "numpy_version": version("numpy"), "jsonschema_version": version("jsonschema"),
            "rfc3339_validator_version": version("rfc3339-validator"),
        },
    }
    return PreparedDevelopmentOutput(payload, _json_bytes(receipt))


def verify_development_output(
    prepared: PreparedDevelopmentOutput, *, expected_record_sha256: str,
    expected_receipt_sha256: str, expected_identity: dict,
    expected_sample_order: list[str] | None, expected_configuration_file: str,
    expected_source_revision: str, expected_configuration_sha256: str,
    expected_input_manifest_sha256: str,
) -> dict:
    """Verify externally anchored bytes, then recheck schema and identity.

    Return a detached decoded record, not scientific authorization. Receipt
    environment fields describe the producer; they are not overwritten with
    the verifier's environment and are not independent proof of execution.
    """
    _require_python314()
    if not isinstance(prepared, PreparedDevelopmentOutput):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "expected prepared development output")
    record_hash = _checked_bytes(prepared.record_bytes, expected_record_sha256)
    _checked_bytes(prepared.receipt_bytes, expected_receipt_sha256)
    record = _decode_canonical(prepared.record_bytes)
    receipt = _decode_canonical(prepared.receipt_bytes)
    validate_development_output(record, expected_identity=expected_identity,
                                expected_sample_order=expected_sample_order,
                                expected_configuration_file=expected_configuration_file)
    _, schema_hash = _schema()
    expected = {
        "receipt_version": "branch-b-development-output-v1",
        "scope": _SCOPE, "scientific_authorization": False,
        "identity": _identity(expected_identity),
        "source_revision": _revision(expected_source_revision),
        "configuration_file": expected_configuration_file,
        "configuration_sha256": _digest(expected_configuration_sha256),
        "input_manifest_sha256": _digest(expected_input_manifest_sha256),
        "output_schema_sha256": schema_hash, "record_sha256": record_hash,
        "record_byte_count": len(prepared.record_bytes),
        "record_creation_timestamp": record["creation_timestamp"],
    }
    if type(receipt) is not dict or set(receipt) != set(expected) | {"producer_environment"}:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "invalid development output receipt")
    if receipt["scientific_authorization"] is not False or type(receipt["record_byte_count"]) is not int:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "invalid receipt scope or size")
    if any(receipt[key] != value for key, value in expected.items()):
        raise BranchBFailure(FailureCode.CHECKSUM_MISMATCH, "receipt differs from external provenance or record bytes")
    environment = receipt["producer_environment"]
    keys = {"python_implementation", "python_version", "numpy_version", "jsonschema_version",
            "rfc3339_validator_version"}
    if (type(environment) is not dict or set(environment) != keys
            or not all(isinstance(value, str) and value for value in environment.values())
            or not re.fullmatch(r"3\.14\.\d+(?:[a-zA-Z0-9.+-]*)", environment["python_version"])):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "receipt must describe its actual Python 3.14 producer")
    return record
