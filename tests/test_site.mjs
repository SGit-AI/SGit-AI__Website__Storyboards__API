// The website as GitHub Pages will serve it (tools/release.py site: www/ plus every release folder), in a real browser:
// every page opens with no error, and the home page's live demo draws a panel with the current release.
import { execFileSync } from 'node:child_process';
import { readFileSync, readdirSync, statSync, existsSync, mkdtempSync, mkdirSync } from 'node:fs';
import { join, relative, extname } from 'node:path';
import { tmpdir } from 'node:os';
import assert from 'node:assert/strict';
import { browser, ROOT, HOST } from './harness.mjs';

const site = join(mkdtempSync(join(tmpdir(), 'sb-api-site-')), 'site');
execFileSync('python3', [join(ROOT, 'tools/release.py'), 'site', '--out', site]);
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.md': 'text/markdown; charset=utf-8', '.woff2': 'font/woff2' };
const { b, ctx } = await browser();
await ctx.route(`${HOST}/**`, (route) => {
  let p = new URL(route.request().url()).pathname;
  if (p.endsWith('/')) p += 'index.html';
  const f = join(site, p);
  if (!existsSync(f) || statSync(f).isDirectory()) return route.fulfill({ status: 404, body: 'not found' });
  return route.fulfill({ status: 200, body: readFileSync(f), headers: { 'content-type': TYPES[extname(f)] || 'application/octet-stream' } });
});
const pages = [];
(function walk(d) { for (const f of readdirSync(d)) { const p = join(d, f); if (statSync(p).isDirectory()) walk(p); else if (f.endsWith('.html')) pages.push(relative(site, p)); } })(site);
const shots = process.env.SHOTS;
if (shots) mkdirSync(shots, { recursive: true });
let n = 0;
try {
  for (const rel of pages) {
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    await page.goto(`${HOST}/${rel}`);
    await page.waitForLoadState('networkidle');
    if (rel === 'index.html') await page.waitForSelector('sg-storyboard figure svg g', { timeout: 15000 });
    if (shots && ['index.html', 'docs/format.html', 'releases/index.html'].includes(rel)) await page.screenshot({ path: join(shots, 'api-' + rel.replace(/\W+/g, '_') + '.png') });
    assert.deepEqual(errors, [], `${rel}: ${errors.join('; ')}`);
    await page.close();
    n++;
  }
} finally {
  await b.close();
}
console.log(`test_site: ${n} pages opened, no errors`);
