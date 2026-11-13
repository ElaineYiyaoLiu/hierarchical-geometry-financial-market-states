"""Run from repository root: python -m branch_b.integration.week10.verify."""
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import platform
import sys

import numpy as np
from jsonschema import Draft202012Validator
from branch_b.failures import BranchBFailure, FailureCode
from branch_b.geometries import correlation_dissimilarity
from branch_b.observable_input import load_development_observable
from validator.validate import validate_observable
from .build_fixtures import produce, encoded

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]

def verify():
    if sys.version_info[:2] != (3,14):
        raise RuntimeError('Python 3.14 required')
    expected=produce()
    for name, content in expected.items():
        assert (ROOT/name).read_bytes()==content, f'fixture reproduction mismatch: {name}'
    receipt=json.loads((ROOT/'generation_receipt.json').read_text())
    assert receipt['python']=='3.14.7'
    assert receipt['files']=={k:sha256(v).hexdigest() for k,v in expected.items()}
    catalog=json.loads(expected['catalog.json'])
    schema=json.loads((REPO/'interface_package/observable_dataset.schema.json').read_text())
    loaded={}
    count=0
    for case in catalog['cases']:
        record=json.loads(expected[case['manifest']])
        Draft202012Validator(schema).validate(record)
        assert not validate_observable(record,(ROOT/case['csv']).parent)
        args=dict(csv_bytes=expected[case['csv']],manifest_bytes=expected[case['manifest']],
                  expected_csv_sha256=case['csv_sha256'],expected_manifest_sha256=case['manifest_sha256'],
                  expected_dataset_id=case['dataset_id'],expected_split=case['split'],expected_schema_version='week10-fixture-v1')
        item=load_development_observable(**args)
        assert item.values.shape==(case['rows'],12)
        assert not item.values.flags.writeable and item.scientific_authorization is False
        loaded[(case['family'],case['split'])]=(item,args)
        count+=1
    base,args=loaded[('regular','train')]
    def rejects(supplied, code):
        try:
            load_development_observable(**supplied)
        except BranchBFailure as exc:
            assert exc.code==code, (exc.code,code)
        else:
            raise AssertionError(f'expected {code}')
    bad=deepcopy(args); bad['expected_csv_sha256']='0'*64
    rejects(bad,FailureCode.CHECKSUM_MISMATCH)
    bad=deepcopy(args); bad['expected_manifest_sha256']='0'*64
    rejects(bad,FailureCode.CHECKSUM_MISMATCH)
    bad=deepcopy(args); bad['expected_split']='test'
    rejects(bad,FailureCode.INPUT_SCHEMA)
    # Rebind checksums to ensure the parser, rather than the hash gate, sees each malformed input.
    import csv,io
    rows=list(csv.reader(io.StringIO(args['csv_bytes'].decode())))
    for mutation,code in [('nonfinite',FailureCode.NONFINITE_INPUT),('duplicate_id',FailureCode.INPUT_SCHEMA),('header',FailureCode.INPUT_SCHEMA),('short_row',FailureCode.INPUT_SCHEMA)]:
        changed=deepcopy(rows)
        if mutation=='nonfinite': changed[1][1]='nan'
        elif mutation=='duplicate_id': changed[2][0]=changed[1][0]
        elif mutation=='header': changed[0][1]='unexpected'
        else: changed[1].pop()
        s=io.StringIO(newline=''); csv.writer(s,lineterminator='\n').writerows(changed)
        b=s.getvalue().encode(); m=json.loads(args['manifest_bytes'])
        m['file_checksum']=sha256(b).hexdigest()
        m['sample_order_checksum']=sha256(encoded([r[0] for r in changed[1:]])).hexdigest()
        mb=encoded(m); supplied=deepcopy(args)
        supplied.update(csv_bytes=b,manifest_bytes=mb,expected_csv_sha256=sha256(b).hexdigest(),expected_manifest_sha256=sha256(mb).hexdigest())
        rejects(supplied,code)
    # Train-only preprocessing feeds the two registered coordinate geometries.
    from branch_b.preprocessing import Standardizer
    from branch_b.geometries import euclidean_dissimilarity, chebyshev_dissimilarity
    from branch_b.normalization import normalize_dissimilarity
    regular_train,_=loaded[('regular','train')]
    scaler=Standardizer.fit(regular_train.values)
    saved_mean=scaler.mean_.copy(); saved_scale=scaler.scale_.copy()
    geometry_checks=0
    for split in ('train','validation','test'):
        item,_=loaded[('regular',split)]
        z=scaler.transform(item.values)
        np.testing.assert_allclose(z,(item.values-saved_mean)/saved_scale)
        for metric in (euclidean_dissimilarity,chebyshev_dissimilarity):
            d=normalize_dissimilarity(metric(z))
            assert d.shape==(item.values.shape[0],)*2
            assert np.isfinite(d).all() and np.max(d)==1.0
            geometry_checks+=1
    np.testing.assert_array_equal(scaler.mean_,saved_mean)
    np.testing.assert_array_equal(scaler.scale_,saved_scale)
    constant,_=loaded[('constant_profiles','train')]
    try: correlation_dissimilarity(constant.values)
    except BranchBFailure as exc: assert exc.code==FailureCode.DEGENERATE_DISTANCE
    else: raise AssertionError('constant correlation must fail')
    dup,_=loaded[('duplicates','train')]
    np.testing.assert_array_equal(dup.values[0],dup.values[1])
    assert dup.sample_order[0]!=dup.sample_order[1]
    cases={x['id']:x for x in json.loads((ROOT/'worked_cases.json').read_text())['cases']}
    occ=cases['D06-occurrences']; masses=[occ['draw_original_ids'].count(x) for x in occ['original_ids']]
    assert masses==occ['expected_masses']
    from itertools import combinations
    weights=[masses[i]*masses[j] for i,j in combinations(range(3),2)]
    assert weights==occ['expected_pair_weights'] and sum(weights)==occ['expected_W']
    tol=cases['D07-boundary']; assert [x<=tol['candidate_tolerance'] for x in tol['values']]==tol['expected_le_candidate']
    assert [x<tol['candidate_tolerance'] for x in tol['values']]==tol['expected_lt_candidate']
    c=cases['D08-correlation']; assert [len(set(x))==1 for x in c['profiles']]==c['expected_exact_constant']
    c=cases['D11-selection']; assert c['candidates'][0] | {'name':'fixture-b'}==c['candidates'][1]
    c=cases['D12-D13-bootstrap']; q=sorted(x['Q'] for x in c['attempts'] if x['status']=='success')
    assert len(c['attempts'])==c['expected_attempt_count'] and len(q)==c['expected_success_count']
    assert q==c['expected_sorted_success_Q'] and math.isclose(sum(q)/len(q),c['expected_success_mean'])
    assert 1-len(q)/len(c['attempts'])==c['expected_failure_fraction']
    c=cases['D15-quantile']; values=sorted(c['successful_values']); index=math.ceil(c['illustrative_p']*len(values))
    assert index==c['expected_inverse_ecdf_one_based_index'] and values[index-1]==c['expected_inverse_ecdf_value']
    assert (values[1]+values[2])/2==c['expected_linear_midpoint_value']
    c=cases['D16-D17-comparison']; pairs=[x for x in c['paired_replicates'] if x['left'] is not None and x['right'] is not None]
    assert len(pairs)==c['expected_complete_pair_count']
    np.testing.assert_allclose([x['left']-x['right'] for x in pairs],c['expected_complete_differences'],atol=1e-15,rtol=0)
    # G2 and G4 use the already public mathematical reference, never a production optimizer.
    from branch_b.recovery_tests.test_week9_objective_reference import _closure,_objective
    c=cases['G2']; assert _closure(3,c['working_weights'])==c['expected_minmax']
    assert _objective([0,0,0],[1,1,1],[2,3,1])==3
    return dict(python=platform.python_version(),numpy=np.__version__,valid_observable_files=count,
                negative_loader_cases=7,train_only_geometry_checks=geometry_checks,constant_correlation_rejected=True,worked_cases_mechanically_checked=8,
                scientific_authorization=False,status='pass')

if __name__=='__main__':
    print(json.dumps(verify(),sort_keys=True))
