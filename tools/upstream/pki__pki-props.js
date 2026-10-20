/* pki-props.js: the props pki.sgit.ai's storyboards need and the gen-z kit does not have, drawn the same way (Rough.js,
 * sketchy, nothing an image). Loaded before assets/storyboard/storyboard.js, which merges them into its PROPS through
 * the one local patch in that file. Every prop is (g, rc, x, y, s, p): x the centre, y the line it stands on, s a
 * scale, p the scene's entry. A prop that names a `label` writes it under (or on) itself.
 *
 *   key        a key; p.colour, p.label (e.g. "sign", "encrypt"), p.private draws it with a small padlock
 *   vault      a safe; p.label, p.colour, p.open (the door ajar), p.size (1 is 240 wide)
 *   qr         a QR code, with the URL printed above it as on this site; p.text, p.size, p.seed
 *   envelope   a sealed message; p.label, p.sealed (a wax seal), p.colour
 *   record     a signed statement on paper; p.lines, p.stamp (the seal's word)
 *   server     a server holding only ciphertext; p.label
 *   arrow      a hand-drawn arrow from x to p.to (both 0..1 of the width), at height y; p.label, p.both, p.dashed, p.colour
 *   mark       a big tick or cross; p.ok
 *   calendar   a date card; p.label, p.colour
 *   terminal   an agent's terminal; p.lines
 *   phoneqr    a phone with a QR code on its screen; p.text
 *   padlock    a padlock; p.open
 */
