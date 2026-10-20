#!/usr/bin/env python3
"""Builds the api.storyboards.sgit.ai website, the developer site for the storyboard kit, into www/ (committed; CI checks
it is what this writes). The release folders are not part of www/: tools/release.py site puts them beside it when GitHub
Pages is assembled, and every page here loads the kit from the newest of them.

    python3 site/build.py           # write www/
    python3 site/build.py --check   # fail if www/ is not what this writes

Sources: site/pages/**/*.md (front matter: title, summary, section, order), policies/*.md (the agent behaviour
policies), briefs/, site/data/versions.json, every release's manifest.json, and tools/upstream/ (the files the kit
began as, for the patch diffs). Generated pages: the docs hub's contents, the gallery (site/gallery.py's specimen,
drawn live by the release), the patches against upstream, one page per release with its diff against the one before,
and the version history. Every page has a markdown twin. Placeholders in pages: {{RELEASE}}, {{BASE}}, {{REPO}},
{{FILES}}, {{VOCAB}}, {{SRI_EXAMPLE}}, {{DEMO}}, {{TOC}}.
"""
import difflib
import hashlib
import html
import json
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
import gallery  # noqa: E402

HOST = "api.storyboards.sgit.ai"
SITE = f"https://{HOST}"
REPO = "https://github.com/SGit-AI/SGit-AI__Website__Storyboards__API"
OUT = ROOT / "www"
SECTIONS = ["Start", "Guides", "Reference", "Internals", "Engineering", "Policies", "Releases"]
NAV = [("Docs", "docs/index.html"), ("Guides", "guides/write-a-storyboard.html"), ("Reference", "docs/format.html"), ("Gallery", "docs/gallery.html"),
       ("Releases", "releases/index.html"), ("Policies", "policies/index.html")]
esc = lambda s: html.escape(str(s if s is not None else ""), quote=True)


def die(m):
    sys.exit(f"site/build: {m}")


