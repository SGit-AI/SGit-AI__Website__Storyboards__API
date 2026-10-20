#!/usr/bin/env python3
"""Claude Code hook for ABP-SB-001, code immutability (policies/code-immutability.md).

    PreToolUse   denies any Edit, Write, MultiEdit or NotebookEdit of a file in a published release folder, and any Bash
                 command whose writes, moves or deletes land in one (reading is always allowed); asks the person before
                 any write to the files that make up this behaviour policy and its enforcement
    SessionStart prints the policy's instructions, so the agent starts the session knowing the rule

A published release folder is vX/vX.Y/vX.Y.Z/ holding a manifest.json, in any repository on this machine: the check
works on absolute paths, so a session in storyboards.sgit.ai cannot edit the API checkout beside it either. The rules
are data, policies/code-immutability.policy.json; this file only applies them. Standard library only.
"""
import json
import re
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY_FILE = HERE.parents[1] / "policies/code-immutability.policy.json"


def load_policy():
    for p in (POLICY_FILE, Path.cwd() / "policies/code-immutability.policy.json"):
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    raise SystemExit("code_immutability: policies/code-immutability.policy.json not found")


def protected_folder(path, policy, cwd):
    """The published release folder a path is in, or None. Relative paths resolve against the session's cwd."""
    p = Path(path)
    if not p.is_absolute():
        p = Path(cwd) / p
    p = Path(str(p.resolve(strict=False)))
    m = re.search(policy["protected"]["folder_regex"], p.as_posix())
    if not m:
        return None
    folder = Path(p.as_posix()[: m.end(1)])
    return folder if (folder / policy["protected"]["marker"]).exists() else None


def _folder_for(word, policy, cwd):
    """The protected folder a word names: a path inside a release, or a whole major or minor folder that holds releases."""
    f = protected_folder(word, policy, cwd) if re.search(r"v\d+", word) else None
    if f is None and re.search(r"(?:^|/)v\d+(?:/v\d+\.\d+)?/?\*?$", word):
        root = (Path(cwd) / word.rstrip("*").rstrip("/")).resolve()
        if root.is_dir() and any(root.rglob(policy["protected"]["marker"])):
            f = root
    return f


def shell_targets(command, policy):
    """Every word a shell command would write to, move or delete: arguments of verbs that change every path they name,
    the destination of verbs that write only their last path, redirect targets, and paths named in an inline script that
    writes. Reading is never a target."""
    if any(command.strip() == a or command.strip().startswith(a + " ") for a in policy["allowed_commands"]):
        return []
    sh = policy["shell"]
    lex = shlex.shlex(command, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    try:
        tokens = list(lex)
    except ValueError:
        tokens = command.split()
    segments, cur = [], []
    for t in tokens:
        if t in (";", "&&", "||", "|", "&", "(", ")"):
            segments.append(cur); cur = []
        else:
            cur.append(t)
    segments.append(cur)
    targets = []
    for seg in segments:
        words = [w for w in seg if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", w)]
        while words and words[0] in ("sudo", "env", "command", "time", "nohup", "xargs"):
            words = words[1:]
        if not words:
            continue
        # redirects: the word after > or >> is written
        for i, w in enumerate(words):
            if w in sh["redirects"] and i + 1 < len(words):
                targets.append(words[i + 1])
        args = [w for i, w in enumerate(words) if w not in sh["redirects"] and not (i and words[i - 1] in sh["redirects"])]
        verb = Path(args[0]).name if args else ""
        two = f"{verb} {args[1]}" if len(args) > 1 else verb
        inplace = any(a == "-i" or a.startswith("-i") for a in args[1:])
        if two in sh["verbs_all_args"] or verb in sh["verbs_all_args"] or (f"{verb} -i" in sh["verbs_all_args"] and inplace):
            targets += [a for a in args[1:] if not a.startswith("-")]
        elif verb in sh["verbs_destination"]:
            paths = [a for a in args[1:] if not a.startswith("-")]
            if verb == "dd":
                targets += [a[3:] for a in paths if a.startswith("of=")]
            elif paths:
                targets.append(paths[-1])
        elif re.search(sh["script_writes_regex"], " ".join(args)):
            # an inline script that writes files: any protected path it names is a target
            targets += [x for a in args for x in re.findall(r"[^\s'\"()]+", a)]
    return [c for t in targets for c in re.split(r"[=:,]", t) if c]


def shell_hits(command, policy, cwd):
    """The published release folders a shell command would write to, move or delete."""
    hits = []
    for cand in shell_targets(command, policy):
        f = _folder_for(cand, policy, cwd)
        if f is not None and f not in hits:
            hits.append(f)
    return hits


def project_root(cwd):
    """The repository the session is working in: the nearest folder above cwd with a .git."""
    p = Path(cwd).resolve()
    for d in [p, *p.parents]:
        if (d / ".git").exists():
            return d
    return p


def self_file(path, policy, cwd):
    """The policy's own file a path is, or None: this repository's enforcement files, or any repository's .claude/settings.json."""
    p = Path(path)
    p = (Path(cwd) / p if not p.is_absolute() else p).resolve(strict=False)
    api = HERE.parents[1]
    names = [api / x for x in policy["self"]["paths_in_api_repo"]] + [project_root(cwd) / x for x in policy["self"]["paths_in_any_repo"]]
    return p if any(p == n.resolve(strict=False) for n in names) else None


def ask(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": reason}}))
    sys.exit(0)


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))
    sys.exit(0)


def main():
    policy = load_policy()
    event = json.load(sys.stdin)
    name = event.get("hook_event_name", "PreToolUse")
    if name == "SessionStart":
        print(f"[{policy['id']} {policy['name']} {policy['version']}] {policy['instructions']}")
        return
    tool, inp, cwd = event.get("tool_name", ""), event.get("tool_input", {}) or {}, event.get("cwd") or str(Path.cwd())
    rule = f"{policy['id']} ({policy['name']}): "
    guard = "This file is part of the behaviour policy that keeps published code immutable; an agent does not change its own controls without the person (riskmandate.ai RM-R0015). Ask them, and say why."
    if tool in policy["tools"]["file_writers"]:
        path = inp.get("file_path") or inp.get("notebook_path") or ""
        f = protected_folder(path, policy, cwd) if path else None
        if f:
            deny(rule + f"{path} is in the published release folder {f}, which is immutable. " + policy["instructions"])
        if path and self_file(path, policy, cwd):
            ask(rule + f"{path}: " + guard)
    elif tool in policy["tools"]["shell"]:
        command = inp.get("command", "")
        hits = shell_hits(command, policy, cwd)
        if hits:
            deny(rule + "this command would write to, move or delete the published release folder(s) " + ", ".join(map(str, hits)) + ". " + policy["instructions"])
        own = [t for t in shell_targets(command, policy) if self_file(t, policy, cwd)]
        if own:
            ask(rule + ", ".join(own) + ": " + guard)
    # anything else: no decision, the normal permission flow applies


if __name__ == "__main__":
    main()
