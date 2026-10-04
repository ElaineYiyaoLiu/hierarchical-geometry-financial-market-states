"""Audit the public pre-pilot register. Evidence review never grants approval."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

REQUIRED_GATES = frozenset({
    "BOUNDARY", "SENTINELS", "A_READINESS", "A_ALL_FAMILY_RUNNER",
    "B_CURRENT_TESTS", "B_CURRENT_CI", "B_CORRELATION", "B_TOLERANCES",
    "B_SIGMOID", "B_INIT", "B_POSITIVITY", "B_VALUATION_SANITY",
    "B_FITTER_EXECUTABLE", "B_METHOD_PACKAGE", "CUSTODIAN_OPERATIONAL",
    "SEALED_PRECISION_CONTRACT", "MINIMUM_EFFECT_PROVENANCE",
    "FACULTY_CONCEPT", "FACULTY_EXCHANGE", "FINAL_PL_EXCHANGE",
})


def checked_file(root: Path, ref: str, digest: str) -> None:
    root = root.resolve()
    path = (root / ref).resolve()
    if not ref or Path(ref).is_absolute() or not path.is_relative_to(root):
        raise ValueError("relative evidence file inside the public repository required")
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("exact-byte SHA-256 required")
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError("evidence absent or checksum mismatch")


def audit(rows: list[dict], root: Path) -> dict:
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Python 3.14 required")
    ids = [row.get("gate_id") for row in rows]
    structural = []
    if len(ids) != len(set(ids)):
        structural.append("duplicate gate IDs")
    missing = sorted(REQUIRED_GATES - set(ids))
    unknown = sorted(set(ids) - REQUIRED_GATES, key=str)
    if missing:
        structural.append("missing required gates: " + ", ".join(missing))
    if unknown:
        structural.append("unknown gate IDs")
    results = []
    for row in rows:
        issues = []
        declared = row.get("status", "")
        verified = False
        if row.get("evidence_sha256"):
            try:
                checked_file(root, row.get("evidence_ref", ""), row["evidence_sha256"])
                verified = True
            except (ValueError, OSError, TypeError) as exc:
                issues.append(str(exc))
        else:
            issues.append("evidence checksum missing")
        if declared != "PASS":
            issues.append("gate is not declared PASS; scoped and recorded evidence retains its scope")
        for field in ("owner", "approval_authority", "approval_ref", "freeze_id"):
            if not row.get(field):
                issues.append(field + " missing")
        if row.get("approval_ref"):
            try:
                checked_file(root, row["approval_ref"], row.get("approval_sha256", ""))
            except (ValueError, OSError, TypeError) as exc:
                issues.append("approval: " + str(exc))
        results.append({
            "gate_id": row.get("gate_id"),
            "declared_status": declared,
            "evidence_checksum_verified": verified,
            "status": "REVIEWABLE" if not issues else "BLOCKED",
            "blockers": issues,
        })
    complete = not structural and all(r["status"] == "REVIEWABLE" for r in results)
    return {
        "record": "pre_pilot_register_audit",
        "structural_blockers": structural,
        "gates": results,
        "evidence_complete": complete,
        "decision": "REVIEWABLE" if complete else "BLOCKED",
        "pilot_exchange_authorized": False,
        "formal_generation_authorized": False,
        "note": "Checks public evidence bytes and declared closure only. Approvers must verify scientific scope, signatures, chronology and operational availability.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=Path("governance/approval_evidence_register.csv"))
    parser.add_argument("--evidence-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    with args.register.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    result = audit(rows, args.evidence_root)
    result["register_sha256"] = hashlib.sha256(args.register.read_bytes()).hexdigest()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(text)
    print(text, end="")
    if args.require_complete and not result["evidence_complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
