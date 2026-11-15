"""Synthetic D13 failure selection/dependence sensitivity; Python 3.14 only.

Development-only, prespecified generic toy models, not project data or a D12
failure-rate policy. Uses the UNCHANGED D13 10,000-secondary-resample interval.
The shared-shift experiment intentionally violates conditional independence
when the shared shift is *not* conditioned on in its overall target.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from math import fsum
from pathlib import Path

import numpy as np

from branch_b.bootstrap.development_d13_interval import development_d13_resampled_mean_interval
from branch_b.tools.d13_synthetic_coverage import wilson_95_interval

SCENARIOS = ("independent_failure", "score_dependent_failure", "shared_random_shift")
OUTER_TRIALS = 200
ATTEMPTS_PER_TRIAL = 60
DEVELOPMENT_SEED = 271828
DESIGN_NAME = "d13-synthetic-sensitivity-2026-11-15-v1"


def design() -> dict:
    return {
        "name": DESIGN_NAME,
        "scenarios": list(SCENARIOS),
        "outer_trials": OUTER_TRIALS,
        "attempts_per_trial": ATTEMPTS_PER_TRIAL,
        "development_seed": DEVELOPMENT_SEED,
        "secondary_resamples_per_interval": 10000,
        "nominal_level": 0.95,
        "status": "synthetic sensitivity diagnostic, not a freeze or coverage certification",
    }


def _serialize(obj: object) -> str:
    return json.dumps(obj, allow_nan=False, sort_keys=True, separators=(",", ":"))


def _design_hash() -> str:
    return hashlib.sha256(_serialize(design()).encode("utf-8")).hexdigest()


def _trial(scenario_index: int, trial_index: int) -> dict:
    name = SCENARIOS[scenario_index]
    attempts_rng = np.random.default_rng(
        np.random.SeedSequence([DEVELOPMENT_SEED, scenario_index, trial_index, 0])
    )
    secondary_rng = np.random.default_rng(
        np.random.SeedSequence([DEVELOPMENT_SEED, scenario_index, trial_index, 1])
    )
    n = ATTEMPTS_PER_TRIAL
    potential_scores = attempts_rng.uniform(-1.0, 1.0, size=n)
    if name == "independent_failure":
        success_flags = attempts_rng.random(n) < 0.5
        true_conditional_mean = 0.0
        true_all_attempt_mean = 0.0
    elif name == "score_dependent_failure":
        # For Q~U(-1,1), P(success|Q=q)=(q+1)/2:
        # P(success)=1/2 and E[Q|success]=1/3 analytically.
        success_flags = attempts_rng.random(n) < ((potential_scores + 1.0) / 2.0)
        true_conditional_mean = 1.0 / 3.0
        true_all_attempt_mean = 0.0
    elif name == "shared_random_shift":
        # Intentional across-attempt dependence. The target zero averages over
        # the *unconditioned* shared shift. It is NOT the conditional-on-shift mean.
        shift = attempts_rng.normal(0.0, 0.5)
        potential_scores += shift
        success_flags = np.ones(n, dtype=bool)
        true_conditional_mean = 0.0
        true_all_attempt_mean = 0.0
    else:
        raise ValueError("unrecognized synthetic scenario")

    successful_scores = potential_scores[success_flags]
    successful_count = int(np.count_nonzero(success_flags))
    failed_count = n - successful_count
    # Keep a complete synthetic failure-status ledger without exposing
    # hypothetical failed Q values as observed scores.
    status = ["SUCCEEDED" if success else "FAILED" for success in success_flags]
    if not successful_count:
        return {
            "scenario": name, "trial_index": trial_index, "attempted": n,
            "succeeded": 0, "failed": n, "statuses": status,
            "calculable": False, "failure_reason": "NO_SUCCESSES",
        }
    interval = development_d13_resampled_mean_interval(
        successful_scores.tolist(), rng=secondary_rng
    )
    return {
        "scenario": name, "trial_index": trial_index, "attempted": n,
        "succeeded": successful_count, "failed": failed_count, "statuses": status,
        "calculable": True, "lower": interval.lower_endpoint,
        "upper": interval.upper_endpoint, "estimate": interval.point_estimate,
        "conditional_target": true_conditional_mean,
        "all_attempt_target": true_all_attempt_mean,
        "contains_conditional_target": interval.lower_endpoint <= true_conditional_mean <= interval.upper_endpoint,
        "contains_all_attempt_target": interval.lower_endpoint <= true_all_attempt_mean <= interval.upper_endpoint,
    }


def _load_rows(path: Path, fingerprint: str) -> dict[tuple[str, int], dict]:
    rows = {}
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as stream:
        for i, line in enumerate(stream, 1):
            if not line.endswith("\n"):
                raise ValueError(f"truncated journal at line {i}; preserve and inspect")
            record = json.loads(line)
            if record.get("design_sha256") != fingerprint:
                raise ValueError(f"design hash mismatch at line {i}")
            row = record["result"]
            key = (row["scenario"], row["trial_index"])
            if (key in rows or key[0] not in SCENARIOS or
                    type(key[1]) is not int or not 0 <= key[1] < OUTER_TRIALS):
                raise ValueError(f"invalid or duplicate trial at line {i}")
            if row["attempted"] != ATTEMPTS_PER_TRIAL or row["succeeded"] + row["failed"] != ATTEMPTS_PER_TRIAL:
                raise ValueError(f"invalid attempt accounting at line {i}")
            if len(row["statuses"]) != ATTEMPTS_PER_TRIAL:
                raise ValueError(f"missing attempt statuses at line {i}")
            if row["statuses"].count("SUCCEEDED") != row["succeeded"] or row["statuses"].count("FAILED") != row["failed"]:
                raise ValueError(f"status accounting mismatch at line {i}")
            rows[key] = row
    return rows


def _summary(rows: dict, fingerprint: str) -> dict:
    results = []
    for name in SCENARIOS:
        observed = [rows[(name, i)] for i in range(OUTER_TRIALS) if (name, i) in rows]
        valid = [row for row in observed if row["calculable"]]
        covered = sum(row["contains_conditional_target"] for row in valid)
        alternate_covered = sum(row["contains_all_attempt_target"] for row in valid)
        item = {
            "scenario": name,
            "completed_trials": len(observed),
            "planned_trials": OUTER_TRIALS,
            "successful_interval_trials": len(valid),
            "uncalculable_trials": len(observed) - len(valid),
            "attempts_recorded": sum(row["attempted"] for row in observed),
            "failed_attempts": sum(row["failed"] for row in observed),
            "mean_success_count": (fsum(row["succeeded"] for row in observed) / len(observed) if observed else None),
        }
        if valid:
            lower, upper = wilson_95_interval(covered, len(valid))
            item.update({
                "conditional_target_covered": covered,
                "conditional_target_empirical_coverage": covered / len(valid),
                "conditional_target_wilson_95": [lower, upper],
                "all_attempt_target_covered": alternate_covered,
                "all_attempt_target_empirical_coverage": alternate_covered / len(valid),
                "mean_interval_width": fsum(row["upper"] - row["lower"] for row in valid) / len(valid),
            })
        results.append(item)
    return {
        "design": design(), "design_sha256": fingerprint,
        "completed_records": len(rows),
        "planned_records": len(SCENARIOS) * OUTER_TRIALS,
        "all_cells_complete": all(r["completed_trials"] == OUTER_TRIALS for r in results),
        "results": results,
        "interpretation_warning": "shared_random_shift target integrates an unconditioned shared shift; not a conditional-on-shift coverage study",
    }


def run(output_dir: Path, *, max_new_trials: int = 50) -> dict:
    if type(max_new_trials) is not int or max_new_trials < 0:
        raise ValueError("max_new_trials must be a nonnegative integer")
    output_dir.mkdir(parents=True, exist_ok=True)
    fingerprint = _design_hash()
    manifest = output_dir / "design.json"
    if manifest.exists():
        if json.loads(manifest.read_text(encoding="utf-8")) != design():
            raise ValueError("design differs from the original study")
    else:
        if (output_dir / "attempts.jsonl").exists():
            raise ValueError("journal exists without design manifest")
        manifest.write_text(json.dumps(design(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    journal = output_dir / "attempts.jsonl"
    rows = _load_rows(journal, fingerprint)
    added = 0
    with journal.open("a", encoding="utf-8") as stream:
        for scenario_index, scenario in enumerate(SCENARIOS):
            for trial_index in range(OUTER_TRIALS):
                key = (scenario, trial_index)
                if key in rows:
                    continue
                if added >= max_new_trials:
                    break
                row = _trial(scenario_index, trial_index)
                stream.write(_serialize({"design_sha256": fingerprint, "result": row}) + "\n")
                stream.flush()
                rows[key] = row
                added += 1
            if added >= max_new_trials:
                break
    result = _summary(rows, fingerprint)
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--max-new-trials", type=int, default=50)
    args = parser.parse_args()
    result = run(args.output_dir, max_new_trials=args.max_new_trials)
    print(_serialize({
        "completed": result["completed_records"],
        "planned": result["planned_records"],
        "all_cells_complete": result["all_cells_complete"],
        "summary": str(args.output_dir / "summary.json"),
    }))


if __name__ == "__main__":
    main()
