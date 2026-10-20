# Pin a release

> Load the kit from one exact release, have the browser refuse anything else, and move to a new release on purpose.

*Source: <https://api.storyboards.sgit.ai/guides/pin-a-release.html>.*

---

## One file names the release

Keep the release and its hashes in one place in your repository. storyboards.sgit.ai's `admin/build/api.json` is a copy of the release's manifest, reduced to what a page needs:

```json
{ "host": "https://api.storyboards.sgit.ai", "release": "v0.1.0", "path": "v0/v0.1/v0.1.0",
  "files": { "storyboard.js": { "sha256": "…", "integrity": "sha384-…" }, "…": {} } }
```

Its build writes every tag from that file, so no page can name another release or forget the integrity string.

## Every tag carries its hash

```html
<link rel="stylesheet" href="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/fonts.css" integrity="sha384-ep4bdPYRUzquMICQMhuOkSZ/CB1FnMh6qnGWS1F74VepoLOlw9JGK+Zg+E6/t9dD" crossorigin="anonymous">
<link rel="stylesheet" href="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/storyboard.css" integrity="sha384-NGJqtVi+93pE7lBuwFU0RQWhqnQVLR33Wp8AYH1iAeyC2A7h2ijgU4bEKF5HIKIf" crossorigin="anonymous">
<script src="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/vendor/rough-4.6.6.js" integrity="sha384-XPr5sCJfqHMzoJ8Cn1UYdXXD+XvRi0yoZm3W0yVJ24QP0ps8SYUskiXqnl4yqWlc" crossorigin="anonymous"></script>
<script src="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/props/security.js" integrity="sha384-IkxAFhrp5pQhBSjFCLMEA+1iqFHJ6xPRLeO2n9g478h7Z8hW9cUyvza3PuOtmsOx" crossorigin="anonymous"></script>
<script src="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/storyboard.js" integrity="sha384-3xZhCe5dUdBXMwV57gyscmlqdIjzz9L6huUkcuiEyC0V3jfrlQEdyEhvvF4kCeOa" crossorigin="anonymous"></script>
<script src="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/export.js" integrity="sha384-AZlBi+8U84fchjU5NkLWax6WlMqeEdfDT8jW+Rkjr7MYfrYxE9qfvToj6ekYas4M" crossorigin="anonymous"></script>
```

`crossorigin="anonymous"` is needed for the browser to check `integrity` on a file from another host. A file whose bytes are not those hashes is not run, and the console says why. This repository's tests check both directions: the manifest's strings are accepted, and a wrong one stops the script.

## The gate checks it

A consuming site's gate should fail when a page loads anything from `api.storyboards.sgit.ai` that is not on the pinned path, not in the pinned manifest, or missing its integrity string. storyboards.sgit.ai's `validate.py` does those three checks on every page.

## Moving to a new release

1. Read the new release's page under [Releases](../releases/index.html): what changed and the diff.
2. Re-pin: copy the new manifest's hashes (storyboards.sgit.ai: `python3 admin/build/build.py --pin PATH/TO/API`).
3. Rebuild, re-render anything drawn at build time, run your tests, ship.

Nothing moves unless you do this. The old release keeps being served, unchanged, for every page still pinned to it.
