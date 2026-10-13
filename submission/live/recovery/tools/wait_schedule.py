"""Observe actual GitHub schedule events; never dispatch or synthesize an event."""
from pathlib import Path
from datetime import datetime,timezone
import importlib.util
import json
import time
import sys

REC=Path(__file__).resolve().parents[1]
helper=REC.parent/'ci/tools/github.py'
spec=importlib.util.spec_from_file_location('aoce_github',helper); github=importlib.util.module_from_spec(spec);spec.loader.exec_module(github)
revision=sys.argv[1]
start=time.monotonic(); last=None
while time.monotonic()-start<3600:
    data=github.request('GET','/repos/huyduong20102004/aoce-live-lab/actions/workflows/schedule-verification.yml/runs?event=schedule&per_page=10')
    (REC/'scheduled-verification-runs.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    runs=[r for r in data['workflow_runs'] if r['head_sha']==revision]
    state=[{k:r.get(k) for k in ['id','event','status','conclusion','head_sha','html_url','created_at']} for r in runs]
    if state!=last:
        print(json.dumps({'observed_at':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':int(time.monotonic()-start),'runs':state}),flush=True);last=state
    else:print('Waiting for actual schedule event; elapsed='+str(int(time.monotonic()-start))+'s',flush=True)
    for run in runs:
        if run['status']=='completed' and run['conclusion']=='success':
            (REC/'scheduled-run.json').write_text(json.dumps(run,indent=2)+'\n',encoding='utf-8');sys.exit(0)
        if run['status']=='completed' and run['conclusion']=='failure':
            (REC/'scheduled-failed-run.json').write_text(json.dumps(run,indent=2)+'\n',encoding='utf-8');sys.exit(1)
    time.sleep(30)
print('No successful actual scheduled run observed within observer budget. Keep status PENDING, not passed.',flush=True)
sys.exit(2)
