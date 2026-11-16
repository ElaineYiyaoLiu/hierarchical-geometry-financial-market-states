"""Independent journal recount for this synthetic PL reproduction, Python 3.14.

Run from the repository root after regenerating or decompressing both journals.
This checks coverage flags from interval endpoints and known toy targets; it
does not certify statistical coverage or choose production settings.
"""

import json
import math
import sys
from collections import Counter
from pathlib import Path


def main():
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Actual Python 3.14 required")
    root = Path(__file__).resolve().parent
    expanded_counts = Counter()
    sensitivity_counts = Counter()
    targets = {"symmetric_uniform": 0.0, "two_point": 0.25, "skewed_beta": -1.4}
    seen = set()
    for line in (root / "expanded/attempts.jsonl").read_text().splitlines():
        row = json.loads(line)["result"]
        scenario, size, index = row["scenario"], row["sample_size"], row["trial_index"]
        key = (scenario, size, index)
        assert key not in seen and scenario in targets and size in (24, 100)
        assert type(index) is int and 0 <= index < 400
        seen.add(key)
        low, high = row["lower"], row["upper"]
        assert all(math.isfinite(x) for x in (low, high, row["point_estimate"]))
        assert low <= high
        covered = low <= targets[scenario] <= high
        assert type(row["covered"]) is bool and row["covered"] == covered
        expanded_counts[scenario, size] += int(covered)
    assert len(seen) == 2400
    expanded_summary = json.loads((root / "expanded/summary.json").read_text())
    for cell in expanded_summary["cells"]:
        assert cell["completed_trials"] == 400
        assert expanded_counts[cell["scenario"], cell["sample_size"]] == cell["covered_trials"]

    seen = set()
    for line in (root / "sensitivity/attempts.jsonl").read_text().splitlines():
        row = json.loads(line)["result"]
        scenario, index = row["scenario"], row["trial_index"]
        key = (scenario, index)
        assert key not in seen and type(index) is int and 0 <= index < 200
        seen.add(key)
        assert len(row["statuses"]) == row["attempted"] == 60
        assert set(row["statuses"]) <= {"SUCCEEDED", "FAILED"}
        assert row["statuses"].count("SUCCEEDED") == row["succeeded"]
        assert row["statuses"].count("FAILED") == row["failed"]
        sensitivity_counts[scenario, "failed"] += row["failed"]
        if not row["calculable"]:
            assert row["succeeded"] == 0
            continue
        low, high = row["lower"], row["upper"]
        assert all(math.isfinite(x) for x in (low, high, row["estimate"])) and low <= high
        target = 1 / 3 if scenario == "score_dependent_failure" else 0.0
        assert scenario in {"independent_failure", "score_dependent_failure", "shared_random_shift"}
        assert row["conditional_target"] == target and row["all_attempt_target"] == 0.0
        assert row["contains_conditional_target"] == (low <= target <= high)
        assert row["contains_all_attempt_target"] == (low <= 0.0 <= high)
        sensitivity_counts[scenario, "calculable"] += 1
        sensitivity_counts[scenario, "target_covered"] += int(low <= target <= high)
        sensitivity_counts[scenario, "zero_covered"] += int(low <= 0.0 <= high)
    assert len(seen) == 600
    summary = json.loads((root / "sensitivity/summary.json").read_text())
    for cell in summary["results"]:
        name = cell["scenario"]
        assert cell["completed_trials"] == 200
        assert cell["failed_attempts"] == sensitivity_counts[name, "failed"]
        assert cell["successful_interval_trials"] == sensitivity_counts[name, "calculable"]
        assert cell["conditional_target_covered"] == sensitivity_counts[name, "target_covered"]
        assert cell["all_attempt_target_covered"] == sensitivity_counts[name, "zero_covered"]
    print(json.dumps({
        "status": "INDEPENDENT_RECOUNT_PASSED",
        "expanded_records": 2400,
        "sensitivity_records": 600,
        "checks": "coverage recomputed from endpoints and analytic toy targets; failure status counts recounted",
        "shared_shift_warning": "zero is the marginal across-shift target, not the mean conditional on a fixed realized shift",
    }, indent=2))


if __name__ == "__main__":
    main()
