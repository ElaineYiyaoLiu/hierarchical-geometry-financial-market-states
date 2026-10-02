"""Project operational resource costs from measured aggregate stage costs."""
from __future__ import annotations

import csv
import json
import sys
from decimal import Decimal
from pathlib import Path


def project(rows: list[dict]) -> dict:
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Python 3.14 required")
    if not rows:
        return {"status": "UNMEASURED", "stages": [], "feasibility_approved": False}
    stages = []
    for row in rows:
        if not row.get("benchmark_ref") or not row.get("stage"):
            raise ValueError("measured benchmark reference and stage required")
        def number(name):
            x = Decimal(row[name])
            if not x.is_finite() or x < 0:
                raise ValueError(f"finite nonnegative {name} required")
            return x
        attempts = number("planned_attempts")
        if attempts != attempts.to_integral_value() or attempts == 0:
            raise ValueError("positive integer planned attempts required")
        core = number("core_hours_per_attempt") * attempts
        storage = number("bytes_per_attempt") * attempts / Decimal(2 ** 30)
        serial = number("wall_seconds_per_attempt") * attempts / Decimal(3600)
        stages.append({"stage": row["stage"], "benchmark_ref": row["benchmark_ref"],
                       "projected_core_hours": str(core), "projected_storage_gib": str(storage),
                       "serial_elapsed_hours": str(serial)})
    return {"status": "PROJECTED_REQUIRES_CAPACITY_REVIEW", "stages": stages,
            "total_core_hours": str(sum(Decimal(r["projected_core_hours"]) for r in stages)),
            "total_storage_gib": str(sum(Decimal(r["projected_storage_gib"]) for r in stages)),
            "feasibility_approved": False}


if __name__ == "__main__":
    with Path(sys.argv[1]).open(newline="", encoding="utf-8") as handle:
        print(json.dumps(project(list(csv.DictReader(handle))), indent=2, sort_keys=True))
