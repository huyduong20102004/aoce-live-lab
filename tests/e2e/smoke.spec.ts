import { test, expect } from '../fixtures/lab.js';

test('F01 @smoke create unique employee and search exact ID + QA', async ({ lab }, info) => {
  lab.annotate(['AC-EMP-01', 'AC-EMP-02', 'LAB-AOCE-05'], 'Unique owned ID; exact search row and QA');
  expect((await lab.lookup()).found).toBe(false);
  await lab.employee.open(); await lab.steps.createAndSearch(lab.id);
  const row = lab.employee.elements.row(lab.id);
  await expect(row).toHaveCount(1); await expect(row.getByRole('cell', { name: 'QA', exact: true })).toBeVisible();
  const record = await lab.lookup(); expect(record.record?.employeeId).toBe(lab.id); expect(record.writes).toBe(1);
  await info.attach('assertion-ui', { body: await lab.employee.page.screenshot(), contentType: 'image/png' });
});
test('F02 @smoke change independent owned seed department and search', async ({ lab }, info) => {
  lab.annotate(['LAB-AOCE-03', 'LAB-AOCE-05'], 'Independent owned QA seed; exact ID + Engineering after edit');
  expect((await lab.lookup()).found).toBe(false); await lab.seed();
  await lab.employee.open(); await lab.employee.search(lab.id);
  await expect(lab.employee.elements.row(lab.id).getByRole('cell', { name: 'QA', exact: true })).toBeVisible();
  await lab.steps.changeAndSearch(lab.id);
  await expect(lab.employee.elements.row(lab.id)).toHaveCount(1);
  await expect(lab.employee.elements.row(lab.id).getByRole('cell', { name: 'Engineering', exact: true })).toBeVisible();
  await info.attach('assertion-ui', { body: await lab.employee.page.screenshot(), contentType: 'image/png' });
});
test('F03 @smoke Viewer Create disabled and attempted ID absent', async ({ lab }, info) => {
  lab.annotate(['LAB-AOCE-04', 'LAB-AOCE-05'], 'Fresh Viewer auth; Create disabled; no owned record');
  expect((await lab.lookup()).found).toBe(false); await lab.employee.open();
  await expect(lab.employee.page.getByText('Viewer', { exact: true })).toBeVisible();
  await expect(lab.employee.elements.create).toBeDisabled();
  expect((await lab.lookup()).found).toBe(false);
  await info.attach('assertion-ui', { body: await lab.employee.page.screenshot(), contentType: 'image/png' });
});
