"""Branch B gate evidence checker (Python 3.14).

Checks explicit, human-reviewed evidence assertions only. It does not infer
approval from file existence, filenames, timestamps, scientific metrics, or
other side channels, and it does not grant protocol authorization.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIREMENTS = {
    "pre_pilot": (
        "method_cards_complete", "golden_tests_passed",
        "valuation_sanity_gate_passed", "selection_rule_frozen",
        "pilot_sentinel_registry_frozen", "sealed_pilot_truth_path_approved",
        "dual_pilot_exchange_approval",
    ),
    "pilot_exit": (
        "pilot_outputs_frozen", "escalation_reconciled",
        "compute_benchmark_recorded", "sealed_release_signed",
        "pilot_reproducibility_audited", "pilot_exit_approved",
    ),
    "gate_5a": (
        "bounded_revision_approved", "revision_checksums_frozen",
        "calibration_seed_release_authorized",
    ),
    "calibration": (
        "gate_5a_satisfied", "official_calibration_bank_complete",
        "frozen_pipeline_used", "calibration_failures_accounted",
        "thresholds_from_test_support_only", "thresholds_frozen",
        "calibration_approval",
    ),
    "common_fitter": (
        "calibration_thresholds_frozen", "blind_validation_authorized",
        "all_eligible_fitters_processed", "frozen_neutral_rule_applied",
        "missing_failure_tie_handling_applied", "fitter_selection_frozen",
        "thresholds_mechanically_activated", "runner_certified",
        "independent_processing_approved",
    ),
}


def inspect(evidence: dict[str, object]) -> dict[str, object]:
    """Return evidence completeness, not a gate decision or authorization."""
    result: dict[str, object] = {}
    for gate, requirements in REQUIREMENTS.items():
        entries = evidence.get(gate, {})
        if not isinstance(entries, dict):
            entries = {}
        confirmed = []
        unresolved = []
        for key in requirements:
            item = entries.get(key)
            # Require a documented human assertion and an evidence reference.
            if (
                isinstance(item, dict)
                and item.get("verified") is True
                and isinstance(item.get("evidence_ref"), str)
                and bool(item["evidence_ref"].strip())
            ):
                confirmed.append(key)
            else:
                unresolved.append(key)
        result[gate] = {
            "documented": confirmed,
            "unverified": unresolved,
            "evidence_complete": not unresolved,
            "authorization": "NOT_GRANTED_BY_THIS_TOOL",
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_json", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    evidence = json.loads(args.evidence_json.read_text(encoding="utf-8"))
    if not isinstance(evidence, dict):
        parser.error("Top-level evidence JSON must be an object")
    output = json.dumps(inspect(evidence), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
