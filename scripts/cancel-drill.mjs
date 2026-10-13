import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawn,spawnSync} from 'node:child_process';
import {ROOT,PRIVATE,loadEnv,assertLabUrl,atomicJson,readJson,redact} from '../server/lib.mjs';
import {client,exportEvidence} from './runtime.mjs';
loadEnv();assertLabUrl();
process.env.LAB_RUN_ID='cancel-'+Date.now().toString(36)+'-'+crypto.randomBytes(3).toString('hex');
const run=process.env.LAB_RUN_ID;
const env={...process.env,LAB_LEASE_MS:'15000'};
const dir=path.join(PRIVATE,'runs',run);
const report={scope:'ACTUAL LOCAL FORCE-CANCEL + OUT-OF-RUNNER WATCHDOG',run_id:run,supervisor_pid:process.pid,started_at:new Date().toISOString(),assertion_outcome:'NOT_EXECUTED',checks:[]};
let victim, marker, watchdogStarted=false;
try{
  const admin=await client('HR Admin',false);
  const demoBefore=(await admin('/api/employees?id=EMP-1001')).records;
  victim=spawn(process.execPath,[path.join(ROOT,'scripts/cancel-victim.mjs')],{cwd:ROOT,env,shell:false,windowsHide:true,stdio:['ignore','pipe','pipe']});
  const exited=new Promise(resolve=>victim.once('exit',(code,signal)=>resolve({code,signal})));
  let buffer='';let errorLog='';
  victim.stderr.on('data',data=>{errorLog+=redact(data.toString());});
  const committed=new Promise((resolve,reject)=>{
    const timeout=setTimeout(()=>reject(new Error('Victim did not commit owned record within20sec')),20000);
    victim.stdout.on('data',data=>{buffer+=data.toString();let end;while((end=buffer.indexOf('\n'))>=0){const line=buffer.slice(0,end);buffer=buffer.slice(end+1);try{const message=JSON.parse(line);if(message.phase==='WRITE_COMMITTED'){clearTimeout(timeout);resolve(message);}}catch{}}});
    victim.once('exit',()=>{if(!marker){clearTimeout(timeout);reject(new Error('Victim exited before write marker: '+errorLog));}});
  });
  marker=await committed;report.victim_pid=marker.pid;assert.equal(victim.pid,marker.pid);
  const call=await client();
  const before=await call(`/api/lab/records/${marker.employee_id}`);
  assert.equal(before.found,true);assert.equal(before.record.owner,run);assert.equal(before.writes,1);
  report.owned_employee_id=marker.employee_id;report.lease_deadline=marker.deadline;
  report.checks.push({check:'owned write committed before cancel',result:'PASSED',writes:before.writes});
  victim.kill('SIGKILL');report.victim_exit=await exited;report.cancelled_at=new Date().toISOString();
  const afterKill=await call(`/api/lab/records/${marker.employee_id}`);
  assert.equal(afterKill.found,true);assert.equal(fs.existsSync(path.join(dir,'cleanup.json')),false);
  report.checks.push({check:'force-killed runner leaves record; its cleanup did not run',result:'PASSED'});
  const executeWatchdog=()=>{
    const result=spawnSync(process.execPath,[path.join(ROOT,'scripts/watchdog.mjs'),'--run-id='+run],{cwd:ROOT,env:process.env,encoding:'utf8',shell:false,timeout:20000});
    if(result.status!==0)throw new Error('Standalone watchdog failed: '+redact(result.stderr||result.stdout));
    return JSON.parse(result.stdout.trim().split('\n').at(-1));
  };
  if(marker.deadline>Date.now()+1000){
    const active=executeWatchdog();
    assert.equal(active.records[0].action,'SKIP_ACTIVE_LEASE');
    assert.equal((await call(`/api/lab/records/${marker.employee_id}`)).found,true);
    report.checks.push({check:'negative control: watchdog does not delete active-lease data',result:'PASSED',watchdog_pid:active.pid});
  }else throw new Error('Active-lease negative control not observable; retain inconclusive result');
  const remaining=marker.deadline-Date.now()+100;
  if(remaining>0)await new Promise(resolve=>setTimeout(resolve,remaining));
  const recovered=executeWatchdog();watchdogStarted=true;
  assert.notEqual(recovered.pid,marker.pid);assert.notEqual(recovered.pid,process.pid);
  assert.equal(recovered.records[0].action,'RECONCILED');assert.equal(recovered.unresolved,0);
  const after=await call(`/api/lab/records/${marker.employee_id}`);
  assert.equal(after.found,false);assert.equal(after.writes,1);
  assert.deepEqual((await admin('/api/employees?id=EMP-1001')).records,demoBefore);
  const released=await call('/api/lab/ledger');assert.equal(released.released,true);
  const repeated=executeWatchdog();assert.equal(repeated.records[0].action,'SKIP_ALREADY_RELEASED');
  report.watchdog_pid=recovered.pid;
  report.checks.push({check:'standalone process outside cancelled runner reconciles expired owned ID',result:'PASSED'},
    {check:'record absent, exactly1 write, no duplicate retry',result:'PASSED'},
    {check:'unowned demo preserved',result:'PASSED'},
    {check:'idempotent repeat skips released run',result:'PASSED'});
  report.status='RECOVERY-VERIFIED';
  const manifest=readJson(path.join(dir,'manifest.json'));report.code_revision=manifest.code_revision;
  atomicJson(path.join(dir,'manifest.json'),{...manifest,label:'CANCELLED',runner_outcome:'CANCELLED',assertion_outcome:'NOT_EXECUTED',cleanup_status:'resolved',finished_at:new Date().toISOString(),controlled_cancel:true});
  atomicJson(path.join(dir,'cancellation-drill.json'),report);
  const exportDir=exportEvidence();atomicJson(path.join(exportDir,'cancellation-drill.json'),report);atomicJson(path.join(exportDir,'watchdog.json'),recovered);
  console.log(JSON.stringify(report));
}catch(error){
  if(victim && victim.exitCode===null)victim.kill('SIGKILL');
  report.status='FAILED/UNKNOWN';report.error=redact(error.message);report.watchdog_started=watchdogStarted;
  atomicJson(path.join(dir,'cancellation-drill.json'),report);console.error(JSON.stringify(report));process.exitCode=1;
}
