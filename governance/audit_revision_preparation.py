"""Check bounded-revision evidence references; never approve a revision or seed release."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_pre_pilot import checked_file

# Field labels implement the six operational categories already listed in G.4.
OPERATIONAL_FIELDS = frozenset({
    "minimum_successful_bootstrap", "common_observation_requirement", "ci_method",
    "timeout", "failed_fit_treatment", "final_monte_carlo_count",
})


def audit_revision(record: dict, rows: list[dict], root: Path) -> dict:
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Python 3.14 required")
    blockers = []
    if record.get("status") != "APPROVED_FROZEN":
        blockers.append("reviewed revision approval and freeze not recorded")
    if record.get("calibration_seed_release_authorized") is not False or record.get("locked_test_authorized") is not False:
        blockers.append("preparation record must not authorize seed release or locked testing")
    changes = record.get("changes")
    if not isinstance(changes, list) or not changes or any(not isinstance(c, dict) for c in changes):
        blockers.append("nonempty explicit change records required")
        changes = []
    ids = [c.get("change_id") for c in changes]
    row_ids = [r.get("change_id") for r in rows]
    if (any(not isinstance(i, str) or not i for i in ids + row_ids)
            or len(set(ids)) != len(ids) or len(set(row_ids)) != len(row_ids)
            or set(ids) != set(row_ids)):
        blockers.append("one compliance row per declared change required")
    if record.get("prohibited_scientific_changes") != []:
        blockers.append("prohibited or unclassified scientific changes remain unresolved")
    allowed_refs = record.get("allowed_evidence_refs")
    if not isinstance(allowed_refs, list) or any(not isinstance(r, str) for r in allowed_refs):
        blockers.append("explicit allowed evidence references required")
        allowed_refs = []
    for prefix in ("pilot_exit_approval", "checksum_freeze"):
        try:
            checked_file(root, record.get(prefix + "_ref"), record.get(prefix + "_sha256"))
        except (ValueError, TypeError, OSError) as exc:
            blockers.append(prefix + ": " + str(exc))
    approvals = record.get("approvals")
    approval_hashes = record.get("approvals_sha256")
    for authority in ("PL", "Faculty"):
        try:
            checked_file(root, approvals.get(authority) if isinstance(approvals, dict) else None,
                         approval_hashes.get(authority) if isinstance(approval_hashes, dict) else None)
        except (ValueError, TypeError, OSError) as exc:
            blockers.append(authority + " revision approval: " + str(exc))
    by_id = {c.get("change_id"): c for c in changes if isinstance(c.get("change_id"), str)}
    for row in rows:
        identity = row.get("change_id", "missing")
        field = row.get("field")
        if field not in OPERATIONAL_FIELDS:
            blockers.append(str(identity) + ": requires separate scope/version review")
        if by_id.get(identity, {}).get("field") != field:
            blockers.append(str(identity) + ": compliance field differs from declared change")
        for name in ("before_value", "proposed_value", "protocol_basis", "scientific_effect", "freeze_id"):
            if not isinstance(row.get(name), str) or not row[name].strip():
                blockers.append(str(identity) + ": missing " + name)
        if row.get("status") != "APPROVED_FROZEN":
            blockers.append(str(identity) + ": actual approval/freeze not recorded")
        if row.get("permitted_evidence_ref") not in allowed_refs:
            blockers.append(str(identity) + ": evidence not in declared allowed list")
        for ref, digest in (("permitted_evidence_ref", "evidence_sha256"),
                            ("artifact_ref", "artifact_sha256"),
                            ("PL_approval_ref", "PL_approval_sha256"),
                            ("Faculty_approval_ref", "Faculty_approval_sha256")):
            try:
                checked_file(root, row.get(ref), row.get(digest))
            except (ValueError, TypeError, OSError) as exc:
                blockers.append(str(identity) + ": " + ref + ": " + str(exc))
    return {"record": "bounded_revision_reference_audit",
            "decision": "BLOCKED" if blockers else "REVIEWABLE", "blockers": blockers,
            "scientific_scope_independently_verified": False,
            "before_inspection_chronology_verified": False, "revision_approved": False,
            "calibration_seed_release_authorized": False, "locked_test_authorized": False,
            "note": "Checks listed public bytes and operational categories only. Actual authority, scientific scope, evidence admissibility, chronology and the single bounded-revision limit require review. Interface or scientific changes require separate scope/version decisions."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path,
                        default=Path("governance/week5/post_pilot_change_set.template.json"))
    parser.add_argument("--compliance", type=Path,
                        default=Path("governance/week5/revision_compliance.template.csv"))
    parser.add_argument("--evidence-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.compliance.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    result = audit_revision(json.loads(args.record.read_text()), rows, args.evidence_root)
    result["record_sha256"] = hashlib.sha256(args.record.read_bytes()).hexdigest()
    result["compliance_sha256"] = hashlib.sha256(args.compliance.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["decision"])


if __name__ == "__main__":
    main()
