import copy
import hashlib
import importlib.util
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).parent))
spec=importlib.util.spec_from_file_location("trace",Path(__file__).with_name("threshold_blind_preparation.py"))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def ref(tmp_path):
    p=tmp_path/"dummy";p.write_bytes(b"dummy only")
    return {"path":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"byte_count":10}

def trace_record(tmp_path):
    r=ref(tmp_path)
    row={"geometry_id":"fixture-G","candidate_fitter_id":"fixture-F","null_family":"fixture-N",
         "threshold_value":.5,"freeze_id":"fixture","planned_count":10,"successful_count":8,
         "failed_count":2,"indeterminate_count":0,**{k:r for k in mod.THRESHOLD_REFS}}
    return {"registered_set_references":[r],"geometries":["fixture-G"],"candidate_fitters":["fixture-F"],
            "null_families":["fixture-N"],"rows":[row]}

def blind_record(tmp_path):
    r=ref(tmp_path)
    return {**{k:r for k in mod.BLIND_REFS},"registered_candidate_fitters":["fixture-F","fixture-F2"],
            "selected_fitter":"fixture-F","registered_geometries":["fixture-G"],
            "permitted_input":"observable_only","truth_keyed_selection":False,
            "threshold_recalibration":False,"precomputed_thresholds":{"fixture-G":{"fixture-F":.5,"fixture-F2":.7}},
            "activated_thresholds":{"fixture-G":.5}}

def test_complete_trace_is_only_reviewable(tmp_path):
    r=mod.trace(trace_record(tmp_path),tmp_path)
    assert r["decision"]=="REVIEWABLE" and not r["thresholds_approved"]

@pytest.mark.parametrize("case",["duplicate","missing","missing_approval","bad_count","nan"])
def test_trace_inconsistent_blocks(tmp_path,case):
    r=trace_record(tmp_path)
    if case=="duplicate":r["rows"]*=2
    elif case=="missing":r["candidate_fitters"].append("fixture-F2")
    elif case=="missing_approval":r["rows"][0]["Faculty_approval"]=None
    elif case=="bad_count":r["rows"][0]["failed_count"]=11
    else:r["rows"][0]["threshold_value"]=float("nan")
    with pytest.raises(ValueError):mod.trace(r,tmp_path)

def test_mechanical_activation_never_approves(tmp_path):
    r=mod.blind(blind_record(tmp_path),tmp_path)
    assert r["decision"]=="REVIEWABLE" and not r["independent_processing_authorized"]

@pytest.mark.parametrize("case",["recalibration","truth","selection","value","missing_fitter","boolean_threshold"])
def test_blind_violation_blocks(tmp_path,case):
    r=blind_record(tmp_path)
    if case=="recalibration":r["threshold_recalibration"]=True
    elif case=="truth":r["truth_keyed_selection"]=True
    elif case=="selection":r["selected_fitter"]="unknown"
    elif case=="value":r["activated_thresholds"]["fixture-G"]=.6
    elif case=="missing_fitter":r["precomputed_thresholds"]["fixture-G"].pop("fixture-F2")
    else:r["activated_thresholds"]["fixture-G"]=True
    with pytest.raises(ValueError):mod.blind(r,tmp_path)
