"""Synthetic Week 3 evidence-inventory checks, not scientific golden tests."""
import pytest

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.golden.readiness import GOLDEN_DOMAINS, audit_golden_readiness


def _case(case_id="synthetic-01", domain="geometry", status="pending"):
    executed = status in ("passed", "failed")
    return {
        "case_id": case_id,
        "domain": domain,
        "status": status,
        "python_version": "3.14.8" if executed else None,
        "evidence_sha256": "a" * 64 if executed else None,
    }


def test_empty_inventory_never_certifies_golden_readiness():
    result = audit_golden_readiness([])
    assert result["missing_domains"] == list(GOLDEN_DOMAINS)
    assert result["all_supplied_cases_passed"] is False
    assert result["scientific_golden_certified"] is False
    assert result["pilot_authorization"] is False


def test_synthetic_all_passed_inventory_still_cannot_certify():
    result = audit_golden_readiness([
        _case(f"synthetic-{i}", domain, "passed")
        for i, domain in enumerate(GOLDEN_DOMAINS)
    ])
    assert result["missing_domains"] == []
    assert result["all_supplied_cases_passed"] is True
    assert result["scientific_golden_certified"] is False
    assert result["pilot_authorization"] is False


@pytest.mark.parametrize("mutations", [
    {"status": "unknown"},
    {"domain": "hidden_truth"},
    {"case_id": ""},
    {"python_version": "3.13.9", "status": "passed", "evidence_sha256": "a" * 64},
    {"python_version": "3.14.8", "status": "pending"},
    {"status": "passed", "python_version": None, "evidence_sha256": "a" * 64},
    {"status": "passed", "python_version": "3.14.8", "evidence_sha256": "not-a-digest"},
])
def test_bad_golden_evidence_is_rejected(mutations):
    record = _case()
    record.update(mutations)
    with pytest.raises(BranchBFailure) as caught:
        audit_golden_readiness([record])
    assert caught.value.code == FailureCode.INPUT_SCHEMA


def test_duplicate_case_ids_are_rejected():
    with pytest.raises(BranchBFailure):
        audit_golden_readiness([_case(), _case()])


def test_blocked_case_keeps_gate_open():
    result = audit_golden_readiness([_case(status="blocked")])
    assert result["status_counts"]["blocked"] == 1
    assert result["pilot_authorization"] is False
