# SGit-AI__Website__Storyboards__API

The repository of **[api.storyboards.sgit.ai](https://api.storyboards.sgit.ai)**: the storyboard kit (the code that draws a storyboard's JSON as sketchy SVG panels in a browser, plus its formats, exports and embed), published so any site can use it, at **a path that is its version and never changes**:

```
https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/embed.js
```

Its twin is **[storyboards.sgit.ai](https://storyboards.sgit.ai)** ([SGit-AI__Website__Storyboards](https://github.com/SGit-AI/SGit-AI__Website__Storyboards)), which hosts the storyboards and uses this API exactly as any other site would. Both are built from [the brief](briefs/2026-10-20__storyboards-sgit-ai.md).

## Layout

| Path | What |
|---|---|
| `src/` | the working tree of the next release: `storyboard.js` (drawing and viewers), `storyboard.css`, `formats.js` (validate, markdown, graph; browser and Node), `export.js` (SVG, animated SVG, PNG, JPEG, contact sheet), `embed.js` (`<sg-storyboard>`), `props/security.js`, `vendor/` (Rough.js), `fonts/` and `fonts.css` |
| `v0/v0.1/v0.1.0/` | release v0.1.0 as published, with `manifest.json` (every file's bytes, SHA-256, SRI and origin). **Never edited.** |
| `tools/version.json` | `version` (the repository's, up on every push) and `release` (the newest cut of `src/`) |
| `tools/release.py` | `cut`, `check`, `bump`, `major --from`, `site` |
| `tools/provenance.json` | where each served file came from, copied into every manifest |
| `tools/render.mjs` | headless rendering for a site's build (thumbnails, previews, SVG, PNG) |
| `tools/live_check.py` | after a deploy: the live host serves every release's bytes |
| `site/` | the developer website: `build.py` (to `www/`, committed), `check.py` (its gate), `pages/` (guides, reference, internals, engineering), `gallery.py` (the specimen every kind, setting and prop is drawn from), `data/versions.json` |
| `policies/` | the agent behaviour policies: `code-immutability.md` (ABP-SB-001, the prose) and `code-immutability.policy.json` (its compiled half, which the hooks read) |
| `.claude/settings.json`, `.claude/hooks/` | the Claude Code hooks that enforce ABP-SB-001: SessionStart prints the rule, PreToolUse denies changes to published releases and asks before changes to the policy's own files |
| `.githooks/pre-commit` | refuses a commit that changes a published release (`git config core.hooksPath .githooks`; the SessionStart hook sets it) |
| `tools/upstream/` | the exact files the kit began as, hashed, so the site can show every patch as a diff |
| `tests/` | `test_formats.mjs` (Node), `test_policy.py` (the hooks, with refusals and allowed twins), `test_render.mjs` and `test_site.mjs` (Chromium, the host routed to this tree), fixtures from both origin sites |

## The agent behaviour policy

`policies/abp.json` (type `abp/site/v1`) describes the agents that work on this repository, what they can do, what they are asked to do, and every rule with its barrier and what enforces it. It is rendered as the site's top-level Behaviour policy page, `/abp/`, by the renderer shared with the twin repository (`site/abp.py` here, `admin/build/abp.py` there; `tests/test_policy.py` holds them equal), and is the shape to copy to every other site.

## The release rule

1. Change `src/` only after `python3 tools/release.py bump patch` (or `minor`), which moves the version in `tools/version.json` and in each file's `VERSION`.
2. `python3 tools/release.py cut` copies `src/` to its folder and writes the manifest. It refuses a folder that exists.
3. `python3 tools/release.py check` (CI, every commit) recomputes every hash of every release and fails if a published byte moved, or if `src/` changed without a bump.
4. A new major: `python3 tools/release.py major --from vX.Y.Z` starts `src/` from that release, byte for byte.
5. Add the line to `site/data/versions.json`, `python3 site/build.py`, `python3 site/check.py`, the tests, push to `dev`. The deploy tags the version, publishes `www/` with every release folder, and asks the live host for every hash.

Every push bumps `version`, even a documentation fix; only a change to `src/` cuts a `release`.

## Code immutability

Code in a published release folder is never changed: the [behaviour policy](https://api.storyboards.sgit.ai/policies/code-immutability.html) (ABP-SB-001), enforced by the hooks above, `tools/release.py check` and CI.

## Run the tests

```bash
node tests/test_formats.mjs
python3 tests/test_policy.py
node tests/test_render.mjs     # needs Playwright (npm install --no-save playwright@1.56.1) and its Chromium
node tests/test_site.mjs
```

Licence: Apache-2.0. Rough.js is MIT; Caveat and Patrick Hand are SIL OFL 1.1; each licence ships beside its file.
