"""Synthetic transport tests, not support calibration or scientific golden tests."""
from copy import deepcopy
from hashlib import sha256
import json
import platform

import numpy as np
import pytest

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.fitters import FitResult
from branch_b.output.checked import (
    PreparedDevelopmentOutput, complete_record_from_checked_pipeline,
    failure_record_for_development, prepare_development_output,
    validate_development_output, verify_development_output,
)
from branch_b.recovery_pipeline import PipelineConfiguration, RecoveryPipeline

IDENTITY = {"dataset_id": "synthetic_transport", "split": "test",
            "geometry_id": "synthetic_geometry", "common_fitter_id": "synthetic_named",
            "schema_version": "development-test"}
ORDER = ["synthetic_c", "synthetic_a", "synthetic_b"]
CONFIG = b'{"purpose":"synthetic transport only"}\n'
INPUT = b'{"purpose":"synthetic manifest binding only"}\n'
CONFIG_REF = "synthetic/config.json"
REVISION = "a" * 40  # A synthetic expected source identifier, not a claimed commit.


def digest(value):
    return sha256(value).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def tree(order=ORDER):
    return {"tree_format_version": "synthetic-v1", "root": "synthetic_root",
            "internal_nodes": ["synthetic_root"], "leaves": list(order),
            "edges": [{"parent": "synthetic_root", "child": name,
                       "branch_length": 1.0, "unresolved": True} for name in order]}


def context():
    return {"runtime_seconds": 0.0, "peak_memory_bytes": 0,
            "software_environment": {"fixture": "synthetic; not an execution environment"},
            "random_seeds": {"fixture_seed": 20261019},
            "configuration_file": CONFIG_REF,
            "creation_timestamp": "2000-01-01T00:00:00+00:00"}


def result():
    return {"sample_order": ORDER.copy(), "geometry_id": IDENTITY["geometry_id"],
            "common_fitter_id": IDENTITY["common_fitter_id"],
            "geometry_parameters": {"nested": {"fixture": 1}},
            "preprocessing": {"fixture": "identity"},
            "diagnostics": {"nested": {"fixture": 1}},
            "dissimilarity_matrix": np.ones((3, 3)) - np.eye(3),
            "ultrametric_matrix": np.ones((3, 3)) - np.eye(3),
            "recovered_tree": tree(), "result_validation": "structural_checks_only",
            "scientific_authorization": False}


def complete(source=None, **changes):
    kwargs = {"context": context(), "expected_identity": IDENTITY,
              "expected_sample_order": ORDER, "expected_configuration_file": CONFIG_REF,
              "common_fitter_parameters": {"fixture": "stub"},
              "hierarchy_support": {"score": 0.25, "decision": "indeterminate"},
              "bootstrap_stability": None}
    kwargs.update(changes)
    return complete_record_from_checked_pipeline(result() if source is None else source, **kwargs)


def failure(**changes):
    kwargs = {"context": context(), "expected_identity": IDENTITY,
              "expected_configuration_file": CONFIG_REF,
              "parameters": {"geometry": {}, "common_fitter": {}, "preprocessing": {}},
              "diagnostics": {"exception_type": "SyntheticFailure", "stage": "test"},
              "failure_code": "NUMERICAL_FIT"}
    kwargs.update(changes)
    return failure_record_for_development(**kwargs)


def validate(record, **changes):
    kwargs = {"expected_identity": IDENTITY, "expected_sample_order": ORDER,
              "expected_configuration_file": CONFIG_REF}
    kwargs.update(changes)
    return validate_development_output(record, **kwargs)


def prepare(record=None, **changes):
    kwargs = {"expected_identity": IDENTITY, "expected_sample_order": ORDER,
              "expected_configuration_file": CONFIG_REF, "source_revision": REVISION,
              "configuration_bytes": CONFIG, "expected_configuration_sha256": digest(CONFIG),
              "input_manifest_bytes": INPUT, "expected_input_manifest_sha256": digest(INPUT)}
    kwargs.update(changes)
    return prepare_development_output(complete() if record is None else record, **kwargs)


