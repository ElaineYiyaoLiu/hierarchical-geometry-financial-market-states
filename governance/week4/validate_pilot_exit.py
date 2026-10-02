"""Validate approved evidence references; never grant operational authorization."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path


def checked_evidence(root: Path, ref: str, sha: str) -> dict:
    root = root.resolve()
    path = (root / ref).resolve()
    if not ref or Path(ref).is_absolute() or not path.is_relative_to(root):
        raise ValueError("evidence must be a permitted relative file inside evidence root")
    if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("exact-byte SHA-256 required")
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != sha:
        raise ValueError("evidence missing or checksum mismatch")
    return {"path": ref, "sha256": sha}


def validate_matrix(rows: list[dict], root: Path) -> dict:
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Python 3.14 required")
    required = {f"J.{i}" for i in range(1, 19)}
    ids = [r.get("criterion_id") for r in rows]
    blockers = []
    if set(ids) != required or len(ids) != 18:
        blockers.append("exactly one record for each J.1-J.18 required")
    for row in rows:
        key = row.get("criterion_id", "missing")
        if row.get("status") not in {"PASS", "WAIVED"}:
            blockers.append(f"{key}: pending")
            continue
        try:
            if not row.get("approver") or not row.get("freeze_id"):
                raise ValueError("approver and freeze entry required")
            date = datetime.fromisoformat(row["approval_date_utc"].replace("Z", "+00:00"))
            if date.tzinfo is None or date.utcoffset().total_seconds() != 0:
                raise ValueError("UTC approval date required")
            checked_evidence(root, row["evidence_ref"], row["evidence_sha256"])
            if row["status"] == "WAIVED":
                waiver = json.loads((root / row["evidence_ref"]).read_text())
                for field in ("criterion_id", "rationale", "scientific_or_operational_effect",
                              "approver", "approval_date_utc", "freeze_id"):
                    if not waiver.get(field):
                        raise ValueError(f"waiver missing {field}")
                for field in ("criterion_id", "approver", "approval_date_utc", "freeze_id"):
                    if waiver[field] != row[field]:
                        raise ValueError(f"waiver {field} does not match register")
        except (ValueError, OSError, KeyError, TypeError) as exc:
            blockers.append(f"{key}: {exc}")
    return {"evidence_complete": not blockers, "decision": "REVIEWABLE" if not blockers else "BLOCKED",
            "blockers": blockers, "pilot_exit_approval_granted": False,
            "generation_authorized": False, "raw_truth_read": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    args = parser.parse_args()
    with args.matrix.open(newline="", encoding="utf-8") as handle:
        result = validate_matrix(list(csv.DictReader(handle)), args.evidence_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["evidence_complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
