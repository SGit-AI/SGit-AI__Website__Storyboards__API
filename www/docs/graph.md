# The graph format

> A storyboard as a semantic graph, storyboards.sgit.ai/graph/v1: the node types, the edge verbs, and what each carries.

*Source: <https://api.storyboards.sgit.ai/docs/graph.html>.*

---

`StoryboardFormats.toGraph(storyboard, cast, { url, seriesTitle })` returns `{ what, format, storyboard, nodes, edges }`. Every storyboard on storyboards.sgit.ai has one at `graph.json`. Nodes are things; edges are verbs a reader can say aloud, "panel 3 features Noor", "Noor says 'Two ways'", in the spirit of [graphs.sgit.ai](https://graphs.sgit.ai/).

## Nodes

| Type | Id | Carries |
|---|---|---|
| `storyboard` | `storyboard:<slug>` | label (the title), subtitle, status, url |
| `panel` | `panel:<slug>/<n>` | label (caption, punchline or title), n, kind, text (the panel as one paragraph) |
| `character`, `agent` | `character:<id>` | label (the name) |
| `prop` | `prop:<kind>` | label |
| `source` | `source:<text>` | label |
| `setting` | `setting:<name>` | label |
| `series`, `shelf`, `author` | `series:<slug>`, `shelf:<title>`, `author:<name>` | label |

A character, prop, source or setting is one node however many panels use it: that is what makes the graph worth having across storyboards.

## Edges

| From | Verb | To | Carries |
|---|---|---|---|
| storyboard | `has_panel` | panel | n |
| panel | `next` | panel | |
| panel | `features` | character | pose, mood |
| character | `says`, `thinks` | panel | text |
| panel | `shows` | prop | |
| panel | `quotes` | source | (the panel quotes it) |
| panel | `drawn_from` | source | (the panel is `not_a_quote`) |
| panel | `cites` | source | (an evidence card's source) |
| panel | `set_in` | setting | |
| storyboard | `part_of`, `on_shelf`, `made_by` | series, shelf, author | |

The format is versioned in its `format` field. A change that removes or renames anything is a new format version, shipped in a new release.
