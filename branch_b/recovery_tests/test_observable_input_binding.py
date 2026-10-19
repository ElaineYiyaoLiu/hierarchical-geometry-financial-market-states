"""Synthetic observable interface and end-to-end transport tests, Python 3.14."""
from copy import deepcopy
import csv
from hashlib import sha256
import io
import json

import numpy as np
import pytest

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.fitters import FitResult
from branch_b.observable_input import load_development_observable
from branch_b.output.checked import complete_record_from_checked_pipeline
from branch_b.recovery_pipeline import PipelineConfiguration, RecoveryPipeline
from branch_b.recovery_tests.test_checked_output_transport import (
    CONFIG_REF, context, prepare, verify,
)

FEATURES = ["3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "15Y", "20Y", "30Y", "AUX"]
DATASET = "D0000000000000001"  # Synthetic schema fixture, not a released dataset.
ORDER = ["synthetic_row_c", "synthetic_row_a", "synthetic_row_b"]


def digest(value):
    return sha256(value).hexdigest()


def encoded(record):
    return (json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def csv_bytes(rows):
    text = io.StringIO(newline="")
    writer = csv.writer(text, lineterminator="\n")
    writer.writerows(rows)
    return text.getvalue().encode()


def rows():
    return [["sample_id", *FEATURES],
            *[[name, *[str(100 * index + column) for column in range(12)]]
              for index, name in enumerate(ORDER)]]


def fixture(*, data_rows=None, manifest_updates=None, split="test"):
    content = csv_bytes(rows() if data_rows is None else data_rows)
    manifest = {
        "dataset_id": DATASET, "split": split, "feature_columns": FEATURES.copy(),
        "aux_feature_type": "volatility", "feature_units": ["synthetic_units"] * 12,
        "feature_order_version": "synthetic-v1", "schema_version": "synthetic-v1",
        "row_count": 3, "column_count": 12,
        "sample_order_checksum": digest(encoded(ORDER)), "file_checksum": digest(content),
    }
    manifest.update({} if manifest_updates is None else manifest_updates)
    manifest_content = encoded(manifest)
    return {
        "csv_bytes": content, "manifest_bytes": manifest_content,
        "expected_csv_sha256": digest(content),
        "expected_manifest_sha256": digest(manifest_content),
        "expected_dataset_id": DATASET, "expected_split": split,
        "expected_schema_version": "synthetic-v1",
    }


def test_loader_preserves_all_rows_columns_values_and_original_order():
    supplied = fixture()
    saved = deepcopy(supplied)
    loaded = load_development_observable(**supplied)
    assert loaded.sample_order == tuple(ORDER)
    np.testing.assert_array_equal(loaded.values,
                                  [[100 * index + column for column in range(12)] for index in range(3)])
    assert not loaded.values.flags.writeable
    assert loaded.csv_sha256 == digest(supplied["csv_bytes"])
    assert loaded.manifest_sha256 == digest(supplied["manifest_bytes"])
    assert loaded.manifest_bytes == supplied["manifest_bytes"]
    assert loaded.scientific_authorization is False
    assert supplied == saved
    copy = loaded.manifest_record()
    copy["feature_columns"].clear()
    assert loaded.manifest_record()["feature_columns"] == FEATURES


@pytest.mark.parametrize("field", ["expected_csv_sha256", "expected_manifest_sha256"])
def test_external_checksums_are_required_before_processing(field):
    supplied = fixture()
    supplied[field] = "0" * 64
    with pytest.raises(BranchBFailure) as caught:
        load_development_observable(**supplied)
    assert caught.value.code == FailureCode.CHECKSUM_MISMATCH


@pytest.mark.parametrize("updates", [
    {"row_count": 4}, {"column_count": 11}, {"feature_columns": FEATURES[::-1]},
    {"extra_field": True}, {"dataset_id": "D0000000000000002"},
    {"split": "validation"}, {"schema_version": "different"},
])
def test_manifest_schema_dimensions_and_external_identity_are_enforced(updates):
    with pytest.raises(BranchBFailure) as caught:
        load_development_observable(**fixture(manifest_updates=updates))
    assert caught.value.code == FailureCode.INPUT_SCHEMA


@pytest.mark.parametrize("field", ["file_checksum", "sample_order_checksum"])
def test_matching_external_manifest_hash_does_not_override_wrong_internal_binding(field):
    with pytest.raises(BranchBFailure) as caught:
        load_development_observable(**fixture(manifest_updates={field: "0" * 64}))
    assert caught.value.code == FailureCode.CHECKSUM_MISMATCH


@pytest.mark.parametrize("mutation", ["wrong_header", "short_row", "long_row", "missing_row", "extra_row",
                                      "duplicate_id", "empty_id", "not_numeric"])
def test_csv_structure_and_id_contracts_are_not_repaired(mutation):
    data = rows()
    if mutation == "wrong_header": data[0][1:3] = data[0][1:3][::-1]
    elif mutation == "short_row": data[1].pop()
    elif mutation == "long_row": data[1].append("13")
    elif mutation == "missing_row": data.pop()
    elif mutation == "extra_row": data.append(data[1].copy())
    elif mutation == "duplicate_id": data[2][0] = data[1][0]
    elif mutation == "empty_id": data[1][0] = ""
    elif mutation == "not_numeric": data[1][1] = "not-a-number"
    supplied = fixture(data_rows=data)
    saved = deepcopy(supplied)
    with pytest.raises(BranchBFailure):
        load_development_observable(**supplied)
    assert supplied == saved


@pytest.mark.parametrize("value", ["nan", "inf", "-inf", "1e9999"])
def test_nonfinite_feature_values_have_the_existing_failure_code(value):
    data = rows()
    data[1][1] = value
    with pytest.raises(BranchBFailure) as caught:
        load_development_observable(**fixture(data_rows=data))
    assert caught.value.code == FailureCode.NONFINITE_INPUT


def test_reordered_rows_fail_the_original_sample_order_binding():
    data = rows()
    data[1:] = data[1:][::-1]
    with pytest.raises(BranchBFailure) as caught:
        load_development_observable(**fixture(data_rows=data))
    assert caught.value.code == FailureCode.CHECKSUM_MISMATCH


def test_approved_external_order_is_preserved_not_sorted():
    data = rows()
    data[1:] = data[1:][::-1]
    supplied = fixture(data_rows=data,
                       manifest_updates={"sample_order_checksum": digest(encoded(ORDER[::-1]))})
    loaded = load_development_observable(**supplied)
    assert loaded.sample_order == tuple(ORDER[::-1])
    np.testing.assert_array_equal(loaded.values[:, 0], [200, 100, 0])


def test_duplicate_manifest_fields_are_rejected_even_with_matching_digest():
    supplied = fixture()
    supplied["manifest_bytes"] = supplied["manifest_bytes"].replace(b'{', b'{"split":"train",', 1)
    supplied["expected_manifest_sha256"] = digest(supplied["manifest_bytes"])
    with pytest.raises(BranchBFailure, match="duplicate"):
        load_development_observable(**supplied)


@pytest.mark.parametrize("content", [b"\xff", b'{"row_count":NaN}', b"[]", b"null"])
def test_malformed_manifest_is_a_structured_input_failure(content):
    supplied = fixture()
    supplied["manifest_bytes"] = content
    supplied["expected_manifest_sha256"] = digest(content)
    with pytest.raises(BranchBFailure) as caught:
        load_development_observable(**supplied)
    assert caught.value.code == FailureCode.INPUT_SCHEMA


@pytest.mark.parametrize("content", [b"\xff", b'"unterminated'])
def test_malformed_csv_is_rejected_without_following_any_path(content):
    supplied = fixture(manifest_updates={"file_checksum": digest(content)})
    supplied["csv_bytes"] = content
    supplied["expected_csv_sha256"] = digest(content)
    with pytest.raises(BranchBFailure) as caught:
        load_development_observable(**supplied)
    assert caught.value.code == FailureCode.INPUT_SCHEMA


def test_csv_manifest_pipeline_record_and_receipt_bind_the_same_sample_order():
    loaded = {split: load_development_observable(**fixture(split=split))
              for split in ("train", "validation", "test")}

    class Identity:
        def transform(self, values): return values.copy()
        def to_record(self): return {"fixture": "identity"}

    class NamedFitter:
        fitter_id = "synthetic_named"
        def fit_with_sample_order(self, dissimilarity, *, sample_order, random_seed=None):
            tree = {"tree_format_version": "synthetic-v1", "root": "root",
                    "internal_nodes": ["root"], "leaves": sample_order.copy(),
                    "edges": [{"parent": "root", "child": name,
                               "branch_length": 1.0, "unresolved": True} for name in sample_order]}
            return FitResult(dissimilarity.copy(), tree, {"fixture": "stub, not a scientific fit"})

    pipeline = RecoveryPipeline(
        config=PipelineConfiguration("synthetic_geometry", "synthetic_named"),
        fit_preprocessor=lambda values: Identity(),
        geometry_factory=lambda values, params: np.ones((3, 3)) - np.eye(3),
        geometry_parameter_candidates=lambda values: [{}],
        select_validation_candidate=lambda candidates: 0, fitter=NamedFitter(),
    )
    checked = pipeline.run_checked(
        loaded["train"].values, loaded["validation"].values, loaded["test"].values,
        validation_sample_order=list(loaded["validation"].sample_order),
        test_sample_order=list(loaded["test"].sample_order),
    )
    identity = {"dataset_id": DATASET, "split": "test", "schema_version": "synthetic-v1",
                "geometry_id": "synthetic_geometry", "common_fitter_id": "synthetic_named"}
    record = complete_record_from_checked_pipeline(
        checked, context=context(), expected_identity=identity,
        expected_sample_order=ORDER, expected_configuration_file=CONFIG_REF,
        common_fitter_parameters={"fixture": "stub"},
        hierarchy_support={"score": 0.25, "decision": "indeterminate"},
        bootstrap_stability=None,
    )
    prepared = prepare(record, expected_identity=identity, expected_sample_order=ORDER,
                       input_manifest_bytes=loaded["test"].manifest_bytes,
                       expected_input_manifest_sha256=loaded["test"].manifest_sha256)
    decoded = verify(prepared, expected_identity=identity, expected_sample_order=ORDER,
                     expected_input_manifest_sha256=loaded["test"].manifest_sha256)
    assert decoded["sample_order"] == list(loaded["test"].sample_order)
    assert decoded["recovered_tree"]["leaves"] == decoded["sample_order"]
    assert decoded["parameters"]["preprocessing"] == {"fixture": "identity"}
