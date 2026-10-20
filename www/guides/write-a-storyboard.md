# Write a storyboard

> From an empty file to a storyboard that validates, draws and embeds, in four steps.

*Source: <https://api.storyboards.sgit.ai/guides/write-a-storyboard.html>.*

---

## 1. A cast

A cast says who can appear and what they look like. Two characters are enough:

```json
{
  "what": "The cast of my first storyboard.",
  "characters": [
    { "id": "rae", "name": "Rae", "kind": "human", "pronouns": "they/them", "role": "the one asking",
      "look": { "skin": "#d8a47f", "hair": "curly", "hairColour": "#3b2a20", "shirt": "#2563eb", "trousers": "#1f2937", "accessory": "glasses" } },
    { "id": "bot", "name": "Bot", "kind": "agent", "pronouns": "it/its", "role": "the one answering", "look": { "colour": "#0f766e" } }
  ]
}
```

The other fields a character can carry (`stands_for`, `personality`, `wants`, `fears`, `line`) are shown on a series' shelf and model sheet; the drawing reads only `kind` and `look`. Hair is `short`, `long`, `curly`, `bun`, `beanie` or `bald`; the accessory is `glasses`, `headphones`, `lanyard` or `none`.

## 2. A storyboard

```json
{
  "slug": "my-first-storyboard",
  "title": "My first storyboard",
  "subtitle": "Three panels.",
  "status": "draft",
  "by": "you, today",
  "scenes": [
    { "kind": "cover", "title": "My first storyboard", "subtitle": "Three panels.",
      "cast": [ { "who": "rae", "pose": "wave", "mood": "happy" }, { "who": "bot", "pose": "wave", "mood": "happy" } ] },
    { "kind": "scene", "setting": "office", "caption": "A question",
      "cast": [ { "who": "rae", "x": 0.25, "pose": "think", "mood": "thinking", "says": "Is a panel really just JSON?" },
                { "who": "bot", "x": 0.75, "pose": "point", "mood": "happy", "says": "Every stroke of it.", "flip": true } ],
      "props": [ { "kind": "laptop", "x": 0.5, "y": 760, "scale": 1.2 } ] },
    { "kind": "punchline", "setting": "none", "punchline": "Change a line, redraw the panel.",
      "cast": [ { "who": "rae", "x": 0.2, "pose": "arms-up", "mood": "excited" } ] }
  ]
}
```

What the numbers mean: a panel is 1600 by 1000, the floor is at 900, `x` is 0 to 1 across the panel, a prop's `y` is in panel units (the line it stands on). `flip` turns a character to face left. `max` is the bubble's wrap width in characters (default 24); `lift` raises a bubble that would collide with another.

## 3. Validate it

`formats.js` runs the same checks every site's build does, in Node or a browser:

```js
const F = require('./formats.js');            // from https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/formats.js
const errors = F.validate(storyboard, cast);   // [] when good
// a storyboard using the security props: F.validate(storyboard, cast, { props: F.PACKS.security })
```

An unknown character, kind, pose, mood, setting or prop is an error with the panel number in it. So is an evidence panel with neither a quote nor bars, a cover with no title, or a graph edge naming a node that does not exist.

## 4. See it, and put it on a page

Put the two in one bundle, `{ "storyboard": ..., "cast": ..., "packs": [] }`, serve it anywhere that sends `access-control-allow-origin` (GitHub Pages does), and:

```html
<script src="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/embed.js" defer></script>
<sg-storyboard src="https://example.org/my-first-storyboard.bundle.json"></sg-storyboard>
```

The markdown script and the graph come from the same file: `F.toMarkdown(storyboard, cast)` and `F.toGraph(storyboard, cast)`. To see every kind, setting and prop drawn before you pick one, open [the gallery](../docs/gallery.html).

## The house rules the origin sites follow

They are not enforced by the kit, but they are why the storyboards on storyboards.sgit.ai can be trusted: a line a character says is the storyboard's own words and the panel says so (`"not_a_quote": true`); an evidence panel quotes its `source` word for word; `note` says what the panel is for; characters use the pronouns their cast file gives.
