// The kit in a real browser: an embed from another origin, both fixtures (gen-z's graphs and maps, pki's security
// props), the three views, the exports, and the SRI strings in the manifest held against what the browser accepts.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { browser, open, BASE, RELEASE, ROOT } from './harness.mjs';

const manifest = JSON.parse(readFileSync(join(ROOT, process.env.SB_UNDER_TEST === 'src' ? 'v0/v0.1/v0.1.0' : RELEASE, 'manifest.json'), 'utf8'));
const sri = (p) => manifest.files.find((f) => f.path === p).integrity;
const { b, ctx } = await browser();
let n = 0;
const t = async (name, fn) => { await fn(); n++; console.log('ok', name); };

try {
  for (const [name, panels] of [['gen-z', 12], ['pki', 9]]) {
    await t(`${name}: <sg-storyboard> draws every panel in the deck, with no errors`, async () => {
      const { page, errors } = await open(ctx, `<!doctype html><title>embed</title><script src="${BASE}embed.js" defer></script>
        <sg-storyboard src="/fixtures/${name}.bundle.json"></sg-storyboard>`);
      await page.waitForFunction((n) => document.querySelectorAll('.sb-deck .sb-slide svg g').length >= n, panels, { timeout: 15000 });
      assert.equal(await page.locator('.sb-deck .sb-slide').count(), panels);
      const paths = await page.locator('.sb-deck .sb-slide path').count();
      assert.ok(paths > panels * 20, `only ${paths} strokes`);
      assert.deepEqual(errors, []);
      await page.close();
    });
  }
  await t('grid and script views, asked for by the embed', async () => {
    const { page, errors } = await open(ctx, `<!doctype html><title>e</title><script src="${BASE}embed.js" defer></script>
      <sg-storyboard id="g" src="/fixtures/pki.bundle.json" view="grid"></sg-storyboard>`);
    await page.waitForSelector('.sb-grid:not([hidden]) .sb-cell');
    assert.equal(await page.locator('.sb-grid .sb-cell').count(), 9);
    await page.click('.sb-views button[data-view="script"]');
    assert.equal(await page.locator('.sb-script article').count(), 9);
    assert.deepEqual(errors, []);
    await page.close();
  });
  await t('one panel, view="panel": the security pack draws its vault', async () => {
    const { page, errors } = await open(ctx, `<!doctype html><title>e</title><script src="${BASE}embed.js" defer></script>
      <sg-storyboard src="/fixtures/pki.bundle.json" view="panel" panel="3"></sg-storyboard>`);
    await page.waitForSelector('sg-storyboard figure svg g');
    const props = await page.evaluate(() => window.StoryboardKit.VOCAB.props());
    for (const k of ['vault', 'key', 'qr', 'laptop']) assert.ok(props.includes(k), k);
    assert.ok((await page.locator('sg-storyboard .prop').count()) >= 3);
    assert.deepEqual(errors, []);
    await page.close();
  });
  await t('scripts load with the integrity strings from the manifest (SRI), and VOCAB agrees with formats.js', async () => {
    const tags = ['vendor/rough-4.6.6.js', 'props/security.js', 'storyboard.js', 'formats.js', 'export.js']
      .map((p) => `<script src="${BASE}${p}" integrity="${sri(p)}" crossorigin="anonymous"></script>`).join('');
    const { page, errors } = await open(ctx, `<!doctype html><title>s</title><link rel="stylesheet" href="${BASE}fonts.css" integrity="${sri('fonts.css')}" crossorigin="anonymous">${tags}`);
    await page.waitForFunction(() => window.StoryboardExport && window.StoryboardKit);
    const v = await page.evaluate(() => {
      const K = window.StoryboardKit.VOCAB, F = window.StoryboardFormats.VOCAB;
      return { kinds: [K.kinds, F.kinds], poses: [K.poses, F.poses], moods: [K.moods, F.moods], settings: [K.settings, F.settings],
        core: [K.props().filter((p) => !window.StoryboardFormats.PACKS.security.includes(p)), F.props],
        pack: [K.props().filter((p) => window.StoryboardFormats.PACKS.security.includes(p)).sort(), [...window.StoryboardFormats.PACKS.security].sort()],
        versions: [window.StoryboardKit.VERSION, window.StoryboardFormats.VERSION, window.StoryboardExport.VERSION] };
    });
    for (const k of ['kinds', 'poses', 'moods', 'settings', 'core', 'pack']) assert.deepEqual(v[k][0], v[k][1], k);
    assert.equal(new Set(v.versions).size, 1);
    assert.deepEqual(errors, []);
    await page.close();
  });
  await t('negative control: a wrong integrity string stops the script', async () => {
    const { page } = await open(ctx, `<!doctype html><title>s</title><script src="${BASE}formats.js" integrity="${sri('storyboard.js')}" crossorigin="anonymous"></script>`);
    await page.waitForTimeout(300);
    assert.equal(await page.evaluate(() => typeof window.StoryboardFormats), 'undefined');
    await page.close();
  });
  await t('exports: SVG (still and animated, fonts linked and embedded), the sheet, PNG and a JPEG thumbnail', async () => {
    const bundle = readFileSync(join(ROOT, 'tests/fixtures/gen-z.bundle.json'), 'utf8');
    const { page, errors } = await open(ctx, `<!doctype html><title>x</title><script src="${BASE}vendor/rough-4.6.6.js"></script><script src="${BASE}storyboard.js"></script><script src="${BASE}export.js"></script>`);
    await page.waitForFunction(() => window.StoryboardExport);
    const r = await page.evaluate(async (bundle) => {
      const { storyboard: sb, cast } = JSON.parse(bundle), X = window.StoryboardExport;
      const svg = await X.svg(sb, cast, 0), anim = await X.svg(sb, cast, 2, { animated: true }), emb = await X.svg(sb, cast, 0, { fonts: 'embed' });
      const sheet = await X.sheet(sb, cast, { cols: 4 });
      const png = await X.image(sb, cast, 0), jpg = await X.image(sb, cast, 0, { type: 'image/jpeg', width: 480 });
      const dims = async (blob) => { const i = await createImageBitmap(blob); return [i.width, i.height]; };
      const again = await X.svg(sb, cast, 0);
      return { svg: svg.slice(0, 400), svgLen: svg.length, same: svg === again, anim: anim.includes('@keyframes sb-draw'), emb: emb.includes('data:font/woff2;base64,'),
        link: svg.includes('fonts/patrick-hand-400-latin.woff2'), sheet: sheet.match(/<svg[^>]*>/)[0], png: [png.type, await dims(png)], jpg: [jpg.type, await dims(jpg), jpg.size] };
    }, bundle);
    assert.ok(r.svg.startsWith('<?xml'), r.svg);
    assert.ok(r.same, 'the same panel exports to the same bytes');
    assert.ok(r.anim && r.emb && r.link);
    assert.match(r.sheet, /viewBox="0 0 6600 3160"/);
    assert.deepEqual(r.png, ['image/png', [1600, 1000]]);
    assert.deepEqual(r.jpg.slice(0, 2), ['image/jpeg', [480, 300]]);
    assert.deepEqual(errors, []);
    await page.close();
  });
} finally {
  await b.close();
}
console.log(`test_render: ${n} passed`);