def page(rel, title, body, desc, version, release, twin, toc="", scripts=""):
    up = "../" * rel.count("/")
    canon = f"{SITE}/{rel}".removesuffix("index.html")
    nav = "".join(f'<a href="{up}{h}">{l}</a>' for l, h in NAV)
    base = f"{up}{R.folder(release)}/"
    main = f'<main id="main" class="docs-main"><div class="docs"><aside class="toc" aria-label="Documentation">{toc}</aside><div class="docs-body">{body}</div></div></main>' if toc \
        else f'<main id="main" class="narrow">\n{body}\n</main>'
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
<span class="ver">site <a href="{up}versions/index.html" title="Release history of this repository">{version}</a> &middot; kit <a href="{up}releases/{release}.html">{release}</a></span></div>
</div></nav>
{main}
<footer class="site"><div class="row">
<div><b>api.storyboards.sgit.ai</b>: the storyboard kit, in immutable versioned folders, and everything about its code. Code Apache-2.0; Rough.js MIT; fonts SIL OFL 1.1.</div>
<div class="netline"><a href="https://storyboards.sgit.ai/">&#8599; storyboards.sgit.ai</a>, where the storyboards live &middot; <a href="https://riskmandate.ai/abp.html">&#8599; riskmandate.ai</a>, the shape of the policies &middot; <a href="https://sgit.ai">&#8599; sgit.ai</a> &middot; <a href="https://api.newsroom.sgit.ai/">&#8599; api.newsroom.sgit.ai</a> &middot; <a href="https://sgit.ai/network/index.html">&#8599; the network</a></div>
<div>&#9888; Participant disclosure: published by the sgit project. <a href="{up}about/participant.html">Read the disclosure</a>.</div>
<div>Site {version} &middot; kit {release} &middot; <a href="{up}versions/index.html">version history</a> &middot; <a href="{esc(twin)}">this page as markdown</a> &middot; <a href="{up}llms.txt">llms.txt</a> &middot; <a href="{up}releases.json">releases.json</a> &middot; <a href="{REPO}">GitHub</a></div>
</div></footer>
{scripts}
</body>
</html>
"""


def sb_tools():
    """The viewer's toolbar, the same markup storyboards.sgit.ai's pages use; the kit wires it."""
    cols = "".join(f'<option value="{n}">{n}</option>' for n in range(1, 7))
    return ('<div class="sb-tools" role="toolbar" aria-label="How to view the panels"><span class="sb-views" role="group" aria-label="View">'
            '<button type="button" data-view="deck" title="One panel at a time (d)">Deck</button><button type="button" data-view="grid" title="Every panel on one page (g)">Grid</button>'
            '<button type="button" data-view="script" title="The storyboard as text (t)">Script</button></span>'
            f'<label class="sb-for-grid">Per row <select class="sb-cols">{cols}</select></label>'
            '<label title="Panels play as they arrive (a)"><input type="checkbox" class="sb-anim"> Animation</label>'
            '<label class="sb-for-grid" title="Each panel\'s script under it (x)"><input type="checkbox" class="sb-showtext"> Text</label>'
            '<button type="button" class="sb-playall sb-for-grid" title="Play the panels one after another (p)">Play in order</button>'
            '<input type="search" class="sb-filter sb-for-list" placeholder="Filter: a word, a kind, a prop" aria-label="Filter the panels"></div>')


def diff_html(a, b, a_name, b_name):
    """A unified diff as HTML, each line classed so additions, removals and hunks read at a glance; and as text."""
    lines = list(difflib.unified_diff(a.splitlines(), b.splitlines(), a_name, b_name, n=2, lineterm=""))
    if not lines:
        return '<p class="small dim">No difference: the bytes are the same.</p>', "No difference: the bytes are the same.\n"
    cls = lambda l: "add" if l.startswith("+") and not l.startswith("+++") else "del" if l.startswith("-") and not l.startswith("---") else "hunk" if l.startswith("@@") else "head" if l[:3] in ("+++", "---") else ""
    body = "\n".join(f'<span class="{cls(l)}">{html.escape(l)}</span>' if cls(l) else html.escape(l) for l in lines)
    return f'<pre class="diff"><code>{body}</code></pre>', "```diff\n" + "\n".join(lines) + "\n```\n"


def build(out):
    V = R.load_version()
    version, release = V["version"], V["release"]
    rels = R.releases()
    if release not in rels:
        die(f"the current release {release} has not been cut")
    base = f"{SITE}/{R.folder(release)}/"
    mans = {v: json.loads((ROOT / R.folder(v) / "manifest.json").read_text(encoding="utf-8")) for v in rels}
    man = mans[release]
    hist = json.loads((HERE / "data/versions.json").read_text(encoding="utf-8"))["versions"]
    if hist[0]["version"] != version:
        die(f"site/data/versions.json starts at {hist[0]['version']}; tools/version.json says {version}: add the line for {version}")
    for h in hist:
        if h["release"] not in rels:
            die(f"site/data/versions.json: {h['version']} names release {h['release']}, which is not published")
    # the release's own formats.js: the vocabulary, and the specimen validated and turned into its script
    sizes = {f["path"]: f["bytes"] for f in man["files"]}
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / "probe.js"
        probe.write_text("const F=require(process.argv[2]);let i='';process.stdin.on('data',d=>i+=d).on('end',()=>{const g=JSON.parse(i);"
                         "process.stdout.write(JSON.stringify({V:F.VOCAB,P:F.PACKS,errors:F.validate(g.storyboard,g.cast,{props:[].concat(...Object.values(F.PACKS))}),"
                         "md:F.toMarkdown(g.storyboard,g.cast)}))});", encoding="utf-8")
        first = json.loads(subprocess.check_output(["node", str(probe), str(ROOT / R.folder(release) / "formats.js")], input=json.dumps({"storyboard": {"slug": "x", "title": "x", "scenes": []}, "cast": {"characters": []}}), text=True))
        spec = gallery.specimen(first["V"], first["P"], sizes)
        res = json.loads(subprocess.check_output(["node", str(probe), str(ROOT / R.folder(release) / "formats.js")], input=json.dumps({"storyboard": spec, "cast": gallery.CAST}), text=True))
    if res["errors"]:
        die("the specimen does not validate against the release's own formats.js:\n  " + "\n  ".join(res["errors"]))
    vocab = {"V": res["V"], "P": res["P"]}

    files_md = "| File | Bytes | SHA-256 | Integrity |\n|---|---|---|---|\n" + "\n".join(
        f"| [{f['path']}]({base}{f['path']}) | {f['bytes']:,} | `{f['sha256'][:16]}…` | `{f['integrity'][:22]}…` |" for f in man["files"])
    vocab_md = "| | |\n|---|---|\n" + "\n".join(f"| {k} | {', '.join(f'`{x}`' for x in v)} |" for k, v in vocab["V"].items()) + \
        "\n" + "\n".join(f"| props, `{p}` pack | {', '.join(f'`{x}`' for x in v)} |" for p, v in vocab["P"].items())
    integ = {f["path"]: f["integrity"] for f in man["files"]}
    sri = "\n".join((f'<link rel="stylesheet" href="{base}{p}" integrity="{integ[p]}" crossorigin="anonymous">' if p.endswith(".css")
                     else f'<script src="{base}{p}" integrity="{integ[p]}" crossorigin="anonymous"></script>')
                    for p in ["fonts.css", "storyboard.css", "vendor/rough-4.6.6.js", "props/security.js", "storyboard.js", "export.js"])
    demo = (f'<div class="hero-panel" style="max-width:720px"><sg-storyboard src="demo/pki.bundle.json" view="panel" panel="4"></sg-storyboard></div>'
            f'<script src="{R.folder(release)}/embed.js" defer></script><p class="small dim">Above: panel 4 of pki.sgit.ai\'s <i>The first key</i>, drawn now, by this release, from '
            f'<a href="demo/pki.bundle.json">a bundle</a>. Click it to play.</p>')

    policy = json.loads((ROOT / "policies/code-immutability.policy.json").read_text(encoding="utf-8"))

    def fill(t):
        return (t.replace("{{INSTRUCTIONS}}", policy["instructions"]).replace("{{RELEASE}}", release).replace("{{BASE}}", base).replace("{{REPO}}", REPO).replace("{{FILES}}", files_md)
                .replace("{{VOCAB}}", vocab_md).replace("{{SRI_EXAMPLE}}", sri))

    # ---- collect every page first, so each can carry the contents of all
    entries = []

    def add(rel, title, desc, md_text, section=None, order=50, raw=None, scripts=""):
        entries.append({"rel": rel, "title": title, "desc": desc, "md": md_text, "section": section, "order": order, "raw": raw, "scripts": scripts})

    for f in sorted((HERE / "pages").rglob("*.md")):
        m, body_md = front_matter(f.read_text(encoding="utf-8"))
        add(f.relative_to(HERE / "pages").with_suffix(".html").as_posix(), fill(m["title"]), fill(m.get("summary", "")), fill(body_md),
            m.get("section"), int(m.get("order", 50)))

    # the gallery: the specimen, drawn by the release in the reader's browser, and the specimen cast's model sheet
    rbase = f"../{R.folder(release)}/"
    kit_scripts = "".join(f'<script src="{rbase}{p}"></script>' for p in ["vendor/rough-4.6.6.js", "props/security.js", "storyboard.js"])
    gal = (f'<p>Every kind, setting and prop that release {release} knows, in one storyboard of {len(spec["scenes"])} panels, drawn in your browser by '
           f'<code>{R.folder(release)}/storyboard.js</code> now. The storyboard is generated by <code>site/gallery.py</code> from the release\'s own vocabulary and validated by its own '
           f'<code>formats.js</code>, so a prop added in a release appears here without anyone drawing a panel for it. Switch to <b>Grid</b> to see them all at once; the script view lists every field used.</p>'
           f'<div class="sb-viewer">{sb_tools()}<div class="sb-deck" hidden><div class="sb-track"></div>'
           '<div class="sb-bar"><button type="button" class="sb-prev" aria-label="Previous panel">&larr;</button><span class="sb-count"></span><button type="button" class="sb-next" aria-label="Next panel">&rarr;</button>'
           '<button type="button" class="sb-replay" title="Play this panel (p)">&#9654; Play</button><button type="button" class="sb-notes-toggle" title="Notes (n)">Notes</button><button type="button" class="sb-full" title="Full screen (f)">Full screen</button></div>'
           f'<div class="sb-notes"></div></div><div class="sb-grid" hidden></div><div class="sb-script" hidden></div><script type="application/json" class="sb-data">{json.dumps({"storyboard": spec, "cast": gallery.CAST}, ensure_ascii=False).replace("</", "<" + chr(92) + "/")}</script></div>'
           '<h2 id="poses-and-moods">Every pose and every mood</h2><p>The model sheet: each specimen character in each of the moods and poses, the way animators check a character is on model.</p>'
           f'<div class="sb-sheet"><script type="application/json" class="sb-data">{json.dumps({"cast": gallery.CAST}, ensure_ascii=False)}</script></div>'
           f'<h2 id="the-data">The data</h2><p>The specimen as JSON is <a href="specimen.bundle.json">specimen.bundle.json</a>; as a script, <a href="gallery.md">gallery.md</a>.</p>')
    add("docs/gallery.html", "The gallery", f"Every kind, setting, prop, pose and mood of release {release}, drawn live by it.", res["md"], "Reference", 2, raw=gal, scripts=kit_scripts)

    # the patches: each served file that began elsewhere, against the exact upstream bytes
    prov = json.loads((ROOT / "tools/provenance.json").read_text(encoding="utf-8"))
    p_html, p_md = [f'<p>The kit began as files on two other sites. These are the exact differences between those files and release {release}, computed by the build from '
                    f'<code>tools/upstream/</code> (each checked against its recorded SHA-256) and the published folder. Every other line is the upstream code, unchanged.</p>'], \
                   [f"The exact differences between the upstream files and release {release}.", ""]
    for rel_path, up in prov.get("upstream", {}).items():
        src = ROOT / up["file"]
        if hashlib.sha256(src.read_bytes()).hexdigest() != up["sha256"]:
            die(f"{up['file']} is not the upstream bytes recorded in tools/provenance.json")
        h, t = diff_html(src.read_text(encoding="utf-8"), (ROOT / R.folder(release) / rel_path).read_text(encoding="utf-8"), up["name"], f"{R.folder(release)}/{rel_path}")
        p_html.append(f'<h2 id="{esc(rel_path.replace("/", "-"))}">{esc(rel_path)}</h2><p class="small dim">Upstream: <a href="{esc(up["url"])}">{esc(up["name"])}</a> '
                      f'(sha256 <code>{up["sha256"][:16]}…</code>). {esc(up.get("note", ""))}</p>{h}')
        p_md += [f"## {rel_path}", "", f"Upstream: [{up['name']}]({up['url']}), sha256 `{up['sha256']}`. {up.get('note', '')}", "", t]
    add("internals/patches.html", "The patches", f"Every line release {release} changes in the code it began from, as a diff.", "\n".join(p_md), "Internals", 2, raw="".join(p_html))

    # one page per release: its files and hashes, where each came from, and what changed from the release before
    intro = {}
    for h in reversed(hist):
        intro.setdefault(h["release"], h)
    for i, v in enumerate(rels):
        mv, b = mans[v], f"{SITE}/{R.folder(v)}/"
        prev = rels[i + 1] if i + 1 < len(rels) else None
        rows = "".join(f'<tr><td><a href="{b}{esc(f["path"])}">{esc(f["path"])}</a></td><td>{f["bytes"]:,}</td><td><code class="hash">{f["sha256"]}</code><br><code class="hash">{esc(f["integrity"])}</code></td><td class="small">{esc(f.get("origin", "written here"))}</td></tr>' for f in mv["files"])
        h_ = [f'<p>Published at <code>{b}</code> on {mv["date"]}: {mv["counts"]["files"]} files, {mv["counts"]["bytes"]:,} bytes. '
              f'<a href="{b}manifest.json">manifest.json</a>. This folder is immutable: these bytes never change at this path.</p>',
              f'<p>{esc(intro.get(v, {}).get("what", ""))}</p>' if v in intro else "",
              f'<h2 id="files">The files</h2><table><thead><tr><th>File</th><th>Bytes</th><th>SHA-256 and SRI</th><th>Where it came from</th></tr></thead><tbody>{rows}</tbody></table>']
        m_ = [f"Published at `{b}` on {mv['date']}: {mv['counts']['files']} files, {mv['counts']['bytes']:,} bytes. Immutable.", "", intro.get(v, {}).get("what", ""), "",
              "| File | Bytes | SHA-256 |", "|---|---|---|"] + [f"| {f['path']} | {f['bytes']} | `{f['sha256']}` |" for f in mv["files"]] + [""]
        if prev:
            pm = {f["path"]: f for f in mans[prev]["files"]}
            cm = {f["path"]: f for f in mv["files"]}
            added, removed = sorted(set(cm) - set(pm)), sorted(set(pm) - set(cm))
            changed = sorted(p for p in set(cm) & set(pm) if cm[p]["sha256"] != pm[p]["sha256"])
            h_.append(f'<h2 id="changes">What changed from {prev}</h2><p>{len(changed)} changed, {len(added)} added, {len(removed)} removed; '
                      f'{len(set(cm) & set(pm)) - len(changed)} byte for byte the same.</p>')
            m_ += [f"## What changed from {prev}", "", f"Changed: {', '.join(changed) or 'none'}. Added: {', '.join(added) or 'none'}. Removed: {', '.join(removed) or 'none'}.", ""]
            for p in changed:
                if p.endswith((".js", ".css", ".txt", ".json")):
                    hh, tt = diff_html((ROOT / R.folder(prev) / p).read_text(encoding="utf-8"), (ROOT / R.folder(v) / p).read_text(encoding="utf-8"), f"{prev}/{p}", f"{v}/{p}")
                    h_.append(f"<h3>{esc(p)}</h3>{hh}")
                    m_ += [f"### {p}", "", tt]
        else:
            h_.append(f'<h2 id="changes">The first release</h2><p>There is no release before it. What it changed in the code it began from is on <a href="../internals/patches.html">the patches</a>.</p>')
        add(f"releases/{v}.html", f"Release {v}", f"Release {v} of the kit: every file, its hash, where it came from and what changed.", "\n".join(m_), "Releases", -int("".join(f"{x:04d}" for x in R.vtuple(v))), raw="".join(h_))
    rl = "".join(f'<li><a href="{v}.html">{v}</a> <span class="small dim">{mans[v]["date"]} &middot; {mans[v]["counts"]["files"]} files &middot; <code>{R.folder(v)}/</code></span><p>{esc(intro.get(v, {}).get("what", ""))}</p></li>' for v in rels)
    add("releases/index.html", "Releases", "Every release of the kit, newest first. Each is a folder that never changes.",
        "\n".join(f"- [{v}]({v}.md), {mans[v]['date']}, `{R.folder(v)}/`: {intro.get(v, {}).get('what', '')}" for v in rels), "Releases", -10**9,
        raw=f'<p>Each release is a folder at <code>/vMAJOR/vMAJOR.MINOR/vX.Y.Z/</code>, published once and never changed; <a href="../releases.json">releases.json</a> lists them for a tool. '
            f'A push that changes only the website or the tooling is a <a href="../versions/index.html">version</a> of this repository, not a release.</p><ul class="list">{rl}</ul>')

    # the policies: the agent behaviour policies this repository runs under, from policies/*.md
    pols = []
    for f in sorted((ROOT / "policies").glob("*.md")):
        m, body_md = front_matter(f.read_text(encoding="utf-8"))
        pols.append((m, f.stem))
        meta = f"*{m.get('id', '')} · version {m.get('version', '')} · {m.get('status', '')} · {m.get('date', '')}*\n\n"
        add(f"policies/{f.stem}.html", m["title"], m.get("summary", ""), meta + fill(body_md), "Policies", int(m.get("order", 10)))
    add("policies/index.html", "Policies", "The agent behaviour policies this repository runs under, and how each is enforced.",
        "The rules an agent working on this code must follow, each written in the shape of riskmandate.ai's Agent Behaviour Policy (what the agent may reach, what it is "
        "mandated to do, the gap between the two and the barriers in place), and each enforced by something that runs, not only by being read.\n\n"
        + "\n".join(f"- [{m['title']}]({stem}.html) ({m.get('id', '')}, {m.get('status', '')}): {m.get('summary', '')}" for m, stem in pols), "Policies", 0)

    # history and brief
    vmd = "| Version | Date | Kit | What changed, and why |\n|---|---|---|---|\n" + "\n".join(f"| {h['version']} | {h['date']} | [{h['release']}](../releases/{h['release']}.html) | {h['what']} |" for h in hist)
    add("versions/index.html", "Version history", "One line per push to dev: the repository's version, the kit release it serves, and what changed.", vmd)
    briefs = sorted((ROOT / "briefs").glob("*.md"), reverse=True)
    for f in briefs:
        m, body_md = front_matter(f.read_text(encoding="utf-8"))
        add(f"brief/{f.stem}.html", m["title"], m.get("summary", ""), f"*{m.get('status', '')} · {m.get('date', '')} · {m.get('by', '')}*\n\n" + body_md)
    add("brief/index.html", "The brief", "The words this site was built from, published in full, never edited afterwards.",
        "\n".join(f"- [{front_matter(f.read_text(encoding='utf-8'))[0]['title']}]({f.stem}.html)" for f in briefs) +
        f"\n\nCorrections go in [BRIEF-CORRECTIONS.md]({REPO}/blob/dev/BRIEF-CORRECTIONS.md), not in the brief.")

    # ---- the contents, by section, for the sidebar and the docs hub
    by_sec = {s: sorted((e for e in entries if e["section"] == s), key=lambda e: (e["order"], e["title"])) for s in SECTIONS}
    toc_md = "\n\n".join(f"## {s}\n\n" + "\n".join(f"- [{e['title']}](../{e['rel']}): {e['desc']}" for e in by_sec[s]) for s in SECTIONS if by_sec[s])

    def toc_for(rel):
        up = "../" * rel.count("/")
        return "".join(f'<p class="toc-h">{s}</p><ul>' + "".join(f'<li><a href="{up}{e["rel"]}"{" aria-current=\"page\"" if e["rel"] == rel else ""}>{esc(e["title"])}</a></li>' for e in by_sec[s]) + "</ul>"
                       for s in SECTIONS if by_sec[s])

    files = {}

    def put(rel, data):
        files[rel] = data.encode("utf-8") if isinstance(data, str) else data

    for e in entries:
        md_text = e["md"].replace("{{TOC}}", toc_md)
        body_html = e["raw"] if e["raw"] is not None else md_render(md_text)
        body_html = body_html.replace("<p>{{DEMO}}</p>", demo)
        body = f'<article class="article"><h1>{esc(e["title"])}</h1><p class="lede">{esc(e["desc"])}</p>{body_html}</article>'
        twin = Path(e["rel"]).with_suffix(".md").name
        docs = e["section"] is not None or e["rel"].startswith(("docs/", "guides/", "internals/", "engineering/", "policies/", "releases/"))
        put(e["rel"], page(e["rel"], e["title"], body, e["desc"], version, release, twin, toc=toc_for(e["rel"]) if docs else "", scripts=e["scripts"]))
        put(str(Path(e["rel"]).with_suffix(".md")), f"# {e['title']}\n\n> {e['desc']}\n\n*Source: <{SITE}/{e['rel']}>.*\n\n---\n\n" + md_text.replace("{{DEMO}}", "").strip() + "\n")

    put("docs/specimen.bundle.json", (json.dumps({"what": "The gallery's specimen: generated by site/gallery.py from release " + release + "'s vocabulary.",
                                                  "packs": list(vocab["P"]), "storyboard": spec, "cast": gallery.CAST}, indent=1, ensure_ascii=False) + "\n"))
    put("demo/pki.bundle.json", (ROOT / "tests/fixtures/pki.bundle.json").read_bytes())
    for a in ("site.css", "site.js"):
        put(f"assets/{a}", (HERE / "assets" / a).read_bytes())
    pages = sorted(r for r in files if r.endswith(".html"))
    llms = [f"# {HOST}", "", f"> The developer site of the storyboard kit, which draws storyboards (JSON) as sketchy SVG panels in the browser, served in immutable versioned folders. "
            f"Current release {release} at {base} (manifest: {base}manifest.json). Site {version}.", "",
            "Every page has a markdown twin: replace .html with .md. Code in a release folder is never changed; see policies/code-immutability.md.", ""]
    for s in SECTIONS:
        if by_sec[s]:
            llms += [f"## {s}", ""] + [f"- [{e['title']}]({SITE}/{Path(e['rel']).with_suffix('.md').as_posix()}): {e['desc']}" for e in by_sec[s]] + [""]
    llms += ["## Where the storyboards are", "", "- https://storyboards.sgit.ai/llms.txt and https://storyboards.sgit.ai/catalogue.json", ""]
    put("llms.txt", "\n".join(llms))
    put("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f"<url><loc>{SITE}/{u.removesuffix('index.html')}</loc></url>\n" for u in pages) + "</urlset>\n")
    put("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    put("404.html", page("404.html", "Not here", '<h1>Not here</h1><p class="lede">Nothing at this address. A release lives at <code>/vX/vX.Y/vX.Y.Z/</code>; <a href="/releases.json">releases.json</a> lists them.</p>',
                         "Not found.", version, release, "/index.md").replace("<head>", '<head>\n<meta name="robots" content="noindex">').replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')
        .replace(f'href="{R.folder(release)}/', f'href="/{R.folder(release)}/').replace('href="versions/', 'href="/versions/').replace('href="releases/', 'href="/releases/')
        .replace('href="docs/', 'href="/docs/').replace('href="guides/', 'href="/guides/').replace('href="internals/', 'href="/internals/').replace('href="policies/', 'href="/policies/')
        .replace('href="about/', 'href="/about/').replace('href="index.html"', 'href="/index.html"').replace('href="llms.txt"', 'href="/llms.txt"'))
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