(function () {
  'use strict';
  window.StoryboardExtraProps = function (k) {
    const { draw, el, textBlock, wrap, INK, W } = k;
    const ink = (o) => Object.assign({ stroke: INK, strokeWidth: 2.4 }, o || {});
    const label = (g, text, x, y, size, o) => { if (text) textBlock(g, wrap(text, (o && o.max) || 20), x, y, (size || 26) * 1.35, Object.assign({ anchor: 'middle' }, o || {})); };
    function rand(seed) { let t = seed >>> 0; return () => { t += 0x6D2B79F5; let r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; }
    const hash = (s) => { let h = 2166136261; for (const c of String(s || '')) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };
    function padlock(g, rc, x, y, s, open) {
      draw(g, rc.rectangle(x - 22 * s, y - 34 * s, 44 * s, 34 * s, ink({ fill: '#f59e0b', fillStyle: 'solid', strokeWidth: 2 })));
      draw(g, rc.path(open ? `M${x - 14 * s},${y - 34 * s} V${y - 52 * s} Q${x - 14 * s},${y - 66 * s} ${x},${y - 66 * s} Q${x + 14 * s},${y - 66 * s} ${x + 14 * s},${y - 56 * s}`
        : `M${x - 14 * s},${y - 34 * s} V${y - 50 * s} Q${x - 14 * s},${y - 64 * s} ${x},${y - 64 * s} Q${x + 14 * s},${y - 64 * s} ${x + 14 * s},${y - 50 * s} V${y - 34 * s}`, ink({ strokeWidth: 3 })));
    }
    function qrModules(g, rc, x0, y0, size, seed) {
      const n = 21, c = size / n, r = rand(seed);
      el('rect', { x: x0, y: y0, width: size, height: size, fill: '#fff' }, g);
      const finder = (fx, fy) => { el('rect', { x: x0 + fx * c, y: y0 + fy * c, width: 7 * c, height: 7 * c, fill: INK }, g); el('rect', { x: x0 + (fx + 1) * c, y: y0 + (fy + 1) * c, width: 5 * c, height: 5 * c, fill: '#fff' }, g); el('rect', { x: x0 + (fx + 2) * c, y: y0 + (fy + 2) * c, width: 3 * c, height: 3 * c, fill: INK }, g); };
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
        const inF = (i < 8 && j < 8) || (i < 8 && j > n - 9) || (i > n - 9 && j < 8);
        if (!inF && r() < 0.48) el('rect', { x: x0 + j * c, y: y0 + i * c, width: c + 0.4, height: c + 0.4, fill: INK }, g);
      }
      finder(0, 0); finder(n - 7, 0); finder(0, n - 7);
      draw(g, rc.rectangle(x0 - 6, y0 - 6, size + 12, size + 12, ink({ strokeWidth: 2 })));
    }
    // drawn at 1.45 times the kit's own scale, so a key or a vault reads next to a person in a 1600-wide panel
    const K = 1.45
    return {
      key(g, rc, x, y, s, p) {
        s *= K
        const c = p.colour || '#0f766e', bx = x - 70 * s, by = y - 60 * s;
        draw(g, rc.circle(bx, by, 70 * s, ink({ fill: c, fillStyle: 'hachure', hachureGap: 6 })));
        draw(g, rc.circle(bx, by, 22 * s, ink({ fill: '#fff', fillStyle: 'solid' })));
        draw(g, rc.rectangle(bx + 34 * s, by - 9 * s, 120 * s, 18 * s, ink({ fill: c, fillStyle: 'solid' })));
        draw(g, rc.rectangle(bx + 118 * s, by + 9 * s, 14 * s, 26 * s, ink({ fill: c, fillStyle: 'solid' })));
        draw(g, rc.rectangle(bx + 92 * s, by + 9 * s, 14 * s, 18 * s, ink({ fill: c, fillStyle: 'solid' })));
        if (p.private) padlock(g, rc, bx, by + 70 * s, 0.8 * s, false);
        label(g, p.label, x, y + 34 * s, 26 * s);
      },
      vault(g, rc, x, y, s, p) {
        s *= (p.size || 1) * K; const w = 240 * s, h = 220 * s, c = p.colour || '#cbd5e1';
        draw(g, rc.rectangle(x - w / 2, y - h, w, h, ink({ fill: c, fillStyle: 'solid', strokeWidth: 3 })));
        if (p.open) draw(g, rc.polygon([[x - w / 2 + 14 * s, y - h + 14 * s], [x - w / 2 - 60 * s, y - h + 40 * s], [x - w / 2 - 60 * s, y - 20 * s], [x - w / 2 + 14 * s, y - 14 * s]], ink({ fill: '#e5e7eb', fillStyle: 'solid' })));
        else {
          draw(g, rc.rectangle(x - w / 2 + 14 * s, y - h + 14 * s, w - 28 * s, h - 28 * s, ink({ strokeWidth: 2 })));
          draw(g, rc.circle(x, y - h / 2, 70 * s, ink({ fill: '#f8fafc', fillStyle: 'solid' })));
          for (let a = 0; a < 6; a++) { const t = a * Math.PI / 3; draw(g, rc.line(x + Math.cos(t) * 20 * s, y - h / 2 + Math.sin(t) * 20 * s, x + Math.cos(t) * 32 * s, y - h / 2 + Math.sin(t) * 32 * s, ink({ strokeWidth: 2 }))); }
          draw(g, rc.line(x + 70 * s, y - h / 2 - 30 * s, x + 70 * s, y - h / 2 + 30 * s, ink({ strokeWidth: 5 })));
        }
        label(g, p.label, x, y - h - 18 * s, 28 * s, { weight: 'bold', max: 18 });
      },
      qr(g, rc, x, y, s, p) {
        s *= K; const size = 200 * s * (p.size || 1);
        qrModules(g, rc, x - size / 2, y - size, size, p.seed || hash(p.text));
        if (p.text) textBlock(g, [p.text.length > 34 ? p.text.slice(0, 31) + '…' : p.text], x, y - size - 18, 20 * s, { anchor: 'middle', font: 'ui-monospace, Menlo, monospace' });
      },
      envelope(g, rc, x, y, s, p) {
        s *= K
        const w = 230 * s, h = 150 * s, c = p.colour || '#fef3c7';
        draw(g, rc.rectangle(x - w / 2, y - h, w, h, ink({ fill: c, fillStyle: 'solid' })));
        draw(g, rc.path(`M${x - w / 2},${y - h} L${x},${y - h / 2.2} L${x + w / 2},${y - h}`, ink()));
        if (p.sealed !== false) { draw(g, rc.circle(x, y - h / 2.2, 46 * s, ink({ fill: '#b91c1c', fillStyle: 'solid' }))); textBlock(g, ['✓'], x, y - h / 2.2 + 8 * s, 24 * s, { anchor: 'middle', fill: '#fff' }); }
        label(g, p.label, x, y + 34 * s, 24 * s);
      },
      record(g, rc, x, y, s, p) {
        s *= K * 0.9
        const w = 280 * s, h = 300 * s;
        draw(g, rc.rectangle(x - w / 2, y - h, w, h, ink({ fill: '#ffffff', fillStyle: 'solid' })));
        if (p.lines) textBlock(g, p.lines.slice(0, 7), x - w / 2 + 18 * s, y - h + 44 * s, 24 * s, { lh: 1.3 });
        else for (let i = 0; i < 6; i++) draw(g, rc.line(x - w / 2 + 24 * s, y - h + (50 + i * 34) * s, x + w / 2 - (30 + (i % 3) * 30) * s, y - h + (50 + i * 34) * s, ink({ stroke: '#9ca3af', strokeWidth: 2 })));
        if (p.stamp !== false) { draw(g, rc.circle(x + w / 2 - 50 * s, y - 50 * s, 70 * s, ink({ stroke: '#b91c1c', strokeWidth: 3 }))); textBlock(g, [p.stamp || 'signed'], x + w / 2 - 50 * s, y - 43 * s, 18 * s, { anchor: 'middle', fill: '#b91c1c' }); }
        label(g, p.label, x, y + 34 * s, 24 * s);
      },
      server(g, rc, x, y, s, p) {
        s *= K * 0.9
        const w = 170 * s, h = 300 * s;
        draw(g, rc.rectangle(x - w / 2, y - h, w, h, ink({ fill: '#e2e8f0', fillStyle: 'solid', strokeWidth: 3 })));
        for (let i = 0; i < 5; i++) { draw(g, rc.rectangle(x - w / 2 + 14 * s, y - h + (18 + i * 54) * s, w - 28 * s, 40 * s, ink({ strokeWidth: 1.8 }))); el('circle', { cx: x + w / 2 - 30 * s, cy: y - h + (38 + i * 54) * s, r: 6 * s, fill: i % 2 ? '#22c55e' : '#f59e0b' }, g); }
        label(g, p.label, x, y + 34 * s, 22 * s, { max: 20 });
      },
      arrow(g, rc, x, y, s, p) {
        const x2 = (p.to == null ? 0.5 : p.to) * W, c = p.colour || INK, d = x2 > x ? 1 : -1;
        draw(g, rc.line(x, y, x2, y, ink({ stroke: c, strokeWidth: 4, strokeLineDash: p.dashed ? [16, 12] : undefined })));
        draw(g, rc.path(`M${x2 - d * 28},${y - 16} L${x2},${y} L${x2 - d * 28},${y + 16}`, ink({ stroke: c, strokeWidth: 4 })));
        if (p.both) draw(g, rc.path(`M${x + d * 28},${y - 16} L${x},${y} L${x + d * 28},${y + 16}`, ink({ stroke: c, strokeWidth: 4 })));
        label(g, p.label, (x + x2) / 2, y - 26, 26, { max: 30, fill: c === INK ? INK : c });
      },
      mark(g, rc, x, y, s, p) {
        s *= K
        if (p.ok) draw(g, rc.path(`M${x - 50 * s},${y - 60 * s} L${x - 12 * s},${y - 20 * s} L${x + 60 * s},${y - 110 * s}`, { stroke: '#15803d', strokeWidth: 12, roughness: 1.2 }));
        else { draw(g, rc.line(x - 50 * s, y - 110 * s, x + 50 * s, y - 10 * s, { stroke: '#b91c1c', strokeWidth: 12, roughness: 1.2 })); draw(g, rc.line(x + 50 * s, y - 110 * s, x - 50 * s, y - 10 * s, { stroke: '#b91c1c', strokeWidth: 12, roughness: 1.2 })); }
        label(g, p.label, x, y + 30 * s, 24 * s);
      },
      calendar(g, rc, x, y, s, p) {
        s *= K * 0.9
        const w = 200 * s, h = 170 * s;
        draw(g, rc.rectangle(x - w / 2, y - h, w, h, ink({ fill: '#fff', fillStyle: 'solid' })));
        draw(g, rc.rectangle(x - w / 2, y - h, w, 44 * s, ink({ fill: p.colour || '#b91c1c', fillStyle: 'solid' })));
        for (const dx of [-50, 50]) draw(g, rc.line(x + dx * s, y - h - 16 * s, x + dx * s, y - h + 14 * s, ink({ strokeWidth: 5 })));
        if (p.label) textBlock(g, wrap(p.label, 12), x, y - h + 90 * s, 28 * s, { anchor: 'middle' });
      },
      terminal(g, rc, x, y, s, p) {
        s *= K * 0.95
        const w = 460 * s, h = 260 * s;
        draw(g, rc.rectangle(x - w / 2, y - h, w, h, ink({ fill: '#0d1117', fillStyle: 'solid', strokeWidth: 3 })));
        (p.lines || ['$ _']).slice(0, 7).forEach((l, i) => { const t = el('text', { x: x - w / 2 + 18 * s, y: y - h + (40 + i * 32) * s, 'font-family': 'ui-monospace, Menlo, monospace', 'font-size': 20 * s, fill: i === 0 ? '#3fb950' : '#e6edf3' }, g); t.textContent = l.length > 38 ? l.slice(0, 37) + '…' : l; });
      },
      phoneqr(g, rc, x, y, s, p) {
        s *= K
        const w = 150 * s, h = 270 * s;
        draw(g, rc.rectangle(x - w / 2, y - h, w, h, ink({ fill: '#111827', fillStyle: 'solid', strokeWidth: 3 })));
        qrModules(g, rc, x - 56 * s, y - h + 60 * s, 112 * s, p.seed || hash(p.text));
        if (p.text) textBlock(g, [p.text.length > 22 ? p.text.slice(0, 20) + '…' : p.text], x, y - h + 42 * s, 13 * s, { anchor: 'middle', fill: '#e5e7eb', font: 'ui-monospace, Menlo, monospace' });
        label(g, p.label, x, y + 34 * s, 22 * s);
      },
      padlock(g, rc, x, y, s, p) { padlock(g, rc, x, y, 2 * s, p.open); label(g, p.label, x, y + 34 * s, 22 * s); },
    };
  };
})();
