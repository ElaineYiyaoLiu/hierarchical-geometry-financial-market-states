"""Exact development inventory reconciliation, not a scientific success rule.

The caller supplies the planned identities and externally anchored verification
arguments for every prepared output. Missing, duplicate, and unexpected outputs
are reported explicitly. A documented failure is an accounted-for record, not
an automatic negative hierarchy-support decision or permission to replace it.
"""
from __future__ import annotations

from copy import deepcopy

from branch_b.failures import BranchBFailure, FailureCode
from .checked import IDENTITY_FIELDS, PreparedDevelopmentOutput, _identity, verify_development_output

_EXPECTATION_FIELDS = {
    "expected_record_sha256", "expected_receipt_sha256", "expected_identity",
    "expected_sample_order", "expected_configuration_file", "expected_source_revision",
    "expected_configuration_sha256", "expected_input_manifest_sha256",
}


def _key(identity: dict) -> tuple[str, ...]:
    checked = _identity(identity)
    return tuple(checked[field] for field in IDENTITY_FIELDS)


def reconcile_development_inventory(
    *, planned_identities: list[dict],
    outputs: list[tuple[PreparedDevelopmentOutput, dict]],
) -> dict:
    """Verify every artifact, then compare actual identities with the exact plan.

    The second element of each output pair contains the keyword arguments for
    verify_development_output, sourced independently of that output's receipt.
    This routine does not authenticate the source of those expectations, open
    any path, repair an artifact, retry an attempt, or freeze the planned set.
    """
    if type(planned_identities) is not list or not planned_identities:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "planned output identities must be a non-empty list")
    if type(outputs) is not list:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "outputs must be an explicit list")
    plan = [_identity(identity) for identity in planned_identities]
    keys = [_key(identity) for identity in plan]
    if len(keys) != len(set(keys)):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "planned output identities must be unique")
    by_key = dict(zip(keys, plan, strict=True))
    positions: dict[tuple[str, ...], list[int]] = {}
    entries = []
    unexpected = []
    for position, item in enumerate(outputs):
        if not isinstance(item, tuple) or len(item) != 2:
            raise BranchBFailure(FailureCode.INPUT_SCHEMA, "each output requires prepared bytes and external expectations")
        prepared, supplied = item
        if type(supplied) is not dict or set(supplied) != _EXPECTATION_FIELDS:
            raise BranchBFailure(FailureCode.INPUT_SCHEMA, "all external output-verification fields are required")
        expectations = deepcopy(supplied)
        record = verify_development_output(prepared, **expectations)
        identity = {field: record[field] for field in IDENTITY_FIELDS}
        key = _key(identity)
        positions.setdefault(key, []).append(position)
        entry = {
            "position": position, "identity": identity,
            "status": record["status"], "failure_code": record.get("failure_code"),
            "record_sha256": expectations["expected_record_sha256"].lower(),
            "receipt_sha256": expectations["expected_receipt_sha256"].lower(),
        }
        entries.append(entry)
        if key not in by_key:
            unexpected.append({"position": position, "identity": identity.copy()})
    missing = [identity.copy() for key, identity in by_key.items() if key not in positions]
    duplicates = [
        {"identity": dict(zip(IDENTITY_FIELDS, key, strict=True)), "positions": rows.copy()}
        for key, rows in positions.items() if len(rows) > 1
    ]
    return {
        "report_version": "branch-b-development-output-inventory-v1",
        "scope": "verified_transport_accounting_only", "scientific_authorization": False,
        "planned_count": len(plan), "observed_count": len(entries),
        "schema_complete_records": sum(entry["status"] == "complete" for entry in entries),
        "failure_records": sum(entry["status"] == "failure" for entry in entries),
        "entries": entries, "missing": missing, "unexpected": unexpected,
        "duplicates": duplicates,
        "inventory_matches_plan": not (missing or unexpected or duplicates),
    }
