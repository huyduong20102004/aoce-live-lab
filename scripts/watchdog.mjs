import fs from 'node:fs';
import path from 'node:path';
import { PRIVATE, readJson, atomicJson, redact } from '../server/lib.mjs';
import {client,reconcile} from './runtime.mjs';

const grants=path.join(PRIVATE,'grants');
const requested=process.argv.find(arg=>arg.startsWith('--run-id='))?.slice('--run-id='.length);
if(requested && !/^[a-zA-Z0-9-]{5,40}$/.test(requested)) throw new Error('Exact validated run ID required');
if(requested && !fs.existsSync(path.join(grants,requested+'.json'))) throw new Error('Owned capability missing; do not infer cleanup success');
const report={scope:'STANDALONE EXPIRED-RUN RECONCILER',pid:process.pid,started_at:new Date().toISOString(),records:[],unresolved:0};
const names=fs.existsSync(grants)?fs.readdirSync(grants).filter(n=>n.endsWith('.json') && (!requested||n===requested+'.json')):[];
for(const file of names){
  const grant=readJson(path.join(grants,file)); process.env.LAB_RUN_ID=grant.runId;
  try{
    const call=await client(); const ledger=await call('/api/lab/ledger');
    if(ledger.released){report.records.push({run_id:grant.runId,action:'SKIP_ALREADY_RELEASED'});continue;}
    if(ledger.deadline>Date.now()){report.records.push({run_id:grant.runId,action:'SKIP_ACTIVE_LEASE',deadline:ledger.deadline});continue;}
    await reconcile();
    const cleanup=readJson(path.join(PRIVATE,'runs',grant.runId,'cleanup.json'));
    if(!cleanup||cleanup.unresolved_count!==0)throw new Error('Cleanup proof incomplete');
    report.records.push({run_id:grant.runId,action:'RECONCILED',deadline:ledger.deadline,owned_ids:cleanup.records.length,unresolved:0});
  }catch(error){report.unresolved++;report.records.push({run_id:grant.runId,action:'UNRESOLVED',error:redact(error.message)});}
}
report.finished_at=new Date().toISOString();
if(requested)atomicJson(path.join(PRIVATE,'runs',requested,'watchdog-last.json'),report);
console.log(JSON.stringify(report));
process.exitCode=report.unresolved?6:0;
