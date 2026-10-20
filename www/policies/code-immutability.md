# Code immutability

> Code in a published release folder is never changed, by any agent, for any reason. The behaviour policy for that one line, in riskmandate.ai's shape, and the hooks, gate and CI that enforce it.

*Source: <https://api.storyboards.sgit.ai/policies/code-immutability.html>.*

---

*ABP-SB-001 · version v1.0.0 · in force from repository v0.2.0; written by the storyboards agent from Dinis Cruz's words, not yet read by him · 2026-10-20*

This is an Agent Behaviour Policy in the shape [riskmandate.ai](https://riskmandate.ai/abp.html) and [abp.sgit.ai](https://abp.sgit.ai/) define: for one agent deployment, what the agent **can** do (the grant), what it was **asked** to do (the mandate), the **delta** between the two, and the **barrier** that stands in the way of each prohibition. It covers one line, and it has two halves, as a prohibition does ("A prohibition has two lives", abp.sgit.ai): this page, the line in prose, which an agent reads and which on its own is an *expectation*; and [code-immutability.policy.json](https://github.com/SGit-AI/SGit-AI__Website__Storyboards__API/blob/dev/policies/code-immutability.policy.json), the same line compiled into the rules a hook and a gate apply, which makes it a control. `tests/test_policy.py` holds the two halves to each other.

## The label

| | |
|---|---|
| Behaviour policy | ABP-SB-001, code immutability, v1.0.0 |
| Applies to | any agent working on SGit-AI__Website__Storyboards__API or on SGit-AI__Website__Storyboards beside it |
| Shape | `anthropic/claude-code-remote/ccr-container`: a Claude Code session in a cloud container, both repositories cloned side by side, push access to both |
| The line | Code in a published release folder is never changed |
| Protected | every file under `vMAJOR/vMAJOR.MINOR/vMAJOR.MINOR.PATCH/` once that folder holds a `manifest.json` |
| Capabilities concerned | `write.file.project`, `write.repository.project` |
| Strongest barrier today | setting (hooks in the repository, the gate in CI) |
| As at | 20 October 2026, repository v0.2.0, release v0.1.0 |

## Why

From the brief: "every version is immutable. I think that's important", and, on 20 October 2026, "the code is immutable. So that's important. So the code, as soon as you have a code in the file path, that code could not be changed. So we need to have a rule for that. In fact, we need to have an agent behavior policy for that" ([the brief](../brief/2026-10-20__code-immutability-and-the-developer-site.html)).

The kit is served at a path that names its version so that a page which pins `/v0/v0.1/v0.1.0/` gets those bytes for as long as it exists, and can prove it with an `integrity` string. One edit in place breaks that promise for every page pinned to the folder, silently, and the browser then refuses the file, so the storyboards on those pages stop drawing. The newsroom's API learnt the same lesson the hard way: its rule R16, "a change is a new version path, always", was "written here because v1.4.0 was edited in place while it was being built".

## The grant, as it bears on this line

What the agent in this deployment can do, measured from the session's own tools, not from what it was told:

| Capability | Undo | How | Known by |
|---|---|---|---|
| `write.file.project`: change any file in either repository | with effort (git) | Edit, Write, MultiEdit, NotebookEdit; Bash (`rm`, `mv`, `sed -i`, redirects, scripts) | the session's tool list |
| `write.repository.project`: push to `dev`, the release branch, which deploys | with effort (a new commit; a published file is cached and pinned by others) | `git push` with the session's credentials | the session's git proxy |
| change its own controls: `.claude/settings.json`, the hook, the policy files, the workflows | with effort | the same file tools | the repository tree |

## The mandate, elicited

- **Want:** a fix, a feature or a major is a **new** release folder, cut from `src/` by `tools/release.py cut`; a new major starts as a byte copy of the last good release (`release.py major --from`); documentation, the website and the tooling change freely, as repository versions, without a release.
- **Do not want:** any change to a file in a published release folder: an edit, an overwrite, a rename, a move, a deletion, a new file added to it, a change of mode; not for a typo, not for a comment, not "before anyone has pinned it".
- **Unstated, decided here:** a folder is protected from the moment it holds a `manifest.json`, pushed or not. The moment a cut exists it may already be tested, pinned or rendered against, and the fix for a bad cut is the next patch, which costs nothing.

## The delta

The grant includes changing every file in the repository; the mandate refuses changing the published ones. That excess is the reason this behaviour policy exists, and each row below is a piece of it, with what stands in its way.

## The prohibitions, each with its barrier

| Row | The agent must not | Barrier today | Enforced today by | A stronger control would sit at |
|---|---|---|---|---|
| R1 | Edit, write or add a file in a published release folder with a file tool | setting | `.claude/hooks/code_immutability.py`, PreToolUse: **deny** | a managed hook the agent cannot write (`allowManagedHooksOnly`) |
| R2 | Write to, move or delete one with a shell command | setting | the same hook: the command's write targets (verb arguments, destinations, redirects, inline scripts) are resolved and checked; reading is allowed | a sandbox mounting release folders read-only |
| R3 | Commit a change to a release folder that exists in HEAD | setting | `.githooks/pre-commit` (enabled by the SessionStart hook); bypassed by `--no-verify` | a host rule |
| R4 | Push a change to a published release to `dev` | setting | CI: `release.py check` (every hash of every release) and "no published release changed against dev"; the deploy's `check` job, so a changed release is never deployed | branch protection on `dev` requiring the `ci` check (a host rule, outside the agent's grant): a **boundary** |
| R5 | Weaken its own controls (the hook, `.claude/settings.json`, the policy files, `.githooks/`, `tools/release.py`, the workflows) without the person | setting | the hook: **ask**, so the person sees the change and decides (riskmandate.ai RM-R0015) | CODEOWNERS and a required review on those paths |
| R6 | Serve other bytes at a published path | detection | `tools/live_check.py` after every deploy compares every live file of every release with its manifest | |
| R7 | Stop and ask if a task seems to need any of the above | expectation | this page, and the instructions the SessionStart hook prints | |

