import { createHash } from 'node:crypto';
import path from 'node:path';
import { test, expect } from '../fixtures/lab.js';
import { route } from '../../controller/contracts.js';
import { ROOT } from '../../server/lib.mjs';

test('F01 @control INC-61 ambiguous Save rejected then scoped overlay recovery', async ({ lab }, info) => {
  lab.annotate(['AC-EMP-01','AC-EMP-02','LAB-AOCE-05','LOCAL-INC-61'], 'Two Save targets reject naive locator; scoped dialog preserves ID/QA');
  await lab.employee.open('ambiguous-save'); await lab.employee.elements.create.click();
  await lab.employee.elements.dialog.getByLabel('Employee ID', { exact: true }).fill(lab.id);
  await lab.employee.elements.dialog.getByLabel('Department', { exact: true }).selectOption('QA');
  await expect(lab.employee.page.getByRole('button', { name: 'Save', exact: true })).toHaveCount(2);
  await expect(lab.employee.page.getByRole('button', { name: 'Save', exact: true }).click({ timeout: 500 })).rejects.toThrow(/strict mode violation/);
  expect((await lab.lookup()).found).toBe(false);
  await expect(lab.employee.elements.save).toHaveCount(1); await lab.employee.elements.save.click();
  await expect(lab.employee.elements.dialog).not.toBeVisible(); await lab.employee.search(lab.id);
  await expect(lab.employee.elements.row(lab.id)).toHaveCount(1);
  await expect(lab.employee.elements.row(lab.id).getByRole('cell', { name: 'QA', exact: true })).toBeVisible();
  await info.attach('recovery-ui', { body: await lab.employee.page.screenshot(), contentType: 'image/png' });
});
test('F01 @control INC-62 delayed acknowledgement reconciles one committed write', async ({ lab }, info) => {
  lab.annotate(['AC-EMP-01','AC-EMP-02','LAB-AOCE-05','LOCAL-INC-62'], 'UI timeout then owned lookup; no duplicate create; exact ID/QA search');
  await lab.employee.open('unknown-write'); await lab.employee.create(lab.id, 'QA', true);
  const existing = await lab.lookup(); expect(existing.found).toBe(true); expect(existing.writes).toBe(1);
  const caseRunId = lab.id.slice('E2E-AOCE-'.length).replace(/-a1-F01$/, '');
  const blocked = route({ flow:'F01', environment:'isolated-lab', actor:'HR Admin', runId:caseRunId, attempt:'a1',
    employeeId:lab.id, revision:'a'.repeat(40), budgetRemainingMs:1000, roleReady:true, writeState:'UNKNOWN' });
  expect(blocked.allowed).toBe(false); expect(blocked.outcome).toBe('UNKNOWN');
  await lab.employee.elements.dialog.getByRole('button', { name:'Cancel', exact:true }).click();
  await lab.employee.search(lab.id); await expect(lab.employee.elements.row(lab.id)).toHaveCount(1);
  await expect(lab.employee.elements.row(lab.id).getByRole('cell', { name:'QA', exact:true })).toBeVisible();
  expect((await lab.lookup()).writes).toBe(1);
  await info.attach('reconciled-ui', { body: await lab.employee.page.screenshot(), contentType:'image/png' });
});
test('F02 @control INC-63 exact search finds record beyond 20 visible iframe rows', async ({ lab }, info) => {
  lab.annotate(['LAB-AOCE-03','LAB-AOCE-05','LOCAL-INC-63'], 'Target absent in first 20 visible rows; exact iframe search then Engineering');
  const extras: string[] = [];
  try {
    for (let index = 0; index < 22; index++) {
      const caseId = 'c' + createHash('sha256').update(`${info.testId}-extra-${index}`).digest('hex').slice(0,8);
      const id = `E2E-AOCE-${lab.runId}-${caseId}-a1-F02`;
      expect((await lab.admin.post('/api/lab/reservations', { data:{ flow:'F02', attempt:'a1', caseId, employeeId:id } })).status()).toBe(201);
      extras.push(id); expect((await lab.admin.post('/api/employees', { data:{employeeId:id, department:'QA'} })).status()).toBe(201);
    }
    await lab.seed(); await lab.employee.open();
    await expect(lab.employee.elements.directory.getByRole('status')).toContainText('Showing first 20');
    await expect(lab.employee.elements.row(lab.id)).toHaveCount(0); expect((await lab.lookup()).found).toBe(true);
    await lab.steps.changeAndSearch(lab.id); await expect(lab.employee.elements.row(lab.id)).toHaveCount(1);
    await expect(lab.employee.elements.row(lab.id).getByRole('cell', {name:'Engineering',exact:true})).toBeVisible();
    await info.attach('iframe-search-ui', {body:await lab.employee.page.screenshot(),contentType:'image/png'});
  } finally { for (const id of extras) expect((await lab.admin.delete(`/api/lab/records/${id}`)).ok()).toBeTruthy(); }
});
test('F01 @control NC wrong department must fail unchanged QA assertion', async ({ lab }, info) => {
  lab.annotate(['AC-EMP-02','LOCAL-NC-DEPARTMENT'], 'Sales row must be rejected by unchanged QA assertion');
  await lab.seed('Sales'); await lab.employee.open(); await lab.employee.search(lab.id);
  await expect(lab.employee.elements.row(lab.id)).toHaveCount(1);
  await expect(lab.employee.elements.row(lab.id).getByRole('cell', {name:'QA',exact:true}).isVisible()).resolves.toBe(false);
  await expect(expect(lab.employee.elements.row(lab.id).getByRole('cell',{name:'QA',exact:true})).toBeVisible({timeout:500})).rejects.toThrow();
  await info.attach('negative-control-ui', {body:await lab.employee.page.screenshot(),contentType:'image/png'});
});
test('F01 @control NC wrong employee ID cannot satisfy exact row assertion', async ({ lab }) => {
  lab.annotate(['AC-EMP-02','LOCAL-NC-ID'], 'Correct department on a different ID does not satisfy target assertion');
  await lab.seed(); await lab.employee.open(); await lab.employee.search(lab.id);
  await expect(lab.employee.elements.row(lab.id)).toHaveCount(1);
  await expect(expect(lab.employee.elements.row('E2E-AOCE-other-run-a1-F01')).toHaveCount(1,{timeout:500})).rejects.toThrow();
});
test('F03 @control backend Viewer write denied by explicit role gate', async ({ lab }) => {
  lab.annotate(['LAB-AOCE-04','LOCAL-AUTH-01'], 'Additional local backend contract: Viewer create returns403 role error and no record');
  await lab.employee.open();
  const response = await lab.employee.page.request.post('/api/employees',{data:{employeeId:lab.id,department:'QA'}});
  expect(response.status()).toBe(403); expect((await response.json()).error).toBe('HR Admin role required');
  expect((await lab.lookup()).found).toBe(false);
});
test('F01 @control collision and cleanup outside exact ownership are rejected', async ({ lab }) => {
  lab.annotate(['LAB-AOCE-05','LOCAL-OWNERSHIP-01'], 'Atomic duplicate reservation409; unowned demo cleanup403; demo remains');
  const caseId = /-(c[a-f0-9]{8})-a1-F01$/.exec(lab.id)![1];
  expect((await lab.admin.post('/api/lab/reservations',{data:{flow:'F01',attempt:'a1',caseId,employeeId:lab.id}})).status()).toBe(409);
  expect((await lab.admin.delete('/api/lab/records/EMP-1001')).status()).toBe(403);
  expect((await (await lab.admin.get('/api/employees?id=EMP-1001')).json()).records.length).toBe(1);
});
test('F01 @control INC-64 controlled missing executable is environment blocked', async ({ lab, playwright }, info) => {
  lab.annotate(['LOCAL-INC-64','LAB-AOCE-05'], 'Browser launch failure before app actions is environment issue, not app flaky');
  let launchError = '';
  try { await playwright.chromium.launch({executablePath:path.join(ROOT,'.lab','missing-browser.exe')}); }
  catch (error) { launchError = String(error); }
  expect(launchError).toContain("doesn't exist"); expect((await lab.lookup()).found).toBe(false);
  await info.attach('environment-classification',{body:JSON.stringify({classification:'BLOCKED-ENVIRONMENT',app_assertions:0,writes:0,controlled_fault:'missing-executable'}),contentType:'application/json'});
});
