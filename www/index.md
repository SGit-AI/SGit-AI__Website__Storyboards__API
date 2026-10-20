# The storyboard kit

> The code that draws every storyboard on storyboards.sgit.ai, served so any page can use it: one script tag, pinned to a folder that never changes.

*Source: <https://api.storyboards.sgit.ai/index.html>.*

---

A storyboard here is data: a JSON file naming who is in each panel, their pose and mood, what they say, the evidence and its source, and a cast file saying what each character looks like. This site serves the code that draws them, as sketchy SVG panels with [Rough.js](https://roughjs.com), in the reader's browser. [storyboards.sgit.ai](https://storyboards.sgit.ai/) is where the storyboards live; this is what draws them, there and anywhere else.

## Two lines

```html
<script src="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/embed.js" defer></script>
<sg-storyboard src="https://storyboards.sgit.ai/pki/the-first-key/bundle.json"></sg-storyboard>
```



## One rule: the path is the version

The current release is **v0.1.0**, at `https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/`. Nothing at that path will ever change: a fix is a new folder, and this one stays. Every file in it is listed below with its SHA-256 and the `integrity` string a browser checks; every release has its own [manifest](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/manifest.json). There is no `latest` path, on purpose: a page moves to a new release by changing one line. [Versioning](docs/versioning.html) has the whole rule and the tools that enforce it.

| File | Bytes | SHA-256 | Integrity |
|---|---|---|---|
| [embed.js](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/embed.js) | 6,618 | `849cd79b2ef346f9…` | `sha384-MJYywdRM1gslaDV…` |
| [export.js](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/export.js) | 6,977 | `f49a784f692499b8…` | `sha384-AZlBi+8U84fchjU…` |
| [fonts.css](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/fonts.css) | 522 | `aa1cef498940e9c9…` | `sha384-ep4bdPYRUzquMIC…` |
| [fonts/OFL-Caveat.txt](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/fonts/OFL-Caveat.txt) | 4,385 | `1f9d81d094273d82…` | `sha384-l911Hl/fkgplR26…` |
| [fonts/OFL-PatrickHand.txt](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/fonts/OFL-PatrickHand.txt) | 4,376 | `377f4f9c19e93522…` | `sha384-dMIp2Y7W7PbACj2…` |
| [fonts/caveat-700-latin.woff2](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/fonts/caveat-700-latin.woff2) | 51,020 | `15f9638095ad5ec9…` | `sha384-8ZKDDsekt9CcGNg…` |
| [fonts/patrick-hand-400-latin.woff2](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/fonts/patrick-hand-400-latin.woff2) | 23,944 | `ac5bc9033b2572bf…` | `sha384-eczLNWFwBaxVkuy…` |
| [formats.js](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/formats.js) | 11,494 | `1e8f89a4dc4a6ec0…` | `sha384-5+Nd7LBeUw3ULih…` |
| [props/security.js](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/props/security.js) | 11,483 | `bd58ffd4885eeb07…` | `sha384-IkxAFhrp5pQhBSj…` |
| [storyboard.css](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/storyboard.css) | 15,822 | `6d8c968a1c3ba7f3…` | `sha384-NGJqtVi+93pE7lB…` |
| [storyboard.js](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/storyboard.js) | 68,150 | `7465946c3a7fa739…` | `sha384-3xZhCe5dUdBXMwV…` |
| [vendor/rough-4.6.6.LICENSE.txt](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/vendor/rough-4.6.6.LICENSE.txt) | 1,068 | `dca9a392272606ac…` | `sha384-QZ87aOxxFPPgpOK…` |
| [vendor/rough-4.6.6.js](https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/vendor/rough-4.6.6.js) | 27,926 | `8589b8664aecfa76…` | `sha384-XPr5sCJfqHMzoJ8…` |

## Where to go next

| | |
|---|---|
| [Quick start](docs/quick-start.html) | Embed a storyboard, or load the kit's files yourself with integrity strings |
| [The format](docs/format.html) | The storyboard and cast JSON, and the vocabulary the renderer knows |
| [The JavaScript](docs/javascript.html) | `StoryboardKit`, `StoryboardFormats`, `StoryboardExport` and `<sg-storyboard>` |
| [Versioning](docs/versioning.html) | Immutable folders, manifests, cutting a release, starting a major |
| [Releases](releases/index.html) | Every release, every file, every hash |
| [The brief](brief/2026-10-20__storyboards-sgit-ai.html) | The voice memo this was built from, in full |
