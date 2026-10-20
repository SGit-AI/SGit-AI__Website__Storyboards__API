#!/usr/bin/env python3
"""Builds the api.storyboards.sgit.ai website into www/ (committed; CI checks it is what this writes). The release folders
are not part of www/: tools/release.py site puts them beside it when GitHub Pages is assembled.

    python3 site/build.py           # write www/
    python3 site/build.py --check   # fail if www/ is not what this writes

Pages are markdown with front matter in site/pages/ (each page's .md twin is its source, with the placeholders filled);
the releases page is generated from every release's manifest, the version history from site/data/versions.json, the
brief from briefs/. Placeholders: {{RELEASE}}, {{BASE}}, {{REPO}}, {{FILES}} (the current release's files and hashes),
{{VOCAB}} (the renderer's vocabulary, read from the release's own formats.js), {{SRI_EXAMPLE}}, {{DEMO}} (a live embed).
"""
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))
from md import front_matter, render as md_render  # noqa: E402
import release as R  # noqa: E402

HOST = "api.storyboards.sgit.ai"
SITE = f"https://{HOST}"
REPO = "https://github.com/SGit-AI/SGit-AI__Website__Storyboards__API"
OUT = ROOT / "www"
esc = lambda s: html.escape(str(s if s is not None else ""), quote=True)
NAV = [("Docs", "docs/index.html"), ("Quick start", "docs/quick-start.html"), ("Format", "docs/format.html"), ("JavaScript", "docs/javascript.html"),
       ("Versioning", "docs/versioning.html"), ("Releases", "releases/index.html"), ("The brief", "brief/index.html")]


def die(m):
    sys.exit(f"site/build: {m}")


def page(rel, title, body, desc, version, release, twin):
    up = "../" * rel.count("/")
    canon = f"{SITE}/{rel}".removesuffix("index.html")
    nav = "".join(f'<a href="{up}{h}">{l}</a>' for l, h in NAV)
    base = f"{up}{R.folder(release)}/"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · api.storyboards.sgit.ai</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canon)}">
