#!/usr/bin/env python3
"""Releases of the storyboard kit: every version is a folder, and a folder is never changed once it is published.

    python3 tools/release.py cut                  # src/ -> v<M>/v<M>.<m>/v<M>.<m>.<p>/ with manifest.json (refuses an existing one)
    python3 tools/release.py cut --out DIR        # the same into DIR (the reproducible-build check cuts twice and compares)
    python3 tools/release.py check                # every release matches its manifest; src/ is the current release
    python3 tools/release.py bump patch|minor     # the next release number, written into tools/version.json and src/
    python3 tools/release.py major [--from vX.Y.Z]  # start the next major from the last good release, byte for byte
    python3 tools/release.py site --out DIR       # the Pages site: www/ + every v*/ folder + releases.json + CNAME

The rule (the brief, 20 October 2026): the file path is the version. A consumer pins the exact path,
https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/storyboard.js, and gets those bytes for ever; the manifest beside them
carries each file's SHA-256 and the SRI string to put in an integrity attribute. There are no floating aliases
("latest", "v0.1/"): a page that wants the new version changes one line, on purpose. `releases.json` at the root lists
every version, newest first, so a tool can find the newest without a mutable path.

Every change to a served file is a new patch or minor version, cut into its own folder. A new major starts as a copy of
the last good release (`major --from`), so v1.0.0 is v0.x.y with only the changes that made it a major, and the history
of what changed is the diff between two folders that both still exist.

tools/version.json: "version" is the repository's version, bumped on every push (docs-only changes too); "release" is
the newest cut of src/, which is never ahead of "version". Dates come from the file, never the clock, so a cut is the
same bytes twice.
"""
import argparse
import base64
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
HOST = "https://api.storyboards.sgit.ai"
VERSION_FILE = ROOT / "tools/version.json"
PROVENANCE = json.loads((ROOT / "tools/provenance.json").read_text(encoding="utf-8"))
# the files that carry their own version string: VERSION = 'vX.Y.Z' or VERSION: 'vX.Y.Z'
VERSIONED = ["storyboard.js", "formats.js", "export.js", "embed.js"]
VERSION_RE = re.compile(r"(VERSION\s*[:=]\s*')(v\d+\.\d+\.\d+)(')")


def load_version():
    return json.loads(VERSION_FILE.read_text(encoding="utf-8"))


def vtuple(v):
    m = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", v or "")
    if not m:
        sys.exit(f"release: {v!r} is not a version of the form vX.Y.Z")
    return tuple(int(x) for x in m.groups())


def vstr(t):
    return "v%d.%d.%d" % t


def folder(v):
    """'v0.1.3' -> 'v0/v0.1/v0.1.3': the published path of a release."""
    M, m, _ = vtuple(v)
    return f"v{M}/v{M}.{m}/{v}"


def releases():
    """Every published release in the tree, newest first."""
    found = []
    for d in ROOT.glob("v*/v*.*/v*.*.*"):
        if d.is_dir() and re.fullmatch(r"v\d+\.\d+\.\d+", d.name) and folder(d.name) == d.relative_to(ROOT).as_posix():
            found.append(d.name)
    return sorted(found, key=vtuple, reverse=True)


def served(root):
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and p.name != "manifest.json")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def sri(data):
    return "sha384-" + base64.b64encode(hashlib.sha384(data).digest()).decode()


def manifest_for(root, v, date):
    files = []
    for rel in served(root):
        data = (root / rel).read_bytes()
        entry = {"path": rel, "bytes": len(data), "sha256": sha256(data), "integrity": sri(data)}
        if rel in PROVENANCE["files"]:
            entry["origin"] = PROVENANCE["files"][rel]
        files.append(entry)
    return {
        "what": f"A release of the storyboard kit, served at {HOST}/{folder(v)}/<path>. Immutable: these bytes never change at this "
                "path. Put a file's 'integrity' in the integrity attribute of the tag that loads it, with crossorigin=\"anonymous\".",
        "release": v,
        "date": date,
        "base": f"{HOST}/{folder(v)}/",
        "counts": {"files": len(files), "bytes": sum(f["bytes"] for f in files)},
        "files": files,
    }


def version_strings(root):
    """{file: version} for every file that names its own version."""
    out = {}
    for name in VERSIONED:
        m = VERSION_RE.findall((root / name).read_text(encoding="utf-8")) if (root / name).exists() else []
        out[name] = sorted({x[1] for x in m})
    return out


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ commands
def cmd_cut(args):
    V = load_version()
    v = V["release"]
    bad = {f: s for f, s in version_strings(SRC).items() if s != [v]}
    if bad:
        sys.exit(f"release: src/ files name another version than {v}: {bad} (python3 tools/release.py bump ...)")
    out = Path(args.out) / folder(v) if args.out else ROOT / folder(v)
    if out.exists() and not args.out:
        sys.exit(f"release: {folder(v)}/ already exists and a published release is never changed; bump to the next version first")
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(SRC, out)
    write_json(out / "manifest.json", manifest_for(out, v, V["date"]))
    print(f"release: cut {v} into {out.relative_to(args.out) if args.out else out.relative_to(ROOT)} ({len(served(out))} files)")


