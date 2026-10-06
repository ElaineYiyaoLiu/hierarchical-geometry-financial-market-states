"""Check supplied provenance bytes and UTC chronology; authority review stays separate."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_pre_pilot import checked_file


REFERENCES = ("primary_metric_definition", "substantive_rationale", "original_decision",
              "approval_signature", "inspection_chronology_attestation")


def utc_time(value):
    if not isinstance(value, str):
        raise ValueError("UTC timestamp required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("UTC timestamp required")
    return parsed


def check(record: dict, root: Path) -> dict:
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Python 3.14 required")
    issues = []
    for key in REFERENCES:
        try:
            checked_file(root, record.get(key + "_ref", ""), record.get(key + "_sha256", ""))
        except (ValueError, TypeError, OSError) as exc:
            issues.append(f"{key}: {exc}")
    value = record.get("minimum_effect_value")
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        issues.append("positive finite substantive effect value required from original decision")
    for key in ("effect_orientation_and_units", "approval_authority", "freeze_id"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            issues.append(key + " missing")
    chronology = False
    try:
        frozen = utc_time(record.get("frozen_at_utc"))
        inspected = utc_time(record.get("earliest_relevant_development_contrast_inspection_at_utc"))
        chronology = frozen < inspected
        if not chronology:
            issues.append("freeze must strictly precede earliest relevant inspection")
    except (ValueError, TypeError, OverflowError) as exc:
        issues.append("chronology: " + str(exc))
    return {"record": "minimum_effect_provenance_consistency_check",
            "status": "BLOCKED" if issues else "REVIEWABLE",
            "blockers": issues, "recorded_chronology_consistent": chronology,
            "historical_chronology_independently_verified": False,
            "approval_granted": False, "pilot_exchange_authorized": False,
            "note": "Exact-byte references and recorded dates are checked. Reviewer must verify original decision contents, signatures, authority and earliest-inspection completeness. A present-day approval cannot establish a historical freeze."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = check(json.loads(args.record.read_text()), args.evidence_root)
    result["input_sha256"] = hashlib.sha256(args.record.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
