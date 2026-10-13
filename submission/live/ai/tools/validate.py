"""Independent raw-event, hash, arithmetic, schema and secret validation for AI runs."""
from pathlib import Path
from statistics import median
from datetime import datetime, timezone
import csv
import hashlib
import json
import re
import subprocess
import sys
import jsonschema

AI=Path(__file__).resolve().parents[1]; WORK=AI.parents[2]; LAB=WORK/'aoce-live-lab'
def load(file): return json.loads(file.read_text(encoding='utf-8-sig'))
def sha(file): return hashlib.sha256(file.read_bytes()).hexdigest()
checks=[]
def check(name,ok,detail): checks.append({'check':name,'status':'OK' if ok else 'ERROR','detail':detail})
protocol=load(AI/'protocol.json'); results=load(AI/'results.json')
expected=['U1-'+s for s in protocol['U1_order']]+[f'U2-{v}-{f}' for f in protocol['U2_cases'] for v in protocol['U2_versions']]
supplemental=['U2-v1-RG-01-complete','U2-v3-RG-01-complete']
check('Nine U1 samples and sixteen original U2 responses',len(expected)==25 and all((AI/'calls'/i/'measurement.json').exists() for i in expected),'No fixture samples substituted for real CLI invocations')
for name,item in protocol['input_files'].items():
    check('Frozen input '+name,sha(AI/'inputs'/name)==item['sha256'],'Original declared input hash')
