#!/usr/bin/env node
// Storyboards to files, headless: the same drawing and the same export.js a reader's browser runs, in Playwright's
// Chromium, with the published release paths routed to this checkout (tests/harness.mjs). For a site's build, which
// commits what it needs (thumbnails, link previews) and leaves the rest to the reader's browser.
//
//   node tools/render.mjs JOBS.json
//   JOBS.json: [{ "bundle": "path/bundle.json", "out": "dir", "make": ["thumb", "og", "svg", "animated", "png", "sheet"] }]
//
//   thumb     thumb.jpg, the cover panel at 480x300            og       og.jpg, the cover at 1200x750 (link previews)
//   svg       panel-NN.svg, every panel, fonts linked         animated panel-NN.anim.svg, every panel, drawing itself
//   png       panel-NN.png, every panel at 1600x1000          sheet    sheet.svg, every panel on one page
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { browser, open, BASE } from '../tests/harness.mjs';

const jobs = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const { b, ctx } = await browser();
try {
  const { page, errors } = await open(ctx, `<!doctype html><title>render</title><script src="${BASE}vendor/rough-4.6.6.js"></script><script src="${BASE}props/security.js"></script><script src="${BASE}storyboard.js"></script><script src="${BASE}export.js"></script>`);
  await page.waitForFunction(() => window.StoryboardExport);
  for (const job of jobs) {
    const bundle = readFileSync(resolve(job.bundle), 'utf8'), out = resolve(job.out);
    mkdirSync(out, { recursive: true });
    const files = await page.evaluate(async ({ bundle, make }) => {
      const { storyboard: sb, cast } = JSON.parse(bundle), X = window.StoryboardExport, files = {};
      const b64 = async (blob) => { const a = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < a.length; i += 0x8000) s += String.fromCharCode.apply(null, a.subarray(i, i + 0x8000)); return btoa(s); };
      const nn = (i) => String(i + 1).padStart(2, '0');
      if (make.includes('thumb')) files['thumb.jpg'] = { b64: await b64(await X.image(sb, cast, 0, { type: 'image/jpeg', width: 480, quality: 0.8, footer: false })) };
      if (make.includes('og')) files['og.jpg'] = { b64: await b64(await X.image(sb, cast, 0, { type: 'image/jpeg', width: 1200, quality: 0.82, footer: false })) };
      if (make.includes('sheet')) files['sheet.svg'] = { text: await X.sheet(sb, cast) };
      for (let i = 0; i < sb.scenes.length; i++) {
        if (make.includes('svg')) files[`panel-${nn(i)}.svg`] = { text: await X.svg(sb, cast, i) };
        if (make.includes('animated')) files[`panel-${nn(i)}.anim.svg`] = { text: await X.svg(sb, cast, i, { animated: true }) };
        if (make.includes('png')) files[`panel-${nn(i)}.png`] = { b64: await b64(await X.image(sb, cast, i)) };
      }
      return files;
    }, { bundle, make: job.make });
    for (const [name, f] of Object.entries(files)) writeFileSync(`${out}/${name}`, f.text != null ? f.text : Buffer.from(f.b64, 'base64'));
    console.log(`render: ${job.bundle} -> ${job.out} (${Object.keys(files).length} files)`);
  }
  if (errors.length) { console.error('render: the page reported errors:', errors.slice(0, 3)); process.exitCode = 1; }
} finally {
  await b.close();
}
