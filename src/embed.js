/* embed.js: <sg-storyboard>, a storyboard on any page, from one script tag. It loads the rest of this release (fonts,
 * styles, Rough.js, the kit and any prop packs) from beside itself, once per page, so an embed pinned to a version keeps
 * drawing exactly what it drew the day it was pinned.
 *
 *   <script src="https://api.storyboards.sgit.ai/v0/v0.1/v0.1.0/embed.js" defer></script>
 *   <sg-storyboard src="https://storyboards.sgit.ai/pki/the-first-key/bundle.json" view="deck"></sg-storyboard>
 *
 * Attributes: src (a bundle: { storyboard, cast, packs }) or storyboard + cast (two URLs); view: deck (default), grid,
 * script or panel; panel: the panel to show when view is panel (1-based, default 1); packs: prop packs to load
 * (comma-separated, e.g. "security"), added to any the bundle names. Light DOM, so the page's own styles may dress it.
 */
(function () {
  'use strict';
  const VERSION = 'v0.1.0';
  const BASE = (document.currentScript && document.currentScript.src || '').replace(/[^/]*$/, '');
  const loaded = {};
  const once = (key, make) => (loaded[key] = loaded[key] || make());
  const css = (path) => once(path, () => new Promise((ok, fail) => {
    const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = BASE + path; l.onload = ok; l.onerror = () => fail(new Error('sg-storyboard: could not load ' + path));
    document.head.appendChild(l);
  }));
  const js = (path) => once(path, () => new Promise((ok, fail) => {
    const s = document.createElement('script'); s.src = BASE + path; s.async = false; s.onload = ok; s.onerror = () => fail(new Error('sg-storyboard: could not load ' + path));
    document.head.appendChild(s);
  }));
  const PACKS = ['security'];
  async function kit(packs) {
    await Promise.all([css('fonts.css'), css('storyboard.css')]);
    await js('vendor/rough-4.6.6.js');
    await Promise.all(packs.filter((p) => PACKS.includes(p)).map((p) => js(`props/${p}.js`)));
    await js('storyboard.js');
    return window.StoryboardKit;
  }
  const getJSON = async (url) => {
    const r = await fetch(url);
    if (!r.ok) throw new Error(`sg-storyboard: ${url} answered ${r.status}`);
    return r.json();
  };
  const h = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; };
  const button = (cls, text, title) => { const b = h('button', cls, text); b.type = 'button'; if (title) b.title = title; return b; };

  function toolbar() {
    const bar = h('div', 'sb-tools'); bar.setAttribute('role', 'toolbar'); bar.setAttribute('aria-label', 'How to view the panels');
    const views = h('span', 'sb-views'); views.setAttribute('role', 'group'); views.setAttribute('aria-label', 'View');
    [['deck', 'Deck'], ['grid', 'Grid'], ['script', 'Script']].forEach(([v, t]) => { const b = button('', t); b.dataset.view = v; views.appendChild(b); });
    bar.appendChild(views);
    const per = h('label', 'sb-for-grid', 'Per row '), sel = h('select', 'sb-cols');
    for (let n = 1; n <= 6; n++) { const o = h('option', '', String(n)); o.value = String(n); sel.appendChild(o); }
    per.appendChild(sel); bar.appendChild(per);
    const box = (cls, text, extra) => { const l = h('label', extra || ''), c = h('input', cls); c.type = 'checkbox'; l.appendChild(c); l.appendChild(document.createTextNode(' ' + text)); return l; };
    bar.appendChild(box('sb-anim', 'Animation'));
    bar.appendChild(box('sb-showtext', 'Text', 'sb-for-grid'));
    bar.appendChild(button('sb-playall sb-for-grid', 'Play in order'));
    const f = h('input', 'sb-filter sb-for-list'); f.type = 'search'; f.placeholder = 'Filter: a word, a name, a mood'; f.setAttribute('aria-label', 'Filter the panels');
    bar.appendChild(f);
    return bar;
  }
  function deckMarkup() {
    const d = h('div', 'sb-deck'); d.hidden = true;
    d.appendChild(h('div', 'sb-track'));
    const bar = h('div', 'sb-bar');
    const prev = button('sb-prev', '\u2190'); prev.setAttribute('aria-label', 'Previous panel');
    const next = button('sb-next', '\u2192'); next.setAttribute('aria-label', 'Next panel');
    [prev, h('span', 'sb-count'), next, button('sb-replay', '\u25b6 Play', 'Play this panel (p)'), button('sb-notes-toggle', 'Notes', 'Notes (n)'), button('sb-full', 'Full screen', 'Full screen (f)')].forEach((e) => bar.appendChild(e));
    d.appendChild(bar);
    d.appendChild(h('div', 'sb-notes'));
    return d;
  }

  class SgStoryboard extends HTMLElement {
    connectedCallback() {
      if (this._started) return;
      this._started = true;
      this.render().catch((e) => { this.textContent = e.message; this.setAttribute('data-error', ''); });
    }
    async render() {
      const src = this.getAttribute('src');
      let data;
      if (src) data = await getJSON(new URL(src, location.href).href);
      else data = { storyboard: await getJSON(this.getAttribute('storyboard')), cast: await getJSON(this.getAttribute('cast')) };
      const packs = (data.packs || []).concat((this.getAttribute('packs') || '').split(',').map((s) => s.trim()).filter(Boolean));
      const K = await kit(packs);
      const sb = data.storyboard, view = this.getAttribute('view') || 'deck';
      this.textContent = '';
      this.classList.add('sg-storyboard');
      if (view === 'panel') {
        const i = Math.min(Math.max(parseInt(this.getAttribute('panel') || '1', 10) - 1, 0), sb.scenes.length - 1);
        const fig = h('figure', 'sb-panel'), svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        fig.appendChild(svg); this.appendChild(fig);
        K.drawScene(svg, sb.scenes[i], data.cast, { seed: 11 + i, footer: `${sb.title} \u00b7 ${i + 1}/${sb.scenes.length}` });
        fig.title = 'Click to play this panel';
        fig.addEventListener('click', () => K.play(fig));
        return;
      }
      const root = h('div', 'sb-viewer');
      root.appendChild(toolbar());
      root.appendChild(deckMarkup());
      root.appendChild(Object.assign(h('div', 'sb-grid'), { hidden: true }));
      root.appendChild(Object.assign(h('div', 'sb-script'), { hidden: true }));
      const payload = h('script', 'sb-data'); payload.type = 'application/json';
      payload.textContent = JSON.stringify({ storyboard: sb, cast: data.cast });
      root.appendChild(payload);
      this.appendChild(root);
      if (['deck', 'grid', 'script'].includes(view)) root.dataset.startView = view;
      K.wire(this);
    }
  }
  if (!customElements.get('sg-storyboard')) customElements.define('sg-storyboard', SgStoryboard);
  window.SgStoryboard = { VERSION, BASE, kit };
})();