No row is a boundary yet: every control above lives in a file this agent's grant can write, and the hooks and gate say so rather than claim more. The one step that turns R4 into a boundary is a GitHub setting only a person can make: protect `dev`, require the `ci` check to pass before a push lands. It is recorded as open in the repository's REALITY.md.

## The compiled half

`policies/code-immutability.policy.json` is the data both hooks read at run time, so the hooks and this page cannot drift apart:

| Field | What it holds |
|---|---|
| `protected.folder_regex`, `protected.marker` | what a published release folder is: the path shape, and `manifest.json` inside it |
| `tools.file_writers`, `tools.shell` | the tools the hook checks |
| `shell.verbs_all_args`, `shell.verbs_destination`, `shell.redirects`, `shell.script_writes_regex` | how a shell command's write targets are found |
| `self.paths_in_api_repo`, `self.paths_in_any_repo`, `self.decision` | the files of this behaviour policy, and that touching them asks |
| `allowed_commands` | `release.py cut`, `check` and `site`, which create a new folder or only read |
| `instructions` | the words the agent is given at session start and with every refusal |

Wiring: in this repository, `.claude/settings.json` runs the hook on `SessionStart` (it prints the instructions and enables `.githooks/`) and on `PreToolUse` for `Edit|Write|MultiEdit|NotebookEdit|Bash`. In SGit-AI__Website__Storyboards, the same entries run this repository's hook from the checkout beside it, so a session started there is refused the same way; when the API checkout is absent there is nothing to protect and the hook does nothing.

The fixtures: `tests/test_policy.py` drives the hook with tool calls shaped as Claude Code sends them and drives the git hook with real commits in a throwaway clone. Every refusal has an allowed twin (reading a release, editing `src/`, cutting a new folder, editing the website), so a hook that refused everything would fail the tests as surely as one that refused nothing. It runs in CI on every commit, and its count of cases is printed by the test rather than written here.

## What to do instead

Code in a published release folder (vX/vX.Y/vX.Y.Z/) is immutable: never edit, move, rename, overwrite or delete a file there, for any reason, including a typo or a comment. To change the kit: python3 tools/release.py bump patch (or minor), edit src/, python3 tools/release.py cut, then add the line to site/data/versions.json and rebuild. A new major starts from the last good release: python3 tools/release.py major --from vX.Y.Z. If you believe a published file must change (a leaked secret, a legal takedown), stop and ask the person; only a person may do it, outside the agent, and it is recorded in BRIEF-CORRECTIONS.md.

The commands are on [the release process](../engineering/release-process.html).

## Provenance

Written by the storyboards agent on 20 October 2026 from Dinis Cruz's words (the brief linked above), in the vocabulary of riskmandate.ai's Agent Behaviour Policy and abp.sgit.ai (mandate, grant, delta, barrier; none, expectation, setting, boundary), with the barrier ladder from pki.sgit.ai's enforcement briefs and the newsroom's "Are hooks the sweet spot": "A hook in a file the agent can write is a setting the agent keeps". riskmandate.ai's catalogue had no immutability rule when this was written; this is offered to it.

## What this is not, and validity

It is not a score or a rating, and it does not judge the agent. It is not a claim that the hooks cannot be bypassed: a PreToolUse hook fails open if it errors or times out, a git hook is skipped with `--no-verify`, and the agent can edit both (R5 makes that visible, not impossible). It describes this deployment as at 20 October 2026; if the deployment changes (another agent product, managed hooks, branch protection on `dev`), this behaviour policy is re-measured and its version moves, and this page is not edited to look as if it had always been so.
