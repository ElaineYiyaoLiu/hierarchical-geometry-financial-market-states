"""Public arithmetic fixtures only. Run with Python 3.14; no randomness or research generator."""
import csv
from hashlib import sha256
import io
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parent
FEATURES = ['3M','6M','1Y','2Y','3Y','5Y','7Y','10Y','15Y','20Y','30Y','AUX']

def encoded(x):
    return (json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)+'\n').encode()

def digest(x):
    return sha256(x).hexdigest()

def produce():
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError('Python 3.14 required')
    out = {}
    catalog = []
    for family in ('regular', 'duplicates', 'constant_profiles'):
        dataset = 'D'+{'regular':'0000000000000010','duplicates':'0000000000000020','constant_profiles':'0000000000000030'}[family]
        for split, count, offset in [('train',8,0),('validation',5,20),('test',5,40)]:
            order = [f'fixture_{split}_{i:02d}' for i in range(count)]
            rows=[]
            for i in range(count):
                k = i//2 if family=='duplicates' else i
                values = ([str(k+offset)]*12 if family=='constant_profiles' else
                          [str(((k+offset+1)*(j+3)+k*k+2*j*j)%29-14) for j in range(12)])
                rows.append([order[i], *values])
            stream=io.StringIO(newline='')
            writer=csv.writer(stream,lineterminator='\n')
            writer.writerows([['sample_id',*FEATURES],*rows])
            content=stream.getvalue().encode()
            stem=f'data/{family}/{dataset}_{split}'
            record=dict(dataset_id=dataset,split=split,feature_columns=FEATURES,aux_feature_type='volatility',
                        feature_units=['public_arithmetic_fixture_unit']*12,feature_order_version='week10-fixture-v1',
                        schema_version='week10-fixture-v1',row_count=count,column_count=12,
                        sample_order_checksum=digest(encoded(order)),file_checksum=digest(content))
            manifest=encoded(record)
            out[stem+'.csv']=content
            out[stem+'.json']=manifest
            catalog.append(dict(family=family,csv=stem+'.csv',manifest=stem+'.json',dataset_id=dataset,
                                split=split,csv_sha256=digest(content),manifest_sha256=digest(manifest),
                                rows=count,expected_loader='accept',scientific_authorization=False))
    out['catalog.json']=encoded(dict(scope='development_only',construction='Public integer formula in build_fixtures.py; no random seed, hidden condition, or research dataset.',cases=catalog))
    return out

if __name__=='__main__':
    output=produce()
    for name, content in output.items():
        path=ROOT/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(content)
    (ROOT/'generation_receipt.json').write_bytes(encoded(dict(python=platform.python_version(),implementation=platform.python_implementation(),files={k:digest(v) for k,v in output.items()},scientific_authorization=False)))
    print(f'Wrote {len(output)} deterministic fixture files using Python {platform.python_version()}')
