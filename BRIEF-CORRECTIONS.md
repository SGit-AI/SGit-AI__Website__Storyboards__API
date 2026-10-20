# Brief corrections

The brief is shared with storyboards.sgit.ai, and so are its corrections: [SGit-AI__Website__Storyboards/BRIEF-CORRECTIONS.md](https://github.com/SGit-AI/SGit-AI__Website__Storyboards/blob/dev/BRIEF-CORRECTIONS.md) holds the readings that shaped both repositories (the hosts, every version immutable with no aliases, the path shape). This file holds the ones that are only about the API.

| Date | The brief, or the guidance, says | What was found | What was done |
|---|---|---|---|
| 2026-10-20 | sgit.ai's code guidance: native web components, three files each, ESM only | The kit being replicated is one classic script (an IIFE defining `window.StoryboardKit`), and the brief says to replicate first | v0.1.0 keeps the classic scripts, and the one component (`<sg-storyboard>`) is a single classic file. Moving to ES modules and three-file components is a candidate for v1.0.0, started from the last good v0 as the brief asks |
| 2026-10-20 | "every release is kind of self-contained" | The kit draws in two hand fonts that were loaded from Google Fonts by the origin sites | Both fonts are vendored in every release (latin subset, OFL), so a release fetches nothing from a third party |
| 2026-10-20 | The embed draws "the storyboard" | In the deck view, the kit's own deck listens to the arrow keys on the whole document and writes `#scene-N` into the address bar, as it does on its own pages | Documented on the embed page; `view="panel"` or `view="grid"` avoid it. Scoping both to the element is a v0.2 change |