<link rel="alternate" type="text/markdown" href="{esc(twin)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canon)}">
<meta name="site-version" content="{version}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect x='4' y='10' width='56' height='44' rx='6' fill='%23fbf7ee' stroke='%2323262b' stroke-width='4'/%3E%3Ctext x='32' y='42' font-size='22' text-anchor='middle' font-family='monospace' fill='%230f766e'%3E%7B%7D%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="{base}fonts.css">
<link rel="stylesheet" href="{base}storyboard.css">
<link rel="stylesheet" href="{up}assets/site.css">
<script>window.StoryboardPrefsKey = 'api.storyboards.sgit.ai.v1';</script>
<script src="{up}assets/site.js"></script>
</head>
<body>
<a class="skip" href="#main">Skip to the content</a>
<nav class="site" aria-label="Site"><div class="row">
<a class="brand" href="{up}index.html">api.storyboards<span>.sgit.ai</span></a>
<div class="nav-items">{nav}</div>
<div class="nav-tools"><a class="parent" href="https://sgit.ai" title="One of the sgit.ai network of sites">&#8599; part of <b>sgit.ai</b></a>
<a class="parent" href="https://storyboards.sgit.ai/" title="Where the storyboards live">&#8599; storyboards</a>
<button type="button" class="theme" aria-label="Switch the theme">dark</button>
<span class="ver">site <a href="{up}versions/index.html" title="Release history of this repository">{version}</a> &middot; kit <a href="{up}{R.folder(release)}/manifest.json">{release}</a></span></div>
</div></nav>
<main id="main" class="narrow">
{body}
</main>
<footer class="site"><div class="row">
<div><b>api.storyboards.sgit.ai</b>: the storyboard kit, in immutable versioned folders. Code Apache-2.0; Rough.js MIT; fonts SIL OFL 1.1.</div>
<div class="netline"><a href="https://storyboards.sgit.ai/">&#8599; storyboards.sgit.ai</a>, where the storyboards live &middot; <a href="https://sgit.ai">&#8599; sgit.ai</a> &middot; <a href="https://api.newsroom.sgit.ai/">&#8599; api.newsroom.sgit.ai</a>, the first API site &middot; <a href="https://sgit.ai/network/index.html">&#8599; the network</a></div>
<div>&#9888; Participant disclosure: published by the sgit project. <a href="{up}about/participant.html">Read the disclosure</a>.</div>
<div>Site {version} &middot; kit {release} &middot; <a href="{up}versions/index.html">version history</a> &middot; <a href="{esc(twin)}">this page as markdown</a> &middot; <a href="{up}llms.txt">llms.txt</a> &middot; <a href="{up}releases.json">releases.json</a> &middot; <a href="{REPO}">GitHub</a></div>
</div></footer>
</body>
</html>
"""


def build(out):
    V = R.load_version()
    version, release = V["version"], V["release"]
    rels = R.releases()
    if release not in rels:
        die(f"the current release {release} has not been cut")
    base = f"{SITE}/{R.folder(release)}/"
    man = json.loads((ROOT / R.folder(release) / "manifest.json").read_text(encoding="utf-8"))
    hist = json.loads((HERE / "data/versions.json").read_text(encoding="utf-8"))["versions"]
    if hist[0]["version"] != version:
        die(f"site/data/versions.json starts at {hist[0]['version']}; tools/version.json says {version}: add the line for {version}")
    vocab = json.loads(subprocess.check_output(["node", "-e", "const F=require(process.argv[1]);process.stdout.write(JSON.stringify({V:F.VOCAB,P:F.PACKS}))",
                                                str(ROOT / R.folder(release) / "formats.js")]))
    files_md = "| File | Bytes | SHA-256 | Integrity |\n|---|---|---|---|\n" + "\n".join(
        f"| [{f['path']}]({base}{f['path']}) | {f['bytes']:,} | `{f['sha256'][:16]}…` | `{f['integrity'][:22]}…` |" for f in man["files"])
    vocab_md = "| | |\n|---|---|\n" + "\n".join(f"| {k} | {', '.join(f'`{x}`' for x in v)} |" for k, v in vocab["V"].items()) + \
        "\n" + "\n".join(f"| props, `{p}` pack | {', '.join(f'`{x}`' for x in v)} |" for p, v in vocab["P"].items())
    sri = "\n".join((f'<link rel="stylesheet" href="{base}{p}" integrity="{man_i}" crossorigin="anonymous">' if p.endswith(".css")
                     else f'<script src="{base}{p}" integrity="{man_i}" crossorigin="anonymous"></script>')
                    for p in ["fonts.css", "storyboard.css", "vendor/rough-4.6.6.js", "props/security.js", "storyboard.js", "export.js"]
                    for man_i in [next(f["integrity"] for f in man["files"] if f["path"] == p)])
    demo = (f'<div class="hero-panel" style="max-width:720px"><sg-storyboard src="demo/pki.bundle.json" view="panel" panel="4"></sg-storyboard></div>'
            f'<script src="{R.folder(release)}/embed.js" defer></script><p class="small dim">Above: panel 4 of pki.sgit.ai\'s <i>The first key</i>, drawn now, by this release, from '
            f'<a href="demo/pki.bundle.json">a bundle</a>. Click it to play.</p>')
    files = {}

    def fill(t):
        return (t.replace("{{RELEASE}}", release).replace("{{BASE}}", base).replace("{{REPO}}", REPO).replace("{{FILES}}", files_md)
                .replace("{{VOCAB}}", vocab_md).replace("{{SRI_EXAMPLE}}", sri))

    def put(rel, data):
        files[rel] = data.encode("utf-8") if isinstance(data, str) else data

    def emit(rel, title, desc, body_md, raw_html=None):
        twin = Path(rel).with_suffix(".md").name
        body_html = raw_html if raw_html is not None else md_render(body_md)
        body_html = body_html.replace("<p>{{DEMO}}</p>", demo)
        body = f'<article class="article"><h1>{esc(title)}</h1><p class="lede">{esc(desc)}</p>{body_html}</article>'
        put(rel, page(rel, title, body, desc, version, release, twin))
        put(str(Path(rel).with_suffix(".md")), f"# {title}\n\n> {desc}\n\n*Source: <{SITE}/{rel}>.*\n\n---\n\n" + body_md.replace("{{DEMO}}", "").strip() + "\n")

    for f in sorted((HERE / "pages").rglob("*.md")):
        m, body_md = front_matter(f.read_text(encoding="utf-8"))
        emit(f.relative_to(HERE / "pages").with_suffix(".html").as_posix(), fill(m["title"]), fill(m.get("summary", "")), fill(body_md))

    # every release, every file
    rmd = ["Every release of the kit, newest first. Each folder is immutable; each manifest names every file's hash.", ""]
    for v in rels:
        mv = json.loads((ROOT / R.folder(v) / "manifest.json").read_text(encoding="utf-8"))
        b = f"{SITE}/{R.folder(v)}/"
        rmd += [f"## {v}", "", f"Released {mv['date']}, at `{b}`: {mv['counts']['files']} files, {mv['counts']['bytes']:,} bytes. [manifest.json]({b}manifest.json).", "",
                "| File | Bytes | SHA-256 | Where it came from |", "|---|---|---|---|"]
        rmd += [f"| [{f['path']}]({b}{f['path']}) | {f['bytes']:,} | `{f['sha256']}` | {f.get('origin', 'written here')} |" for f in mv["files"]] + [""]
    emit("releases/index.html", "Releases", "Every release of the kit, every file, every hash.", "\n".join(rmd))
    vmd = "| Version | Date | Kit | What changed, and why |\n|---|---|---|---|\n" + "\n".join(f"| {h['version']} | {h['date']} | {h['release']} | {h['what']} |" for h in hist)
    emit("versions/index.html", "Version history", "One line per push to dev: the repository's version, the kit release it serves, and what changed.", vmd)
    briefs = sorted((ROOT / "briefs").glob("*.md"), reverse=True)
    for f in briefs:
        m, body_md = front_matter(f.read_text(encoding="utf-8"))
        emit(f"brief/{f.stem}.html", m["title"], m.get("summary", ""), f"*{m.get('status', '')} · {m.get('date', '')} · {m.get('by', '')}*\n\n" + body_md)
    emit("brief/index.html", "The brief", "The words this site was built from, published in full, never edited afterwards.",
         "\n".join(f"- [{front_matter(f.read_text(encoding='utf-8'))[0]['title']}]({f.stem}.html)" for f in briefs) +
         f"\n\nCorrections go in [BRIEF-CORRECTIONS.md]({REPO}/blob/dev/BRIEF-CORRECTIONS.md), not in the brief.")
    put("demo/pki.bundle.json", (ROOT / "tests/fixtures/pki.bundle.json").read_bytes())
    for a in ("site.css", "site.js"):
        put(f"assets/{a}", (HERE / "assets" / a).read_bytes())
    pages = sorted(r for r in files if r.endswith(".html"))
    llms = [f"# {HOST}", "", f"> The storyboard kit: draws storyboards (JSON) as sketchy SVG panels in the browser, served in immutable versioned folders. "
            f"Current release {release} at {base} (manifest: {base}manifest.json). Site {version}.", "",
            "Every page has a markdown twin: replace .html with .md.", "", "## Pages", ""] + \
           [f"- [{fill(front_matter((HERE / 'pages' / Path(p).with_suffix('.md')).read_text(encoding='utf-8'))[0]['title']) if (HERE / 'pages' / Path(p).with_suffix('.md')).exists() else p}]({SITE}/{Path(p).with_suffix('.md').as_posix()})" for p in pages] + \
           ["", "## Releases", ""] + [f"- {v}: {SITE}/{R.folder(v)}/manifest.json" for v in rels] + \
           ["", "## Where the storyboards are", "", "- https://storyboards.sgit.ai/llms.txt and https://storyboards.sgit.ai/catalogue.json", ""]
    put("llms.txt", "\n".join(llms))
    put("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f"<url><loc>{SITE}/{u.removesuffix('index.html')}</loc></url>\n" for u in pages) + "</urlset>\n")
    put("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    put("404.html", page("404.html", "Not here", '<h1>Not here</h1><p class="lede">Nothing at this address. A release lives at <code>/vX/vX.Y/vX.Y.Z/</code>; <a href="/releases.json">releases.json</a> lists them.</p>',
                         "Not found.", version, release, "/index.md").replace("<head>", '<head>\n<meta name="robots" content="noindex">').replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/').replace(f'href="{R.folder(release)}/', f'href="/{R.folder(release)}/'))
    if out.exists():
        shutil.rmtree(out)
    for rel, data in files.items():
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return files


def main():
    if "--check" in sys.argv:
        with tempfile.TemporaryDirectory() as tmp:
            files = build(Path(tmp) / "www")
            have = {p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()} if OUT.exists() else set()
            bad = sorted(r for r in files if r not in have or (OUT / r).read_bytes() != files[r]) + sorted(have - set(files))
            if bad:
                die("www/ is not what site/build.py writes (run it and commit): " + ", ".join(bad[:20]))
        print(f"site/build --check: www/ is what the build writes ({len(files)} files)")
    else:
        files = build(OUT)
        print(f"site/build: www/ written ({len(files)} files)")


if __name__ == "__main__":
    main()
