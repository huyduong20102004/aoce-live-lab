"""Close the temporary timer only after a genuine successful scheduled smoke."""
import importlib.util
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
spec = importlib.util.spec_from_file_location('github', ROOT.parent / 'ci/tools/github.py')
github = importlib.util.module_from_spec(spec)
spec.loader.exec_module(github)
repo = '/repos/' + github.REPO
SHA = 'c27f9b8eff44a4875f2922831890dc8d8abf1851'

def save(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

run = json.loads((ROOT / 'scheduled-run.json').read_text(encoding='utf-8'))
run = github.request('GET', repo + '/actions/runs/' + str(run['id']))
assert run['event'] == 'schedule' and run['head_sha'] == SHA and run['conclusion'] == 'success'
save('scheduled-run.json', run)
jobs = github.request('GET', repo + f"/actions/runs/{run['id']}/jobs")
save('scheduled-jobs.json', jobs)
artifacts = github.request('GET', repo + f"/actions/runs/{run['id']}/artifacts")
save('scheduled-artifacts.json', artifacts)
artifact = next(a for a in artifacts['artifacts'] if a['name'] == f"live-{run['id']}-{run['run_attempt']}")
assert not artifact['expired']
destination = WORKSPACE / 'aoce-live-lab/.lab/ci-artifacts' / str(run['id'])
github.download_artifact(artifact['id'], destination)
manifest_path = next(destination.rglob('manifest.json'))
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
assert manifest['code_revision'] == SHA and manifest['trigger'] == 'github-schedule'
assert manifest['schedule_purpose'] == 'verification' and manifest['schedule_expression'] == '*/5 * * * *'
assert manifest['label'] == 'RUN-PASSED' and manifest['selected_count'] == manifest['executed_count'] == 3
assert len(manifest['cases']) == 3 and all(c['status'] == 'passed' for c in manifest['cases'])
cleanup = json.loads((manifest_path.parent / 'cleanup.json').read_text(encoding='utf-8'))
assert cleanup['unresolved_count'] == 0 and cleanup['cleanup_status'] == 'resolved'
evidence = json.loads((manifest_path.parent / 'evidence-check.json').read_text(encoding='utf-8'))
assert evidence['status'] == 'COMPLETE' and not evidence['gaps']
public = ROOT / 'hosted-scheduled'
public.mkdir(exist_ok=True)
for file in manifest_path.parent.iterdir():
    if file.suffix in {'.json', '.png'} and file.name in {
        'manifest.json', 'preflight.json', 'cleanup.json', 'discovery.json', 'evidence-check.json'} | {
            a.name for a in manifest_path.parent.glob('*.png')}:
        shutil.copy2(file, public / file.name)

github.request('PATCH', repo + '/actions/variables/AOCE_VERIFY_SCHEDULE_ENABLED',
               {'name': 'AOCE_VERIFY_SCHEDULE_ENABLED', 'value': 'false'})
github.request('PUT', repo + '/actions/workflows/schedule-verification.yml/disable')
diagnostic = github.request('GET', repo + '/actions/workflows/schedule-verification.yml')
daily = github.request('GET', repo + '/actions/workflows/lab.yml')
variables = github.request('GET', repo + '/actions/variables')['variables']
values = {v['name']: v['value'] for v in variables}
state = {'captured_at': datetime.now(timezone.utc).isoformat(), 'tested_revision': SHA,
         'scheduled_run_id': run['id'], 'scheduled_run_url': run['html_url'],
         'diagnostic_workflow_state': diagnostic['state'],
         'diagnostic_variable': values['AOCE_VERIFY_SCHEDULE_ENABLED'],
         'daily_workflow_state': daily['state'], 'daily_variable': values['AOCE_SCHEDULE_ENABLED'],
         'validated_revision': values['AOCE_MANUAL_VALIDATED_REVISION'],
         'daily_cron_utc': '17 18 * * *', 'daily_target_vietnam': '01:17 UTC+7',
         'scope_note': 'Actual schedule event verified using temporary five-minute cron; next daily slot is future.'}
save('scheduler-final-state.json', state)
print(json.dumps(state))
