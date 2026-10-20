---
title: The release process
section: Engineering
order: 2
summary: A patch, a minor and a major, step by step, with the commands, what each refuses to do, and what the website shows afterwards.
---

There are two numbers in `tools/version.json`, and they move for different reasons:

| Number | Moves when | Example |
|---|---|---|
| `version` | every push to `dev`, the release branch, including a documentation or CI change | `v0.1.1`: a CI fix, no code changed |
| `release` | only when a file in `src/` changes; it names the folder cut | `v0.1.0` |

A push that changes only the website or the tooling moves `version` and nothing a consumer loads. A push that changes code moves both, and adds a folder.

## A patch (a fix in the kit)

```bash
python3 tools/release.py bump patch     # tools/version.json and each src/ file's VERSION: v0.1.0 -> v0.1.1
# edit src/; add or change the test that fails without the fix
python3 tools/release.py cut            # src/ -> v0/v0.1/v0.1.1/ with manifest.json; refuses if the folder exists
python3 tools/release.py check          # every release's hashes; src/ equals the newest
# a line in site/data/versions.json: the version, the release, what changed and why
python3 site/build.py && python3 site/check.py
node tests/test_formats.mjs && node tests/test_render.mjs && node tests/test_site.mjs
git commit -am "v0.1.1: what changed" && git push origin dev
```

On `dev` the deploy tags `v0.1.1`, publishes the website with every release folder, and `tools/live_check.py` asks the live host for the hash of every file of every release. Then re-pin the consuming site ([pin a release](../guides/pin-a-release.html)).

## A minor (something new, nothing broken)

The same, with `bump minor`: `v0.1.1` becomes `v0.2.0`, in `v0/v0.2/v0.2.0/`. New props, a new export, a new attribute on the embed.

## A major (something a consumer must change for)

```bash
python3 tools/release.py major --from v0.2.3    # src/ becomes v0.2.3's bytes, renamed v1.0.0
# make only the changes that make it a major
python3 tools/release.py cut                    # v1/v1.0/v1.0.0/
```

Starting from the last good release, not from whatever was in `src/`, means the first v1 differs from the last v0 by exactly the breaking change, and both folders stay published to compare.

## A documentation change

Move `version` only (edit `tools/version.json` by hand, the next patch), add its line to `site/data/versions.json`, rebuild the site. `release.py check` passes because `src/` still equals the newest release.

## What refuses what

| Mistake | Stopped by |
|---|---|
| Editing a file in a published folder | `release.py check` (every hash), CI's comparison with `dev`, and the [code immutability policy](../policies/code-immutability.html)'s hook in an agent session |
| Changing `src/` without a bump | `release.py check`: "src/ differs from the published v0.1.0" |
| Cutting over an existing folder | `release.py cut` |
| Pushing to `dev` without a new version | CI's version check |
| A version without its history line | `site/build.py` |
| The live host serving other bytes | `tools/live_check.py` after the deploy |
