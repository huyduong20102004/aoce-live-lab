import path from 'node:path';
import {PRIVATE,readJson,atomicJson} from '../server/lib.mjs';
import {bootstrap,preflight,client,runId,runDir} from './runtime.mjs';
bootstrap('manual-local','controlled-cancel');
await preflight();
const call=await client();
const caseId='c'+runId().replace(/[^a-f0-9]/g,'').padEnd(8,'0').slice(0,8);
const employeeId=`E2E-AOCE-${runId()}-${caseId}-a1-F01`;
await call('/api/lab/reservations',{method:'POST',body:JSON.stringify({flow:'F01',attempt:'a1',caseId,employeeId})});
const created=await call('/api/employees',{method:'POST',body:JSON.stringify({employeeId,department:'QA'})});
if(created.record.owner!==runId())throw new Error('Ownership mismatch');
const grant=readJson(path.join(PRIVATE,'grants',runId()+'.json'));
const manifest=readJson(path.join(runDir(),'manifest.json'));
atomicJson(path.join(runDir(),'manifest.json'),{...manifest,command:'node scripts/cancel-victim.mjs',write_state:'CREATED',owned_employee_id:employeeId});
console.log(JSON.stringify({phase:'WRITE_COMMITTED',pid:process.pid,run_id:runId(),employee_id:employeeId,deadline:grant.deadline}));
await new Promise(()=>setInterval(()=>{},1000)); // No finally cleanup: supervisor force-kills this worker.
