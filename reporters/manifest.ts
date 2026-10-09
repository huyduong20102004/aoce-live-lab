import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import type { Reporter, FullConfig, Suite, TestCase, TestResult, FullResult } from '@playwright/test/reporter';
import { ROOT, BUILD, loadEnv, atomicJson, readJson, redact } from '../server/lib.mjs';
loadEnv();
export default class ManifestReporter implements Reporter {
  private cases: Record<string, unknown>[] = [];
  private selected: { id: string; title: string }[] = [];
  onBegin(_config: FullConfig, suite: Suite) {
    this.selected = suite.allTests().map(t => ({ id: t.id, title: t.title }));
  }
  onTestEnd(test: TestCase, result: TestResult) {
    const annotation = (type: string) => test.annotations.find(a => a.type === type)?.description ?? null;
    const imageDir=path.join(ROOT,'.lab','runs',process.env.LAB_RUN_ID!,'screenshots');
    const artifacts = result.attachments.filter(a => (a.path || a.body) && a.contentType === 'image/png').map((a,index) => {
      const file=a.path || path.join(imageDir,`${test.id}-${result.retry}-${index}.png`);
      if (!a.path) { fs.mkdirSync(imageDir,{recursive:true}); fs.writeFileSync(file,a.body!); }
      return {name:a.name,path:path.relative(ROOT,file),sha256:createHash('sha256').update(fs.readFileSync(file)).digest('hex')};
    });
    this.cases.push({ logical_case_id: test.id, title: test.title, kind: test.title.includes('@smoke') ? 'business-smoke' : 'lab-control',
      flow: annotation('flow'), actor: annotation('actor'), employee_id: annotation('employee_id'), case_run_id: annotation('case_run_id'),
      attempt_id: annotation('attempt_id'), attempts: result.retry + 1, status: result.status, expected_status: test.expectedStatus,
      source_refs: test.annotations.filter(a => a.type === 'source').map(a => a.description),
      oracle: annotation('oracle'), cleanup: annotation('cleanup'), test_seconds: result.duration / 1000,
      started_at: result.startTime.toISOString(), artifacts, errors: result.errors.map(e => redact(e.message ?? 'runner error')) });
  }
  onEnd(result: FullResult) {
    const runId = process.env.LAB_RUN_ID;
    if (!runId) return;
    const dir = path.join(ROOT, '.lab', 'runs', runId);
    const prior = readJson(path.join(dir, 'manifest.json'), {});
    atomicJson(path.join(dir, 'manifest.json'), { ...prior, schema_version: 'aoce-live-run-1', mode: 'LIVE',
      app_build: BUILD, environment_alias: 'isolated-lab', prompt_version: 'aoce-prompt-v3', context_version: 'aoce-context-v3',
      model_calls: 0, usage_status: 'not-applicable', model_cost: 0, ci_billable_cost: null, cost_unit: 'NOT_SPECIFIED',
      runner_outcome: result.status, runner_started_at: result.startTime.toISOString(), runner_finished_at: new Date().toISOString(),
      runner_seconds: result.duration / 1000, selected_count: this.selected.length,
      executed_count: this.cases.filter(c => c.status !== 'skipped').length, selected: this.selected, cases: this.cases });
  }
}
