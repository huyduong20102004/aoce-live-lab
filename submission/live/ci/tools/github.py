"""GitHub REST via existing Git Credential Manager; never log/store credential values."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import urllib.request
import urllib.error
import zipfile

REPO='huyduong20102004/aoce-live-lab'
def credential():
    env=os.environ.copy(); env.update(GCM_INTERACTIVE='Never',GIT_TERMINAL_PROMPT='0')
    result=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\nusername=huyduong20102004\n\n',
        capture_output=True,text=True,env=env,timeout=20)
    fields=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
    if result.returncode or not fields.get('password'): raise RuntimeError('GitHub credential unavailable; interactive sign-in required')
    return fields['password']
def request(method,path,body=None):
    token=credential()
    url='https://api.github.com'+path
    req=urllib.request.Request(url,method=method,headers={'User-Agent':'AOCE-lab-automation',
        'Accept':'application/vnd.github+json','Authorization':'Bearer '+token,'Content-Type':'application/json'},
        data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req,timeout=30) as response:
            data=response.read(); return json.loads(data) if data else {'http_status':response.status}
    except urllib.error.HTTPError as error:
        data=error.read().decode('utf-8',errors='replace')
        raise RuntimeError(f'GitHub API {method} {path}: HTTP{error.code}: {data.replace(token,"[REDACTED]")}') from None
def download_artifact(artifact_id,destination):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,req,fp,code,msg,headers,newurl): return None
    token=credential()
    req=urllib.request.Request(f'https://api.github.com/repos/{REPO}/actions/artifacts/{artifact_id}/zip',
        headers={'User-Agent':'AOCE-lab-automation','Authorization':'Bearer '+token,'Accept':'application/vnd.github+json'})
    opener=urllib.request.build_opener(NoRedirect)
    try:
        response=opener.open(req,timeout=30); content=response.read()
    except urllib.error.HTTPError as error:
        if error.code not in [301,302,303,307,308]: raise RuntimeError('Artifact download failed HTTP'+str(error.code)) from None
        location=error.headers['Location']
        if not location.startswith('https://'): raise RuntimeError('Refuse non-HTTPS artifact redirect')
        # Do not forward GitHub Authorization to signed cloud-storage URLs.
        with urllib.request.urlopen(urllib.request.Request(location,headers={'User-Agent':'AOCE-lab-automation'}),timeout=60) as response:
            content=response.read()
    destination=Path(destination).resolve(); destination.mkdir(parents=True,exist_ok=True)
    zip_path=destination/'artifact.zip'; zip_path.write_bytes(content)
    with zipfile.ZipFile(zip_path) as archive:
        for entry in archive.infolist():
            target=(destination/entry.filename).resolve()
            if destination not in target.parents and target!=destination: raise RuntimeError('Artifact ZIP path escapes extraction directory')
            archive.extract(entry,destination)
    return {'artifact_id':artifact_id,'destination':str(destination),'bytes':len(content)}
if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('method'); parser.add_argument('path'); parser.add_argument('--body-file'); parser.add_argument('--output')
    args=parser.parse_args(); body=json.loads(Path(args.body_file).read_text(encoding='utf-8')) if args.body_file else None
    result=download_artifact(int(args.path),args.output) if args.method=='DOWNLOAD' else request(args.method,args.path,body)
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output and args.method!='DOWNLOAD': Path(args.output).parent.mkdir(parents=True,exist_ok=True); Path(args.output).write_text(text,encoding='utf-8')
    else: print(text)
