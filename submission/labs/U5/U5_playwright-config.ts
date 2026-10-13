// DRY-RUN DRAFT. Integrate as playwright.config.ts in the authorized lab project.
// No live app/tests/helpers are provided by this document workspace.
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  forbidOnly: Boolean(process.env.CI),
  fullyParallel: false,
  workers: 1,
  retries: 0, // Diagnostic baseline. A safe runner retry requires controller review.
  timeout: 60_000, // Lab test limit; not a product search SLA.
  expect: { timeout: 10_000 }, // Condition polling only; preserve oracle.
  globalTimeout: 12 * 60_000, // Reserve job time for cleanup/export; total controller budget 20min.
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
  ],
  outputDir: 'test-results',
  use: {
    baseURL: process.env.LAB_BASE_URL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'off',
  },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
  // F03 creates a fresh Viewer auth/browser context in its fixture.
  // No shared HR Admin storageState or secret literals in config.
});
