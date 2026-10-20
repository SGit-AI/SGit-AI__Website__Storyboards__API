# How the kit works

> The files of a release and how they load each other, how one panel is drawn, why the same data always gives the same picture, and how the animation works without a script.

*Source: <https://api.storyboards.sgit.ai/internals/architecture.html>.*

---

## The files, and who loads whom

| File | Needs | Defines | Runs where |
|---|---|---|---|
| `vendor/rough-4.6.6.js` | nothing | `rough` | browser |
| `props/security.js` | nothing (queues itself) or the kit (registers) | a prop pack | browser |
| `storyboard.js` | `rough` | `StoryboardKit`; wires the page | browser |
| `storyboard.css` | the page's theme tokens | the deck, grid, script, shelf, model sheet | browser |
| `fonts.css` | `fonts/*.woff2`, beside it | Caveat, Patrick Hand | browser |
| `formats.js` | nothing | `StoryboardFormats` | browser and Node |
| `export.js` | `StoryboardKit` | `StoryboardExport` | browser |
| `embed.js` | everything above, loaded from beside itself | `<sg-storyboard>` | browser |

Every file is a classic script: one IIFE, one global, no imports, no build step. Files find each other by their own address: `embed.js` and `export.js` read `document.currentScript.src` once and resolve everything else against it, so a page that loads `embed.js` from `/v0/v0.1/v0.1.0/` can only ever get the rest of `v0.1.0`. That is the property the immutable folder exists to give.

## One panel: `drawScene(svg, scene, cast, { seed, footer })`

1. **Clear and size.** The SVG is emptied and given `viewBox="0 0 1600 1000"`, `role="img"` and an `aria-label` made of the caption, the punchline and every line spoken.
2. **A seeded canvas.** `rough.svg(svg, { options: { seed, roughness: 1, bowing: 1.2 } })`. Every stroke in the panel comes from this canvas, so the wobble is a function of the seed.
3. **Paper.** A rectangle in `#fbf7ee`, in every theme: a panel is a printed picture.
4. **The kind.** Each kind draws its own layout, then the people:

| Kind | Draws, in order | People at |
|---|---|---|
| `cover` | a frame, the title (Caveat, 96), the subtitle | 72% scale, on the floor |
| `scene` | the setting, the props, the people, the caption | the scene's `scale` |
| `evidence` | the setting, the people, a quote card or a bar chart, the caption | full size |
| `punchline` | the setting, the punchline with a red underline, the people, the caption | full size |
| `spectrum` | the setting, a line with stops and badges, the people, the caption | 80% |
| `map` | a Wardley map (axes, stages, links, moves, nodes), the people, the caption | 55% |
| `graph` | groups, edges (with the highlighted path), nodes, the people, the caption | 55% |

5. **People.** For each cast entry: the character from the cast, at `x` (or spread evenly), in its pose and mood; its name under it; a gravity badge if the character has one; then, after everyone is placed, the bubbles, so a bubble is never under a person.
6. **The footer**, if asked for (`title · n/N`).
7. **Ready to play.** Every path without a fill gets `pathLength="1"`.

A human is drawn from the floor up: shadow, legs (or a stool when sitting), the body with hatching in the shirt colour, the arms from the pose table, the neck, hair behind the head when long, the head, hair, the face from the mood (eyes, brows from a table of offsets, the mouth), and the accessory. An agent is a screen on a hatched body, with an antenna, and eyes and mouth from the same mood table.

## Same data, same picture

Nothing in the drawing reads the clock or `Math.random()`. The deck seeds panel `i` with `11 + i`, and so do the grid, the shelf's thumbnails and `export.js`, so a panel exported to SVG is the panel on the screen, and a thumbnail drawn at build time matches the deck. The model sheet uses its own seeds per character, mood and pose. The tests check the consequence: the same panel exported twice is the same bytes.

## The animation, which is only CSS

A panel that is waiting to play has the class `wait` (everything hidden). `play(panel)` swaps it for `play` for as long as the last element takes, then removes it:

- every `path[pathLength]` animates `stroke-dashoffset` from 1 to 0: the stroke draws itself;
- each person (`.actor`) slides up and fades in, and each bubble, card or node (`.pop`) pops in, at its own `--d` delay, set when it was drawn, so they arrive in order.

With reduced motion asked for, there is no animation at all. The animated SVG export is the same rules placed inside the file.

## Wiring a page: the data contract

`wire(root)` looks for markup and data, never for configuration in script: a `.sb-viewer` (the toolbar, `.sb-deck`, `.sb-grid`, `.sb-script`) with a `<script type="application/json" class="sb-data">` holding `{ storyboard, cast }`; `.sb-contact` for many boards; `.sb-sheet` for the model sheet; `.sbx` for a shelf. It runs once per element on `DOMContentLoaded`, or at once when the kit loads after it, which is the case inside `<sg-storyboard>`.

A reader's choices (animation, panels per row, text under panels, last view) are kept in `localStorage` under the key the page sets in `window.StoryboardPrefsKey`, or `storyboards.v1`. `?view=deck|grid|script` in the address overrides them for one visit, and an embed's `view` attribute sets where it starts.

## Exports

`export.js` draws the panel into a detached SVG with the deck's seed, adds a `<style>` with the fonts (an `@font-face` pointing at the release, or the font files inlined as base64) and, for the animated version, the animation rules, and serialises it. For PNG and JPEG it draws that SVG, fonts inlined, into a canvas (an SVG used as an image cannot fetch anything) on the paper colour, and returns `canvas.toBlob`.

## Why classic scripts, not modules

The kit being replicated was one classic script, and the brief said to replicate first. A classic script also works from any page, any framework and a `file://` page without a server. The estate's house style is ES modules and three-file web components; that move is recorded as a candidate for v1.0.0, which will start from the last good v0 release.
