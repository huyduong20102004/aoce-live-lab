import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { ROOT, PRIVATE, BUILD, FLOWS, loadEnv, assertLabUrl, atomicJson, readJson, sha, equalSecret } from './lib.mjs';

loadEnv();
const origin = assertLabUrl();
if (!process.env.LAB_PASSWORD || !process.env.LAB_VIEWER_PASSWORD) throw new Error('Run npm run lab:init first');
const stateFile = path.join(PRIVATE, 'state.json');
let state = readJson(stateFile);
if (!state) throw new Error('Lab state not initialized');
const sessions = new Map();
const departments = ['QA', 'Engineering', 'Sales'];
function failure(status, message) { return Object.assign(new Error(message), { status }); }
function save() { atomicJson(stateFile, state); }
function audit(action, data = {}) {
  state.audit.push({ time: new Date().toISOString(), action, ...data });
  save();
}
function json(res, status, body, headers = {}) {
  res.writeHead(status, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', ...headers });
  res.end(JSON.stringify(body));
}
async function body(req) {
  let text = '';
  for await (const chunk of req) {
    text += chunk;
    if (text.length > 16384) throw failure(413, 'Request too large');
  }
  try { return JSON.parse(text || '{}'); } catch { throw failure(400, 'Invalid JSON'); }
}
function session(req) {
  const sid = /(?:^|;\s*)lab_session=([^;]+)/.exec(req.headers.cookie || '')?.[1];
  const value = sessions.get(sid);
  if (!value || value.expires < Date.now()) throw failure(401, 'Login required');
  return value;
}
function admin(user) { if (user.role !== 'HR Admin') throw failure(403, 'HR Admin role required'); }
function grant(req, allowExpired = false) {
  const runId = req.headers['x-lab-run-id'];
  const token = req.headers['x-lab-token'];
  const run = state.runs[runId];
  if (!run || !token || !equalSecret(sha(token), run.tokenHash)) throw failure(403, 'Invalid run ownership capability');
  if (!allowExpired && (run.released || run.deadline < Date.now())) throw failure(409, 'Run lease expired/released');
  return run;
}
function validateRecord(input) {
  if (!/^[A-Za-z0-9-]{3,100}$/.test(input.employeeId || '') || !departments.includes(input.department))
    throw failure(400, 'Valid unique Employee ID and Department required');
}
function ownedId(run, id) {
  const reservation = run.records[id];
  if (!reservation || !id.startsWith(`E2E-AOCE-${run.runId}-`)) throw failure(403, 'Exact reserved owned ID required');
  return reservation;
}
const assets = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/directory', ['directory.html', 'text/html; charset=utf-8']],
  ['/app.js', ['app.js', 'text/javascript; charset=utf-8']],
  ['/directory.js', ['directory.js', 'text/javascript; charset=utf-8']],
  ['/style.css', ['style.css', 'text/css; charset=utf-8']],
  ['/favicon.svg', ['favicon.svg', 'image/svg+xml']],
]);
const server = http.createServer(async (req, res) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Referrer-Policy', 'no-referrer');
  res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; frame-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'");
  try {
    if (req.headers.host !== new URL(origin).host) throw failure(400, 'Unexpected host');
    const url = new URL(req.url, origin);
    if (req.method !== 'GET' && req.headers.origin && req.headers.origin !== origin) throw failure(403, 'Cross-origin mutation blocked');
    if (req.method === 'GET' && assets.has(url.pathname)) {
      const [name, type] = assets.get(url.pathname);
      res.writeHead(200, { 'Content-Type': type, 'Cache-Control': 'no-store' });
      res.end(fs.readFileSync(path.join(ROOT, 'public', name))); return;
    }
    if (url.pathname === '/api/health' && req.method === 'GET') {
      json(res, 200, { app: 'AOCE PortalLite', build: BUILD, environment: 'isolated-lab', persistent: true }); return;
    }
    if (url.pathname === '/api/login' && req.method === 'POST') {
      const input = await body(req);
      let role;
      if (input.username === process.env.LAB_USERNAME && equalSecret(input.password, process.env.LAB_PASSWORD)) role = 'HR Admin';
      if (input.username === process.env.LAB_VIEWER_USERNAME && equalSecret(input.password, process.env.LAB_VIEWER_PASSWORD)) role = 'Viewer';
      if (!role) throw failure(401, 'Invalid account');
      const sid = crypto.randomBytes(32).toString('base64url');
      sessions.set(sid, { role, username: input.username, expires: Date.now() + 3600000 });
      json(res, 200, { role, username: input.username }, { 'Set-Cookie': `lab_session=${sid}; HttpOnly; SameSite=Strict; Path=/; Max-Age=3600` }); return;
    }
    const user = session(req);
    if (url.pathname === '/api/me') { json(res, 200, { role: user.role, username: user.username }); return; }
    if (url.pathname === '/api/logout' && req.method === 'POST') {
      const sid = /lab_session=([^;]+)/.exec(req.headers.cookie || '')?.[1]; sessions.delete(sid);
      json(res, 200, {}, { 'Set-Cookie': 'lab_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0' }); return;
    }
    if (url.pathname === '/api/lab/runs' && req.method === 'POST') {
      admin(user); const input = await body(req);
      if (!/^[a-zA-Z0-9-]{5,40}$/.test(input.runId || '') || !/^[a-f0-9]{40}$/.test(input.revision || '')) throw failure(400, 'Valid run ID/revision required');
      if (state.runs[input.runId]) throw failure(409, 'Run ID already registered');
      const blocking = Object.values(state.runs).find(r => !r.released &&
        (r.deadline > Date.now() || Object.values(r.records).some(v => v.writeState !== 'NOT_WRITTEN' && v.cleanup !== 'success' && v.cleanup !== 'absent')));
      if (blocking) throw failure(409, 'Lab lease busy or unresolved owned data; reconcile first');
      const token = crypto.randomBytes(32).toString('base64url');
      state.runs[input.runId] = { runId: input.runId, tokenHash: sha(token), revision: input.revision,
        started: new Date().toISOString(), deadline: Date.now() + 1200000, released: false, records: {} };
      audit('run-registered', { runId: input.runId, revision: input.revision });
      json(res, 201, { runId: input.runId, token, deadline: state.runs[input.runId].deadline }); return;
    }
    if (url.pathname === '/api/lab/reservations' && req.method === 'POST') {
      const run = grant(req); const input = await body(req);
      if (!FLOWS.includes(input.flow) || !/^a[1-2]$/.test(input.attempt) || !/^c[a-f0-9]{8}$/.test(input.caseId || '') ||
        input.employeeId !== `E2E-AOCE-${run.runId}-${input.caseId}-${input.attempt}-${input.flow}`) throw failure(400, 'Namespace/flow/attempt mismatch');
      if (run.records[input.employeeId] || state.employees.some(e => e.employeeId === input.employeeId)) throw failure(409, 'ID reservation collision');
      run.records[input.employeeId] = { employeeId: input.employeeId, caseId: input.caseId, flow: input.flow, attempt: input.attempt,
        owner: run.runId, reservedAt: new Date().toISOString(), writeState: 'NOT_WRITTEN', cleanup: 'not-applicable', writes: 0 };
      audit('id-reserved', { runId: run.runId, employeeId: input.employeeId, flow: input.flow });
      json(res, 201, { employeeId: input.employeeId, owner: run.runId }); return;
    }
    if (url.pathname === '/api/lab/ledger' && req.method === 'GET') {
      const run = grant(req, true);
      json(res, 200, { runId: run.runId, revision: run.revision, deadline: run.deadline, released: run.released, records: Object.values(run.records) }); return;
    }
    if (url.pathname === '/api/lab/release' && req.method === 'POST') {
      admin(user); const run = grant(req, true);
      if (state.employees.some(e => e.owner === run.runId)) throw failure(409, 'Unresolved owned records');
      run.released = true; audit('run-released', { runId: run.runId }); json(res, 200, { released: true }); return;
    }
    const lookup = /^\/api\/lab\/records\/([A-Za-z0-9-]+)$/.exec(url.pathname);
    if (lookup) {
      const run = grant(req, true); const id = lookup[1]; const entry = ownedId(run, id);
      const record = state.employees.find(e => e.employeeId === id);
      if (record && record.owner !== run.runId) throw failure(403, 'Ownership mismatch');
      if (req.method === 'GET') {
        json(res, 200, { found: Boolean(record), record: record || null, writes: entry.writes, writeState: entry.writeState }); return;
      }
      if (req.method === 'DELETE') {
        admin(user);
        state.employees = state.employees.filter(e => e.employeeId !== id);
        entry.cleanup = record ? 'success' : 'absent'; entry.cleanedAt = new Date().toISOString();
        audit('owned-cleanup', { runId: run.runId, employeeId: id, outcome: entry.cleanup });
        json(res, 200, { cleanup: entry.cleanup, employeeId: id }); return;
      }
    }
    if (url.pathname === '/api/employees' && req.method === 'GET') {
      const query = url.searchParams.get('id') || '';
      const records = query ? state.employees.filter(e => e.employeeId === query) : state.employees;
      json(res, 200, { total: records.length, records: records.slice(0, 20) }); return;
    }
    if (url.pathname === '/api/employees' && req.method === 'POST') {
      admin(user); const input = await body(req); validateRecord(input);
      let run, entry;
      if (input.employeeId.startsWith('E2E-AOCE-') || req.headers['x-lab-run-id']) {
        run = grant(req); entry = ownedId(run, input.employeeId);
        if (entry.flow === 'F03') throw failure(403, 'F03 mutation is forbidden');
        if (entry.writeState !== 'NOT_WRITTEN') throw failure(409, 'Write already dispatched: reconcile instead of repeating');
      }
      if (state.employees.some(e => e.employeeId === input.employeeId)) throw failure(409, 'Employee ID already exists');
      if (input.fault && (!run || input.fault !== 'ack-delay')) throw failure(400, 'Only reviewed owned ack-delay fault allowed');
      if (entry) { entry.writeState = 'DISPATCHED'; save(); }
      const record = { employeeId: input.employeeId, department: input.department, owner: run?.runId || null, recordRef: crypto.randomUUID() };
      state.employees.push(record);
      if (entry) { entry.writeState = 'CREATED'; entry.writes++; entry.cleanup = 'pending'; entry.recordRef = record.recordRef; }
      audit('employee-created', { employeeId: record.employeeId, runId: record.owner, department: record.department });
      // Explicit local fault contract: commit is durable BEFORE delayed acknowledgement.
      if (input.fault === 'ack-delay') {
        setTimeout(() => { if (!res.destroyed) json(res, 201, { record }); }, 1800); return;
      }
      json(res, 201, { record }); return;
    }
    const edit = /^\/api\/employees\/([A-Za-z0-9-]+)$/.exec(url.pathname);
    if (edit && req.method === 'PUT') {
      admin(user); const input = await body(req);
      if (!departments.includes(input.department)) throw failure(400, 'Department invalid');
      const record = state.employees.find(e => e.employeeId === edit[1]);
      if (!record) throw failure(404, 'Employee not found');
      if (record.owner || req.headers['x-lab-run-id']) {
        const run = grant(req); ownedId(run, record.employeeId);
        if (record.owner !== run.runId) throw failure(403, 'Ownership mismatch');
      }
      record.department = input.department;
      audit('department-changed', { employeeId: record.employeeId, runId: record.owner, department: record.department });
      json(res, 200, { record }); return;
    }
    throw failure(404, 'Not found');
  } catch (error) {
    if (!res.headersSent) json(res, error.status || 500, { error: error.status ? error.message : 'Internal lab error' });
    else res.end();
  }
});
server.listen(Number(new URL(origin).port), '127.0.0.1', () => console.log(`AOCE PortalLite ready at ${origin}`));
