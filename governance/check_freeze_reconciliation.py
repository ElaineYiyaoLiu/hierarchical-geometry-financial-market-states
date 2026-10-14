"""Cross-check public gate references with recorded freeze bytes; no approval."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_pre_pilot import audit, checked_file
from check_minimum_effect_provenance import utc_time


def reconcile(gates: list[dict], freezes: list[dict], root: Path) -> dict:
    baseline = audit(gates, root)
    structural = list(baseline["structural_blockers"])
    index = {}
    for row in freezes:
        key = row.get("freeze_id")
        if not isinstance(key, str) or not key.strip():
            structural.append("freeze record missing identity")
            continue
        if key in index:
            structural.append("duplicate freeze identity: " + key)
        index[key] = row
    checked = []
    for row in gates:
        issues = []
        freeze = index.get(row.get("freeze_id"))
        if freeze is None:
            issues.append("referenced freeze entry missing")
        else:
            if freeze.get("status") != "frozen":
                issues.append("referenced entry is not frozen")
            for field in ("owner", "approved_by", "version"):
                if not isinstance(freeze.get(field), str) or not freeze[field].strip():
                    issues.append("freeze " + field + " missing")
            if isinstance(freeze.get("version"), str) and freeze["version"].lower() == "pending":
                issues.append("freeze version remains pending")
            try:
                utc_time(freeze.get("frozen_at_utc"))
            except (ValueError, TypeError, OverflowError):
                issues.append("freeze UTC timestamp missing or invalid")
            artifact = freeze.get("artifact")
            matches = [(row.get(ref), row.get(digest)) for ref, digest in
                       (("evidence_ref", "evidence_sha256"),
                        ("approval_ref", "approval_sha256"))
                       if row.get(ref) and row.get(ref) == artifact]
            if not matches:
                issues.append("freeze artifact differs from gate evidence and approval")
            elif not any(digest == freeze.get("checksum") for _, digest in matches):
                issues.append("freeze checksum differs from referenced artifact")
            else:
                try:
                    checked_file(root, artifact, freeze.get("checksum"))
                except (ValueError, TypeError, OSError) as exc:
                    issues.append("freeze artifact: " + str(exc))
        checked.append({"gate_id": row.get("gate_id"),
                        "freeze_reference_consistent": not issues,
                        "blockers": issues})
    complete = (baseline["evidence_complete"] and not structural
                and all(r["freeze_reference_consistent"] for r in checked))
    return {"record": "public_gate_freeze_reconciliation",
            "decision": "REVIEWABLE" if complete else "BLOCKED",
            "reference_consistency_complete": complete,
            "structural_blockers": structural, "gates": checked,
            "gate_audit_decision": baseline["decision"],
            "approval_granted": False, "formal_generation_authorized": False,
            "pilot_exchange_authorized": False,
            "note": "Checks recorded public references and bytes only. Authority, signatures, substantive scope and before-inspection chronology require independent review."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path,
                        default=Path("governance/approval_evidence_register.csv"))
    parser.add_argument("--freezes", type=Path, default=Path("governance/freeze_registry.csv"))
    parser.add_argument("--evidence-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.register.open(newline="", encoding="utf-8") as handle:
        gates = list(csv.DictReader(handle))
    with args.freezes.open(newline="", encoding="utf-8") as handle:
        freezes = list(csv.DictReader(handle))
    result = reconcile(gates, freezes, args.evidence_root)
    result["register_sha256"] = hashlib.sha256(args.register.read_bytes()).hexdigest()
    result["freeze_registry_sha256"] = hashlib.sha256(args.freezes.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["decision"])


if __name__ == "__main__":
    main()
