import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import crypto from 'node:crypto';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const PRIVATE = path.join(ROOT, '.lab');
export const BUILD = 'portallite-local-1';
export const FLOWS = ['F01', 'F02', 'F03'];
export function loadEnv() {
  const file = path.join(ROOT, '.env');
  if (fs.existsSync(file)) for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const m = /^([A-Z_]+)=(.*)$/.exec(line);
    if (m && process.env[m[1]] === undefined) process.env[m[1]] = m[2];
  }
}
export function atomicJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.${process.pid}.${crypto.randomUUID()}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(value, null, 2) + '\n', { mode: 0o600 });
  fs.renameSync(tmp, file);
}
/** @param {string} file @param {any} [fallback] */
export function readJson(file, fallback = null) {
  return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : fallback;
}
export function sha(value) { return crypto.createHash('sha256').update(value).digest('hex'); }
export function equalSecret(a, b) {
  if (!a || !b) return false;
  return crypto.timingSafeEqual(Buffer.from(sha(String(a))), Buffer.from(sha(String(b))));
}
export function assertLabUrl() {
  const url = new URL(process.env.LAB_BASE_URL || 'http://127.0.0.1:4173');
  if (process.env.LAB_ENVIRONMENT !== 'isolated-lab' || url.protocol !== 'http:' ||
      url.hostname !== '127.0.0.1' || url.pathname !== '/' || url.username || url.password ||
      url.search || url.hash || process.env.LAB_URL_ALLOWLIST !== url.origin) {
    throw new Error('BLOCKED: isolated loopback lab URL/allowlist required');
  }
  return url.origin;
}
export function redact(value) {
  let text = typeof value === 'string' ? value : JSON.stringify(value);
  for (const key of ['LAB_PASSWORD', 'LAB_VIEWER_PASSWORD', 'LAB_TOKEN']) {
    if (process.env[key]) text = text.split(process.env[key]).join('[REDACTED]');
  }
  return text;
}
