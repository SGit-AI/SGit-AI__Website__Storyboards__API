---
title: Render in a build
section: Guides
order: 3
summary: Thumbnails, link previews, SVG and PNG files from a site's build, drawn by the same release a reader's browser runs.
---

A browser draws panels as it needs them. A build sometimes needs files before any browser is involved: a thumbnail for a shelf, the image a chat app shows when a link is shared. `tools/render.mjs` in [this repository]({{REPO}}) makes them with the real kit, in Playwright's Chromium, with the release's published paths routed to a checkout of this repository, so the build draws with exactly the bytes it will serve.

```bash
npm install --no-save playwright@1.56.1 && npx playwright install chromium
cat > jobs.json <<'JSON'
[{ "bundle": "path/my-storyboard.bundle.json", "out": "out/my-storyboard", "make": ["thumb", "og", "svg", "png"] }]
JSON
SB_RELEASE=v0/v0.1/v0.1.0 node path/to/SGit-AI__Website__Storyboards__API/tools/render.mjs jobs.json
```

| `make` | Writes |
|---|---|
| `thumb` | `thumb.jpg`, the cover panel at 480 by 300, no footer |
| `og` | `og.jpg`, the cover at 1200 by 750 |
| `svg` | `panel-NN.svg` for every panel, fonts linked to the release |
| `animated` | `panel-NN.anim.svg`, each panel drawing itself when opened |
| `png` | `panel-NN.png` at 1600 by 1000, fonts embedded |
| `sheet` | `sheet.svg`, every panel on one page |

`SB_RELEASE` names the folder to draw with; without it, the newest release in the checkout. Pin it to the release your site loads, or the thumbnails will be drawn by different code from the pages.

## How storyboards.sgit.ai does it

Its `admin/build/render.py` writes each storyboard's bundle, runs `render.mjs` for the stale ones, and records in `renders.json` the SHA-256 of the bundle and the release each image was drawn from. Its build refuses to publish a storyboard whose images were drawn from an older bundle or another release. The images are committed rather than built, because a font rasterises slightly differently from one machine to the next and the build must make the same bytes twice.
