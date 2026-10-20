---
title: Tests
section: Engineering
order: 3
summary: What each test checks, against real files in a real browser, and the negative control that proves each check can fail.
---

No mocks: the tests load the real release files, from the published path, into a real browser. `tests/harness.mjs` launches Playwright's Chromium (or `BROWSER=firefox|webkit`) and routes `https://api.storyboards.sgit.ai/` to this checkout, so a test that loads `/v0/v0.1/v0.1.0/storyboard.js` gets the bytes in the tree, with the headers GitHub Pages sends. `SB_UNDER_TEST=src` routes every release path to `src/`, to test the next release before it is cut.

| Test | Checks | Its negative control |
|---|---|---|
| `test_formats.mjs` (Node) | a gen-z and a pki storyboard validate clean; the markdown has a heading per panel and is the same bytes twice; the graph's ids are unique, every edge names real nodes, there is a `has_panel` per panel and a `next` between each | a storyboard with an unknown character, an unknown mood and an unknown kind fails, naming each; the pki storyboard without the security pack fails on its props |
| `test_render.mjs` (Chromium) | `<sg-storyboard>` on another origin draws every panel of both fixtures with no console error; the grid and script views; `view="panel"` with the security pack's vault; scripts load with the manifest's SRI strings; the kit's vocabulary equals `formats.js`'s, list by list; the SVG, animated SVG, embedded-font SVG, sheet, PNG and JPEG exports, their sizes, and the same panel exporting to the same bytes | a script given another file's integrity string does not run |
| `test_site.mjs` (Chromium) | every page of the website, assembled as Pages serves it, opens with no error; the home page's live embed draws | |

The fixtures in `tests/fixtures/` are real storyboards from the two origin sites (gen-z's *Everything is connected*, with graphs and a map, and pki's *The first key*, with the security props), with their casts.

```bash
node tests/test_formats.mjs
npm install --no-save playwright@1.56.1 && npx playwright install chromium
node tests/test_render.mjs && node tests/test_site.mjs
```

Not yet: Firefox and WebKit have not been run.
