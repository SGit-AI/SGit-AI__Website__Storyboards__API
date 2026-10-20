// The browser for the tests: Playwright's Chromium (or BROWSER=firefox|webkit), with https://api.storyboards.sgit.ai/
// routed to this checkout, so a test loads the real published path (/v0/v0.1/v0.1.0/storyboard.js) and gets the bytes in
// the tree. SB_UNDER_TEST=src routes every release path to src/ instead, to test the next release before it is cut.
import { createRequire } from 'node:module';
import { readFileSync, existsSync, statSync } from 'node:fs';
import { join, extname, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
export const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
export const HOST = 'https://api.storyboards.sgit.ai';
export const VERSION = JSON.parse(readFileSync(join(ROOT, 'tools/version.json'), 'utf8')).release;
const [M, m] = VERSION.slice(1).split('.');
// SB_RELEASE names another published folder (v0/v0.1/v0.1.0): a site renders with the release it pins, not the newest
export const RELEASE = process.env.SB_RELEASE || `v${M}/v${M}.${m}/${VERSION}`;
export const BASE = `${HOST}/${RELEASE}/`;

async function playwright() {
  try { return await import('playwright'); } catch (e) { /* fall through to a global install */ }
  for (const p of [process.env.PLAYWRIGHT_PATH, '/opt/node22/lib/node_modules/playwright'].filter(Boolean)) {
    if (existsSync(p)) return require(p);
  }
  throw new Error('playwright is not installed: npm install --no-save playwright@1.56.1');
}
// charset as GitHub Pages sends it, so a test sees the bytes a reader's browser decodes
const TYPES = { '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.html': 'text/html; charset=utf-8', '.woff2': 'font/woff2', '.txt': 'text/plain', '.svg': 'image/svg+xml' };

export async function browser() {
  const pw = await playwright();
  const kind = process.env.BROWSER || 'chromium';
  const opts = {};
  if (kind === 'chromium' && existsSync('/opt/pw-browsers/chromium-1194/chrome-linux/chrome') && !process.env.CI) opts.executablePath = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
  const b = await pw[kind].launch(opts);
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  await ctx.route(`${HOST}/**`, (route) => {
    let path = new URL(route.request().url()).pathname.slice(1);
    if (process.env.SB_UNDER_TEST === 'src') path = path.replace(/^v\d+\/v\d+\.\d+\/v\d+\.\d+\.\d+\//, 'src/');
    const file = join(ROOT, path);
    if (!existsSync(file) || statSync(file).isDirectory()) return route.fulfill({ status: 404, body: 'not found' });
    return route.fulfill({ status: 200, body: readFileSync(file), headers: { 'content-type': TYPES[extname(file)] || 'application/octet-stream', 'access-control-allow-origin': '*' } });
  });
  // a page on another origin, as an embedding site would be
  await ctx.route('https://embedder.example/**', (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path.startsWith('/fixtures/')) return route.fulfill({ status: 200, body: readFileSync(join(ROOT, 'tests', path)), headers: { 'content-type': 'application/json; charset=utf-8' } });
    return route.fulfill({ status: 200, body: globalThis.__page || '<!doctype html><title>t</title>', headers: { 'content-type': 'text/html; charset=utf-8' } });
  });
  return { b, ctx };
}

export async function open(ctx, html) {
  globalThis.__page = html;
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('https://embedder.example/index.html');
  return { page, errors };
}
