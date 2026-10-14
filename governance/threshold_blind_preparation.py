"""Preparation checks for complete threshold references and frozen blind activation."""
from __future__ import annotations
import argparse
import itertools
import json
import math
from pathlib import Path
from later_stage_audit import evidence

THRESHOLD_REFS = ("calibration_manifest", "processing_config", "test_support_output",
                  "within_dataset_selection_rule", "failure_accounting", "threshold_rule",
                  "PL_approval", "Faculty_approval", "threshold_registry")
BLIND_REFS = ("selection_rule", "blind_input_manifest", "selection_audit",
              "bank_separation_attestation", "threshold_registry", "configuration_registry")

def names(values):
    if not isinstance(values,list) or not values or any(not isinstance(x,str) or not x.strip() for x in values) or len(set(values))!=len(values):
        raise ValueError("nonempty unique frozen registry required")
    return values

def trace(record, root):
    for ref in record["registered_set_references"]: evidence(root,ref)
    if not record["registered_set_references"]: raise ValueError("frozen set references required")
    expected=set(itertools.product(names(record["geometries"]),names(record["candidate_fitters"]),names(record["null_families"])))
    keys=[]
    for row in record["rows"]:
        keys.append((row["geometry_id"],row["candidate_fitter_id"],row["null_family"]))
        for key in THRESHOLD_REFS: evidence(root,row[key])
        value=row["threshold_value"]
        if type(value) not in (int,float) or not math.isfinite(value):
            raise ValueError("finite recorded threshold required")
        if not isinstance(row["freeze_id"],str) or not row["freeze_id"].strip():
            raise ValueError("actual freeze reference required")
        planned=row["planned_count"]
        if type(planned) is not int or planned<=0:
            raise ValueError("positive scheduled denominator required")
        for key in ("successful_count","failed_count","indeterminate_count"):
            count=row[key]
            if type(count) is not int or not 0<=count<=planned:
                raise ValueError("recorded count outside scheduled denominator")
        # Denominator classification is scientific: verify against frozen accounting in review.
    if len(set(keys))!=len(keys) or set(keys)!=expected:
        raise ValueError("each registered geometry/fitter/null family requires exactly one trace row")
    return {"decision":"REVIEWABLE","trace_rows":len(keys),"thresholds_approved":False,
            "percentile_and_family_max_rule_independently_verified":False,
            "failure_accounting_independently_verified":False,"blind_handoff_authorized":False}

def blind(record,root):
    for key in BLIND_REFS: evidence(root,record[key])
    fitters=names(record["registered_candidate_fitters"])
    selected=record["selected_fitter"]
    if selected not in fitters: raise ValueError("selection outside frozen candidate set")
    if record["permitted_input"]!="observable_only" or record["truth_keyed_selection"] is not False or record["threshold_recalibration"] is not False:
        raise ValueError("blind-only selection without recalibration required")
    geometries=names(record["registered_geometries"])
    frozen=record["precomputed_thresholds"]
    if set(frozen)!=set(geometries):raise ValueError("geometry registry mismatch")
    selected_values={}
    for geometry in geometries:
        if set(frozen[geometry])!=set(fitters):raise ValueError("incomplete geometry/fitter threshold matrix")
        for value in frozen[geometry].values():
            if type(value) not in (int,float) or not math.isfinite(value):
                raise ValueError("finite precomputed threshold required")
        selected_values[geometry]=frozen[geometry][selected]
    active=record["activated_thresholds"]
    if set(active)!=set(geometries) or any(type(active[g]) not in (int,float) or not math.isfinite(active[g]) or active[g]!=selected_values[g] for g in geometries):
        raise ValueError("activation must retain exactly the selected precomputed thresholds")
    return {"decision":"REVIEWABLE","selected_fitter_recorded":True,
            "fitter_selection_approved":False,"permitted_input_independently_verified":False,
            "threshold_registry_contents_independently_verified":False,
            "independent_processing_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=("trace","blind"),required=True)
    p.add_argument("--record",type=Path,required=True)
    p.add_argument("--evidence-root",type=Path,default=Path("."))
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    try:
        record=json.loads(a.record.read_text())
        result=globals()[a.mode](record,a.evidence_root)
    except (ValueError,KeyError,TypeError,OSError) as exc:
        result={"decision":"BLOCKED","blocker":str(exc),"authorization_granted":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x") as h:
        json.dump(result,h,indent=2,sort_keys=True);h.write("\n")
    print(a.mode+": "+result["decision"]+"; no authorization granted")

if __name__=="__main__":main()
