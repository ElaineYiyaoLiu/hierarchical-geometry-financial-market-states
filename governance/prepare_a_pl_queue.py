"""Turn the existing gate audit into an A/PL closure queue without granting authority."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_pre_pilot import audit


# Work order is an operational recommendation, not a protocol gate redefinition.
TASKS = (
    ("A_ALL_FAMILY_RUNNER", "A", "Certify the approved formal runner and retain restricted evidence; publish only a permitted attestation."),
    ("A_READINESS", "A/PL", "Bind scoped readiness to reviewed evidence, authority and freeze references."),
    ("BOUNDARY", "PL", "Reconcile access review, approval reference and freeze entry."),
    ("SENTINELS", "PL", "Reconcile the public-safe registry approval and freeze evidence."),
    ("CUSTODIAN_OPERATIONAL", "custodian/PL", "Obtain actual identity, independent key registration, availability and operated dummy-rehearsal evidence."),
    ("SEALED_PRECISION_CONTRACT", "custodian/PL", "Complete the exact calculation/release contract and required decisions before inspection."),
    ("MINIMUM_EFFECT_PROVENANCE", "PL", "Obtain the original decision and earliest relevant inspection chronology; validate consistency and review authority."),
    ("FINAL_PL_EXCHANGE", "PL", "Reconcile the final decision only after every applicable gate closes."),
)


def prepare(rows: list[dict], root: Path) -> dict:
    result = audit(rows, root)
    by_id = {r["gate_id"]: r for r in result["gates"]}
    queue = [{"priority": i, "gate_id": gate, "work_owner": owner,
              "action": action, "status": by_id.get(gate, {}).get("status", "BLOCKED"),
              "missing_evidence": by_id.get(gate, {}).get("blockers", ["required gate absent"])}
             for i, (gate, owner, action) in enumerate(TASKS, 1)]
    return {"record": "a_pl_closure_queue", "scope": "A/PL operational preparation",
            "work_items": queue, "structural_blockers": result["structural_blockers"],
            "overall_gate_audit_decision": result["decision"],
            "other_gate_count": len(result["gates"]) - sum(g in by_id for g, _, _ in TASKS),
            "pilot_exchange_authorized": False, "formal_generation_authorized": False,
            "note": "Work priority grants no approval. B and Faculty records are preserved and are not changed by this command."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=Path("governance/approval_evidence_register.csv"))
    parser.add_argument("--evidence-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.register.open(newline="", encoding="utf-8") as handle:
        result = prepare(list(csv.DictReader(handle)), args.evidence_root)
    result["register_sha256"] = hashlib.sha256(args.register.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"Prepared {len(result['work_items'])} A/PL work items; no authorization granted.")


if __name__ == "__main__":
    main()
