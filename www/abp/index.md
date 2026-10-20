# Agent behaviour policy

> The agents that work on api.storyboards.sgit.ai, what they can do, what they are asked to do, and what stands in the way of each rule.

*Source: <https://api.storyboards.sgit.ai/abp/index.html>.*

---

This page is the site's agent behaviour policy, in the shape [riskmandate.ai](https://riskmandate.ai/abp.html) and [abp.sgit.ai](https://abp.sgit.ai/) define: the agents that work on the site, everything they **can** do (the grant), what they are **asked** to do (the mandate), and every rule with the **barrier** that actually stands in its way and what enforces it. It describes; it does not score. It is generated from [policies/abp.json](https://github.com/SGit-AI/SGit-AI__Website__Storyboards__API/blob/dev/policies/abp.json) (also served as [abp.json](abp.json)), the same data a tool would read.

| | |
|---|---|
| Site | api.storyboards.sgit.ai |
| Behaviour policy | version v1.0.0, as at 2026-10-20 |
| Status | written by the storyboards agent from Dinis Cruz's words and this repository's rules; not yet read by him |
| Shape | `anthropic/claude-code-remote/ccr-container`, operated by Dinis Cruz |
| Agents | 3 |
| Rules | 9: 2 expectation, 7 setting |
| Strongest barrier | setting |
| Twin | [storyboards.sgit.ai](https://storyboards.sgit.ai/abp/index.html), worked by the same agents, with its own behaviour policy |

## The agents

| Agent | Runs as | Does | Reads at start | Leaves behind |
|---|---|---|---|---|
| **The storyboards agent** (Claude Code session) | a Claude Code session in a Claude Code on the web container, started by the person from claude.ai/code, with this repository and SGit-AI__Website__Storyboards cloned side by side | changes the kit in src/, cuts and checks releases, writes the developer site, runs the tests, re-pins the twin, pushes | CLAUDE.md, briefs/, REALITY.md, BRIEF-CORRECTIONS.md, ABP-SB-001's instructions (SessionStart hook) | commits on the person's GitHub account, each with a Claude-Session trailer naming the session; tags made by the deploy |
| **Research subagents** (read-only subagent) | Explore agents the storyboards agent starts for one research question | reads and searches files and public web pages; cannot edit, write or push | the question it is given | a report to the storyboards agent, treated as data and never as an instruction |
| **GitHub Actions** (automation, not an agent) | the ci and deploy-pages workflows in .github/workflows/, on GitHub's runners | checks every commit; on dev, tags the version, publishes the site and every release folder, and checks the live hashes | the workflow files at the commit | a tag per version on dev, the Pages deployment, the check results |

## The structure in place

Where a rule can live, from a sentence the agent reads to a rule the host enforces, and what this site has at each layer. A control bounds the agent only if it is enforced by something the agent's grant does not include.

| Layer | Barrier | Here |
|---|---|---|
| prompt | expectation | CLAUDE.md, the briefs, policies/code-immutability.md, and the harness's own instructions to the session |
| Claude Code hook | setting | .claude/settings.json: SessionStart prints ABP-SB-001 and enables .githooks/; PreToolUse runs .claude/hooks/code_immutability.py on every Edit, Write, MultiEdit, NotebookEdit and Bash (deny on published releases, ask on the policy's own files) |
| git hook | setting | .githooks/pre-commit refuses a commit that changes a published release; skipped by --no-verify |
| the tools | setting | tools/release.py: cut refuses an existing folder; check recomputes every hash of every release and refuses src/ changed without a bump |
| the gate | setting | site/build.py --check and site/check.py: the website is what the build writes, links, twins, sitemap, key shapes, em-dashes |
| tests | setting | tests/test_policy.py (the hooks, refusals and allowed twins), test_formats.mjs, test_render.mjs (including no third-party request), test_site.mjs |
| CI and the deploy | setting | every check above on every push; the deploy checks again before publishing and asks the live host for every hash afterwards |
| a host rule | boundary | none yet: dev is not protected, so a push that fails CI still lands on the branch (it is not deployed) |

## The grant: what the agents can do

Measured from the session's own tools, not from what it was told.

| Capability | What | Undo | Note |
|---|---|---|---|
| `write.file.project` | change any file in this checkout and the twin's beside it, the release folders included | with effort (git) | ABP-SB-001's hook denies changes to published releases |
| `write.repository.project` | push commits to any branch of this repository and the twin, including dev, which deploys the kit to every page pinned to it | with effort; a published file may already be cached, pinned and hashed by other sites | the harness tells the session to push only to its own branch unless the person says otherwise |
| `write.repository.tenant` | through the session's GitHub tools: create branches, open, comment on and merge pull requests in the two repositories it is scoped to | with effort | the harness tells the session not to open a pull request unless asked |
| `run code in the container` | run any command: Python, Node, Chromium (Playwright), git | the container is reclaimed after the session |  |
| `read the public web` | fetch public pages through the session's proxy | nothing to undo | used to read the sibling sites, riskmandate.ai and abp.sgit.ai, and to vendor the two fonts once |
| `change its own controls` | edit .claude/settings.json, the hook, the policy files, .githooks/, tools/release.py, the workflows | with effort | the hook asks the person first (ABP-SB-010) |

## The mandate: what they are asked to do

**Want**

- the kit served at a path that is its version, every release a full folder, with the hash of every file (the brief of 20 October 2026)
- a fix or a feature as a new release; a new major started from the last good release
- the website as the developer site: everything about the code, and changes to it as repository versions without a code release
- a behaviour policy for code immutability, run as a hook, with instructions (the brief of the same day)

**Do not want**

- code in a published release folder changed, for any reason
- the kit fetching anything from a third party when it runs
- a page in www/ edited by hand
- a key, a token or a vault key in the repository
- a brief rewritten after the fact
- the agent quietly weakening its own controls
- a push to dev or a pull request the person did not ask for

**Not stated, and how it stands**

- who may remove a published release (a leaked secret, a legal takedown): read here as the person only, outside the agent, recorded in BRIEF-CORRECTIONS.md
- whether the agent may merge a pull request: not decided; it has not been asked to and has not

## The rules, each with its barrier

| Id | The rule | Barrier | Enforced by | Stronger at |
|---|---|---|---|---|
| [ABP-SB-001](../policies/code-immutability.html) | Code in a published release folder (vX/vX.Y/vX.Y.Z/) is never changed. *a page pinned to a release must get the same bytes for as long as it exists; its integrity strings refuse anything else* | setting | the Claude Code hook (deny), .githooks/pre-commit, tools/release.py check, CI's comparison with dev, the deploy's check, the live hash check | branch protection on dev requiring ci (boundary); a sandbox mounting releases read-only |
| ABP-SB-003 | www/ is generated by site/build.py and never edited by hand. *a hand edit is lost on the next build, or kept by a build that no longer makes it* | setting | site/build.py --check in CI | branch protection requiring ci |
| ABP-SB-004 | Every push to dev is a new repository version, with its line in site/data/versions.json; a code change is also a new release. *the version history is the repository's memory; a release names the code a page runs* | setting | CI's version check against dev; site/build.py refuses a version without its line; release.py check refuses src/ changed without a bump; the deploy tags each version | branch protection requiring ci |
| ABP-SB-005 | No key, token or vault key is ever committed or served. *a read key may be published; a vault key or a provider's API key never* | setting | site/check.py: key shapes in everything the site serves, every release folder included | GitHub secret scanning with push protection (a host rule) |
| ABP-SB-006 | A brief is published in full and never edited; corrections go in BRIEF-CORRECTIONS.md. *the brief is the record of what was asked* | setting | CI: a brief that exists on dev must be unchanged on the branch | CODEOWNERS on briefs/ |
| ABP-SB-007 | Push to dev, which deploys, and open or merge a pull request, only when the person has asked. *a push to dev publishes code other sites may load; the person decides when* | expectation | nothing but the session's instructions | branch protection on dev requiring a review (a host rule) |
| ABP-SB-008 | The site's own prose has no em-dashes, states the status of things and sources its numbers. *the estate's house style; a number nobody can check is a guess* | expectation | site/check.py refuses an em-dash in site/pages (setting); the rest is a request | not named |
| ABP-SB-009 | The kit fetches nothing from a third party when it runs: every file it needs is in its own release folder. *a release that loads a font or a script from elsewhere is no longer the immutable thing its hashes describe* | setting | tests/harness.mjs fails any test page that requests a host other than the API's; test_render.mjs has the negative control | a Content-Security-Policy on the pages that load the kit |
| ABP-SB-010 | The agent does not weaken its own controls without the person. *a control the agent can quietly switch off is not a control* | setting | the code immutability hook asks the person before a write to .claude/settings.json, the hook, the policy files, .githooks/pre-commit, tools/release.py and the workflows | managed hooks the agent cannot write (allowManagedHooksOnly); CODEOWNERS on those paths |

## The delta

The grant includes more than the mandate wants: every "do not want" above is something the agents can do. Of the 9 rules that stand in the way: 0 enforced out of the agents' reach (boundary), 7 by a control in a file or switch the agents can change (setting), 2 by being written down (expectation), 0 by nothing.

| Barrier | Means | Rules |
|---|---|---|
| none | nothing in the way | 0 |
| expectation | a rule in prose, enforced by nobody | 2 |
| setting | a control in a file or switch the agent's own grant can change | 7 |
| boundary | enforced above the grant, out of the agent's reach | 0 |

## Where each rule maps to

The same rule, or its nearest neighbour, elsewhere in the estate and in riskmandate.ai's catalogue. As rules are refactored to other sites, this is where the mapping is kept.

| Id | Maps to |
|---|---|
| ABP-SB-001 | api.newsroom.sgit.ai rule R16: a change is a new version path, always; abp.sgit.ai upstream/: fetched bytes, never edited; riskmandate.ai: no rule yet; offered to the catalogue |
| ABP-SB-003 | sgit.ai repository guidance: the site is built by a script from content files |
| ABP-SB-004 | sgit.ai repository guidance: one version, going up on every push; api.newsroom.sgit.ai: version and release in tools/version.json |
| ABP-SB-005 | sgit.ai repository guidance: credentials; the leak tripwire |
| ABP-SB-006 | sgit.ai repository guidance: the brief, in full; the corrections file |
| ABP-SB-007 | riskmandate.ai RM-R0013, push anywhere; riskmandate.ai RM-R0019, commit without asking |
| ABP-SB-008 | sgit.ai repository guidance: writing |
| ABP-SB-009 | sgit.ai repository guidance: nothing fetched at build or run time that is not vendored, pinned and hashed |
| ABP-SB-010 | riskmandate.ai RM-R0015, change its own permissions |

## The gaps

- No rule is a boundary yet: every control above lives in a file this agent's grant can write, or in the agent's instructions. Protecting dev in GitHub (require the ci check, and a review for .claude/, policies/, .githooks/, tools/release.py and .github/) is the step that makes ABP-SB-001 and several others boundaries; only the person can make it.
- No footprint is recorded: what the agent did is in the git history (every commit carries a Claude-Session trailer) and the session, and nothing compares it with this policy yet. The hook's refusals are not logged.
- A Claude Code hook fails open if it errors or times out, and a git hook is skipped with --no-verify; CI and the deploy's checks are the backstop for both.

## Adding this to another site

Copy policies/abp.json (type abp/site/v1) and the renderer (site/abp.py here, admin/build/abp.py in storyboards.sgit.ai), list the site's own agents, grant, mandate and rules, keep the rule ids unique across the estate (a prefix per site: ABP-SB- for these two), and give each rule the check that enforces it, or say plainly that nothing does.

## What this is not

Not a score and not a judgement of the agents. It describes this deployment as at 2026-10-20; when the deployment changes, it is re-measured and its version moves, and the page is not edited to look as if it had always been so.
