import path from 'node:path';
import crypto from 'node:crypto';
import fs from 'node:fs';
import { spawnSync } from 'node:child_process';
import { ROOT, PRIVATE, atomicJson } from '../server/lib.mjs';
import { bootstrap, discover } from './runtime.mjs';

// These checks execute real script failure paths, with no runner writes.
process.env.LAB_RUN_ID = 'guard-' + Date.now().toString(36) + '-' + crypto.randomBytes(2).toString('hex');
bootstrap('manual-local','smoke');
const missing=spawnSync(process.execPath,[path.join(ROOT,'scripts/cli.mjs'),'preflight'],{
  cwd:ROOT,shell:false,encoding:'utf8',env:{...process.env,LAB_PASSWORD:''},timeout:10000 });
const credentialsBlocked=missing.status!==0 && (missing.stderr||'').includes('LAB_PASSWORD missing');
let noTestsBlocked=false,noTestsExit=null;
try { discover('@does-not-exist'); }
catch (error) { noTestsBlocked=/NO-TESTS/.test(error.message); noTestsExit=error.exitCode; }
const invalidTrigger=spawnSync(process.execPath,[path.join(ROOT,'scripts/live-run.mjs'),'--trigger=github-schedule'],{
  cwd:ROOT,shell:false,encoding:'utf8',env:{...process.env,GITHUB_ACTIONS:'false'},timeout:10000 });
const forgedCIBlocked=invalidTrigger.status!==0 && (invalidTrigger.stderr||'').includes('Actual GitHub event context required');
const output={mode:'LIVE-LOCAL SCRIPT GUARD CHECK',code_revision:(await import('./runtime.mjs')).revision(),checks:[
  {scenario:'CI-52',required:'missing secret must block',exit_code:missing.status,detected:credentialsBlocked,writes:0},
  {scenario:'CI-53',required:'no tests must fail',exit_code:noTestsExit,detected:noTestsBlocked,writes:0},
  {scenario:'LOCAL-TRIGGER',required:'manual invocation cannot claim GitHub schedule',exit_code:invalidTrigger.status,detected:forgedCIBlocked,writes:0},
]};
atomicJson(path.join(path.dirname(ROOT),'bai-nop-AOCE/live/runtime-guard-checks.json'),output);
// Keep guard run separate from business execution ledger: no app run was dispatched.
fs.renameSync(path.join(PRIVATE,'runs',process.env.LAB_RUN_ID),path.join(PRIVATE,process.env.LAB_RUN_ID));
console.log(JSON.stringify(output,null,2));
process.exitCode=output.checks.every(c=>c.detected)?0:1;
