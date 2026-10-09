import test from 'node:test';
import assert from 'node:assert/strict';
import { route, acceptEvidence, compactContext, authorizeTool, validateCompactContext, type Request, type Evidence } from '../controller/contracts.js';
import { redact } from '../server/lib.mjs';

const input: Request = { flow: 'F01', environment: 'isolated-lab', actor: 'HR Admin', runId: 'fixture-r02', attempt: 'a1',
  employeeId: 'E2E-AOCE-fixture-r02-a1-F01', revision: 'a'.repeat(40), budgetRemainingMs: 1200000, roleReady: true };
const evidence: Evidence = { ...input, flow: 'F01', department: 'QA', runnerAssertions: true, label: 'SIMULATED', cleanup: 'success' };
test('RG-01 positive matching fixture accepted without claiming live execution', () => assert.equal(acceptEvidence(input, evidence), true));
test('RG-02 Success toast without runner assertions rejected', () => assert.equal(acceptEvidence(input, { ...evidence, runnerAssertions: false }), false));
test('RG-03 previous run pointer rejected', () => assert.equal(acceptEvidence(input, { ...evidence, runId: 'fixture-r01' }), false));
test('RG-04 exact ID but Sales rejected', () => assert.equal(acceptEvidence(input, { ...evidence, department: 'Sales' }), false));
test('RG-05 unknown write blocks repeat mutation', () => assert.equal(route({ ...input, writeState: 'UNKNOWN' }).outcome, 'UNKNOWN'));
test('RG-06 injection cannot dispatch arbitrary delete tool', () => assert.equal(route({ ...input, flow: 'delete-all' }).allowed, false));
test('RG-07 F99 rejected', () => assert.equal(route({ ...input, flow: 'F99' }).outcome, 'REJECTED'));
test('RG-08 missing actor/revision blocks; compact context missing actor throws', () => {
  assert.equal(route({ ...input, actor: '', revision: '' }).allowed, false);
  assert.throws(() => compactContext({ ...input, actor: '' }), /incomplete/);
});
test('NC wrong ID, correct department rejected', () => assert.equal(acceptEvidence(input, { ...evidence, employeeId: 'another-id' }), false));
test('NC stale revision rejected', () => assert.equal(acceptEvidence(input, { ...evidence, revision: 'b'.repeat(40) }), false));
test('wrong environment / exhausted budget / missing F02 seed blocked', () => {
  assert.equal(route({ ...input, environment: 'production' }).allowed, false);
  assert.equal(route({ ...input, budgetRemainingMs: 0 }).outcome, 'STOP');
  assert.equal(route({ ...input, flow: 'F02', employeeId: 'E2E-AOCE-fixture-r02-a1-F02' }).allowed, false);
});
test('compact context preserves invariants and <=250 words', () => {
  const value = compactContext(input);
  assert.ok(value.split(/\s+/).length <= 250);
  for (const word of ['AC-EMP-02', 'department', 'Actor', 'Unknown', 'owned', 'revision']) assert.ok(value.includes(word));
});
test('tool allowlist rejects page injection shell/delete and unknown-write mutation', () => {
  assert.equal(authorizeTool(input,'delete_all_employees'),false);
  assert.equal(authorizeTool(input,'general_shell'),false);
  assert.equal(authorizeTool({...input,writeState:'UNKNOWN'},'run_reviewed_flow'),false);
  assert.equal(authorizeTool({...input,writeState:'UNKNOWN'},'lookup_owned_record'),true);
  assert.equal(authorizeTool({...input,writeState:'UNKNOWN'},'cleanup_owned_record',input.runId),false);
  assert.equal(authorizeTool(input,'cleanup_owned_record','other-run'),false);
});
test('context truncation dropping source or actor detected; valid context accepted', () => {
  const context=compactContext(input);
  assert.equal(validateCompactContext(context,input),true);
  assert.equal(validateCompactContext(context.replace('AC-EMP-02',''),input),false);
  assert.equal(validateCompactContext(context.replace(input.actor,''),input),false);
});
test('report error strings redact session/capability/auth header values', () => {
  const raw='cookie: lab_session=synthetic-session\nx-lab-token: synthetic-capability\nAuthorization: Bearer synthetic-bearer';
  const sanitized=redact(raw);
  for (const value of ['synthetic-session','synthetic-capability','synthetic-bearer']) assert.equal(sanitized.includes(value),false);
});
