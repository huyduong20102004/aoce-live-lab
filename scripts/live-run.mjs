import path from 'node:path';
import crypto from 'node:crypto';
import fs from 'node:fs';
import { spawn } from 'node:child_process';
import { ROOT, PRIVATE, loadEnv, assertLabUrl, readJson, atomicJson, redact } from '../server/lib.mjs';
import { bootstrap, preflight, discover, execute, reconcile, finalize, evidence, exportEvidence, runDir } from './runtime.mjs';

loadEnv();
const suite = process.argv.find(a => a.startsWith('--suite='))?.split('=')[1] || 'smoke';
const trigger = process.argv.find(a => a.startsWith('--trigger='))?.split('=')[1] || 'manual-local';
if (!['all','smoke'].includes(suite) || !['manual-local','windows-schedule','github-manual','github-schedule'].includes(trigger)) throw new Error('Unsupported suite/trigger');
if (trigger === 'windows-schedule' && !process.env.AOCE_SCHEDULER_TASK) throw new Error('OS task marker required; manual invocation is not schedule evidence');
if (trigger.startsWith('github-') && (process.env.GITHUB_ACTIONS !== 'true' ||
    process.env.GITHUB_EVENT_NAME !== (trigger === 'github-schedule' ? 'schedule' : 'workflow_dispatch')))
  throw new Error('Actual GitHub event context required; local manual invocation is not GitHub CI evidence');
process.env.LAB_RUN_ID ||= `${Date.now().toString(36)}-${crypto.randomBytes(4).toString('hex')}`;
const grep = suite === 'smoke' ? '@smoke' : null;
let server, error, initialized = false;
async function ready() {
  try { return (await fetch(assertLabUrl() + '/api/health', { signal: AbortSignal.timeout(1000) })).ok(); }
  catch { return false; }
}
try {
  bootstrap(trigger, suite); initialized = true;
  if (!await ready()) {
    server = spawn(process.execPath, [path.join(ROOT, 'server/server.mjs')], { cwd: ROOT, env: process.env, shell: false, stdio: 'ignore', windowsHide: true });
    const deadline = Date.now() + 10000;
    while (!await ready()) {
      if (Date.now() > deadline || server.exitCode !== null) throw new Error('BLOCKED-ENVIRONMENT: local server did not start');
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }
  await preflight(); discover(grep); execute(grep);
} catch (issue) { error = issue; console.error(redact(issue.message)); }
finally {
  if (initialized) {
    const grant = path.join(PRIVATE, 'grants', process.env.LAB_RUN_ID + '.json');
    if (fs.existsSync(grant)) try { await reconcile(); } catch (issue) { error ||= issue; console.error(redact(issue.message)); }
    else atomicJson(path.join(runDir(), 'cleanup.json'), { mode: 'LIVE', run_id: process.env.LAB_RUN_ID,
      cleanup_status: 'resolved', unresolved_count: 0, records: [], rationale: 'Preflight did not issue capability; runner never dispatched.' });
    finalize(error);
    try { evidence(); } catch (issue) { error ||= issue; finalize(error); console.error(redact(issue.message)); }
    exportEvidence();
    const manifest = readJson(path.join(runDir(), 'manifest.json'));
    console.log(JSON.stringify({ run_id: manifest.run_id, revision: manifest.code_revision, trigger: manifest.trigger,
      label: manifest.label, selected: manifest.selected_count, executed: manifest.executed_count, cleanup: manifest.cleanup_status }));
  }
  if (server) server.kill();
}
process.exitCode = error ? error.exitCode || 1 : 0;