def cmd_check(args):
    V = load_version()
    errors = []
    if vtuple(V["release"]) > vtuple(V["version"]):
        errors.append(f"tools/version.json: release {V['release']} is ahead of version {V['version']}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", V.get("date", "")):
        errors.append("tools/version.json: date is not YYYY-MM-DD")
    rel = releases()
    if V["release"] not in rel:
        errors.append(f"release {V['release']} is named in tools/version.json but {folder(V['release'])}/ does not exist: cut it")
    for v in rel:
        d = ROOT / folder(v)
        mf = d / "manifest.json"
        if not mf.exists():
            errors.append(f"{folder(v)}: no manifest.json")
            continue
        m = json.loads(mf.read_text(encoding="utf-8"))
        listed = {f["path"]: f for f in m["files"]}
        on_disk = set(served(d))
        for extra in sorted(on_disk - set(listed)):
            errors.append(f"{folder(v)}/{extra}: on disk, not in the manifest (a published release is never changed)")
        for path, f in listed.items():
            p = d / path
            if not p.exists():
                errors.append(f"{folder(v)}/{path}: in the manifest, missing on disk")
                continue
            data = p.read_bytes()
            if sha256(data) != f["sha256"] or sri(data) != f["integrity"] or len(data) != f["bytes"]:
                errors.append(f"{folder(v)}/{path}: the bytes are not the bytes in the manifest (a published release is never changed)")
        if m.get("release") != v:
            errors.append(f"{folder(v)}/manifest.json names release {m.get('release')}")
    # the working tree is the current release, or the version has moved on and the next cut is due
    if V["release"] in rel:
        cur = ROOT / folder(V["release"])
        if served(cur) != served(SRC) or any((cur / f).read_bytes() != (SRC / f).read_bytes() for f in served(SRC)):
            changed = [f for f in sorted(set(served(SRC)) | set(served(cur)))
                       if not (cur / f).exists() or not (SRC / f).exists() or (cur / f).read_bytes() != (SRC / f).read_bytes()]
            errors.append(f"src/ differs from the published {V['release']} ({', '.join(changed[:6])}): "
                          f"bump (tools/release.py bump patch) and cut a new release; {folder(V['release'])}/ stays as it is")
    if errors:
        print("\n".join("release check: " + e for e in errors))
        sys.exit(1)
    print(f"release check: {len(rel)} release(s) match their manifests ({', '.join(rel)}); src/ is {V['release']}")


def set_version_strings(v):
    for name in VERSIONED:
        p = SRC / name
        p.write_text(VERSION_RE.sub(lambda m: m.group(1) + v + m.group(3), p.read_text(encoding="utf-8")), encoding="utf-8")


def cmd_bump(args):
    V = load_version()
    M, m, p = vtuple(V["release"])
    nxt = (M, m, p + 1) if args.part == "patch" else (M, m + 1, 0)
    v = vstr(nxt)
    V["release"] = v
    if vtuple(V["version"]) < nxt:
        V["version"] = v
    if args.date:
        V["date"] = args.date
    write_json(VERSION_FILE, V)
    set_version_strings(v)
    print(f"release: src/ is now {v}; edit, then: python3 tools/release.py cut")


def cmd_major(args):
    V = load_version()
    rel = releases()
    base = args.base or rel[0]
    if base not in rel:
        sys.exit(f"release: {base} is not a published release ({', '.join(rel)})")
    v = vstr((vtuple(base)[0] + 1, 0, 0))
    if v in rel:
        sys.exit(f"release: {v} already exists")
    shutil.rmtree(SRC)
    shutil.copytree(ROOT / folder(base), SRC)
    (SRC / "manifest.json").unlink()
    V["release"] = v
    if vtuple(V["version"]) < vtuple(v):
        V["version"] = v
    if args.date:
        V["date"] = args.date
    write_json(VERSION_FILE, V)
    set_version_strings(v)
    print(f"release: src/ is {base}, byte for byte, renamed {v}; make only the changes that make it a major, then cut")


def cmd_site(args):
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(ROOT / "www", out)
    rel = releases()
    for v in rel:
        shutil.copytree(ROOT / folder(v), out / folder(v))
    V = load_version()
    index = {"what": "Every release of the storyboard kit, newest first. Each path is immutable.", "host": HOST,
             "version": V["version"], "newest": rel[0],
             "releases": [{"release": v, "path": folder(v) + "/", "manifest": f"{folder(v)}/manifest.json",
                           "date": json.loads((ROOT / folder(v) / "manifest.json").read_text(encoding="utf-8"))["date"]} for v in rel]}
    write_json(out / "releases.json", index)
    shutil.copy(ROOT / "CNAME", out / "CNAME")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"release: site in {out}: www/ + {len(rel)} release(s)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cut"); c.add_argument("--out")
    sub.add_parser("check")
    b = sub.add_parser("bump"); b.add_argument("part", choices=["patch", "minor"]); b.add_argument("--date")
    mj = sub.add_parser("major"); mj.add_argument("--from", dest="base"); mj.add_argument("--date")
    s = sub.add_parser("site"); s.add_argument("--out", required=True)
    args = ap.parse_args()
    {"cut": cmd_cut, "check": cmd_check, "bump": cmd_bump, "major": cmd_major, "site": cmd_site}[args.cmd](args)


if __name__ == "__main__":
    main()
