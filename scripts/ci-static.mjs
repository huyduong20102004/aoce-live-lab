import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {ROOT, atomicJson, redact} from '../server/lib.mjs';
const output=path.join(ROOT,'evidence-export','pr');
fs.mkdirSync(output,{recursive:true});
const ref=spawnSync('git',['rev-parse','HEAD'],{cwd:ROOT,encoding:'utf8',shell:false});
const checks=[];
const tasks=[
  ['typecheck',['node_modules/typescript/bin/tsc','--noEmit']],
  ['context-regression',['node_modules/tsx/dist/cli.mjs','--test','tests/controller-regression.test.ts']],
  ['smoke-discovery',['scripts/cli.mjs','discover']],
];
for(const [name,args] of tasks){
  const start=Date.now();
  const result=spawnSync(process.execPath,args,{cwd:ROOT,env:{...process.env,LAB_LANE:'pr'},encoding:'utf8',shell:false,timeout:120000});
  const log=redact((result.stdout||'')+(result.stderr||''));
  fs.writeFileSync(path.join(output,name+'.txt'),log);
  checks.push({check:name,exit_code:result.status,seconds:(Date.now()-start)/1000,status:result.status===0?'PASSED':'FAILED'});
  console.log(log);
  atomicJson(path.join(output,'checks.json'),{scope:'ACTUAL PR STATIC/FIXTURE/DISCOVERY, NOT LIVE APP PASS',
    code_revision:ref.stdout.trim(),github_head_sha:process.env.GITHUB_SHA||null,
    github_run_url:process.env.GITHUB_ACTIONS==='true'?`${process.env.GITHUB_SERVER_URL}/${process.env.GITHUB_REPOSITORY}/actions/runs/${process.env.GITHUB_RUN_ID}`:null,
    started_checks:checks.length,checks});
  if(result.status!==0){process.exitCode=result.status||1;break;}
}
