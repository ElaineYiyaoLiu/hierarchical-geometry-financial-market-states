"""Week 5–8 operational audits. Supplied evidence consistency never grants authority."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

COVERAGE = {"primary", "structural_variant", "locked_null", "registered_geometries",
            "required_subsamples", "bootstrap", "reconciliation", "frozen_evaluation"}

def evidence(root, ref):
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256", "byte_count"}:
        raise ValueError("exact path/checksum/byte-count evidence required")
    relative = Path(ref["path"])
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError("relative contained evidence path required")
    path = root / relative
    if any(p.is_symlink() for p in [root, *path.parents, path]) or not path.is_file():
        raise ValueError("evidence must be a real contained file")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("evidence outside root")
    raw = path.read_bytes()
    if type(ref["byte_count"]) is not int or ref["byte_count"] != len(raw):
        raise ValueError("evidence byte count mismatch")
    if not isinstance(ref["sha256"], str) or not re.fullmatch("[a-f0-9]{64}", ref["sha256"]) or hashlib.sha256(raw).hexdigest() != ref["sha256"]:
        raise ValueError("evidence checksum mismatch")

def number(value, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError("finite nonnegative number required")
    return value

def receipt(record, root):
    planned = record["planned_ids"]
    if not planned or any(not isinstance(x, str) or not re.fullmatch("D[0-9a-f]{16}", x) for x in planned) or len(set(planned)) != len(planned):
        raise ValueError("unique opaque planned dataset IDs required")
    outcomes = record["outcomes"]
    ids = [r["dataset_id"] for r in outcomes]
    if len(set(ids)) != len(ids) or set(ids) - set(planned):
        raise ValueError("duplicate or unscheduled output")
    for ref in record["frozen_references"]: evidence(root, ref)
    if not record["frozen_references"]: raise ValueError("frozen configuration/manifest references required")
    for row in outcomes:
        if row["status"] == "success":
            if row.get("failure_code") is not None: raise ValueError("success cannot claim failure")
            evidence(root, row["observable_manifest"])
            evidence(root, row["sealed_truth_receipt"])
        elif row["status"] == "failure":
            if row.get("failure_code") not in record["registered_failure_codes"]:
                raise ValueError("failure outside supplied frozen code registry")
            if row.get("observable_manifest") is not None or row.get("sealed_truth_receipt") is not None:
                raise ValueError("failure cannot claim successful output")
        else: raise ValueError("terminal scientific outcome required")
    missing = sorted(set(planned)-set(ids))
    return {"decision": "REVIEWABLE" if not missing else "BLOCKED",
            "planned": len(planned), "successes": sum(r["status"]=="success" for r in outcomes),
            "failures": sum(r["status"]=="failure" for r in outcomes), "missing": missing,
            "truth_contents_inspected": False, "continuation_authorized": False}

def capacity(record, root):
    for ref in record["benchmark_references"]: evidence(root, ref)
    if not record["benchmark_references"]: raise ValueError("actual throughput evidence required")
    coverage = set()
    hours, storage = 0.0, 0.0
    stages = record["stages"]
    if not stages or len({s["stage_id"] for s in stages}) != len(stages):
        raise ValueError("unique nonempty workload stages required")
    for s in stages:
        coverage.update(s["coverage"])
        jobs = s["planned_jobs"]
        if type(jobs) is not int or jobs <= 0: raise ValueError("positive planned job count required")
        parallel = number(s["effective_parallelism"], True)
        if parallel > jobs: raise ValueError("parallelism exceeds scheduled jobs")
        # Conservative full-wave ceiling; partial final waves still consume job duration.
        hours += math.ceil(jobs/parallel)*number(s["measured_seconds_per_job"], True)/3600
        hours += number(s["queue_hours"])+number(s["storage_io_hours"])
        storage += jobs*number(s["bytes_per_job"])
    if coverage != COVERAGE: raise ValueError("full frozen workload coverage required")
    contingency = number(record["time_contingency_fraction"])
    if contingency < 0.25: raise ValueError("minimum 25 percent contingency required")
    required = hours*(1+contingency)
    available = number(record["available_hours"], True)
    storage_available = number(record["storage_available_bytes"], True)
    return {"decision": "REVIEWABLE" if required <= available and storage <= storage_available else "BLOCKED",
            "base_hours": hours, "hours_with_contingency": required, "projected_bytes": storage,
            "scientific_coverage_independently_verified": False, "compute_plan_approved": False,
            "protocol_lock_approved": False}

def allocation(record):
    planned = record["planned_ids"]
    rows = record["allocation"]
    if not planned or len(set(planned)) != len(planned) or any(not isinstance(x,str) or not re.fullmatch("D[0-9a-f]{16}",x) for x in planned):
        raise ValueError("unique opaque planned IDs required")
    ids = [r["dataset_id"] for r in rows]
    if len(set(ids)) != len(ids) or set(ids) != set(planned):
        raise ValueError("each scheduled slot must be allocated once")
    if any(type(r["batch"]) is not int or r["batch"] not in (1,2) for r in rows):
        raise ValueError("only prespecified batches 1 and 2")
    if {r["batch"] for r in rows} != {1,2}: raise ValueError("both batch allocations required")
    return {"decision":"REVIEWABLE", "batch_1":sum(r["batch"]==1 for r in rows),
            "batch_2":sum(r["batch"]==2 for r in rows), "allocation_frozen":False,
            "locked_generation_authorized":False}

def burn(record, root):
    evidence(root, record["approved_capacity_reference"])
    for ref in record["resource_log_references"]: evidence(root, ref)
    if not record["resource_log_references"]: raise ValueError("actual resource logs required")
    available = number(record["remaining_available_hours"], True)
    remaining = number(record["remaining_base_hours"])
    overhead = number(record["remaining_queue_storage_hours"])
    contingency = number(record["time_contingency_fraction"])
    if contingency < .25: raise ValueError("minimum 25 percent contingency required")
    required = (remaining+overhead)*(1+contingency)
    storage_ok = number(record["remaining_required_bytes"]) <= number(record["remaining_storage_bytes"])
    if record["frozen_science_unchanged"] is not True:
        raise ValueError("scientific plan change requires separate scope review")
    return {"decision":"REVIEWABLE" if required<=available and storage_ok else "BLOCKED",
            "remaining_required_hours":required, "continuation_authorized":False,
            "authority_and_scientific_plan_independently_verified":False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("receipt","capacity","allocation","burn"), required=True)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record = json.loads(args.record.read_text())
    try:
        result = allocation(record) if args.mode=="allocation" else globals()[args.mode](record,args.evidence_root)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        result = {"decision":"BLOCKED", "blocker":str(exc), "authorization_granted":False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.mode+": "+result["decision"]+"; no authorization granted")

if __name__ == "__main__": main()
