import { test as base, expect, type APIRequestContext } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { ROOT, loadEnv } from '../../server/lib.mjs';
import { route, type Flow } from '../../controller/contracts.js';
import { EmployeePage } from '../pages/EmployeePage.js';
import { EmployeeSteps } from '../steps/EmployeeSteps.js';
loadEnv();
export type Lab = {
  runId: string; flow: Flow; id: string; admin: APIRequestContext; employee: EmployeePage; steps: EmployeeSteps;
  lookup(): Promise<{ found: boolean; record: { employeeId: string; department: string; owner: string } | null; writes: number }>;
  seed(department?: string): Promise<void>;
  annotate(sources: string[], oracle: string): void;
};
export const test = base.extend<{ lab: Lab }>({
  lab: async ({ playwright, browser }, use, testInfo) => {
    const runId = process.env.LAB_RUN_ID;
    if (!runId) throw new Error('Run through npm run lab:smoke or npm test: preflight/run manifest required');
    const meta = /\b(F0[123])\b/.exec(testInfo.title);
    if (!meta) throw new Error('Explicit F01/F02/F03 flow required');
    const flow = meta[1] as Flow, attempt = `a${testInfo.retry + 1}`;
    const caseId = `c${createHash('sha256').update(testInfo.testId).digest('hex').slice(0, 8)}`;
    const caseRunId = `${runId}-${caseId}`;
    const id = `E2E-AOCE-${caseRunId}-${attempt}-${flow}`;
    const capability = JSON.parse(fs.readFileSync(path.join(ROOT, '.lab', 'grants', `${runId}.json`), 'utf8'));
    const actor = flow === 'F03' ? 'Viewer' : 'HR Admin';
    const headers = { 'x-lab-run-id': runId, 'x-lab-token': capability.token };
    const admin = await playwright.request.newContext({ baseURL: process.env.LAB_BASE_URL, extraHTTPHeaders: headers });
    const auth = await admin.post('/api/login', { data: { username: process.env.LAB_USERNAME, password: process.env.LAB_PASSWORD } });
    expect(auth.ok()).toBeTruthy();
    const reserve = await admin.post('/api/lab/reservations', { data: { flow, attempt, caseId, employeeId: id } });
    expect(reserve.status()).toBe(201);
    const decision = route({ flow, environment: process.env.LAB_ENVIRONMENT!, actor, runId: caseRunId, attempt, employeeId: id,
      revision: capability.revision, budgetRemainingMs: capability.deadline - Date.now(), roleReady: true,
      seedOwned: flow === 'F02', seedDepartment: flow === 'F02' ? 'QA' : undefined });
    expect(decision.allowed, decision.reason).toBeTruthy();
    const actorApi = actor === 'HR Admin' ? admin : await playwright.request.newContext({ baseURL: process.env.LAB_BASE_URL, extraHTTPHeaders: headers });
    if (actor === 'Viewer') expect((await actorApi.post('/api/login', { data: { username: process.env.LAB_VIEWER_USERNAME, password: process.env.LAB_VIEWER_PASSWORD } })).ok()).toBeTruthy();
    const context = await browser.newContext({ baseURL: process.env.LAB_BASE_URL, extraHTTPHeaders: headers, viewport: { width: 1365, height: 900 } });
    const cookies = (await actorApi.storageState()).cookies; // Memory only. Never write auth state to evidence/source.
    await context.addCookies(cookies);
    await context.tracing.start({ screenshots: true, snapshots: true, sources: true });
    const page = await context.newPage(); const employee = new EmployeePage(page);
    const lookup = async () => {
      const response = await admin.get(`/api/lab/records/${id}`); expect(response.ok()).toBeTruthy(); return response.json();
    };
    const seed = async (department = 'QA') => {
      const response = await admin.post('/api/employees', { data: { employeeId: id, department } });
      expect(response.status()).toBe(201);
    };
    testInfo.annotations.push({ type: 'flow', description: flow }, { type: 'actor', description: actor },
      { type: 'employee_id', description: id }, { type: 'attempt_id', description: attempt },
      { type: 'case_run_id', description: caseRunId });
    try {
      await use({ runId, flow, id, admin, employee, steps: new EmployeeSteps(employee), lookup, seed,
        annotate(sources, oracle) {
          for (const source of sources) testInfo.annotations.push({ type: 'source', description: source });
          testInfo.annotations.push({ type: 'oracle', description: oracle });
        } });
    } finally {
      const before = await lookup();
      if (before.found) {
        expect(before.record?.owner).toBe(runId);
        const cleanup = await admin.delete(`/api/lab/records/${id}`); expect(cleanup.ok()).toBeTruthy();
        expect((await lookup()).found).toBe(false);
        testInfo.annotations.push({ type: 'cleanup', description: 'success' });
      } else testInfo.annotations.push({ type: 'cleanup', description: 'not-applicable' });
      if (testInfo.status !== testInfo.expectedStatus) {
        const trace = testInfo.outputPath('trace.zip'); await context.tracing.stop({ path: trace });
        await testInfo.attach('private-trace', { path: trace, contentType: 'application/zip' });
      } else await context.tracing.stop();
      await context.close(); if (actorApi !== admin) await actorApi.dispose(); await admin.dispose();
    }
  },
});
export { expect };
