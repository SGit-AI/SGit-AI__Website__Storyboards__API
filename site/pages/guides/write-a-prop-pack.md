---
title: Write a prop pack
section: Guides
order: 2
summary: Teach the kit to draw a new thing, without touching the kit: a prop pack is one function that returns drawing functions.
---

The kit draws six props of its own (`laptop`, `desk`, `book`, `board`, `phone`, `sign`). Everything else comes in a pack: [the security pack](../docs/gallery.html) is pki.sgit.ai's keys, vaults and QR codes, packaged this way. A pack never edits `storyboard.js`; it registers itself, and a name the kit already has is ignored, so a pack cannot redraw a core prop.

## The shape

```js
(function () {
  'use strict';
  const pack = function (k) {
    // k holds the kit's drawing primitives: draw, el, textBlock, wrap, INK, PAPER, FONT, TITLE, W, H, FLOOR
    const { draw, textBlock, INK } = k;
    return {
      // every prop: g (an SVG group), rc (a Rough.js canvas), x (the centre, in panel units),
      // y (the line it stands on), s (its scale), p (the prop's own entry from the storyboard)
      cup(g, rc, x, y, s, p) {
        draw(g, rc.rectangle(x - 30 * s, y - 60 * s, 60 * s, 60 * s,
          { fill: p.colour || '#fde68a', fillStyle: 'solid', stroke: INK, strokeWidth: 2.4 }));
        draw(g, rc.arc(x + 30 * s, y - 30 * s, 30 * s, 30 * s, -Math.PI / 2, Math.PI / 2, false, { stroke: INK, strokeWidth: 2.4 }));
        if (p.label) textBlock(g, [p.label], x, y + 34 * s, 24 * s, { anchor: 'middle' });
      },
    };
  };
  // before the kit loads, wait in the queue; after, register at once
  if (window.StoryboardKit && window.StoryboardKit.addProps) window.StoryboardKit.addProps(pack);
  else (window.StoryboardPropPacks = window.StoryboardPropPacks || []).push(pack);
})();
```

Then a storyboard can say `{ "kind": "cup", "x": 0.5, "y": 760, "label": "coffee" }`.

## The details that matter

- **Use `draw(g, node)`** to add a Rough.js shape: it appends the node and tags it (`class="ink"`) the way the kit's own props are. Animation needs nothing from you: when a panel is drawn, every unfilled path in it gets `pathLength="1"`, which is what lets it draw itself when the panel plays.
- **Seeded wobble.** Use `rc` for every shape. The canvas is seeded per panel, so a prop drawn with `rc` looks the same on every load and in every export; `Math.random()` would not. The security pack's QR code derives its modules from a hash of `p.text` for the same reason.
- **Text** goes through `textBlock(g, lines, x, y, size, { anchor, fill, weight, font })`, and `wrap(text, max)` splits it into lines.
- **Validation** does not know your kinds: pass them, `F.validate(storyboard, cast, { props: ['cup'] })`.

## Shipping a pack with the kit

A pack in your own page is yours to version. A pack that should load with `<sg-storyboard packs="...">` belongs in this repository's `src/props/`, its kinds in `PACKS` in `formats.js` and in `embed.js`'s list, and ships in the next minor release, in a new folder, like every other change ([the release process](../engineering/release-process.html)).
