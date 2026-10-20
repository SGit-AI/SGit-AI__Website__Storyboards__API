---
title: Pin a release
section: Guides
order: 4
summary: Load the kit from one exact release, have the browser refuse anything else, and move to a new release on purpose.
---

## One file names the release

Keep the release and its hashes in one place in your repository. storyboards.sgit.ai's `admin/build/api.json` is a copy of the release's manifest, reduced to what a page needs:

```json
{ "host": "https://api.storyboards.sgit.ai", "release": "{{RELEASE}}", "path": "v0/v0.1/{{RELEASE}}",
  "files": { "storyboard.js": { "sha256": "…", "integrity": "sha384-…" }, "…": {} } }
```

Its build writes every tag from that file, so no page can name another release or forget the integrity string.

## Every tag carries its hash

```html
{{SRI_EXAMPLE}}
```

`crossorigin="anonymous"` is needed for the browser to check `integrity` on a file from another host. A file whose bytes are not those hashes is not run, and the console says why. This repository's tests check both directions: the manifest's strings are accepted, and a wrong one stops the script.

## The gate checks it

A consuming site's gate should fail when a page loads anything from `api.storyboards.sgit.ai` that is not on the pinned path, not in the pinned manifest, or missing its integrity string. storyboards.sgit.ai's `validate.py` does those three checks on every page.

## Moving to a new release

1. Read the new release's page under [Releases](../releases/index.html): what changed and the diff.
2. Re-pin: copy the new manifest's hashes (storyboards.sgit.ai: `python3 admin/build/build.py --pin PATH/TO/API`).
3. Rebuild, re-render anything drawn at build time, run your tests, ship.

Nothing moves unless you do this. The old release keeps being served, unchanged, for every page still pinned to it.
