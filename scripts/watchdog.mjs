import fs from 'node:fs';
import path from 'node:path';
import { PRIVATE, readJson, redact } from '../server/lib.mjs';

const grants = path.join(PRIVATE, 'grants');
let unresolved = 0;
if (fs.existsSync(grants)) for (const file of fs.readdirSync(grants)) {
  const grant = readJson(path.join(grants, file));
  if (grant.deadline > Date.now()) continue;
  process.env.LAB_RUN_ID = grant.runId;
  try {
    const { reconcile } = await import('./runtime.mjs');
    await reconcile();
  } catch (error) { unresolved++; console.error(redact(`Reconciliation unresolved for ${grant.runId}: ${error.message}`)); }
}
console.log(`Expired-run watchdog complete; unresolved=${unresolved}.`);
process.exitCode = unresolved ? 6 : 0;
