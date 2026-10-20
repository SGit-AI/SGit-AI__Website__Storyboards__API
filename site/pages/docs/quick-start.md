---
section: Start
order: 1
title: Quick start
summary: Draw a storyboard on any page, with the embed or with the kit's files loaded by hand.
---

## The embed

```html
<script src="{{BASE}}embed.js" defer></script>
<sg-storyboard src="https://storyboards.sgit.ai/gen-z-developers/the-opening/bundle.json" view="deck"></sg-storyboard>
```

`embed.js` loads the rest of release {{RELEASE}} from beside itself, once per page: `fonts.css`, `storyboard.css`, `vendor/rough-4.6.6.js`, any prop pack the bundle names, then `storyboard.js`. Attributes:

| Attribute | Means | Default |
|---|---|---|
| `src` | a bundle: `{ "storyboard": ..., "cast": ..., "packs": [...] }` | |
| `storyboard`, `cast` | two URLs instead of a bundle | |
| `view` | `deck`, `grid`, `script`, or `panel` (one still panel) | `deck` |
| `panel` | with `view="panel"`, which panel, from 1 | `1` |
| `packs` | extra prop packs, comma separated: today `security` | the bundle's |

The JSON can be served from any host that sends `access-control-allow-origin` (GitHub Pages does, for every file).

## The files by hand, with integrity

For a page that wants the browser to refuse any byte that is not the release's, load the files with the `integrity` strings from the [manifest]({{BASE}}manifest.json). This is what storyboards.sgit.ai does on every page:

```html
{{SRI_EXAMPLE}}
```

Then the page's own markup: a `.sb-viewer` holding the toolbar, `.sb-deck`, `.sb-grid`, `.sb-script` and a `<script type="application/json" class="sb-data">` with `{ "storyboard", "cast" }`. The kit wires every such element on the page when it loads (`StoryboardKit.wire(root)` does it again for markup added later). The simplest copy to start from is any storyboard page on storyboards.sgit.ai: view its source.

## Draw one panel yourself

```js
const svg = document.querySelector('svg');
StoryboardKit.drawScene(svg, storyboard.scenes[0], cast, { seed: 11 });
```

Seeds make the wobble repeatable: the same panel with the same seed is the same picture on every load. The deck uses `11 + panel index`, and so do the exports.