for identifier in expected+supplemental:
    directory=AI/'calls'/identifier; measurement=load(directory/'measurement.json')
    stream=[json.loads(line) for line in (directory/'events.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    usage=[e['usage'] for e in stream if e.get('type') in ['turn.completed','thread.completed'] and 'usage' in e]
    aggregate={k:sum(u[k] for u in usage) if usage and all(k in u for u in usage) else None for k in measurement['usage']}
    tools=[e for e in stream if e.get('type')=='item.completed' and e.get('item',{}).get('type') not in ['error','reasoning','agent_message']]
    input_file=AI/measurement['input_file'].replace('\\','/')
    schema_file=AI/'inputs'/('summary.schema.json' if identifier.startswith('U1-') else 'decision.schema.json')
    output=load(directory/'response.json'); valid=True
    try: jsonschema.validate(output,load(schema_file))
    except jsonschema.ValidationError: valid=False
    valid=valid and aggregate==measurement['usage'] and len(usage)==measurement['completed_turns']==1
    valid=valid and measurement['exit_code']==0 and measurement['usage_status']=='COMPLETE' and not tools and measurement['actual_tool_items']==0
    valid=valid and sha(input_file)==measurement['input_sha256'] and sha(schema_file)==measurement['schema_sha256']
    valid=valid and measurement['requested_model']==protocol['requested_model'] and measurement['reasoning_effort']==protocol['reasoning_effort']
    valid=valid and 'forced_login_method="chatgpt"' in measurement['command'] and measurement['monetary_cost']=='UNKNOWN'
    check('Actual model call '+identifier,valid,'Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth')
with (AI/'U1_actual-ledger.csv').open(encoding='utf-8',newline='') as f: ledger=list(csv.DictReader(f))
for config in 'ABC':
    rows=[r for r in ledger if r['config']==config]; group=results['U1']['configs'][config]
    valid=len(rows)==3 and group['samples']==3
    for key,csvkey in [('input_total','input_total'),('output','output'),('elapsed_seconds','elapsed_seconds')]:
        values=[float(r[csvkey]) for r in rows]
        valid=valid and median(values)==group[key]['median'] and min(values)==group[key]['min'] and max(values)==group[key]['max']
    for row in rows:
        raw=load(AI/'calls'/('U1-'+row['sample'])/'measurement.json')['usage']
        valid=valid and int(row['input_total'])==raw['input_tokens'] and int(row['cached'])==raw['cached_input_tokens']
        valid=valid and int(row['uncached_derived'])==raw['input_tokens']-raw['cached_input_tokens']
        valid=valid and all(row[k]=='UNKNOWN' for k in ['model_cost','ci_cost','measured_total','human_QA_review_minutes'])
    check('U1 independently recalculated config '+config,valid,'3samples, medians/ranges/usage partition match raw metadata; money/reviewer time not invented')
check('U2 original fixture/version denominators',len(results['U2']['rows'])==16 and all(sum(r['version']==v for r in results['U2']['rows'])==8 for v in ['v1','v3']),'Supplemental complete-positive excluded from original8 per version')
check('Complete positive control accepted',len(results['positive_control_complete'])==2 and all(r['gate']=='ACCEPT' for r in results['positive_control_complete']),'Same richer synthetic fixture for both versions, original RG01 retained')
check('Four nonvacuous negative controls detected',len(results['negative_controls'])==4 and all(c['detected'] for c in results['negative_controls']), 'Actual accepted outputs corrupted by stale run/wrong department/arbitrary delete/toast oracle')
revision=subprocess.check_output(['git','-C',str(LAB),'rev-parse','HEAD'],text=True).strip()
evidence_file=WORK/protocol.get('actual_source_manifest','bai-nop-AOCE/live/runs/mv0nfj0v-fcf1b44e/manifest.json')
baseline=protocol['source_lab_revision']
baseline_exists=subprocess.run(['git','-C',str(LAB),'cat-file','-e',baseline+'^{commit}'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
baseline_ancestor=subprocess.run(['git','-C',str(LAB),'merge-base','--is-ancestor',baseline,revision],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
clean=not subprocess.check_output(['git','-C',str(LAB),'status','--porcelain'],text=True).strip()
check('Benchmark source revision matches historical runner evidence and Git history',
      baseline_exists and baseline_ancestor and load(evidence_file)['code_revision']==baseline and clean,
      f'Frozen benchmark revision={baseline}; current clean HEAD={revision}; later app/CI commits are separate from the benchmark cohort')
evidence=load(AI/'inputs/actual-evidence.json')
check('U1 actual runner evidence hash matches',sha(evidence_file)==evidence['source_manifest_sha256'],'Underlying F01 reporter evidence not fabricated by model')
secrets=[]
for line in (LAB/'.env').read_text(encoding='utf-8').splitlines():
    if line.startswith(('LAB_PASSWORD=','LAB_VIEWER_PASSWORD=')): secrets.append(line.split('=',1)[1])
for file in (LAB/'.lab/grants').glob('*.json'): secrets.append(load(file)['token'])
leaks=[]
for file in AI.rglob('*'):
    if file.is_file() and file.suffix in ['.json','.jsonl','.md','.txt','.csv','.py']:
        content=file.read_text(encoding='utf-8-sig')
        if any(value and value in content for value in secrets): leaks.append(str(file.relative_to(AI)))
check('No app credentials/capabilities in AI inputs or outputs',not leaks,'Private-value comparison done locally; secret values never logged')
missing=[]
for file in (WORK/'bai-nop-AOCE').rglob('*.md'):
    if (AI/'inputs') in file.parents: continue # Frozen copied source/prompt data, not navigation documents.
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',file.read_text(encoding='utf-8-sig')):
        if target.startswith(('http://','https://','mailto:','#')): continue
        name=target.split('#')[0].strip('<>')
        if name and not (file.parent/name).exists(): missing.append(str(file.relative_to(WORK))+': '+target)
check('Submission links resolve',not missing,'; '.join(missing) if missing else 'Original and AI supplementary document links present; frozen input archive is data, validated by source hash')
result={'scope':'ACTUAL AI BENCHMARK ARTIFACT VALIDATION','generated_at':datetime.now(timezone.utc).isoformat(),'checks':checks,'errors':sum(c['status']=='ERROR' for c in checks)}
(AI/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# Actual AI benchmark validation','',f"{len(checks)-result['errors']}/{len(checks)} checks OK, errors={result['errors']}.",'','| Check | Actual result | Detail |','| --- | --- | --- |']
lines += [f"| {c['check']} | {c['status']} | {c['detail']} |" for c in checks]
lines += ['','Schema checks do not replace semantic policy review. Actual model calls use synthetic U2 fixtures; app runtime evidence and model evaluations remain distinct. No provider invoice/monetary saving inference.','']
(AI/'validation.md').write_text('\n'.join(lines),encoding='utf-8')
for c in checks: print(c['status']+': '+c['check'])
print(f"{len(checks)-result['errors']}/{len(checks)} OK; errors={result['errors']}")
sys.exit(1 if result['errors'] else 0)