def verify(prepared, **changes):
    kwargs = {"expected_record_sha256": digest(prepared.record_bytes),
              "expected_receipt_sha256": digest(prepared.receipt_bytes),
              "expected_identity": IDENTITY, "expected_sample_order": ORDER,
              "expected_configuration_file": CONFIG_REF,
              "expected_source_revision": REVISION,
              "expected_configuration_sha256": digest(CONFIG),
              "expected_input_manifest_sha256": digest(INPUT)}
    kwargs.update(changes)
    return verify_development_output(prepared, **kwargs)


def test_round_trip_preserves_values_and_records_actual_serializer_environment():
    original = complete()
    prepared = prepare(original)
    assert verify(prepared) == original
    receipt = json.loads(prepared.receipt_bytes)
    assert receipt["scientific_authorization"] is False
    assert receipt["scope"] == "schema_structure_finiteness_only"
    assert receipt["producer_environment"]["python_version"] == platform.python_version()
    assert receipt["record_byte_count"] == len(prepared.record_bytes)
    assert receipt["record_sha256"] == digest(prepared.record_bytes)
    assert original["software_environment"] == context()["software_environment"]
    assert "checksum" not in original


def test_serialization_is_deterministic_without_rewriting_supplied_timestamp():
    record = complete()
    reversed_record = dict(reversed(list(record.items())))
    assert prepare(record) == prepare(reversed_record)
    assert verify(prepare(record))["creation_timestamp"] == context()["creation_timestamp"]


def test_adapter_and_prepared_bytes_are_detached_from_all_input_records():
    source, supplied_context = result(), context()
    parameters = {"nested": {"fixture": 1}}
    support = {"score": 0.25, "decision": "indeterminate"}
    record = complete(source, context=supplied_context, common_fitter_parameters=parameters,
                      hierarchy_support=support)
    prepared = prepare(record)
    original = deepcopy(record)
    source["dissimilarity_matrix"].fill(999)
    source["diagnostics"]["nested"]["fixture"] = 999
    source["geometry_parameters"]["nested"]["fixture"] = 999
    supplied_context["random_seeds"]["fixture_seed"] = 999
    parameters["nested"]["fixture"] = 999
    support["decision"] = "supported"
    assert record == original
    record["diagnostics"].clear()
    decoded = verify(prepared)
    assert decoded == original
    decoded["parameters"].clear()
    assert verify(prepared) == original


@pytest.mark.parametrize("field", ["dataset_id", "split", "geometry_id", "common_fitter_id", "schema_version"])
def test_external_identity_is_checked(field):
    record = complete()
    record[field] = "train" if field == "split" else "different"
    with pytest.raises(BranchBFailure):
        validate(record)


@pytest.mark.parametrize("order", [None, [], ORDER[::-1], ORDER[:-1], ["other", *ORDER[1:]]])
def test_external_order_cannot_be_inferred_from_returned_record(order):
    with pytest.raises(BranchBFailure):
        validate(complete(), expected_sample_order=order)


