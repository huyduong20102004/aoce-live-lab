import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { ROOT, PRIVATE, BUILD, loadEnv, assertLabUrl, atomicJson, readJson, redact } from '../server/lib.mjs';

loadEnv();
export const runId = () => {
  const id = process.env.LAB_RUN_ID;
  if (!/^[a-zA-Z0-9-]{5,40}$/.test(id || '')) throw new Error('Valid LAB_RUN_ID required');
  return id;
};
export const runDir = () => path.join(PRIVATE, 'runs', runId());
export function revision() {
  const ref = spawnSync('git', ['rev-parse', 'HEAD'], { cwd: ROOT, encoding: 'utf8', shell: false });
  if (ref.status || !/^[a-f0-9]{40}$/.test(ref.stdout.trim())) throw new Error('Committed lab Git revision required');
  const status = spawnSync('git', ['status', '--porcelain', '--untracked-files=normal'], { cwd: ROOT, encoding: 'utf8', shell: false });
  if (status.status || status.stdout.trim()) throw new Error('BLOCKED: source working tree must be committed and clean');
  return ref.stdout.trim();
}
export function bootstrap(trigger = 'manual-local', suite = 'smoke') {
  const ref = revision();
  const file = path.join(runDir(), 'manifest.json');
  if (fs.existsSync(file)) throw new Error('Never overwrite previous run evidence');
  atomicJson(file, { schema_version: 'aoce-live-run-1', run_id: runId(), code_revision: ref, mode: 'LIVE', label: 'NOT_STARTED',
    trigger, suite, scheduler_task: trigger === 'windows-schedule' ? process.env.AOCE_SCHEDULER_TASK : null,
    github_run_url: process.env.GITHUB_ACTIONS === 'true' ? `${process.env.GITHUB_SERVER_URL}/${process.env.GITHUB_REPOSITORY}/actions/runs/${process.env.GITHUB_RUN_ID}` : null,
    environment_alias: 'isolated-lab', app_build: BUILD, started_at: new Date().toISOString(),
    deadline: Date.now() + 1200000, command: suite === 'smoke' ? 'playwright test --project=chromium --grep=@smoke' : 'playwright test --project=chromium',
    selected_count: 0, executed_count: 0, cases: [], cleanup_status: 'UNKNOWN', usage_status: 'not-applicable', model_calls: 0 });
}
export async function client(role = 'HR Admin', owned = true) {
  const base = assertLabUrl();
  const login = await fetch(base + '/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json', Connection: 'close' },
    body: JSON.stringify({ username: process.env[role === 'Viewer' ? 'LAB_VIEWER_USERNAME' : 'LAB_USERNAME'],
      password: process.env[role === 'Viewer' ? 'LAB_VIEWER_PASSWORD' : 'LAB_PASSWORD'] }), signal: AbortSignal.timeout(5000) });
  if (!login.ok) throw new Error(`BLOCKED: ${role} login failed (${login.status})`);
  const cookie = login.headers.get('set-cookie')?.split(';')[0];
  const grant = owned ? readJson(path.join(PRIVATE, 'grants', runId() + '.json')) : null;
  if (owned && !grant) throw new Error('Owned grant missing; preflight required');
  return async (url, options = {}) => {
    const response = await fetch(base + url, { ...options, headers: { 'Content-Type': 'application/json', Connection: 'close', Cookie: cookie,
      ...(grant ? { 'x-lab-run-id': runId(), 'x-lab-token': grant.token } : {}), ...options.headers }, signal: options.signal || AbortSignal.timeout(5000) });
    const data = await response.json();
    if (!response.ok) throw Object.assign(new Error(data.error || 'Lab helper failed'), { status: response.status });
    return data;
  };
}
export async function preflight() {
  assertLabUrl();
  for (const key of ['LAB_USERNAME','LAB_PASSWORD','LAB_VIEWER_USERNAME','LAB_VIEWER_PASSWORD']) if (!process.env[key])
    throw new Error(`BLOCKED: required ${key} missing`);
  const manifest = readJson(path.join(runDir(), 'manifest.json'));
  if (!manifest || manifest.deadline < Date.now()) throw new Error('Run bootstrap/budget missing or exhausted');
  const health = await fetch(assertLabUrl() + '/api/health', { headers: { Connection: 'close' }, signal: AbortSignal.timeout(5000) });
  const app = await health.json();
  if (!health.ok || app.environment !== 'isolated-lab' || app.build !== BUILD || !app.persistent) throw new Error('Wrong app/readiness/build');
  const admin = await client('HR Admin', false), viewer = await client('Viewer', false);
  if ((await admin('/api/me')).role !== 'HR Admin' || (await viewer('/api/me')).role !== 'Viewer') throw new Error('Role mismatch');
  const grantFile = path.join(PRIVATE, 'grants', runId() + '.json');
  if (!fs.existsSync(grantFile)) {
    const result = await admin('/api/lab/runs', { method: 'POST', body: JSON.stringify({ runId: runId(), revision: manifest.code_revision }) });
    atomicJson(grantFile, { ...result, revision: manifest.code_revision });
  }
  atomicJson(path.join(runDir(), 'preflight.json'), { mode: 'LIVE', status: 'READY', run_id: runId(), code_revision: manifest.code_revision,
    app_build: app.build, actors: ['HR Admin', 'Viewer'], namespace: 'E2E-AOCE-<suiteRun>-<caseHash>-<attempt>-<flow>',
    character_limit: 100, lease: 'acquired', durable_ledger: true, time: new Date().toISOString() });
  console.log('Preflight READY: isolated lab, both roles, owned namespace, lease and durable ledger verified.');
}
export function cli(args, { timeout = 120000, capture = false } = {}) {
  return spawnSync(process.execPath, [path.join(ROOT, 'node_modules/playwright/cli.js'), ...args], {
    cwd: ROOT, env: process.env, encoding: 'utf8', shell: false, timeout, stdio: capture ? 'pipe' : 'inherit',
  });
}
function flatten(suites = []) {
  return suites.flatMap(s => [...(s.specs || []), ...flatten(s.suites || [])]);
}
export function discover(grep = '@smoke') {
  const args = ['test', '--project=chromium', '--list', '--reporter=json', ...(grep ? [`--grep=${grep}`] : [])];
  const output = cli(args, { capture: true });
  let data;
  try { data = JSON.parse(output.stdout); }
  catch { throw new Error('Discovery failed: ' + redact(output.stderr || 'invalid reporter output')); }
  const cases = flatten(data.suites).map(s => ({ id: s.id, title: s.title, flow: /\b(F0[123])\b/.exec(s.title)?.[1] }));
  if (!cases.length && (data.errors || []).some(e => /No tests found/.test(e.message)))
    throw Object.assign(new Error('NO-TESTS: selector chose zero cases'), { exitCode: 8 });
  if (output.status) throw new Error('Discovery failed: ' + redact((data.errors || []).map(e=>e.message).join('; ') || output.stderr || 'selector error'));
  if (!cases.length) throw Object.assign(new Error('NO-TESTS: selector chose zero cases'), { exitCode: 8 });
  if (grep === '@smoke' && (cases.length !== 3 || new Set(cases.map(c => c.flow)).size !== 3)) throw new Error('Smoke must select exactly F01/F02/F03');
  const target = process.env.LAB_LANE === 'pr' ? path.join(ROOT, 'evidence-export/pr') : runDir();
  atomicJson(path.join(target, 'discovery.json'), { mode: 'DISCOVERY', selected_count: cases.length, project: 'chromium', grep, cases });
  console.log(`Discovery: ${cases.length} selected; no execution/pass claim.`); return cases;
}
export function execute(grep = '@smoke') {
  const manifest = readJson(path.join(runDir(), 'manifest.json'));
  const ready = readJson(path.join(runDir(), 'preflight.json'));
  if (!ready || ready.code_revision !== revision() || manifest.deadline < Date.now() + 60000) throw new Error('Preflight/revision/budget gate failed');
  const result = cli(['test', '--project=chromium', ...(grep ? [`--grep=${grep}`] : [])], { timeout: Math.min(720000, manifest.deadline - Date.now() - 60000) });
  if (result.error || result.status !== 0) throw Object.assign(new Error(result.error ? 'Runner timed out/environment error' : 'Runner assertions failed'), { exitCode: result.status || 10 });
}
export async function reconcile() {
  const call = await client();
  const ledger = await call('/api/lab/ledger');
  const rows = [];
  for (const entry of ledger.records) {
    const lookup = await call(`/api/lab/records/${entry.employeeId}`);
    if (lookup.found && lookup.record.owner !== runId()) throw new Error('Ownership mismatch: cleanup blocked');
    let outcome = entry.cleanup;
    if (lookup.found) outcome = (await call(`/api/lab/records/${entry.employeeId}`, { method: 'DELETE' })).cleanup;
    else if (entry.writeState !== 'NOT_WRITTEN' && !['success','absent'].includes(outcome))
      outcome = (await call(`/api/lab/records/${entry.employeeId}`, { method: 'DELETE' })).cleanup;
    const after = await call(`/api/lab/records/${entry.employeeId}`);
    rows.push({ employee_id: entry.employeeId, owner: entry.owner, write_state: entry.writeState, writes: entry.writes,
      cleanup: outcome, record_absent_after: !after.found });
  }
  const unresolved = rows.filter(r => !r.record_absent_after).length;
  atomicJson(path.join(runDir(), 'cleanup.json'), { mode: 'LIVE', run_id: runId(), records: rows, unresolved_count: unresolved,
    cleanup_status: unresolved ? 'unresolved' : 'resolved', time: new Date().toISOString() });
  if (unresolved) throw Object.assign(new Error('Unresolved cleanup'), { exitCode: 6 });
  await call('/api/lab/release', { method: 'POST' });
  console.log(`Cleanup: ${rows.length} exact owned IDs verified absent; unresolved=0.`);
}
export function finalize(error = null) {
  const file = path.join(runDir(), 'manifest.json'), manifest = readJson(file);
  if (!manifest) throw new Error('Manifest missing');
  const cleanup = readJson(path.join(runDir(), 'cleanup.json'));
  manifest.cleanup_status = cleanup?.cleanup_status || 'UNKNOWN';
  manifest.finished_at = new Date().toISOString();
  manifest.end_to_end_seconds = (Date.parse(manifest.finished_at) - Date.parse(manifest.started_at)) / 1000;
  manifest.operational_error = error ? redact(error.message) : null;
  manifest.label = !error && manifest.runner_outcome === 'passed' && cleanup?.unresolved_count === 0 ? 'RUN-PASSED' : 'RUN-FAILED/UNKNOWN';
  atomicJson(file, manifest);
}
export function evidence() {
  const manifest = readJson(path.join(runDir(), 'manifest.json'));
  const discovery = readJson(path.join(runDir(), 'discovery.json'));
  const cleanup = readJson(path.join(runDir(), 'cleanup.json'));
  const gaps = [];
  if (!manifest || manifest.run_id !== runId() || manifest.code_revision !== revision()) gaps.push('manifest/revision mismatch');
  if (!discovery?.selected_count || discovery.selected_count !== manifest?.selected_count) gaps.push('selection mismatch/no-tests');
  if (manifest?.executed_count !== manifest?.selected_count) gaps.push('incomplete execution');
  if (!cleanup || cleanup.unresolved_count !== 0) gaps.push('cleanup unknown/unresolved');
  for (const item of manifest?.cases || []) {
    if (!item.employee_id || !item.flow || !item.oracle || !item.source_refs.length || !item.cleanup) gaps.push(`case ${item.logical_case_id} lacks assertion/ownership metadata`);
    if (item.kind === 'business-smoke' && !item.artifacts.length) gaps.push(`case ${item.logical_case_id} screenshot missing`);
    for (const artifact of item.artifacts) {
      const file = path.join(ROOT, artifact.path);
      if (!fs.existsSync(file) || shaFile(file) !== artifact.sha256) gaps.push(`artifact missing/hash mismatch ${artifact.name}`);
    }
  }
  atomicJson(path.join(runDir(), 'evidence-check.json'), { mode: 'LIVE', run_id: runId(), status: gaps.length ? 'INCOMPLETE' : 'COMPLETE', gaps });
  if (gaps.length) throw Object.assign(new Error('Evidence incomplete: ' + gaps.join('; ')), { exitCode: 13 });
  console.log('Evidence COMPLETE: selected/executed, revision, source/oracle/artifact and cleanup linked.');
}
export function shaFile(file) { return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'); }
export function exportEvidence() {
  const manifest = readJson(path.join(runDir(), 'manifest.json'));
  const destination = path.join(path.dirname(ROOT), 'bai-nop-AOCE', 'live', 'runs', runId());
  fs.mkdirSync(destination, { recursive: true });
  for (const name of ['manifest.json','preflight.json','discovery.json','cleanup.json','evidence-check.json']) {
    const file = path.join(runDir(), name);
    if (fs.existsSync(file)) fs.writeFileSync(path.join(destination, name), redact(fs.readFileSync(file, 'utf8')));
  }
  for (const item of manifest?.cases || []) for (const artifact of item.artifacts) {
    const file = path.join(ROOT, artifact.path);
    if (fs.existsSync(file)) fs.copyFileSync(file, path.join(destination, `${item.flow}-${crypto.createHash('sha256').update(item.logical_case_id).digest('hex').slice(0,12)}-${artifact.name}.png`));
  }
  console.log(`Sanitized evidence exported: bai-nop-AOCE/live/runs/${runId()}`);
  return destination;
}
