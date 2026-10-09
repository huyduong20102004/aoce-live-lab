import { defineConfig } from '@playwright/test';
import path from 'node:path';
import { loadEnv, assertLabUrl, ROOT } from './server/lib.mjs';
loadEnv();
const runId = process.env.LAB_RUN_ID || 'discovery';
const output = path.join(ROOT, '.lab', 'runs', runId);
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  forbidOnly: Boolean(process.env.CI),
  timeout: 45_000,
  globalTimeout: 12 * 60_000,
  expect: { timeout: 5000 },
  reporter: [['list'], ['json', { outputFile: path.join(output, 'reporter.json') }],
    ['html', { outputFolder: path.join(output, 'html'), open: 'never' }], ['./reporters/manifest.ts']],
  outputDir: path.join(output, 'artifacts'),
  use: { baseURL: process.env.LAB_LANE === 'pr' ? 'http://127.0.0.1:4173' : assertLabUrl(),
    trace: 'retain-on-failure', screenshot: 'only-on-failure', video: 'off', viewport: { width: 1365, height: 900 } },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
});
