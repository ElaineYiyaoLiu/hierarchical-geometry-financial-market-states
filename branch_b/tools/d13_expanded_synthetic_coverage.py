"""Resumable D13 expanded synthetic coverage study; Python 3.14 only.

Prespecified diagnostic design: 3 existing synthetic distributions x sample sizes
24 and 100 x 400 outer trials, with the UNCHANGED 10,000-resample D13 routine.
No hidden data, project calibration, scientific thresholds or method tuning.

CLI records remain local outside the shared public repository. The run is
deliberately substantial; interruption leaves an auditable append-only journal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from math import fsum
from pathlib import Path

import numpy as np

from branch_b.bootstrap.development_d13_interval import (
    development_d13_resampled_mean_interval,
)
from branch_b.tools.d13_synthetic_coverage import (
    SCENARIOS,
    _known_conditional_mean,
    _sample_synthetic,
    wilson_95_interval,
)

SAMPLE_SIZES = (24, 100)
OUTER_TRIALS = 400
DEVELOPMENT_SEED = 314159
DESIGN_NAME = "d13-expanded-synthetic-2026-11-15-v1"


def design() -> dict:
    return {
        "design_name": DESIGN_NAME,
        "purpose": "synthetic conditional Monte Carlo coverage diagnostic only",
        "sample_sizes": list(SAMPLE_SIZES),
        "outer_trials_per_cell": OUTER_TRIALS,
        "scenarios": list(SCENARIOS),
        "development_seed": DEVELOPMENT_SEED,
        "secondary_resamples_per_interval": 10_000,
        "nominal_interval_level": 0.95,
        "not_coverage_certification": True,
    }


def _json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _trial(scenario_index: int, size: int, trial_index: int) -> dict:
    # Per-trial development-only seeds isolate resumptions and avoid advancing
    # any project's primary, D13, D14, calibration or locked-test streams.
    sample_rng = np.random.default_rng(
        np.random.SeedSequence([DEVELOPMENT_SEED, scenario_index, size, trial_index, 0])
    )
    interval_rng = np.random.default_rng(
        np.random.SeedSequence([DEVELOPMENT_SEED, scenario_index, size, trial_index, 1])
    )
    name = SCENARIOS[scenario_index]
    values = _sample_synthetic(name, size, sample_rng)
    result = development_d13_resampled_mean_interval(values, rng=interval_rng)
    true_mean = _known_conditional_mean(name)
    return {
        "scenario": name,
        "sample_size": size,
        "trial_index": trial_index,
        "covered": result.lower_endpoint <= true_mean <= result.upper_endpoint,
        "lower": result.lower_endpoint,
        "upper": result.upper_endpoint,
        "point_estimate": result.point_estimate,
    }


def _read_journal(journal: Path, *, design_hash: str) -> dict[tuple[str, int, int], dict]:
    rows = {}
    if not journal.exists():
        return rows
    with journal.open("r", encoding="utf-8") as stream:
        for lineno, line in enumerate(stream, start=1):
            if not line.endswith("\n"):
                raise ValueError(f"incomplete journal line {lineno}; preserve and inspect file")
            entry = json.loads(line)
            if entry.get("design_sha256") != design_hash:
                raise ValueError(f"journal design mismatch on line {lineno}")
            row = entry["result"]
            key = (row["scenario"], row["sample_size"], row["trial_index"])
            if key in rows:
                raise ValueError(f"duplicate trial record on line {lineno}")
            if row["scenario"] not in SCENARIOS or row["sample_size"] not in SAMPLE_SIZES:
                raise ValueError(f"out-of-design trial on line {lineno}")
            if type(row["trial_index"]) is not int or not 0 <= row["trial_index"] < OUTER_TRIALS:
                raise ValueError(f"invalid trial index on line {lineno}")
            if type(row["covered"]) is not bool:
                raise ValueError(f"invalid coverage value on line {lineno}")
            if not all(np.isfinite(row[x]) for x in ("lower", "upper", "point_estimate")):
                raise ValueError(f"invalid nonfinite interval on line {lineno}")
            if row["lower"] > row["upper"]:
                raise ValueError(f"inverted interval on line {lineno}")
            rows[key] = row
    return rows


def _summary(rows: dict, *, design_hash: str) -> dict:
    cells = []
    for scenario in SCENARIOS:
        for size in SAMPLE_SIZES:
            available = [
                rows[(scenario, size, index)]
                for index in range(OUTER_TRIALS)
                if (scenario, size, index) in rows
            ]
            completed = len(available)
            covered = sum(int(row["covered"]) for row in available)
            entry = {
                "scenario": scenario,
                "sample_size": size,
                "completed_trials": completed,
                "planned_trials": OUTER_TRIALS,
                "complete": completed == OUTER_TRIALS,
                "covered_trials": covered,
            }
            if completed:
                low, high = wilson_95_interval(covered, completed)
                widths = [row["upper"] - row["lower"] for row in available]
                entry.update({
                    "empirical_coverage": covered / completed,
                    "wilson_95_lower": low,
                    "wilson_95_upper": high,
                    "mean_width": fsum(widths) / completed,
                    "zero_width_count": sum(w == 0.0 for w in widths),
                })
            cells.append(entry)
    return {
        "design": design(),
        "design_sha256": design_hash,
        "completed_trial_records": len(rows),
        "total_planned_trial_records": len(SCENARIOS) * len(SAMPLE_SIZES) * OUTER_TRIALS,
        "all_cells_complete": all(row["complete"] for row in cells),
        "cells": cells,
    }


def run(*, output_dir: Path, max_new_trials: int | None = None) -> dict:
    """Continue a fixed design; max_new_trials only bounds a development run."""
    if max_new_trials is not None and (type(max_new_trials) is not int or max_new_trials < 0):
        raise ValueError("max_new_trials must be a nonnegative integer")
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError("output path is not a directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    current_design = design()
    design_hash = _digest(current_design)
    manifest = output_dir / "design.json"
    if manifest.exists():
        if json.loads(manifest.read_text(encoding="utf-8")) != current_design:
            raise ValueError("existing design manifest differs from prespecified design")
    else:
        if (output_dir / "attempts.jsonl").exists():
            raise ValueError("journal present but design manifest missing")
        manifest.write_text(json.dumps(current_design, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    journal = output_dir / "attempts.jsonl"
    rows = _read_journal(journal, design_hash=design_hash)
    added = 0
    with journal.open("a", encoding="utf-8") as stream:
        for si, scenario in enumerate(SCENARIOS):
            for size in SAMPLE_SIZES:
                for idx in range(OUTER_TRIALS):
                    if (scenario, size, idx) in rows:
                        continue
                    if max_new_trials is not None and added >= max_new_trials:
                        break
                    # Do not swallow errors: failures are preserved in the
                    # caller's log and missing trials remain visibly incomplete.
                    row = _trial(si, size, idx)
                    record = {"design_sha256": design_hash, "result": row}
                    stream.write(_json_bytes(record).decode("utf-8") + "\n")
                    stream.flush()
                    rows[(scenario, size, idx)] = row
                    added += 1
                if max_new_trials is not None and added >= max_new_trials:
                    break
            if max_new_trials is not None and added >= max_new_trials:
                break
    summary = _summary(rows, design_hash=design_hash)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--max-new-trials", type=int, default=None)
    args = parser.parse_args()
    result = run(output_dir=args.output_dir, max_new_trials=args.max_new_trials)
    print(json.dumps({
        "completed": result["completed_trial_records"],
        "planned": result["total_planned_trial_records"],
        "all_cells_complete": result["all_cells_complete"],
        "summary_file": str(args.output_dir / "summary.json"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
