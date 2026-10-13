"""Audit Git blobs and staged/working source without ever printing known secret values."""
from pathlib import Path
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from github import credential

TOOLS=Path(__file__).resolve().parent
CI=TOOLS.parent
WORK=CI.parents[2]
LAB=WORK/'aoce-live-lab'
def git(*args): return subprocess.check_output(['git','-C',str(LAB),*args])
secrets=[credential()]
for line in (LAB/'.env').read_text(encoding='utf-8').splitlines():
    if line.startswith(('LAB_PASSWORD=','LAB_VIEWER_PASSWORD=')): secrets.append(line.split('=',1)[1])
for file in (LAB/'.lab/grants').glob('*.json'):
    secrets.append(json.loads(file.read_text(encoding='utf-8'))['token'])
findings=[]
def forbidden(name):
    return name=='.env' or any(name.startswith(p) for p in ['.lab/','node_modules/','playwright/.auth/','test-results/','playwright-report/']) or name.endswith(('/auth.json','/trace.zip'))
def inspect(name,data):
    if forbidden(name): findings.append({'path':name,'reason':'private/auth/raw-artifact path'})
    if any(value and value.encode() in data for value in secrets): findings.append({'path':name,'reason':'known secret present (value not logged)'})
    if re.search(rb'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',data):
        findings.append({'path':name,'reason':'credential/private-key pattern'})
objects=git('rev-list','--objects','--all').decode('utf-8').splitlines()
blobs=0
for line in objects:
    if ' ' not in line: continue
    oid,name=line.split(' ',1)
    kind=git('cat-file','-t',oid).decode().strip()
    if kind=='blob': blobs+=1; inspect(name,git('cat-file','blob',oid))
tracked=git('ls-files','--cached','--others','--exclude-standard','-z').decode('utf-8').split('\0')
for name in filter(None,tracked):
    file=LAB/name
    if file.is_file(): inspect(name,file.read_bytes())
result={'scope':'PUBLIC REPO HISTORY + CURRENT TRACKED FILE AUDIT','generated_at':datetime.now(timezone.utc).isoformat(),
  'reviewed_git_blobs':blobs,'known_secret_values_checked':len(secrets),'findings':findings,'safe_to_publish':not findings}
(CI/'publication-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['scope','reviewed_git_blobs','known_secret_values_checked','findings','safe_to_publish']},indent=2))
sys.exit(1 if findings else 0)
