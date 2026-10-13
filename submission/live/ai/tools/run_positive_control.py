"""A new explicit-complete positive control, not replacement of original RG-01."""
from pathlib import Path
import copy
import hashlib
import json
from run import call, AI, INPUT

fixture=copy.deepcopy(json.loads((INPUT/'U2-fixtures.json').read_text(encoding='utf-8'))[0])
fixture.update({'fixture_variant':'LOCAL-RG-01-COMPLETE','evidence_mode':'SIMULATED',
    'environment_allowlisted':True,'actor_verified':True,'revision':'synthetic-fixture-revision-1',
    'source_versions':{'REQ-PACKET-AOCE':'synthetic-contract-v1','POLICY-PACKET-AOCE':'synthetic-policy-v1'},
    'source_note':'Additional explicitly defined synthetic harness fixture; not an actual app run or SHA.'})
fixture['runner'].update({'revision':'synthetic-fixture-revision-1','actor':'HR Admin','environment':'isolated-lab',
    'employee_id':fixture['employee_id'],'unique_id_assertion':True,'exact_search_id_assertion':fixture['employee_id'],
    'department_assertion':'QA','cleanup_owned_id':fixture['employee_id'],'cleanup_owner_run':'r02','cleanup':'success'})
(INPUT/'U2-positive-complete.json').write_text(json.dumps(fixture,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources={}
for version in ['v1','v3']:
    # Same original version-specific prompt and common harness; only missing positive input fields are supplied.
    original=(INPUT/f'U2-{version}-RG-01.txt').read_text(encoding='utf-8')
    text=original.split('FIXTURE:\n')[0]+'FIXTURE:\n'+json.dumps(fixture,ensure_ascii=False,indent=2)+'\n'
    file=INPUT/f'U2-{version}-RG-01-complete.txt'; file.write_text(text,encoding='utf-8')
    sources[file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
(AI/'positive-control-protocol.json').write_text(json.dumps({'scope':'Additional complete positive control, original eight-fixture results retained',
    'reason':'Original RG01 input said id_assertion=true but did not explicitly name uniqueness/exact-search ID or matching revision. Model rightly requested more evidence.',
    'new_fixture':'LOCAL-RG-01-COMPLETE','source_type':'SYNTHETIC harness extension, no fabricated live telemetry','input_hashes':sources},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for version in ['v1','v3']:
    measurement=call(f'U2-{version}-RG-01-complete',INPUT/f'U2-{version}-RG-01-complete.txt',INPUT/'decision.schema.json')
    if measurement['exit_code']: raise SystemExit(1)
