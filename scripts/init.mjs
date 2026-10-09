import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { ROOT, PRIVATE, atomicJson } from '../server/lib.mjs';

fs.mkdirSync(PRIVATE, { recursive: true });
const env = path.join(ROOT, '.env');
if (!fs.existsSync(env)) {
  fs.writeFileSync(env, [
    'LAB_ENVIRONMENT=isolated-lab', 'LAB_BASE_URL=http://127.0.0.1:4173',
    'LAB_URL_ALLOWLIST=http://127.0.0.1:4173', 'LAB_USERNAME=admin-lab',
    `LAB_PASSWORD=${crypto.randomBytes(24).toString('base64url')}`,
    'LAB_VIEWER_USERNAME=viewer-lab',
    `LAB_VIEWER_PASSWORD=${crypto.randomBytes(24).toString('base64url')}`, '',
  ].join('\n'), { mode: 0o600 });
}
const state = path.join(PRIVATE, 'state.json');
if (!fs.existsSync(state)) atomicJson(state, {
  schema: 1,
  employees: [
    { employeeId: 'EMP-1001', department: 'Engineering', owner: null, recordRef: 'demo-1' },
    { employeeId: 'EMP-1002', department: 'QA', owner: null, recordRef: 'demo-2' },
    { employeeId: 'EMP-1003', department: 'Sales', owner: null, recordRef: 'demo-3' },
  ],
  runs: {}, audit: [],
});
console.log('Local lab initialized. Private account values saved in ignored .env; existing data preserved.');
