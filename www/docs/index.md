# Documentation

> Everything about the code: how to use the kit, the reference, how it works inside, how it is released and the policy that keeps every release immutable.

*Source: <https://api.storyboards.sgit.ai/docs/index.html>.*

---

The storyboards themselves, and what they are for, are on [storyboards.sgit.ai](https://storyboards.sgit.ai/). This site is about the code that draws them: use it, read it, change it.

## Start

- [Documentation](../docs/index.html): Everything about the code: how to use the kit, the reference, how it works inside, how it is released and the policy that keeps every release immutable.
- [Quick start](../docs/quick-start.html): Draw a storyboard on any page, with the embed or with the kit's files loaded by hand.

## Guides

- [Write a storyboard](../guides/write-a-storyboard.html): From an empty file to a storyboard that validates, draws and embeds, in four steps.
- [Write a prop pack](../guides/write-a-prop-pack.html): Teach the kit to draw a new thing, without touching the kit: a prop pack is one function that returns drawing functions.
- [Render in a build](../guides/render-in-a-build.html): Thumbnails, link previews, SVG and PNG files from a site's build, drawn by the same release a reader's browser runs.
- [Pin a release](../guides/pin-a-release.html): Load the kit from one exact release, have the browser refuse anything else, and move to a new release on purpose.

## Reference

- [The format](../docs/format.html): A storyboard is one JSON file, its cast another. Every field the renderer reads, and every word of its vocabulary.
- [The gallery](../docs/gallery.html): Every kind, setting, prop, pose and mood of release v0.1.0, drawn live by it.
- [The JavaScript](../docs/javascript.html): The four globals release v0.1.0 defines, and what each function takes and returns.
- [The graph format](../docs/graph.html): A storyboard as a semantic graph, storyboards.sgit.ai/graph/v1: the node types, the edge verbs, and what each carries.

## Internals

- [How the kit works](../internals/architecture.html): The files of a release and how they load each other, how one panel is drawn, why the same data always gives the same picture, and how the animation works without a script.
- [The patches](../internals/patches.html): Every line release v0.1.0 changes in the code it began from, as a diff.

## Engineering

- [The release rule](../docs/versioning.html): Every release is a folder at a path that names it, never changed once published, with a manifest of hashes. How it works and how a release is made.
- [The release process](../engineering/release-process.html): A patch, a minor and a major, step by step, with the commands, what each refuses to do, and what the website shows afterwards.
- [Tests](../engineering/tests.html): What each test checks, against real files in a real browser, and the negative control that proves each check can fail.
- [CI and the deploy](../engineering/ci.html): What runs on every commit, what runs on a push to dev, and how a release is proved live.

## Policies

- [Policies](../policies/index.html): The agent behaviour policies this repository runs under, and how each is enforced.
- [Code immutability](../policies/code-immutability.html): Code in a published release folder is never changed, by any agent, for any reason. The behaviour policy for that one line, in riskmandate.ai's shape, and the hooks, gate and CI that enforce it.

## Releases

- [Releases](../releases/index.html): Every release of the kit, newest first. Each is a folder that never changes.
- [Release v0.1.0](../releases/v0.1.0.html): Release v0.1.0 of the kit: every file, its hash, where it came from and what changed.
