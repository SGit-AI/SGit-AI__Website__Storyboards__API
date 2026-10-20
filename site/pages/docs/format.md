---
section: Reference
order: 1
title: The format
summary: A storyboard is one JSON file, its cast another. Every field the renderer reads, and every word of its vocabulary.
---

The 23 storyboards on [storyboards.sgit.ai](https://storyboards.sgit.ai/catalogue.json) are the worked examples: each has its `storyboard.json` and its series' `cast.json` beside it. `StoryboardFormats.validate(storyboard, cast, { props })` runs every check below and returns the problems, in Node or a browser.

## A storyboard

| Field | Required | What it is |
|---|---|---|
| `slug` | yes | lower-case-with-dashes, the storyboard's name in a URL |
| `title` | yes | the title |
| `subtitle` | | one line under it |
| `status` | | `draft`, `built`, `proposed`, `superseded`: shown as a pill |
| `by` | | who made it, and when |
| `rule` | | the rule its lines follow (e.g. that every line is the storyboard's, not a quote) |
| `scenes` | yes | the panels, in order |

## A panel (a scene)

| Field | For | What it is |
|---|---|---|
| `kind` | all | one of the kinds below; `scene` if absent |
| `caption` | most | the yellow caption box |
| `title`, `subtitle` | `cover` | the cover's text |
| `punchline` | `punchline` | the big line, underlined in red |
| `setting` | `scene`, `evidence`, `punchline`, `spectrum` | the background |
| `cast` | all | who is in the panel: `{ who, x, pose, mood, says, thinks, flip, max, scale, lift }` |
| `props` | `scene` | things in the panel: `{ kind, x, y, scale, label, lines, colour, ... }` |
| `evidence` | `evidence` | `{ quote, source }` or `{ title, bars: [{ label, value, shown, colour }] }` |
| `stops` | `spectrum` | `[{ label, note, colour, badge }]` along a line |
| `map` | `map` | a Wardley map: `{ axis, nodes: [{ id, label, x, y, anchor, highlight }], links: [[a, b]], moves: [{ from, to, label }] }` |
| `graph` | `graph` | a network: `{ style, nodes: [{ id, label, x, y, kind, colour }], edges: [{ from, to, label }], groups, path }` |
| `note` | all | the speaker's notes under the deck |
| `source` | all | where the panel's content comes from |
| `not_a_quote` | all | true when the lines are the storyboard's own words |

`x` and node coordinates are 0 to 1 across the panel; a panel is 1600 by 1000 with the floor at 900.

## A cast

`{ "what": ..., "characters": [ ... ] }`, each character `{ id, name, kind, pronouns, role, stands_for, personality, wants, fears, line, look }`. `kind` is `human` or `agent`. A human's `look` is `{ skin, hair, hairColour, hatColour, shirt, trousers, accessory, accentColour, height }`; an agent's is `{ colour }`. A character with a `gravity` (`explorer`, `villager`, `town-planner`) wears its badge by its name.

## A bundle

`{ "storyboard": {...}, "cast": {...}, "packs": ["security"] }`: what `<sg-storyboard src>` fetches.

## The vocabulary of {{RELEASE}}

{{VOCAB}}
