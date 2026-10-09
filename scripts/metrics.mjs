import fs from 'node:fs';
import path from 'node:path';
import { ROOT, atomicJson, readJson } from '../server/lib.mjs';
const evidenceRoot = path.join(path.dirname(ROOT),'bai-nop-AOCE','live');
const runsPath = path.join(evidenceRoot,'runs');
const runs = fs.existsSync(runsPath) ? fs.readdirSync(runsPath).map(id=>readJson(path.join(runsPath,id,'manifest.json'))).filter(Boolean) : [];
const groups = {};
const median = values => {
  const sorted=[...values].sort((a,b)=>a-b), n=sorted.length;
  return n ? (n%2 ? sorted[(n-1)/2] : (sorted[n/2-1]+sorted[n/2])/2) : null;
};
for (const run of runs) {
  const group=groups[run.code_revision] ||= {revision:run.code_revision,runs:[],business:[],controls:[]};
  group.runs.push({run_id:run.run_id,trigger:run.trigger,label:run.label,started_at:run.started_at,end_to_end_seconds:run.end_to_end_seconds});
  for (const item of run.cases || []) group[item.kind==='business-smoke'?'business':'controls'].push({...item,run_id:run.run_id});
}
const result={mode:'LIVE-LOCAL',generated_at:new Date().toISOString(),cost_total:'UNKNOWN',cost_reason:'No provider calls at runner runtime; no monetary rate for local compute/CI. Synthetic packet ledger excluded.',groups:[]};
for (const group of Object.values(groups)) {
  const executed=group.business.filter(c=>c.status!=='skipped'), passes=executed.filter(c=>c.status==='passed');
  const needs=executed.filter(c=>c.flow!=='F03'), cleanupSuccess=needs.filter(c=>c.cleanup==='success');
  const full=executed.filter(c=>c.oracle && c.source_refs.length && c.artifacts.length);
  const attempts=executed.reduce((n,c)=>n+c.attempts,0), times=executed.map(c=>c.test_seconds);
  const scheduled=group.runs.filter(r=>r.trigger==='windows-schedule'||r.trigger==='github-schedule');
  result.groups.push({revision:group.revision,runs:group.runs,
    business_metrics:{selected:group.business.length,executed:executed.length,first_pass:passes.filter(c=>c.attempts===1).length,
      eventual_pass:passes.length,failed:executed.filter(c=>c.status==='failed'||c.status==='timedOut').length,
      flaky_pass:passes.filter(c=>c.attempts>1).length,attempts,retry_overhead:attempts-executed.length,
      evidence_full:full.length,cleanup_needed:needs.length,cleanup_success:cleanupSuccess.length,
      model_calls:0,usage_status:'not-applicable',model_cost:0,total_measured_money:'UNKNOWN',
      test_seconds:{n:times.length,median:median(times),min:times.length?Math.min(...times):null,max:times.length?Math.max(...times):null}},
    robustness_controls:{selected:group.controls.length,executed:group.controls.filter(c=>c.status!=='skipped').length,
      passed:group.controls.filter(c=>c.status==='passed').length,not_business_requirement_passes:true},
    observed_scheduled_runs:scheduled.length, schedule_completeness:'Requires separate expected slot ledger; manual runs not schedule proof'});
}
atomicJson(path.join(evidenceRoot,'actual-metrics.json'),result);
const lines=['# Actual local execution metrics','',`Generated: ${result.generated_at}. LIVE-LOCAL, not production telemetry; synthetic U7 cohort excluded.`,
  '', '| Revision | Runs | Business selected/executed | First/eventual pass | Flaky / failed | Cleanup success/needed | Full evidence | Control pass/selected | Scheduled observed |',
  '| --- | ---: | --- | --- | --- | --- | --- | --- | ---: |'];
for (const group of result.groups) {
  const m=group.business_metrics,c=group.robustness_controls;
  lines.push(`| ${group.revision} | ${group.runs.length} | ${m.selected}/${m.executed} | ${m.first_pass}/${m.eventual_pass} | ${m.flaky_pass}/${m.failed} | ${m.cleanup_success}/${m.cleanup_needed} | ${m.evidence_full}/${m.executed} | ${c.passed}/${c.selected} | ${group.observed_scheduled_runs} |`);
  lines.push('');
  lines.push(`Test duration: n=${m.test_seconds.n}, median=${m.test_seconds.median}s, range=${m.test_seconds.min}–${m.test_seconds.max}s. Queue/install/cleanup excluded. No inference of production reliability from this small local cohort.`);
}
lines.push('','Runner model calls=0 (deterministic tests), usage=N/A, model cost=0; total local execution/CI money UNKNOWN because no compute rate supplied. Scheduled observed count requires OS/CI trigger evidence in separate reports; expected daily slots must not be invented.','');
fs.writeFileSync(path.join(evidenceRoot,'actual-metrics.md'),lines.join('\n'));
console.log(JSON.stringify(result,null,2));
