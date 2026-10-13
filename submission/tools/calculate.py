"""Recompute synthetic packet costs/metrics. No app/network access."""
from pathlib import Path
from decimal import Decimal as D
from statistics import median
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
ROWS = [
    ('A1', 18000, 2000, 2400, '4.0', 290, 8, 10, 'ACCEPT'),
    ('A2', 17500, 1500, 2300, '4.1', 301, 9, 10, 'ACCEPT'),
    ('A3', 19000, 2000, 2500, '4.2', 318, 9, 10, 'ACCEPT'),
    ('B1', 6000, 1000, 900, '3.5', 239, 12, 1, 'REJECT'),
    ('B2', 6200, 1000, 950, '3.6', 245, 13, 1, 'REJECT'),
    ('B3', 5900, 900, 920, '3.4', 233, 11, 1, 'REJECT'),
    ('C1', 8500, 1500, 1400, '3.7', 251, 6, 10, 'ACCEPT'),
    ('C2', 8200, 1200, 1450, '3.8', 260, 7, 10, 'ACCEPT'),
    ('C3', None, None, None, '3.9', 267, 8, 5, 'REJECT'),
]
REASONS = {
    'A': 'Required ID+department; matching EV-bench-1; owned cleanup; SIMULATED',
    'B': 'Missing department oracle; toast-only pass; unowned cleanup; missing synthetic label',
    'C': 'Required ID+department; matching EV-bench-1; owned cleanup; SIMULATED',
    'C3': 'EV-other-1 belongs to bench-previous; current-pass unsupported; usage missing',
}

def stats(values):
    return {'n': len(values), 'median': median(values), 'min': min(values), 'max': max(values)}

def compute():
    ledger = []
    for name, total, cached, output, minutes, seconds, qa, score, gate in ROWS:
        uncached = total - cached if total is not None else None
        model = (D(uncached) + D(cached) * D('.25') + D(output) * 4) / 1000000 if total is not None else None
        ci = D(minutes) * D('.02')
        measured = model + ci if model is not None else None
        ledger.append(dict(sample=name, input_total=total, cached=cached, uncached=uncached,
                           output=output, model_cost=model, ci_cost=ci, measured_total=measured,
                           usage_status='COMPLETE' if total is not None else 'MISSING',
                           quality_score=score, gate=gate, reason=REASONS.get(name, REASONS[name[0]])))
    configs = {}
    for config in 'ABC':
        items = [r for r in ledger if r['sample'].startswith(config)]
        raw = [r for r in ROWS if r[0].startswith(config)]
        known = [r for r in items if r['measured_total'] is not None]
        subtotal = sum((r['measured_total'] for r in known), D(0))
        bound = subtotal + sum((r['ci_cost'] for r in items if r['measured_total'] is None), D(0))
        accepted = sum(r['gate'] == 'ACCEPT' for r in items)
        configs[config] = {
            'input_total_known': stats([r['input_total'] for r in known]),
            'output_known': stats([r['output'] for r in known]),
            'total_tokens_known': stats([r['input_total'] + r['output'] for r in known]),
            'e2e_seconds': stats([r[5] for r in raw]), 'qa_minutes': stats([r[6] for r in raw]),
            'ci_minutes': stats([float(r[4]) for r in raw]), 'accepted': accepted,
            'known_complete_rows_cost': str(subtotal), 'cost_lower_bound': str(bound),
            'cost_total': str(bound) if len(known) == len(items) else 'UNKNOWN',
            'cost_per_accepted': str(bound / accepted) if accepted and len(known) == len(items) else 'UNKNOWN' if accepted else 'N/A',
            'cost_per_accepted_lower_bound': str(bound / accepted) if accepted else 'N/A',
        }
    # EID, flow, outcome, attempts, evidence, cleanup, calls, usage, subtotal, test seconds.
    cohort = [
        ('E01','F01','first-pass',1,'full','success',0,'not-applicable','.10',80),
        ('E02','F02','flaky-pass',2,'full','success',1,'complete','.16',150),
        ('E03','F03','first-pass',1,'full','not-applicable',0,'not-applicable','.04',40),
        ('E04','F01','failed',2,'full','failed',1,'complete','.18',170),
        ('E05','F02','flaky-pass',2,'partial','success',1,'complete','.17',145),
        ('E06','F03','blocked',0,'none','not-applicable',0,'not-applicable','.02',None),
        ('E07','F01','skipped',0,'none','not-applicable',0,'not-applicable','.00',None),
        ('E08','F02','first-pass',1,'full','unknown',1,'missing','.08',85),
        ('E09','F03','failed',1,'full','not-applicable',0,'not-applicable','.05',55),
        ('E10','F01','first-pass',1,'full','success',0,'not-applicable','.09',75),
    ]
    executed = [r for r in cohort if r[3] > 0]
    full_pass = [r for r in executed if r[2] in ('first-pass','flaky-pass') and r[4]=='full']
    measured = sum((D(r[8]) for r in cohort), D(0))
    metrics = dict(selected=len(cohort), executed=len(executed), attempts=sum(r[3] for r in cohort),
                   retry_overhead=sum(r[3] for r in cohort)-len(executed),
                   first_pass=sum(r[2]=='first-pass' for r in executed),
                   eventual_pass=sum(r[2] in ('first-pass','flaky-pass') for r in executed),
                   flaky=sum(r[2]=='flaky-pass' for r in executed),
                   full_evidence=sum(r[4]=='full' for r in executed),
                   cleanup_needed=sum(r[5]!='not-applicable' for r in cohort),
                   cleanup_success=sum(r[5]=='success' for r in cohort),
                   evidence_complete_pass_ids=[r[0] for r in full_pass],
                   measured_subtotal=str(measured), total_cost='UNKNOWN',
                   evidence_complete_pass_cost_lower_bound=str(measured/len(full_pass)),
                   test_seconds=stats([r[9] for r in executed]),
                   schedule_completeness={'numerator':3,'denominator':4},
                   dispatch_delay_minutes=stats([3,0,2]), queue_delay_minutes=stats([2,8,1]))
    return ledger, configs, cohort, metrics

def main():
    ledger, configs, cohort, metrics = compute()
    with (ROOT/'U1_cost-ledger.csv').open('w', encoding='utf-8', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=list(ledger[0]))
        writer.writeheader()
        for row in ledger:
            writer.writerow({k: 'UNKNOWN' if v is None else v for k,v in row.items()})
    with (ROOT/'evidence/U7_execution-ledger.csv').open('w', encoding='utf-8', newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['eid','flow','outcome','attempts','evidence','cleanup','model_calls','usage_status','measured_subtotal','test_seconds'])
        for row in cohort:
            writer.writerow([v if v is not None else 'not-executed' for v in row])
    result={'label':'SIMULATED','rate':'RATE-SYN-01','U1':configs,'U7':metrics}
    (ROOT/'evidence/calculations.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__=='__main__':
    (ROOT/'evidence').mkdir(exist_ok=True)
    main()
