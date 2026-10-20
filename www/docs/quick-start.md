# Quick start

> Draw a storyboard on any page, with the embed or with the kit's files loaded by hand.

*Source: <https://api.storyboards.sgit.ai/docs/quick-start.html>.*

---

## The embed

```html
<script src="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/embed.js" defer></script>
<sg-storyboard src="https://storyboards.sgit.ai/gen-z-developers/the-opening/bundle.json" view="deck"></sg-storyboard>
```

`embed.js` loads the rest of release v0.1.0 from beside itself, once per page: `fonts.css`, `storyboard.css`, `vendor/rough-4.6.6.js`, any prop pack the bundle names, then `storyboard.js`. Attributes:

| Attribute | Means | Default |
|---|---|---|
| `src` | a bundle: `{ "storyboard": ..., "cast": ..., "packs": [...] }` | |
| `storyboard`, `cast` | two URLs instead of a bundle | |
| `view` | `deck`, `grid`, `script`, or `panel` (one still panel) | `deck` |
| `panel` | with `view="panel"`, which panel, from 1 | `1` |
| `packs` | extra prop packs, comma separated: today `security` | the bundle's |

The JSON can be served from any host that sends `access-control-allow-origin` (GitHub Pages does, for every file).

## The files by hand, with integrity

For a page that wants the browser to refuse any byte that is not the release's, load the files with the `integrity` strings from the [manifest](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/manifest.json). This is what storyboards.sgit.ai does on every page:

```html
<link rel="stylesheet" href="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/fonts.css" integrity="sha384-ep4bdPYRUzquMICQMhuOkSZ/CB1FnMh6qnGWS1F74VepoLOlw9JGK+Zg+E6/t9dD" crossorigin="anonymous">
<link rel="stylesheet" href="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/storyboard.css" integrity="sha384-NGJqtVi+93pE7lBuwFU0RQWhqnQVLR33Wp8AYH1iAeyC2A7h2ijgU4bEKF5HIKIf" crossorigin="anonymous">
<script src="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/vendor/rough-4.6.6.js" integrity="sha384-XPr5sCJfqHMzoJ8Cn1UYdXXD+XvRi0yoZm3W0yVJ24QP0ps8SYUskiXqnl4yqWlc" crossorigin="anonymous"></script>
<script src="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/props/security.js" integrity="sha384-IkxAFhrp5pQhBSjFCLMEA+1iqFHJ6xPRLeO2n9g478h7Z8hW9cUyvza3PuOtmsOx" crossorigin="anonymous"></script>
<script src="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/storyboard.js" integrity="sha384-3xZhCe5dUdBXMwV57gyscmlqdIjzz9L6huUkcuiEyC0V3jfrlQEdyEhvvF4kCeOa" crossorigin="anonymous"></script>
<script src="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/export.js" integrity="sha384-AZlBi+8U84fchjU5NkLWax6WlMqeEdfDT8jW+Rkjr7MYfrYxE9qfvToj6ekYas4M" crossorigin="anonymous"></script>
```

Then the page's own markup: a `.sb-viewer` holding the toolbar, `.sb-deck`, `.sb-grid`, `.sb-script` and a `<script type="application/json" class="sb-data">` with `{ "storyboard", "cast" }`. The kit wires every such element on the page when it loads (`StoryboardKit.wire(root)` does it again for markup added later). The simplest copy to start from is any storyboard page on storyboards.sgit.ai: view its source.

## Draw one panel yourself

```js
const svg = document.querySelector('svg');
StoryboardKit.drawScene(svg, storyboard.scenes[0], cast, { seed: 11 });
```

Seeds make the wobble repeatable: the same panel with the same seed is the same picture on every load. The deck uses `11 + panel index`, and so do the exports.
