"""Validate submitted artifacts against ORIGINAL packets, not live app behavior."""
from pathlib import Path
from decimal import Decimal as D
from statistics import median
from datetime import datetime, timedelta, timezone
import csv
import hashlib
import json
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'L3_AIQE_AOCE_exercises_vi.md'
EXPECTED = [
    'U1_benchmark.md','U1_cost-ledger.csv','U2_context-and-prompt.md','U2_regression-matrix.md',
    'U3_multi-flow-design.md','U3_data-and-evidence.md','U4_change-review.md','U4_PR.md',
    'U5_ci-design.md','U5_workflow.yml','U5_playwright-config.ts','U5_run-review.md',
    'U6_incident-triage.md','U6_recovery-and-validation.md','U7_metrics-and-claims.md',
    'U7_risk-register.md','U7_sprint-review.md',
]
checks = []

def check(name, condition, detail):
    checks.append({'check': name, 'status': 'OK' if condition else 'ERROR', 'detail': detail})

def table_rows(text, pattern):
    return [[v.strip() for v in line.strip().strip('|').split('|')]
            for line in text.splitlines() if re.match(pattern, line)]

def number(s):
    return D(s.replace(',', '.'))

def run():
    check('17 required deliverables', all((ROOT/p).is_file() for p in EXPECTED), ', '.join(EXPECTED))
    text=SOURCE.read_text(encoding='utf-8')
    manifest=json.loads((ROOT/'evidence/source-manifest.json').read_text(encoding='utf-8'))
    for record in manifest['files']:
        actual=hashlib.sha256((ROOT.parent/record['name']).read_bytes()).hexdigest()
        check('Original source unchanged: '+record['name'], actual==record['sha256'], actual)
    # C3 also has a prose output-card row; select only the 9-column usage table.
    raw=[r for r in table_rows(text,r'^\| [ABC][123] \|') if len(r)==9]
    with (ROOT/'U1_cost-ledger.csv').open(encoding='utf-8',newline='') as f:
        ledger={r['sample']:r for r in csv.DictReader(f)}
    check('U1 nine sample IDs',set(ledger)=={r[0] for r in raw} and len(raw)==9,'A1–C3 present; no dropped rejected samples')
    for row in raw:
        name, inp, cached, output, calls, tools, minutes, seconds, qa=row
        item=ledger[name]
        ci=number(minutes)*D('.02')
        if inp=='UNKNOWN':
            valid=all(item[k]=='UNKNOWN' for k in ['input_total','cached','uncached','output','model_cost','measured_total'])
            valid=valid and item['usage_status']=='MISSING' and D(item['ci_cost'])==ci
        else:
            u=number(inp)-number(cached)
            m=(u+number(cached)*D('.25')+number(output)*4)/1000000
            valid=(D(item['input_total'])==number(inp) and D(item['cached'])==number(cached)
                   and D(item['uncached'])==u and D(item['output'])==number(output)
                   and D(item['model_cost'])==m and D(item['ci_cost'])==ci
                   and D(item['measured_total'])==m+ci and item['usage_status']=='COMPLETE')
        check('U1 source-derived cost '+name,valid,'Uncached partition/model/CI/total checked against original BENCH table')
    scores=table_rows((ROOT/'U1_benchmark.md').read_text(encoding='utf-8'),r'^\| [ABC][123] \|')[:9]
    score_ok=all(int(ledger[r[0]]['quality_score'])==sum(int(v) for v in r[1:5])==int(r[5]) for r in scores)
    check('U1 rubric scores/ledger consistency',len(scores)==9 and score_ok,'A=10, B=1, C1/2=10, C3=5; hard gates separate')
    calc=json.loads((ROOT/'evidence/calculations.json').read_text(encoding='utf-8'))
    sums={c:sum((D(r['measured_total']) for r in ledger.values() if r['sample'][0]==c and r['measured_total']!='UNKNOWN'),D(0)) for c in 'ABC'}
    bound=sums['C']+D(ledger['C3']['ci_cost'])
    check('U1 all-sample config cost bounds',sums['A']==D('.325175') and sums['B']==D('.237005') and bound==D('.254075')
          and D(calc['U1']['C']['cost_per_accepted_lower_bound'])==bound/2 and calc['U1']['C']['cost_total']=='UNKNOWN',
          'C accepted=2; rejected C3 contributes known CI; total remains UNKNOWN')
    for c in 'ABC':
        rows=[r for r in raw if r[0][0]==c]
        valid=(calc['U1'][c]['e2e_seconds']['median']==float(median([number(r[7]) for r in rows]))
               and calc['U1'][c]['qa_minutes']['median']==float(median([number(r[8]) for r in rows])))
        check('U1 config median '+c,valid,'Latency/QA calculated independently from source rows')
    context=(ROOT/'U2_context-and-prompt.md').read_text(encoding='utf-8')
    compact=re.search(r'<!-- compact-context:start -->(.*?)<!-- compact-context:end -->',context,re.S).group(1)
    count=len(compact.split())
    check('U2 compact word budget',count<=250,f'{count} whitespace-delimited words; limit250, not tokens')
    check('U2 eight fragment IDs',all(f'CTX-{i:02}' in context for i in range(1,9)),'Keep/drop/quarantine source manifest')
    matrix=(ROOT/'U2_regression-matrix.md').read_text(encoding='utf-8')
    check('U2 eight fixtures and >=2 negatives',all(f'RG-{i:02}' in matrix for i in range(1,9)) and len(set(re.findall(r'NC-U2-\d+',matrix)))>=2,'Walkthrough only; no model/runner executed')
    u3=(ROOT/'U3_multi-flow-design.md').read_text(encoding='utf-8')
    check('U3 three flow contracts/stop scenarios',all(v in u3 for v in ['F01-create-search','F02-change-department','F03-viewer-create-denied','F99','production','seedRef','Budget 0','Check employee','Delete everyone']), 'Structural coverage only; UI/backend boundary reviewed semantically')
    workflow=yaml.safe_load((ROOT/'U5_workflow.yml').read_text(encoding='utf-8'))
    check('U5 YAML syntax + minimum permissions',workflow['permissions']=={'contents':'read'},'PyYAML parse; no GitHub execution/actionlint claim')
    check('U5 cron UTC conversion',workflow['on']['schedule'][0]['cron']=='17 18 * * *'
          and (datetime(2026,10,7,18,17,tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=7))).strftime('%Y-%m-%d %H:%M')=='2026-10-08 01:17'), '18:17 UTC -> 01:17 next Vietnam day')
    live=workflow['jobs']['live-smoke']
    group=live['concurrency']
    check('U5 environment concurrency/no forced cancellation',group['group']=='aoce-isolated-lab-live' and group['cancel-in-progress'] is False,'Shared environment group; not cross-repo lock')
    check('U5 live authorization gates',all(v in live['if'] for v in ['default_branch','AOCE_MANUAL_ENABLED','AOCE_SCHEDULE_ENABLED','AOCE_MANUAL_VALIDATED_REVISION']), 'Actual variables/repo/manual proof absent; no deployment')
    yaml_text=(ROOT/'U5_workflow.yml').read_text(encoding='utf-8')
    check('U5 no suppressed failures or no-tests pass',all(v not in yaml_text for v in ['continue-on-error','|| true','--pass-with-no-tests','pull_request_target']), 'Wrapper script implementations still prerequisite')
    uploads=[s for j in workflow['jobs'].values() for s in j['steps'] if 'upload-artifact@' in s.get('uses','')]
    check('U5 failure artifact export',len(uploads)==2 and all('always()' in s['if'] and s['with']['if-no-files-found']=='error' and s['with']['path'].startswith('evidence-export/') for s in uploads),'Safe export paths; force cancel still requires external reconciler')
    type_versions=json.loads((ROOT/'evidence/typecheck-versions.json').read_text(encoding='utf-8-sig'))
    type_output=(ROOT/'evidence/typecheck-output.txt').read_text(encoding='utf-8-sig')
    config_hash=hashlib.sha256((ROOT/'U5_playwright-config.ts').read_bytes()).hexdigest()
    check('U5 actual draft config typecheck and hash',type_versions['exit_code']==0
          and type_versions['config_sha256']==config_hash and 'Exit code: 0' in type_output,
          f"tsc {type_versions['typescript']}, Playwright types {type_versions['playwright_test']}, Node types {type_versions['node_types']}; config unchanged since compile; not live project runtime")
    u5=(ROOT/'U5_ci-design.md').read_text(encoding='utf-8')
    u5review=(ROOT/'U5_run-review.md').read_text(encoding='utf-8')
    check('U5 eight scenarios/three packets',all(f'CI-{i}' in u5 for i in range(51,59)) and all(f'CI-RUN-{v}' in u5review for v in 'ABC'),'Source cards addressed, not actual CI evidence')
    triage=(ROOT/'U6_incident-triage.md').read_text(encoding='utf-8')
    recovery=(ROOT/'U6_recovery-and-validation.md').read_text(encoding='utf-8')
    check('U6 incidents/retry outcomes/negative controls',all(f'INC-{i}' in triage for i in range(61,65))
          and all(f'| {v} |' in triage for v in 'XYZ') and len(set(re.findall(r'NC-U6-\d+',recovery)))>=2,'4 incidents, 3 retry outcomes, >=2 proposed negative controls')
    source_u7=table_rows(text,r'^\| E\d{2} \|')
    with (ROOT/'evidence/U7_execution-ledger.csv').open(encoding='utf-8',newline='') as f:
        metric_ledger=list(csv.DictReader(f))
    valid=len(source_u7)==len(metric_ledger)==10
    for r,s in zip(metric_ledger,source_u7):
        valid=valid and (r['eid'],r['flow'],r['outcome'],r['attempts'],r['evidence'],r['cleanup'])==(s[0],s[1],s[2],s[3],s[4],s[6])
        call,usage=[v.strip() for v in s[7].split('/')]
        valid=valid and r['model_calls']==call and r['usage_status']==usage and D(r['measured_subtotal'])==number(s[8]) and r['test_seconds']==s[9]
    check('U7 all 10 source rows preserved',valid,'Outcome/attempts/evidence/cleanup/calls/usage/cost/time checked against original table')
    m=calc['U7']; executed=[r for r in source_u7 if int(r[3])>0]
    attempts=sum(int(r[3]) for r in source_u7)
    passes=[r for r in executed if r[2] in ['first-pass','flaky-pass']]
    full=[r for r in executed if r[4]=='full']
    complete_pass=[r[0] for r in passes if r[4]=='full']
    needed=[r for r in source_u7 if r[5]=='yes']
    valid=(m['selected']==len(source_u7)==10 and m['executed']==len(executed)==8 and m['attempts']==attempts==11
           and m['retry_overhead']==attempts-len(executed)==3 and m['first_pass']==sum(r[2]=='first-pass' for r in executed)==4
           and m['eventual_pass']==len(passes)==6 and m['flaky']==sum(r[2]=='flaky-pass' for r in executed)==2
           and m['full_evidence']==len(full)==7 and m['cleanup_needed']==len(needed)==6
           and m['cleanup_success']==sum(r[6]=='success' for r in needed)==4 and m['evidence_complete_pass_ids']==complete_pass)
    check('U7 denominators/outcome partitions',valid,'selected10/executed8/attempts11/pass4+2/fail2/full7/cleanup4of6/fullpasses5')
    cost=sum((number(r[8]) for r in source_u7),D(0))
    check('U7 source-derived subtotal and lower-bound cost',cost==D('.89')==D(m['measured_subtotal']) and D(m['evidence_complete_pass_cost_lower_bound'])==cost/len(complete_pass)==D('.178') and m['total_cost']=='UNKNOWN','All cohort costs included; E08 missing model usage !=zero')
    times=[int(r[9]) for r in executed]
    check('U7 test-duration stats',median(times)==m['test_seconds']['median']==82.5 and min(times)==40 and max(times)==170,'n8, excludes not-executed; not E2E latency')
    schedule=table_rows(text,r'^\| SL-0[1-4] \|')
    delays=[]; queues=[]
    for row in schedule:
        match=re.search(r'dispatch (\d{2}:\d{2}), start (\d{2}:\d{2})',row[2])
        if match:
            expected=datetime.strptime(row[1],'%Y-%m-%d %H:%M')
            dispatch=datetime.combine(expected.date(),datetime.strptime(match[1],'%H:%M').time())
            start=datetime.combine(expected.date(),datetime.strptime(match[2],'%H:%M').time())
            delays.append((dispatch-expected).total_seconds()/60); queues.append((start-dispatch).total_seconds()/60)
    check('U7 schedule source-derived metrics',len(schedule)==4 and len(delays)==3 and delays==[3,0,2] and queues==[2,8,1]
          and m['dispatch_delay_minutes']['median']==median(delays) and m['queue_delay_minutes']['median']==median(queues), 'Completeness3/4; SL-04 missing, no zero fill')
    risks=table_rows((ROOT/'U7_risk-register.md').read_text(encoding='utf-8'),r'^\| R\d{2} ')
    check('U7 >=6 complete risk rows',len(risks)>=6 and all(len(r)>=10 for r in risks),f'{len(risks)} proposed risk rows with source/control/detection/owner/action/closure/residual')
    missing=[]
    for p in ROOT.rglob('*.md'):
        if (ROOT/'live/ai/inputs') in p.parents: continue # Immutable copied source data; navigation links are not rewritten after inference.
        contents=p.read_text(encoding='utf-8')
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',contents):
            if target.startswith(('https://','http://','mailto:','#')):
                continue
            file=target.split('#')[0].strip('<>')
            if file and not (p.parent/file).exists():
                missing.append(str(p.relative_to(ROOT))+': '+target)
    check('All local Markdown links resolve',not missing,'; '.join(missing) if missing else 'All referenced files present')
    check('Draft/manual-first provenance disclosed',(ROOT/'review/00_analysis-first-draft.md').exists()
          and 'Không có bằng chứng' in (ROOT/'README.md').read_text(encoding='utf-8'), 'AI-authored draft; no fabricated human/peer review')
    check('No deployed workflow or app/auth payload created',not (ROOT.parent/'.github/workflows').exists()
          and not any(p.suffix=='.env' or '.auth' in p.parts for p in ROOT.rglob('*')), 'Submission-only drafts; original workspace documents preserved')

