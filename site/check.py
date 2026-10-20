#!/usr/bin/env python3
"""The website's gate, run on the site as GitHub Pages will serve it (www/ plus every release folder, assembled by
tools/release.py site): every internal link resolves, every page has its markdown twin, carries the version and is in
the sitemap, canonicals name this host, and no key shapes appear anywhere in what is served.

    python3 site/check.py
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HOST = "api.storyboards.sgit.ai"
V = json.loads((ROOT / "tools/version.json").read_text(encoding="utf-8"))["version"]
KEYS = [re.compile(p) for p in (r"sgit_private_\S+", r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"\bAKIA[0-9A-Z]{16}\b", r"\bsk-(?:or-|ant-)?[A-Za-z0-9_-]{24,}", r"\bghp_[A-Za-z0-9]{30,}")]


def main():
    errors = []
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp) / "site"
        subprocess.run([sys.executable, str(ROOT / "tools/release.py"), "site", "--out", str(site)], check=True, capture_output=True)
        pages = sorted(site.rglob("*.html"))
        for p in pages:
            rel = p.relative_to(site).as_posix()
            t = p.read_text(encoding="utf-8")
            m = re.search(r'<meta name="site-version" content="([^"]+)">', t)
            if not m or m.group(1) != V:
                errors.append(f"{rel}: site-version {m.group(1) if m else 'missing'}, the repository is {V}")
            for attr, url in re.findall(r'\b(href|src)="([^"]+)"', t):
                u = urlparse(url)
                if u.scheme in ("mailto", "data") or url.startswith("#") or (u.scheme in ("http", "https") and u.netloc != HOST) or (not u.path and not u.scheme):
                    continue
                target = site / u.path.lstrip("/") if (u.scheme or u.path.startswith("/")) else p.parent / u.path
                if target.is_dir() or u.path.endswith("/") or u.path == "":
                    target = target / "index.html"
                if not target.resolve().exists():
                    errors.append(f"{rel}: {attr}={url} does not resolve")
            tw = re.search(r'<link rel="alternate" type="text/markdown" href="([^"]+)">', t)
            if rel != "404.html" and (not tw or not (p.parent / tw.group(1)).exists()):
                errors.append(f"{rel}: no markdown twin")
            for c in re.findall(r'<link rel="canonical" href="([^"]+)">', t):
                if urlparse(c).netloc != HOST:
                    errors.append(f"{rel}: canonical {c} is not on {HOST}")
        sm = (site / "sitemap.xml").read_text(encoding="utf-8")
        listed = {u.replace(f"https://{HOST}/", "") for u in re.findall(r"<loc>([^<]+)</loc>", sm)}
        listed = {(u + "index.html") if (u == "" or u.endswith("/")) else u for u in listed}
        have = {p.relative_to(site).as_posix() for p in pages} - {"404.html"}
        errors += [f"sitemap.xml: {x} is missing" for x in sorted(have - listed)] + [f"sitemap.xml: lists {x}, not a page" for x in sorted(listed - have)]
        for p in site.rglob("*"):
            if p.is_file() and p.suffix in (".html", ".md", ".json", ".txt", ".js", ".css", ".xml"):
                text = p.read_text(encoding="utf-8", errors="replace")
                errors += [f"{p.relative_to(site)}: matches the key shape {k.pattern}" for k in KEYS if k.search(text)]
        for p in list((ROOT / "site/pages").rglob("*.md")):
            if "—" in p.read_text(encoding="utf-8"):
                errors.append(f"{p.relative_to(ROOT)}: an em-dash in prose")
    if errors:
        print("\n".join("site/check: " + e for e in errors[:60]))
        sys.exit(f"site/check: {len(errors)} problem(s)")
    print(f"site/check: {len(pages)} pages, version {V}: links, twins, sitemap, canonicals and key shapes hold")


if __name__ == "__main__":
    main()
