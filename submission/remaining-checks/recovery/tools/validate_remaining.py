"""Validate exported evidence; do not synthesize a scheduled run or change the app."""
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA = 'c27f9b8eff44a4875f2922831890dc8d8abf1851'
checks = []

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def check(name, condition):
    checks.append({'check': name, 'result': 'PASSED' if condition else 'FAILED'})

def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

def hosted(folder, api, event):
    m = read(folder / 'manifest.json')
    c = read(folder / 'cleanup.json')
    e = read(folder / 'evidence-check.json')
    check(event + ': actual API event and successful tested revision',
          api['event'] == event and api['conclusion'] == 'success' and api['head_sha'] == SHA)
    check(event + ': source and API run agree', m['code_revision'] == SHA and
          m['github_run_url'] == api['html_url'] and m['run_id'] == f"gh-{api['id']}-{api['run_attempt']}")
    cases = m['cases']
    check(event + ': three executed F01-F03 business assertions pass',
          m['label'] == 'RUN-PASSED' and m['selected_count'] == m['executed_count'] == 3 and
          len(cases) == 3 and {x['flow'] for x in cases} == {'F01', 'F02', 'F03'} and
          all(x['status'] == 'passed' and x['attempts'] == 1 and not x['errors'] for x in cases))
    check(event + ': cleanup resolved and records absent', c['unresolved_count'] == 0 and
          c['cleanup_status'] == m['cleanup_status'] == 'resolved' and
          all(x['record_absent_after'] for x in c['records']))
    hashes = {hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.png')}
    check(event + ': exported assertion screenshots match manifest hashes',
          all(a['sha256'] in hashes for x in cases for a in x['artifacts']) and len(hashes) == 3)
    check(event + ': evidence completeness', e['status'] == 'COMPLETE' and not e['gaps'])
    if event == 'schedule':
        check('schedule: genuine timer context and reviewed verification purpose',
              m['trigger'] == 'github-schedule' and m['schedule_purpose'] == 'verification' and
              m['schedule_expression'] == '*/5 * * * *')

hosted(ROOT / 'hosted-manual', read(ROOT / 'manual-run.json'), 'workflow_dispatch')
cancel_dir = ROOT.parent / 'runs' / 'cancel-mv63z50h-ec1f9a'
d = read(cancel_dir / 'cancellation-drill.json')
w = read(cancel_dir / 'watchdog.json')
c = read(cancel_dir / 'cleanup.json')
m = read(cancel_dir / 'manifest.json')
check('cancel: exact tested revision and all seven recorded checks', d['code_revision'] == SHA and
      d['status'] == 'RECOVERY-VERIFIED' and len(d['checks']) == 7 and
      all(x['result'] == 'PASSED' for x in d['checks']))
check('cancel: actual SIGKILL and separate watchdog process', d['victim_exit']['signal'] == 'SIGKILL' and
      len({d['supervisor_pid'], d['victim_pid'], d['watchdog_pid']}) == 3 and w['pid'] == d['watchdog_pid'])
check('cancel: reconciliation starts after real lease deadline',
      instant(w['started_at']).timestamp() * 1000 >= d['lease_deadline'] and
      instant(d['cancelled_at']).timestamp() * 1000 < d['lease_deadline'])
check('cancel: one exact owned ID absent and cleanup resolved', c['unresolved_count'] == w['unresolved'] == 0 and
      len(c['records']) == 1 and c['records'][0]['employee_id'] == d['owned_employee_id'] and
      c['records'][0]['owner'] == d['run_id'] and c['records'][0]['writes'] == 1 and
      c['records'][0]['record_absent_after'] and w['records'][0]['action'] == 'RECONCILED')
check('cancel: recovery does not relabel unexecuted assertions as pass',
      m['label'] == m['runner_outcome'] == 'CANCELLED' and
      m['assertion_outcome'] == d['assertion_outcome'] == 'NOT_EXECUTED')
state = read(ROOT / 'local-state-verification.json')
check('cancel: subsequent persistent state has no owned leftover, one write, demo retained',
      state['run_id'] == d['run_id'] and state['lease_released'] and
      state['owned_records_remaining'] == 0 and state['owned_write_count'] == 1 and state['unowned_demo_present'])
full_dir = ROOT.parent / 'runs' / 'mv642583-879ae7b4'
full = read(full_dir / 'manifest.json')
full_cleanup = read(full_dir / 'cleanup.json')
check('full suite: eleven successful executed cases on same source, cleanup33 resolved',
      full['code_revision'] == SHA and full['label'] == 'RUN-PASSED' and
      full['selected_count'] == full['executed_count'] == len(full['cases']) == 11 and
      all(c['status'] == 'passed' for c in full['cases']) and full_cleanup['unresolved_count'] == 0 and
      len(full_cleanup['records']) == 33 and all(c['record_absent_after'] for c in full_cleanup['records']))

windows = read(ROOT / 'windows-diagnosis.json')
vn = timezone(timedelta(hours=7))
slots = []
for day in (10, 11, 12, 13):
    slot = datetime(2026, 10, day, 1, 17, tzinfo=vn)
    intervals = [i for i in windows['sleep_intervals']
                 if instant(i['sleep_utc']) <= slot <= instant(i['wake_utc'])]
    slots.append({'slot_vietnam': slot.isoformat(), 'asleep': bool(intervals),
                  'power_event_record_ids': [i['record_id'] for i in intervals],
                  'wake_vietnam': [instant(i['wake_utc']).astimezone(vn).isoformat() for i in intervals]})
check('windows: actual sleep intervals cover all four observed missed slots', all(s['asleep'] for s in slots))
check('windows: catch-up enabled, waking disabled, interactive identity',
      windows['settings']['start_when_available'] and not windows['settings']['wake_to_run'] and
      windows['settings']['logon_type'] == 'Interactive')
(ROOT / 'windows-slot-analysis.json').write_text(json.dumps({'slots': slots,
    'historical_dispatch_detail': 'UNKNOWN: TaskScheduler Operational log was disabled'}, indent=2) + '\n', encoding='utf-8')

pending = []
if (ROOT / 'scheduled-run.json').exists():
    hosted(ROOT / 'hosted-scheduled', read(ROOT / 'scheduled-run.json'), 'schedule')
else:
    pending.append('actual scheduled run')
if (ROOT / 'scheduler-final-state.json').exists():
    s = read(ROOT / 'scheduler-final-state.json')
    check('schedule: diagnostic disabled and daily enabled with validated source',
          s['diagnostic_workflow_state'] == 'disabled_manually' and
          s['diagnostic_variable'] == 'false' and s['daily_workflow_state'] == 'active' and
          s['daily_variable'] == 'true' and s['validated_revision'] == SHA)
else:
    pending.append('final GitHub scheduler state')
if (ROOT / 'windows-retired.json').exists():
    s = read(ROOT / 'windows-retired.json')
    check('windows: own task disabled; GitHub chosen as primary',
          s['task'] == 'AOCE-PortalLite-Live-Smoke' and s['state'] == 'Disabled' and
          s['primary_scheduler'] == 'GitHub Actions')
else:
    pending.append('Windows task retirement')

failed = [x for x in checks if x['result'] != 'PASSED']
report = {'scope': 'INDEPENDENT EXPORTED-EVIDENCE CONSISTENCY CHECKS', 'tested_revision': SHA,
          'status': 'FAILED' if failed else 'PENDING' if pending else 'VERIFIED',
          'passed': len(checks) - len(failed), 'failed': len(failed), 'pending': pending, 'checks': checks}
(ROOT / 'validation-results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'checks'}))
raise SystemExit(1 if failed else 0)