def write_report():
    errors=[c for c in checks if c['status']=='ERROR']
    data={'scope':'ACTUAL LOCAL ARTIFACT VALIDATION, NOT APP/CI RUNTIME','date':'2026-10-07','timezone':'UTC+7','checks':checks,'errors':len(errors)}
    (ROOT/'evidence/validation-results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Actual local validation — bài nộp dry-run','',
           'Ngày 2026-10-07 (UTC+7). Các checks chạy thật trên file tại máy; packets app/CI/model vẫn SIMULATED. Không có RUN-PASSED app/CI.','',
           '`python bai-nop-AOCE/tools/calculate.py` tính lại CSV/JSON bằng Decimal; `python bai-nop-AOCE/tools/validate.py` đối chiếu bảng trong handout gốc, hashes, word budget, links và YAML.','',
           f'Kết quả: {len(checks)-len(errors)}/{len(checks)} checks OK, {len(errors)} errors.','',
           '| Check | Actual result | Evidence / limitation |','| --- | --- | --- |']
    lines += [f"| {c['check']} | {c['status']} | {c['detail']} |" for c in checks]
    lines += ['', 'Typecheck config draft: xem [compiler output](typecheck-output.txt) và [tool versions](typecheck-versions.json). Đây là kiểm tra config độc lập với các package types tạm, không project lab typecheck/test execution.','',
              'Không kiểm được: actual lab runner/assertions, CI trigger/action execution, script implementations, permissions/helper behavior, live cleanup, provider usage/pricing, production readiness. Human manual-first và independent QA approval chưa có.', '',
              'YAML parse/structural checks không thay GitHub workflow/actionlint/runtime validation. Row/ID coverage checks không chứng minh behavior controller. Proposed negative controls là walkthrough, chưa model/app executed.', '',
              '[Machine-readable results](validation-results.json); [source snapshot](source-manifest.json); [review decisions](../review/01_review-decisions.md).','']
    (ROOT/'evidence/validation-report.md').write_text('\n'.join(lines),encoding='utf-8')
    for c in checks:
        print(c['status']+': '+c['check'])
    print(f'{len(checks)-len(errors)}/{len(checks)} local artifact checks OK; {len(errors)} errors. No app/CI runtime executed.')
    return bool(errors)

if __name__=='__main__':
    try:
        run()
    except Exception as exc:
        check('Validator exception',False,repr(exc))
    sys.exit(1 if write_report() else 0)
