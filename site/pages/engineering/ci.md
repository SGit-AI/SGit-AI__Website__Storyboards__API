---
title: CI and the deploy
section: Engineering
order: 4
summary: What runs on every commit, what runs on a push to dev, and how a release is proved live.
---

## Every commit: `.github/workflows/ci.yml`

| Step | Fails when |
|---|---|
| Syntax | any `.js` or `.mjs` does not parse, any tool does not compile |
| `release.py check` | a published byte moved, a manifest disagrees with its folder, or `src/` changed without a bump |
| A cut, twice | two cuts of the same tree differ (the build must be reproducible) |
| Published releases untouched | a release folder that exists on `dev` differs on this branch |
| The version is bumped | this branch's `version` is not above `dev`'s (skipped for a commit already on `dev`) |
| The website | `www/` is not what `site/build.py` writes, or `site/check.py` finds a broken link, a missing twin, a sitemap gap or a key shape |
| `test_formats.mjs` | see [Tests](tests.html) |
| Browser job | `test_render.mjs` or `test_site.mjs` fails in Chromium |

## A push to dev: `.github/workflows/deploy-pages.yml`

1. **check**: syntax, `release.py check`, the website, `test_formats.mjs`.
2. **tag**: tags the commit with `version`; refuses a version that is already the tag of another commit.
3. **deploy**: `release.py site` assembles `www/`, every release folder, `releases.json`, `CNAME`; GitHub Pages publishes it.
4. **live**: `tools/live_check.py` fetches every file of every release from the live host and compares its SHA-256 with the manifest, for up to eight minutes while the CDN catches up.

A release is done when step 4 passes, not when the push succeeds.
