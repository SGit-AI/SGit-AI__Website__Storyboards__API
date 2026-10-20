#!/usr/bin/env python3
"""ABP-SB-001, code immutability, against the hooks that enforce it: the Claude Code hook given real tool calls as Claude
Code sends them (JSON on stdin), and the git pre-commit hook given real commits in a throwaway clone. Every refusal has
an allowed twin, so a hook that refused everything would fail as surely as one that refused nothing.

    python3 tests/test_policy.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude/hooks/code_immutability.py"
REL = "v0/v0.1/v0.1.0"
SIBLING = ROOT.parent / "SGit-AI__Website__Storyboards"
n = 0


def decide(tool, tool_input, cwd=ROOT):
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input, "cwd": str(cwd)}),
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"] if r.stdout.strip() else "allow"


def case(expect, tool, tool_input, cwd=ROOT):
    global n
    got = decide(tool, tool_input, cwd)
    shown = tool_input.get("command") or tool_input.get("file_path")
    assert got == expect, f"{tool} {shown!r}: expected {expect}, got {got}"
    n += 1
    print(f"ok {expect:5} {tool:6} {shown}")


# file tools
case("deny", "Edit", {"file_path": f"{ROOT}/{REL}/storyboard.js", "old_string": "a", "new_string": "b"})
case("deny", "Write", {"file_path": f"{REL}/manifest.json", "content": "{}"})
case("deny", "Write", {"file_path": f"{REL}/new-file.js", "content": "x"})          # adding to a published folder is changing it
case("deny", "MultiEdit", {"file_path": f"{ROOT}/{REL}/fonts.css", "edits": []})
case("allow", "Edit", {"file_path": f"{ROOT}/src/storyboard.js", "old_string": "a", "new_string": "b"})
case("allow", "Write", {"file_path": f"{ROOT}/v0/v0.1/v0.1.9/storyboard.js", "content": "x"})  # no manifest: not a published release
case("allow", "Write", {"file_path": f"{ROOT}/site/pages/docs/v0.1.0-notes.md", "content": "x"})
# shell: writes, moves and deletes
for cmd in [f"rm -rf {REL}", "rm -rf v0", "rm -rf ./v0/v0.1", f"sed -i 's/a/b/' {REL}/embed.js", f"echo x > {REL}/storyboard.js",
            f"echo x >> {REL}/notes.txt", f"mv {REL} v0/v0.1/old", f"cp src/storyboard.js {REL}/storyboard.js", f"touch {REL}/x",
            f"git checkout -- {REL}/storyboard.js", f"git rm -r {REL}", f"cat src/a.js | tee {REL}/a.js",
            f"python3 -c \"open('{REL}/a.js','w').write('x')\"", f"node -e \"require('fs').writeFileSync('{REL}/a.js','x')\"",
            f"cd /tmp && rm -rf {ROOT}/{REL}", f"chmod 644 {REL}/storyboard.js", f"rsync -a src/ {REL}/"]:
    case("deny", "Bash", {"command": cmd})
# shell: reading is never refused
for cmd in [f"cat {REL}/storyboard.js", f"sha256sum {REL}/*", f"diff -r {REL} src", f"grep -n VERSION {REL}/storyboard.js > /tmp/out.txt",
            f"cp {REL}/storyboard.js /tmp/copy.js", "python3 tools/release.py cut", "python3 tools/release.py check", f"ls -la {REL}",
            f"node --check {REL}/storyboard.js", f"git diff dev -- {REL}", "rm -rf www/docs", "sed -i 's/a/b/' src/embed.js"]:
    case("allow", "Bash", {"command": cmd})
# from the twin repository: absolute and relative paths into this checkout are refused the same way
if SIBLING.exists():
    case("deny", "Edit", {"file_path": f"{ROOT}/{REL}/storyboard.js", "old_string": "a", "new_string": "b"}, cwd=SIBLING)
    case("deny", "Bash", {"command": f"rm -rf ../{ROOT.name}/{REL}"}, cwd=SIBLING)
    case("allow", "Bash", {"command": f"cat ../{ROOT.name}/{REL}/manifest.json"}, cwd=SIBLING)

# the policy's own files: the agent asks the person
case("ask", "Edit", {"file_path": f"{ROOT}/.claude/hooks/code_immutability.py", "old_string": "a", "new_string": "b"})
case("ask", "Write", {"file_path": "policies/code-immutability.policy.json", "content": "{}"})
case("ask", "Edit", {"file_path": f"{ROOT}/tools/release.py", "old_string": "a", "new_string": "b"})
case("ask", "Bash", {"command": "sed -i 's/deny/allow/' .claude/hooks/code_immutability.py"})
case("ask", "Bash", {"command": "echo '{}' > .claude/settings.json"})
case("allow", "Bash", {"command": "cat .claude/hooks/code_immutability.py policies/code-immutability.policy.json"})
case("allow", "Edit", {"file_path": f"{ROOT}/site/pages/docs/format.md", "old_string": "a", "new_string": "b"})
if SIBLING.exists():
    case("ask", "Write", {"file_path": f"{SIBLING}/.claude/settings.json", "content": "{}"}, cwd=SIBLING)

# the session-start instructions
out = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"hook_event_name": "SessionStart"}), capture_output=True, text=True, check=True).stdout
assert "ABP-SB-001" in out and "immutable" in out and "release.py bump patch" in out, out
n += 1
print("ok SessionStart prints the instructions")

# the git pre-commit hook, in a throwaway clone
with tempfile.TemporaryDirectory() as tmp:
    clone = Path(tmp) / "c"
    subprocess.run(["git", "clone", "-q", "--no-local", str(ROOT), str(clone)], check=True)
    for sub in ("policies", ".githooks"):  # the hooks as they are in this tree, committed or not
        shutil.copytree(ROOT / sub, clone / sub, dirs_exist_ok=True)
    git = lambda *a, ok=True: subprocess.run(["git", "-C", str(clone), "-c", "user.name=t", "-c", "user.email=t@example.org", *a], capture_output=True, text=True, check=False)
    git("add", "-A"); git("commit", "-q", "-m", "hooks")
    git("config", "core.hooksPath", ".githooks")
    (clone / REL / "storyboard.js").write_text("// changed\n")
    git("add", "-A")
    r = git("commit", "-q", "-m", "edit a release")
    assert r.returncode != 0 and "ABP-SB-001" in r.stderr, r.stderr
    n += 1
    print("ok pre-commit refuses a commit that edits a published release")
    git("reset", "-q", "--hard")
    (clone / "src/storyboard.js").write_text((clone / "src/storyboard.js").read_text() + "\n")
    (clone / "v0/v0.1/v0.1.9").mkdir(parents=True)
    (clone / "v0/v0.1/v0.1.9/manifest.json").write_text("{}")
    git("add", "-A")
    r = git("commit", "-q", "-m", "edit src and add a new release")
    assert r.returncode == 0, r.stderr
    n += 1
    print("ok pre-commit allows editing src/ and adding a new release folder")
    git("rm", "-rq", REL)
    r = git("commit", "-q", "-m", "delete a release")
    assert r.returncode != 0 and "ABP-SB-001" in r.stderr, r.stderr
    n += 1
    print("ok pre-commit refuses deleting a published release")

# the two halves of the behaviour policy name the same thing
sys.path.insert(0, str(ROOT / "site"))
from md import front_matter  # noqa: E402
policy = json.loads((ROOT / "policies/code-immutability.policy.json").read_text(encoding="utf-8"))
meta, prose = front_matter((ROOT / "policies/code-immutability.md").read_text(encoding="utf-8"))
assert meta["id"] == policy["id"] and meta["version"] == policy["version"], (meta, policy["id"], policy["version"])
assert "{{INSTRUCTIONS}}" in prose, "the prose half must show the compiled half's instructions, not a copy of them"
for f in policy["self"]["paths_in_api_repo"]:
    assert (ROOT / f).exists(), f"the policy names {f}, which does not exist"
n += 1
print("ok the prose and the compiled halves agree (id, version, instructions, the files they name)")

print(f"test_policy: {n} passed")
