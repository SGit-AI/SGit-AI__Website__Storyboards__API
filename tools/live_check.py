#!/usr/bin/env python3
"""After a deploy: ask the live host for every file of every release and compare it with the manifest. A clean push is
not a release; the release is done when the live host serves these bytes.

    python3 tools/live_check.py [--wait SECONDS]
"""
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release as R  # noqa: E402


def fetch(url):
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "storyboards-api-live-check"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def once():
    bad = []
    for v in R.releases():
        man = json.loads((R.ROOT / R.folder(v) / "manifest.json").read_text(encoding="utf-8"))
        for f in man["files"]:
            url = f"{R.HOST}/{R.folder(v)}/{f['path']}"
            try:
                if hashlib.sha256(fetch(url)).hexdigest() != f["sha256"]:
                    bad.append(f"{url}: served bytes differ from the manifest")
            except Exception as e:  # noqa: BLE001 (a network error is a finding, reported, not a crash)
                bad.append(f"{url}: {e}")
    return bad


def main():
    wait = int(sys.argv[sys.argv.index("--wait") + 1]) if "--wait" in sys.argv else 0
    end = time.time() + wait
    while True:
        bad = once()
        if not bad or time.time() > end:
            break
        time.sleep(20)
    if bad:
        print("\n".join("live_check: " + b for b in bad[:30]))
        sys.exit(1)
    print(f"live_check: {R.HOST} serves every file of {', '.join(R.releases())} with the hash in its manifest")


if __name__ == "__main__":
    main()
