# Reality: what exists, as of repository v0.2.0, kit release v0.1.0 (20 October 2026)

A feature not in this file does not exist.

## Exists, and was checked

- Release v0.1.0 at `v0/v0.1/v0.1.0/`: 13 files, 233,769 bytes, each with SHA-256 and SRI in `manifest.json`.
- `storyboard.js`: gen-z-developers.sgit.ai's kit (sha256 86212ff5...) with four marked patches: prop packs, a per-site preferences key, `VOCAB`/`VERSION`/`addProps`/`wire()` (and wiring when loaded after DOMContentLoaded), an embed's start view.
- `props/security.js`: pki.sgit.ai's twelve props, registering as a pack.
- `formats.js`: validate, markdown, semantic graph, text, stats; runs in Node and the browser; its vocabulary is held equal to the kit's by a test.
- `export.js`: one panel as SVG (fonts linked, embedded or none; still or animated), every panel as one SVG, PNG and JPEG at any width.
- `embed.js`: `<sg-storyboard>` with `src` or `storyboard`+`cast`, `view` deck/grid/script/panel, `panel`, `packs`.
- `tools/release.py` cut/check/bump/major/site; `check` caught `src/formats.js` drifting from the cut on 20 October 2026, before anything was published.
- Tests: `test_formats.mjs` 7 passing (with a negative control), `test_render.mjs` 7 passing in Chromium (embed from another origin, both fixtures, the three views, the security pack, SRI accepted and a wrong SRI refused, every export), `test_site.mjs` 12 pages with no errors.
- The website: home with a live embed, docs (quick start, format, JavaScript, versioning), releases with every hash, version history, the brief in full, participant disclosure, `llms.txt`, twins, sitemap.

- The developer website (v0.2.0): guides, reference, the live gallery (every kind, setting, prop, pose and mood of the release), the graph format, internals, the patches against upstream as diffs, a page per release, tests, CI, the release process, a documentation sidebar.
- ABP-SB-001, code immutability: the prose (`policies/code-immutability.md`), the compiled half (`policies/code-immutability.policy.json`), the Claude Code hook (deny on published releases, ask on the policy's own files, instructions at SessionStart), the git pre-commit hook, and `tests/test_policy.py`, run in CI. The same hook is wired into storyboards.sgit.ai's `.claude/settings.json`.

## Does not exist yet

- A boundary for ABP-SB-001: every control is a setting (files the agent can write). Branch protection on `dev` requiring the `ci` check, and CODEOWNERS on the policy's files, are GitHub settings only a person can make.
- A ledger of the hook's decisions (footprint): refusals are seen in the session, not recorded.

- The live host: DNS for api.storyboards.sgit.ai (a CNAME to `sgit-ai.github.io`) and Pages enabled on this repository.
- Tests in Firefox and WebKit.
- The `review/` folder from the sgit.ai repository guidance.
- ES-module, three-file components (see BRIEF-CORRECTIONS.md).
- The origin sites loading the kit from here instead of their own copies.
