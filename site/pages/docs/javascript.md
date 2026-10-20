---
section: Reference
order: 3
title: The JavaScript
summary: The four globals release {{RELEASE}} defines, and what each function takes and returns.
---

Classic scripts, no build step, no framework, no dependency but Rough.js (vendored). Each file names its own version (`VERSION`), which is the folder it is served from.

## storyboard.js: `StoryboardKit`

The drawing, from gen-z-developers.sgit.ai's kit, with four marked patches ([the manifest]({{BASE}}manifest.json) says which).

| Function | Does |
|---|---|
| `drawScene(svg, scene, cast, { seed, footer })` | draws one 1600 by 1000 panel into an `<svg>` |
| `drawCharacter(g, rc, who, x, floor, { pose, mood, flip, scale })` | one character, on a Rough.js canvas |
| `wire(root)` | wires every `.sb-viewer`, `.sb-deck`, `.sb-contact`, `.sb-sheet`, `.sb-cast` and `.sbx` under `root`, once each (it runs on load) |
| `play(panel)` | plays a panel's arrival: strokes draw themselves, people and bubbles arrive in order |
| `addProps(pack)` | adds a prop pack: a function given the drawing primitives that returns `{ kind: draw(g, rc, x, y, s, p) }` |
| `sceneText(scene, cast)` | one panel as text, as a DOM node |
| `VOCAB` | `{ kinds, poses, moods, settings, props() }` |

A page may set `window.StoryboardPrefsKey` before loading the kit, so a reader's viewing preferences (animation, panels per row, text under panels) are kept under that site's own key in their browser.

## props/security.js

The security prop pack from pki.sgit.ai: `key`, `vault`, `qr`, `envelope`, `record`, `server`, `arrow`, `mark`, `calendar`, `terminal`, `phoneqr`, `padlock`. Load it before or after `storyboard.js`.

## formats.js: `StoryboardFormats`

No DOM; runs in a browser (a global) and in Node (`require`).

| Function | Returns |
|---|---|
| `validate(storyboard, cast, { props })` | a list of problems, empty when the storyboard is good |
| `toMarkdown(storyboard, cast, { url, castHref })` | the script, as markdown |
| `toGraph(storyboard, cast, { url, seriesTitle })` | the storyboard as a semantic graph: `{ nodes, edges }`, edges `has_panel`, `next`, `features`, `says`, `thinks`, `shows`, `quotes`, `drawn_from`, `cites`, `set_in`, `part_of`, `on_shelf`, `made_by` |
| `toText(scene, cast)` | one panel as one paragraph |
| `stats(storyboard)` | panels, kinds, cast, words spoken |
| `VOCAB`, `PACKS` | the vocabulary, and each pack's prop kinds |

## export.js: `StoryboardExport`

Needs `storyboard.js`. Every function returns a promise of a string or a Blob; nothing leaves the browser.

| Function | Returns |
|---|---|
| `svg(storyboard, cast, i, { animated, fonts })` | one panel as a standalone SVG; `fonts` is `link` (default), `embed` or `none`; `animated` adds the drawing animation as CSS inside the file |
| `sheet(storyboard, cast, { cols })` | every panel on one SVG |
| `image(storyboard, cast, i, { type, width, quality })` | a PNG or JPEG Blob; `width: 480` makes a thumbnail |
| `download(data, filename, type)` | saves it |

## embed.js: `<sg-storyboard>`

See the [quick start](quick-start.html). `window.SgStoryboard.kit(packs)` loads the kit into a page without drawing anything.

## Headless: tools/render.mjs

Not served; in the [repository]({{REPO}}). The same drawing and the same `export.js` in Playwright's Chromium, for a site's build: `node tools/render.mjs jobs.json` writes thumbnails, link previews, SVGs, animated SVGs, PNGs and contact sheets. storyboards.sgit.ai draws its thumbnails with it.
