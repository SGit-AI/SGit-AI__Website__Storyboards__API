# api.storyboards.sgit.ai: for the agent working here

Read first: `briefs/` (shared with storyboards.sgit.ai), `REALITY.md`, `BRIEF-CORRECTIONS.md` (here and in the twin), then `README.md`.

The one rule: **a published release folder (`vX/vX.Y/vX.Y.Z/`) is never edited.** Not for a typo, not for a comment. `tools/release.py check` and CI enforce it. To change the kit: `release.py bump patch`, edit `src/`, `release.py cut`, add the line to `site/data/versions.json`, `site/build.py`, `site/check.py`, the tests. A new major starts from the last good release: `release.py major --from vX.Y.Z`.

Every push bumps `tools/version.json` "version" (a docs-only push too); only a change to `src/` moves "release".

The twin, `SGit-AI__Website__Storyboards` (storyboards.sgit.ai), is normally checked out beside this one and pins a release in `admin/build/api.json`. After cutting a release, re-pin and rebuild it in the same session (`build.py --pin`, `render.py --all`, `build.py`, `validate.py`, `node tests/test_site.mjs`), so the two never drift.

Code: classic scripts with a `VERSION` constant (see BRIEF-CORRECTIONS.md for why not ESM yet); no dependencies but the vendored ones; nothing fetched from a third party at run time. Prose: no em-dashes, state the status of things.
