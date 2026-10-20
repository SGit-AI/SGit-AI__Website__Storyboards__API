# The release rule

> Every release is a folder at a path that names it, never changed once published, with a manifest of hashes. How it works and how a release is made.

*Source: <https://api.storyboards.sgit.ai/docs/versioning.html>.*

---

## The rule

- A release lives at `/vMAJOR/vMAJOR.MINOR/vMAJOR.MINOR.PATCH/`: v0.1.0 is at `https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/`.
- The folder holds every file the kit needs, so the files inside it only ever meet files of the same release.
- Nothing in a published folder changes. A fix, however small, is the next patch, in its own folder.
- Every folder has a `manifest.json`: each file's path, size, SHA-256, and the `sha384-` string for an `integrity` attribute.
- There is no floating path (no `/v0/latest/`, no `/v0.1/`). [`/releases.json`](../releases.json) lists every release, newest first.
- A new major begins as the last good release of the one before, byte for byte, and changes only what makes it a major.

This is the brief's own rule: "every version is immutable. I think that's important" ([the brief](../brief/2026-10-20__storyboards-sgit-ai.html)).

## How it is enforced

`tools/release.py` in the [repository](https://github.com/SGit-AI/SGit-AI__Website__Storyboards__API) does each step, and CI runs `check` on every commit:

| Command | Does |
|---|---|
| `python3 tools/release.py bump patch` (or `minor`) | moves `tools/version.json` and the `VERSION` string in each file of `src/` to the next release |
| `python3 tools/release.py cut` | copies `src/` into the release's folder and writes its manifest; refuses a folder that already exists |
| `python3 tools/release.py check` | recomputes every hash of every release; fails if any published byte moved, or if `src/` differs from the current release without a bump |
| `python3 tools/release.py major --from vX.Y.Z` | resets `src/` to that release's bytes as the next major |
| `python3 tools/release.py site --out DIR` | assembles what GitHub Pages serves: this site, every release folder, `releases.json` |

After a deploy, `tools/live_check.py` asks the live host for every file of every release and compares it with the manifest.

## Two numbers

`tools/version.json` holds `version`, the repository's version, which goes up on every push (a documentation fix too), and `release`, the newest cut of the kit, which consumers pin. The [version history](../versions/index.html) is the first; the [releases](../releases/index.html) are the second.

## For a consuming site

Pin one release in one place (storyboards.sgit.ai keeps it in `admin/build/api.json`, copied from the manifest), load every file from that exact path with its integrity string, and have the gate check both. Moving to a new release is a one-line change and a rebuild.
