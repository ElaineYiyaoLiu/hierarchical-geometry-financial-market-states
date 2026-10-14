import copy
import hashlib
import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location("later",Path(__file__).with_name("later_stage_audit.py"))
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def ref(tmp_path):
    p=tmp_path/"dummy.txt"
    p.write_bytes(b"dummy operational fixture")
    return {"path":p.name,"byte_count":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}

def receipt(tmp_path):
    r=ref(tmp_path)
    return {"planned_ids":["D0000000000000000","D0000000000000001"],"frozen_references":[r],
            "registered_failure_codes":["DUMMY_FAILURE"],"outcomes":[
            {"dataset_id":"D0000000000000000","status":"success","observable_manifest":r,"sealed_truth_receipt":r},
            {"dataset_id":"D0000000000000001","status":"failure","failure_code":"DUMMY_FAILURE"}]}

def model(tmp_path):
    return {"benchmark_references":[ref(tmp_path)],"stages":[{"stage_id":"dummy","coverage":sorted(mod.COVERAGE),
        "planned_jobs":3,"effective_parallelism":2,"measured_seconds_per_job":3600,"queue_hours":1,
        "storage_io_hours":1,"bytes_per_job":100}],"time_contingency_fraction":.25,
        "available_hours":5,"storage_available_bytes":300}

def test_receipt_keeps_failed_denominator(tmp_path):
    result=mod.receipt(receipt(tmp_path),tmp_path)
    assert result["decision"]=="REVIEWABLE" and result["planned"]==2
    assert result["successes"]==result["failures"]==1
    assert not result["continuation_authorized"] and not result["truth_contents_inspected"]

@pytest.mark.parametrize("case",["duplicate","unscheduled","invalid_failure","success_failure","tampered"])
def test_receipt_rejects_inconsistent_evidence(tmp_path,case):
    r=receipt(tmp_path)
    if case=="duplicate": r["outcomes"].append(copy.deepcopy(r["outcomes"][0]))
    elif case=="unscheduled": r["outcomes"][0]["dataset_id"]="D0000000000000002"
    elif case=="invalid_failure": r["outcomes"][1]["failure_code"]="UNKNOWN"
    elif case=="success_failure": r["outcomes"][0]["failure_code"]="DUMMY_FAILURE"
    else: (tmp_path/"dummy.txt").write_bytes(b"tampered")
    with pytest.raises(ValueError): mod.receipt(r,tmp_path)

def test_receipt_missing_blocks(tmp_path):
    r=receipt(tmp_path);r["outcomes"].pop()
    assert mod.receipt(r,tmp_path)["decision"]=="BLOCKED"

def test_capacity_full_waves_and_contingency(tmp_path):
    r=mod.capacity(model(tmp_path),tmp_path)
    assert r["hours_with_contingency"]==5 and r["projected_bytes"]==300
    assert r["decision"]=="REVIEWABLE" and not r["compute_plan_approved"]

@pytest.mark.parametrize("case",["low_contingency","missing_coverage","nan","boolean_count","parallelism"])
def test_capacity_malformed_blocks(tmp_path,case):
    r=model(tmp_path)
    if case=="low_contingency":r["time_contingency_fraction"]=.249
    elif case=="missing_coverage":r["stages"][0]["coverage"].remove("bootstrap")
    elif case=="nan":r["stages"][0]["measured_seconds_per_job"]=float("nan")
    elif case=="boolean_count":r["stages"][0]["planned_jobs"]=True
    else:r["stages"][0]["effective_parallelism"]=4
    with pytest.raises(ValueError):mod.capacity(r,tmp_path)

@pytest.mark.parametrize("field",["available_hours","storage_available_bytes"])
def test_insufficient_capacity_blocks(tmp_path,field):
    r=model(tmp_path);r[field]=1
    assert mod.capacity(r,tmp_path)["decision"]=="BLOCKED"

def test_allocation_complete_no_freeze():
    r={"planned_ids":["D0000000000000000","D0000000000000001"],
       "allocation":[{"dataset_id":"D0000000000000000","batch":1},{"dataset_id":"D0000000000000001","batch":2}]}
    assert not mod.allocation(r)["allocation_frozen"]
    r["allocation"][1]["dataset_id"]=r["allocation"][0]["dataset_id"]
    with pytest.raises(ValueError):mod.allocation(r)

@pytest.mark.parametrize("case",["absolute","traversal","symlink","boolean_bytes"])
def test_evidence_path_boundary(tmp_path,case):
    r=ref(tmp_path)
    if case=="absolute":r["path"]=str(tmp_path/"dummy.txt")
    elif case=="traversal":r["path"]="../dummy.txt"
    elif case=="symlink":
        (tmp_path/"link").symlink_to(tmp_path/"dummy.txt");r["path"]="link"
    else:r["byte_count"]=True
    with pytest.raises(ValueError):mod.evidence(tmp_path,r)

def test_remaining_capacity_requires_contingency(tmp_path):
    r={"approved_capacity_reference":ref(tmp_path),"resource_log_references":[ref(tmp_path)],
       "remaining_available_hours":5,"remaining_base_hours":3,"remaining_queue_storage_hours":1,
       "time_contingency_fraction":.25,"remaining_required_bytes":100,"remaining_storage_bytes":100,
       "frozen_science_unchanged":True}
    result=mod.burn(r,tmp_path)
    assert result["decision"]=="REVIEWABLE" and not result["continuation_authorized"]
    r["remaining_available_hours"]=4.99
    assert mod.burn(r,tmp_path)["decision"]=="BLOCKED"