@pytest.mark.parametrize("mutation", [
    "extra_top_level", "missing_timestamp", "invalid_timestamp", "wrong_configuration",
    "wrong_matrix_size", "nonnumeric_matrix", "matrix_nan", "tree_order", "tree_missing_edge",
    "negative_runtime", "invalid_support_decision", "missing_support", "nonfinite_support",
    "nonfinite_diagnostics", "nonstring_diagnostic_key", "tuple_diagnostics", "numpy_diagnostics",
    "cyclic_diagnostics",
])
def test_transport_rejects_malformed_or_lossy_records(mutation):
    record = complete()
    if mutation == "extra_top_level": record["unexpected"] = True
    elif mutation == "missing_timestamp": del record["creation_timestamp"]
    elif mutation == "invalid_timestamp": record["creation_timestamp"] = "not-a-timestamp"
    elif mutation == "wrong_configuration": record["configuration_file"] = "other.json"
    elif mutation == "wrong_matrix_size": record["ultrametric_matrix"] = [[0.0]]
    elif mutation == "nonnumeric_matrix": record["ultrametric_matrix"][0][1] = "1"
    elif mutation == "matrix_nan": record["ultrametric_matrix"][0][1] = float("nan")
    elif mutation == "tree_order": record["recovered_tree"]["leaves"].reverse()
    elif mutation == "tree_missing_edge": record["recovered_tree"]["edges"].pop()
    elif mutation == "negative_runtime": record["runtime_seconds"] = -1.0
    elif mutation == "invalid_support_decision": record["hierarchy_support"]["decision"] = "unknown"
    elif mutation == "missing_support": del record["hierarchy_support"]
    elif mutation == "nonfinite_support": record["hierarchy_support"]["score"] = float("inf")
    elif mutation == "nonfinite_diagnostics": record["diagnostics"]["bad"] = float("nan")
    elif mutation == "nonstring_diagnostic_key": record["diagnostics"][1] = "value"
    elif mutation == "tuple_diagnostics": record["diagnostics"]["bad"] = (1, 2)
    elif mutation == "numpy_diagnostics": record["diagnostics"]["bad"] = np.int64(1)
    elif mutation == "cyclic_diagnostics": record["diagnostics"]["bad"] = record
    with pytest.raises(BranchBFailure):
        validate(record)


def test_self_checksum_is_not_silently_recomputed_or_dropped():
    record = complete()
    record["checksum"] = "a" * 64
    with pytest.raises(ConfigurationRequired, match="self-checksum"):
        prepare(record)
    assert record["checksum"] == "a" * 64


@pytest.mark.parametrize("code", ["NUMERICAL_FIT", "DEGENERATE_TREE", "TIMEOUT", "OUTPUT_SCHEMA"])
def test_explicit_failures_are_preserved_without_a_support_decision(code):
    record = failure(failure_code=code)
    checked = verify(prepare(record, expected_sample_order=None), expected_sample_order=None)
    assert checked["status"] == "failure" and checked["failure_code"] == code
    assert "hierarchy_support" not in checked and "bootstrap_stability" not in checked
    assert checked["diagnostics"] == record["diagnostics"]


@pytest.mark.parametrize("value", [None, "", 1, False])
def test_failure_code_must_be_supplied_explicitly(value):
    with pytest.raises(BranchBFailure):
        failure(failure_code=value)


@pytest.mark.parametrize("field", ["hierarchy_support", "bootstrap_stability"])
def test_failure_transport_does_not_imply_scientific_support(field):
    record = failure()
    record[field] = {"score": 0.0, "decision": "not supported"} if field == "hierarchy_support" else 0.0
    with pytest.raises(BranchBFailure):
        validate(record, expected_sample_order=None)


@pytest.mark.parametrize("field", ["geometry_id", "common_fitter_id", "sample_order",
                                    "result_validation", "scientific_authorization"])
def test_adapter_rejects_changed_or_unchecked_result_bindings(field):
    source = result()
    source[field] = ORDER[::-1] if field == "sample_order" else "changed"
    with pytest.raises(BranchBFailure):
        complete(source)


def test_bootstrap_attempt_cannot_be_mislabeled_as_a_final_support_record():
    source = result()
    source["bootstrap_draws"] = {"synthetic": True}
    with pytest.raises(ConfigurationRequired, match="bootstrap attempts"):
        complete(source)


@pytest.mark.parametrize("field", ["expected_configuration_sha256", "expected_input_manifest_sha256"])
def test_input_binding_mismatch_is_rejected_before_preparation(field):
    with pytest.raises(BranchBFailure) as caught:
        prepare(**{field: "0" * 64})
    assert caught.value.code == FailureCode.CHECKSUM_MISMATCH


