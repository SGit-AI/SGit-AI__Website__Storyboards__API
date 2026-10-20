# Version history

> One line per push to main: the repository's version, the kit release it serves, and what changed.

*Source: <https://api.storyboards.sgit.ai/versions/index.html>.*

---

| Version | Date | Kit | What changed, and why |
|---|---|---|---|
| v0.1.0 | 2026-10-20 | v0.1.0 | The first release. The kit gen-z-developers.sgit.ai and pki.sgit.ai each carried a copy of is served once, from /v0/v0.1/v0.1.0/, never to change: the drawing (four marked patches: prop packs, a per-site preferences key, the vocabulary and wire(), an embed's start view), pki.sgit.ai's props as the security pack, Rough.js and the two fonts vendored, and three new files: formats.js (validate, markdown, semantic graph), export.js (SVG, animated SVG, PNG, JPEG, contact sheet) and embed.js (<sg-storyboard>). Each file's SHA-256 and SRI string in the manifest; tools/release.py cuts and checks it; tests in Node and three browsers. |
