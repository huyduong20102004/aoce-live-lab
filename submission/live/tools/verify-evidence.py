"""Independent checks for LOCAL runtime evidence, separate from synthetic ledger."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
import subprocess
import sys

LIVE=Path(__file__).resolve().parents[1]
WORKSPACE=LIVE.parents[1]
LAB=WORKSPACE/'aoce-live-lab'
checks=[]
def check(name,ok,detail): checks.append({'check':name,'status':'OK' if ok else 'ERROR','detail':detail})
def sha(file): return hashlib.sha256(file.read_bytes()).hexdigest()
def load(file): return json.loads(file.read_text(encoding='utf-8-sig'))
def git(*args): return subprocess.check_output(['git','-C',str(LAB),*args],text=True).strip()

revision=git('rev-parse','HEAD')
check('Actual source revision and clean Git tree',len(revision)==40 and not git('status','--porcelain'),revision)
tracked=git('ls-files').splitlines()
check('No credentials/raw auth/state/artifacts tracked',not any(p=='.env' or p.startswith(('.lab/','node_modules/','playwright/.auth/')) for p in tracked),'Only reviewed source paths tracked')
source=load(WORKSPACE/'bai-nop-AOCE/evidence/source-manifest.json')
check('Original source packets unchanged',all(sha(WORKSPACE/item['name'])==item['sha256'] for item in source['files']),'Handout/content hashes match original snapshot')
typecheck=(LIVE/'typecheck.txt').read_text(encoding='utf-8-sig')
regression=(LIVE/'controller-regression.txt').read_text(encoding='utf-8-sig')
check('Actual TypeScript check', 'Exit code: 0' in typecheck and revision in typecheck,'Compiler command and current revision captured')
check('Actual controller regression', 'Exit code: 0' in regression and revision in regression and '# pass 15' in regression and '# fail 0' in regression,'15 deterministic tests incl RG01–08, negative controls and auth redaction; not model calls')
guards=load(LIVE/'runtime-guard-checks.json')
check('Runtime missing-secret/no-tests/forged-trigger gates',guards['code_revision']==revision and all(c['detected'] and c['exit_code']!=0 for c in guards['checks']),'Actual child script exits; no app writes')
runs=[]
for directory in sorted((LIVE/'runs').iterdir()):
    manifest=load(directory/'manifest.json')
    runs.append(manifest)
    subprocess.run(['git','-C',str(LAB),'cat-file','-e',manifest['code_revision']+'^{commit}'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if manifest['label']!='RUN-PASSED': continue
    discovery=load(directory/'discovery.json'); cleanup=load(directory/'cleanup.json'); evidence=load(directory/'evidence-check.json')
    counts=(manifest['selected_count']==manifest['executed_count']==len(manifest['cases'])==discovery['selected_count'])
    cases_ok=all(c['status']=='passed' and c['source_refs'] and c['oracle'] and c['attempt_id']=='a1' for c in manifest['cases'])
    owned_ok=cleanup['run_id']==manifest['run_id'] and cleanup['unresolved_count']==0 and all(r['owner']==manifest['run_id'] and r['record_absent_after'] for r in cleanup['records'])
    art_ok=True
    for case in manifest['cases']:
        if case['kind']=='business-smoke' and not case['artifacts']: art_ok=False
        for artifact in case['artifacts']:
            name=f"{case['flow']}-{hashlib.sha256(case['logical_case_id'].encode()).hexdigest()[:12]}-{artifact['name']}.png"
            file=directory/name
            if not file.is_file() or sha(file)!=artifact['sha256']: art_ok=False
    check('Run evidence integrity '+manifest['run_id'],counts and cases_ok and owned_ok and art_ok and evidence['status']=='COMPLETE',f"revision={manifest['code_revision']}; cases={manifest['executed_count']}; owned IDs={len(cleanup['records'])}; screenshot hashes checked")
current=[r for r in runs if r['code_revision']==revision and r['label']=='RUN-PASSED']
check('Current revision has manual three-flow smoke',any(r['suite']=='smoke' and r['trigger']=='manual-local' and r['selected_count']==3 for r in current),'Actual runner assertions, no discovery-only substitution')
check('Current revision full robustness suite',any(r['suite']=='all' and r['selected_count']==11 for r in current),'3 business cases +8 controls; negative-control passes are detection results')
failed=[r['run_id'] for r in runs if r['label']!='RUN-PASSED']
check('Historical failures retained',bool(failed),', '.join(failed)+'; not overwritten as pass')
scheduled=[r for r in current if r['trigger']=='windows-schedule']
status=load(LIVE/'windows-schedule-status.json') if (LIVE/'windows-schedule-status.json').exists() else {}
check('Actual OS scheduled launch, separate from manual',bool(scheduled) and all(r.get('scheduler_task')=='AOCE-PortalLite-Live-Smoke' for r in scheduled) and status.get('LastTaskResult')==0,'Requires manifest task marker plus observed Task Scheduler result0; no GitHub scheduled claim')
for file in (LIVE/'runs').rglob('*'):
    if file.is_file() and file.suffix in ('.json','.md','.txt'):
        text=file.read_text(encoding='utf-8-sig')
        # Raw headers/credential keys must never be exported. Secret values checked below privately.
        if any(value in text.lower() for value in ('"token":','"password":','lab_session=')):
            check('Export excludes raw auth '+file.name,False,str(file.relative_to(LIVE)))
secrets=[]
for line in (LAB/'.env').read_text().splitlines():
    if line.startswith(('LAB_PASSWORD=','LAB_VIEWER_PASSWORD=')): secrets.append(line.split('=',1)[1])
for file in (LAB/'.lab/grants').glob('*.json'): secrets.append(load(file)['token'])
leaks=[]
for file in LIVE.rglob('*'):
    if file.is_file() and file.suffix in ('.json','.md','.txt'):
        text=file.read_text(encoding='utf-8-sig')
        if any(value and value in text for value in secrets): leaks.append(str(file.relative_to(LIVE)))
check('Export does not contain actual private secrets',not leaks,'Local secret comparison performed without logging secret values')
actual_state=load(LAB/'.lab/state.json')
check('No remaining E2E owned employees',not any(e.get('owner') for e in actual_state['employees']),'State inspected locally; values/credentials not exported')
check('Unowned demo employee preserved',any(e['employeeId']=='EMP-1001' and e['owner'] is None for e in actual_state['employees']),'Cross-owner cleanup negative control protected demo')
missing=[]
paths=list((WORKSPACE/'bai-nop-AOCE').rglob('*.md'))+list((LAB/'docs').rglob('*.md'))+[LAB/'README.md']
for file in paths:
    if (LIVE/'ai/inputs') in file.parents: continue # Immutable original source archive used as prompt input, not a navigation document.
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',file.read_text(encoding='utf-8-sig')):
        if target.startswith(('https://','http://','mailto:','#')): continue
        local=target.split('#')[0].strip('<>')
        if local and not (file.parent/local).exists(): missing.append(str(file.relative_to(WORKSPACE))+': '+target)
check('Submission and lab Markdown links resolve',not missing,'; '.join(missing) if missing else 'Dry-run and live-local references present')
result={'scope':'ACTUAL LOCAL EVIDENCE VALIDATION','generated_at':datetime.now(timezone.utc).isoformat(),'timezone':'UTC+7','revision':revision,'checks':checks,'errors':sum(c['status']=='ERROR' for c in checks)}
(LIVE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# Local live validation','',f"Generated {datetime.now(timezone(timedelta(hours=7))).isoformat()}. Source revision `{revision}`.",'',f"{len(checks)-result['errors']}/{len(checks)} checks OK; {result['errors']} errors.",'','| Check | Actual result | Evidence/limitation |','| --- | --- | --- |']
lines += [f"| {c['check']} | {c['status']} | {c['detail']} |" for c in checks]
lines += ['','No production reliability/provider-price/AI-model benchmark or GitHub hosted run claim. Controller regressions use synthetic input fixtures, but actual checker execution is captured. Windows scheduled evidence is OS-local and needs an active signed-in session and powered-on machine.','']
(LIVE/'validation.md').write_text('\n'.join(lines),encoding='utf-8')
for c in checks: print(c['status']+': '+c['check'])
print(f"{len(checks)-result['errors']}/{len(checks)} OK; errors={result['errors']}")
sys.exit(1 if result['errors'] else 0)