@pytest.mark.parametrize("field,value", [
    ("expected_record_sha256", "0" * 64), ("expected_receipt_sha256", "0" * 64),
    ("expected_configuration_sha256", "0" * 64),
    ("expected_input_manifest_sha256", "0" * 64), ("expected_source_revision", "b" * 40),
])
def test_verifier_requires_external_provenance_not_only_self_consistent_receipt(field, value):
    with pytest.raises(BranchBFailure) as caught:
        verify(prepare(), **{field: value})
    assert caught.value.code == FailureCode.CHECKSUM_MISMATCH


@pytest.mark.parametrize("field,value", [
    ("scientific_authorization", True), ("scientific_authorization", 0),
    ("scope", "certified"), ("record_byte_count", False),
    ("record_byte_count", 1), ("output_schema_sha256", "0" * 64),
    ("configuration_file", "wrong.json"), ("record_creation_timestamp", "2001-01-01T00:00:00Z"),
    ("extra", "not allowed"),
])
def test_self_consistent_receipt_tampering_is_detected(field, value):
    original = prepare()
    receipt = json.loads(original.receipt_bytes)
    receipt[field] = value
    altered = PreparedDevelopmentOutput(original.record_bytes, encoded(receipt))
    with pytest.raises(BranchBFailure):
        verify(altered)


def test_decoding_rejects_duplicate_keys_even_when_external_hash_matches():
    original = prepare()
    payload = original.record_bytes.replace(b'{', b'{"status":"failure",', 1)
    altered = PreparedDevelopmentOutput(payload, original.receipt_bytes)
    with pytest.raises(BranchBFailure, match="duplicate"):
        verify(altered)


def test_verifier_does_not_normalize_different_bytes_into_matching_evidence():
    original = prepare()
    altered = PreparedDevelopmentOutput(b" " + original.record_bytes, original.receipt_bytes)
    with pytest.raises(BranchBFailure, match="canonical"):
        verify(altered)


def test_new_record_bytes_cannot_keep_old_receipt_even_with_a_new_external_payload_hash():
    original = prepare()
    record = json.loads(original.record_bytes)
    record["diagnostics"]["changed"] = True
    altered = PreparedDevelopmentOutput(encoded(record), original.receipt_bytes)
    with pytest.raises(BranchBFailure) as caught:
        verify(altered)
    assert caught.value.code == FailureCode.CHECKSUM_MISMATCH


def test_checked_pipeline_to_schema_record_to_verified_bytes():
    class Identity:
        def transform(self, values): return values.copy()
        def to_record(self): return {"fixture": "identity"}

    class NamedFitter:
        fitter_id = "synthetic_named"
        def fit_with_sample_order(self, dissimilarity, *, sample_order, random_seed=None):
            return FitResult(dissimilarity.copy(), tree(sample_order), {"seed": random_seed})

    pipeline = RecoveryPipeline(
        config=PipelineConfiguration("synthetic_geometry", "synthetic_named"),
        fit_preprocessor=lambda values: Identity(),
        geometry_factory=lambda values, params: np.ones((3, 3)) - np.eye(3),
        geometry_parameter_candidates=lambda values: [{}],
        select_validation_candidate=lambda candidates: 0, fitter=NamedFitter(),
    )
    x = np.zeros((3, 12))
    checked = pipeline.run_checked(x, x, x, validation_sample_order=ORDER,
                                   test_sample_order=ORDER, random_seed=20261019)
    record = complete(checked)
    assert verify(prepare(record)) == record
    assert record["diagnostics"]["seed"] == 20261019
    assert "scientific_authorization" not in record  # Not an added shared-schema field.


def test_record_and_receipt_checksums_are_both_required_to_detect_byte_changes():
    original = prepare()
    altered = PreparedDevelopmentOutput(original.record_bytes + b" ", original.receipt_bytes)
    with pytest.raises(BranchBFailure) as caught:
        verify(altered, expected_record_sha256=digest(original.record_bytes))
    assert caught.value.code == FailureCode.CHECKSUM_MISMATCH
