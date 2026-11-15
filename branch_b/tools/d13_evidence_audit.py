"""Read-only D13 synthetic evidence integrity audit. Python 3.14 only.

This checks local, Branch B-owned synthetic study journals and summaries against
their committed development source logic. It does not rerun trials, infer hidden
information, certify coverage, or authorize a scientific freeze.

Reads only the two explicitly supplied synthetic evidence directories. The audit
report is printed to stdout and is NOT automatically placed in the public repo.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from branch_b.tools import d13_expanded_synthetic_coverage as expanded
from branch_b.tools import d13_synthetic_sensitivity as sensitivity

STUDIES = {
    "expanded": {
        "design": expanded.design,
        "hash": expanded._digest,
        "read": expanded._read_journal,
        "summary": expanded._summary,
        "expected": 2400,
    },
    "sensitivity": {
        "design": sensitivity.design,
        "hash": lambda value: hashlib.sha256(
            sensitivity._serialize(value).encode("utf-8")
        ).hexdigest(),
        "read": sensitivity._load_rows,
        "summary": sensitivity._summary,
        "expected": 600,
    },
}


def audit_study(kind: str, directory: Path) -> dict:
    """Validate an existing local journal without modifying any study files."""
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("This project evidence audit requires actual Python 3.14.")
    if kind not in STUDIES:
        raise ValueError("unknown synthetic evidence type")
    spec = STUDIES[kind]
    manifest = directory / "design.json"
    journal = directory / "attempts.jsonl"
    summary = directory / "summary.json"
    for file in (manifest, journal, summary):
        if not file.is_file():
            raise ValueError(f"missing original evidence file: {file}")
    observed_design = json.loads(manifest.read_text(encoding="utf-8"))
    expected_design = spec["design"]()
    if observed_design != expected_design:
        raise ValueError(f"{kind} manifest differs from committed synthetic design")
    digest = spec["hash"](expected_design)
    if kind == "expanded":
        rows = spec["read"](journal, design_hash=digest)
        recomputed = spec["summary"](rows, design_hash=digest)
    else:
        rows = spec["read"](journal, digest)
        recomputed = spec["summary"](rows, digest)
    existing_summary = json.loads(summary.read_text(encoding="utf-8"))
    if existing_summary != recomputed:
        raise ValueError(f"{kind} summary disagrees with full journal recount")
    if not recomputed["all_cells_complete"]:
        raise ValueError(f"{kind} study is incomplete")
    count_key = "completed_trial_records" if kind == "expanded" else "completed_records"
    if len(rows) != spec["expected"] or recomputed[count_key] != spec["expected"]:
        raise ValueError(f"{kind} trial count not equal to prespecified complete design")
    files = {}
    for label, file in (("design", manifest), ("journal", journal), ("summary", summary)):
        files[label] = hashlib.sha256(file.read_bytes()).hexdigest()
    return {
        "study": kind,
        "status": "AUDIT_PASSED",
        "trial_records": len(rows),
        "design_sha256": digest,
        "file_sha256": files,
        "note": "read-only synthetic evidence consistency, NOT coverage certification",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expanded-dir", type=Path, required=True)
    parser.add_argument("--sensitivity-dir", type=Path, required=True)
    args = parser.parse_args()
    results = [
        audit_study("expanded", args.expanded_dir),
        audit_study("sensitivity", args.sensitivity_dir),
    ]
    print(json.dumps({"python_version": sys.version, "audits": results},
                     sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
