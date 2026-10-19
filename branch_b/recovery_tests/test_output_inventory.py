"""Synthetic output-accounting and timestamp regressions under Python 3.14."""
from copy import deepcopy
from types import SimpleNamespace

import pytest

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.output import checked
from branch_b.output.inventory import reconcile_development_inventory
from branch_b.recovery_tests.test_checked_output_transport import (
    IDENTITY, ORDER, CONFIG, INPUT, CONFIG_REF, REVISION,
    complete, failure, digest, prepare, validate,
)


def identity(name):
    return {**IDENTITY, "dataset_id": name}


def item(name="synthetic_first", *, failed=False):
    expected = identity(name)
    record = failure(expected_identity=expected) if failed else complete(expected_identity=expected)
    prepared = prepare(record, expected_identity=expected,
                       expected_sample_order=None if failed else ORDER)
    expectations = {
        "expected_record_sha256": digest(prepared.record_bytes),
        "expected_receipt_sha256": digest(prepared.receipt_bytes),
        "expected_identity": expected, "expected_sample_order": None if failed else ORDER.copy(),
        "expected_configuration_file": CONFIG_REF, "expected_source_revision": REVISION,
        "expected_configuration_sha256": digest(CONFIG),
        "expected_input_manifest_sha256": digest(INPUT),
    }
    return prepared, expectations


def test_documented_failure_is_accounted_for_but_never_turned_into_support():
    plan = [identity("synthetic_first"), identity("synthetic_second")]
    report = reconcile_development_inventory(
        planned_identities=plan,
        outputs=[item(), item("synthetic_second", failed=True)],
    )
    assert report["inventory_matches_plan"] is True
    assert report["schema_complete_records"] == 1
    assert report["failure_records"] == 1
    assert report["entries"][1]["failure_code"] == "NUMERICAL_FIT"
    assert report["scientific_authorization"] is False
    assert report["scope"] == "verified_transport_accounting_only"
    assert "hierarchy_support" not in report["entries"][1]


def test_missing_unexpected_and_duplicate_outputs_are_all_reported():
    plan = [identity("synthetic_first"), identity("synthetic_missing")]
    report = reconcile_development_inventory(
        planned_identities=plan,
        outputs=[item(), item(failed=True), item("synthetic_unexpected")],
    )
    assert report["inventory_matches_plan"] is False
    assert report["planned_count"] == 2 and report["observed_count"] == 3
    assert report["missing"] == [identity("synthetic_missing")]
    assert report["duplicates"] == [{"identity": identity("synthetic_first"), "positions": [0, 1]}]
    assert report["unexpected"] == [{"identity": identity("synthetic_unexpected"), "position": 2}]
    assert len(report["entries"]) == 3  # No dropping, deduplication, or replacement.


def test_no_received_output_reports_the_entire_missing_plan():
    plan = [identity("synthetic_first")]
    report = reconcile_development_inventory(planned_identities=plan, outputs=[])
    assert report["missing"] == plan
    assert report["observed_count"] == report["failure_records"] == 0
    assert report["inventory_matches_plan"] is False


def test_all_failures_can_match_inventory_without_claiming_scientific_success():
    report = reconcile_development_inventory(
        planned_identities=[identity("synthetic_first")], outputs=[item(failed=True)],
    )
    assert report["inventory_matches_plan"] is True
    assert report["schema_complete_records"] == 0 and report["failure_records"] == 1
    assert report["scientific_authorization"] is False


@pytest.mark.parametrize("plan", [None, [], [IDENTITY, IDENTITY], [{}]])
def test_plan_must_be_explicit_unique_complete_identities(plan):
    with pytest.raises(BranchBFailure) as caught:
        reconcile_development_inventory(planned_identities=plan, outputs=[])
    assert caught.value.code == FailureCode.INPUT_SCHEMA


@pytest.mark.parametrize("outputs", [None, {}, [None], [(None, {})]])
def test_inventory_requires_prepared_outputs_and_all_external_expectations(outputs):
    with pytest.raises(BranchBFailure):
        reconcile_development_inventory(planned_identities=[IDENTITY], outputs=outputs)


def test_an_invalid_artifact_is_not_counted_or_silently_turned_into_a_failed_fit():
    prepared, expectations = item()
    expectations["expected_record_sha256"] = "0" * 64
    with pytest.raises(BranchBFailure) as caught:
        reconcile_development_inventory(planned_identities=[identity("synthetic_first")],
                                        outputs=[(prepared, expectations)])
    assert caught.value.code == FailureCode.CHECKSUM_MISMATCH


def test_swapped_external_expectations_cannot_relabel_verified_artifacts():
    first, second = item(), item("synthetic_second")
    with pytest.raises(BranchBFailure):
        reconcile_development_inventory(
            planned_identities=[identity("synthetic_first"), identity("synthetic_second")],
            outputs=[(first[0], second[1]), (second[0], first[1])],
        )


def test_received_order_does_not_determine_dataset_association():
    report = reconcile_development_inventory(
        planned_identities=[identity("synthetic_first"), identity("synthetic_second")],
        outputs=[item("synthetic_second", failed=True), item()],
    )
    assert report["inventory_matches_plan"] is True
    assert report["entries"][0]["identity"] == identity("synthetic_second")
    assert report["entries"][0]["status"] == "failure"
    assert report["entries"][1]["identity"] == identity("synthetic_first")


def test_inventory_does_not_mutate_plan_expectations_or_source_bytes():
    plan, outputs = [identity("synthetic_first")], [item()]
    saved_plan, saved_outputs = deepcopy(plan), deepcopy(outputs)
    report = reconcile_development_inventory(planned_identities=plan, outputs=outputs)
    report["entries"][0]["identity"]["dataset_id"] = "changed"
    assert plan == saved_plan and outputs == saved_outputs


def test_timestamp_checker_absence_is_a_configuration_failure_not_a_silent_pass(monkeypatch):
    record = complete()
    monkeypatch.setattr(checked, "FormatChecker", lambda: SimpleNamespace(checkers={}))
    with pytest.raises(ConfigurationRequired, match="date-time validation is unavailable"):
        validate(record)


@pytest.mark.parametrize("timestamp", [
    "not-a-timestamp", "2020-01-01", "2020-01-01T00:00:00",
    "2019-02-29T00:00:00Z", "2020-01-01T25:00:00Z", "2020-01-01T00:00:00+99:00",
])
def test_timestamp_format_is_actually_enforced(timestamp):
    record = complete()
    record["creation_timestamp"] = timestamp
    with pytest.raises(BranchBFailure) as caught:
        validate(record)
    assert caught.value.code == FailureCode.OUTPUT_SCHEMA


@pytest.mark.parametrize("timestamp", [
    "2020-02-29T23:59:59Z", "2020-02-29t23:59:59z",
    "2020-01-01T00:00:00.123456789+05:30", "2020-01-01T00:00:00-04:00",
])
def test_valid_supplied_timestamp_is_not_reformatted_or_replaced(timestamp):
    record = complete()
    record["creation_timestamp"] = timestamp
    validate(record)
    assert record["creation_timestamp"] == timestamp
