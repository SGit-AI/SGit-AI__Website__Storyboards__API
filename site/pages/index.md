---
title: The storyboard kit
summary: The code that draws every storyboard on storyboards.sgit.ai, served so any page can use it: one script tag, pinned to a folder that never changes.
---

A storyboard here is data: a JSON file naming who is in each panel, their pose and mood, what they say, the evidence and its source, and a cast file saying what each character looks like. This site serves the code that draws them, as sketchy SVG panels with [Rough.js](https://roughjs.com), in the reader's browser. [storyboards.sgit.ai](https://storyboards.sgit.ai/) is where the storyboards live; this is what draws them, there and anywhere else.

## Two lines

```html
<script src="{{BASE}}embed.js" defer></script>
<sg-storyboard src="https://storyboards.sgit.ai/pki/the-first-key/bundle.json"></sg-storyboard>
```

{{DEMO}}

## One rule: the path is the version

The current release is **{{RELEASE}}**, at `{{BASE}}`. Nothing at that path will ever change: a fix is a new folder, and this one stays. Every file in it is listed below with its SHA-256 and the `integrity` string a browser checks; every release has its own [manifest]({{BASE}}manifest.json). There is no `latest` path, on purpose: a page moves to a new release by changing one line. [Versioning](docs/versioning.html) has the whole rule and the tools that enforce it.

{{FILES}}

## Where to go next

| | |
|---|---|
| [Quick start](docs/quick-start.html) | Embed a storyboard, or load the kit's files yourself with integrity strings |
| [The format](docs/format.html) | The storyboard and cast JSON, and the vocabulary the renderer knows |
| [The JavaScript](docs/javascript.html) | `StoryboardKit`, `StoryboardFormats`, `StoryboardExport` and `<sg-storyboard>` |
| [Versioning](docs/versioning.html) | Immutable folders, manifests, cutting a release, starting a major |
| [Releases](releases/index.html) | Every release, every file, every hash |
| [The brief](brief/2026-10-20__storyboards-sgit-ai.html) | The voice memo this was built from, in full |
