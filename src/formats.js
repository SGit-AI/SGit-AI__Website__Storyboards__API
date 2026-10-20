/* formats.js: a storyboard in the other shapes it can take, with no DOM and no drawing. Runs in a browser (window.StoryboardFormats)
 * and in Node (require / import), so a site's build and a reader's browser produce the same bytes from the same data.
 *
 *   validate(storyboard, cast, { props })   -> [errors]      the checks every site's build ran by hand until now
 *   toMarkdown(storyboard, cast, { url })   -> string        the script: every panel as text, a .md twin
 *   toGraph(storyboard, cast, { url })      -> object        a semantic graph: nodes, and edges that carry the meaning
 *   toText(scene, cast)                     -> string        one panel as one paragraph (alt text, search)
 *   stats(storyboard)                       -> object        panels, kinds, cast, words
 *
 * The vocabulary below is the renderer's (storyboard.js exports the same lists as StoryboardKit.VOCAB; the tests hold the
 * two equal). A storyboard may use a prop from a prop pack: pass the pack's kinds in { props }.
 */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.StoryboardFormats = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const VERSION = 'v0.1.0';
  const VOCAB = Object.freeze({
    kinds: ['cover', 'scene', 'evidence', 'punchline', 'spectrum', 'map', 'graph'],
    poses: ['stand', 'point', 'wave', 'arms-up', 'shrug', 'think', 'sit'],
    moods: ['neutral', 'happy', 'excited', 'calm', 'worried', 'sad', 'surprised', 'thinking', 'confused', 'determined'],
    settings: ['none', 'office', 'interview', 'street', 'night', 'classroom'],
    props: ['laptop', 'desk', 'book', 'board', 'phone', 'sign'],
  });
  const PACKS = Object.freeze({
    security: ['key', 'vault', 'qr', 'envelope', 'record', 'server', 'arrow', 'mark', 'calendar', 'terminal', 'phoneqr', 'padlock'],
  });

  const label = (sc) => sc.caption || sc.punchline || sc.title || '';
  const byId = (cast) => {
    const m = {};
    ((cast && cast.characters) || []).forEach((c) => { m[c.id] = c; });
    return m;
  };

  // ------------------------------------------------------------ validate
  function validate(sb, cast, opts) {
    opts = opts || {};
    const errors = [], who = byId(cast), props = VOCAB.props.concat(opts.props || []);
    const at = (i) => `${sb && sb.slug ? sb.slug : 'storyboard'} panel ${i + 1}`;
    if (!sb || typeof sb !== 'object') return ['not a storyboard object'];
    for (const k of ['slug', 'title', 'scenes']) if (!sb[k]) errors.push(`storyboard: missing "${k}"`);
    if (sb.slug && !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(sb.slug)) errors.push(`storyboard: slug "${sb.slug}" is not lower-case-with-dashes`);
    (sb.scenes || []).forEach((sc, i) => {
      const kind = sc.kind || 'scene';
      if (!VOCAB.kinds.includes(kind)) errors.push(`${at(i)}: unknown kind "${kind}" (the renderer knows ${VOCAB.kinds.join(', ')})`);
      if (!VOCAB.settings.includes(sc.setting || 'none')) errors.push(`${at(i)}: unknown setting "${sc.setting}"`);
      (sc.props || []).forEach((p) => { if (!props.includes(p.kind)) errors.push(`${at(i)}: unknown prop "${p.kind}" (load its pack and pass its kinds)`); });
      (sc.cast || []).forEach((c) => {
        if (!who[c.who]) errors.push(`${at(i)}: "${c.who}" is not in the cast`);
        if (!VOCAB.poses.includes(c.pose || 'stand')) errors.push(`${at(i)}: unknown pose "${c.pose}" for ${c.who}`);
        if (!VOCAB.moods.includes(c.mood || 'neutral')) errors.push(`${at(i)}: unknown mood "${c.mood}" for ${c.who}`);
        if (c.x != null && (c.x < 0 || c.x > 1)) errors.push(`${at(i)}: x for ${c.who} is outside 0..1`);
      });
      if (kind === 'evidence' && !(sc.evidence && (sc.evidence.quote || sc.evidence.bars))) errors.push(`${at(i)}: evidence needs a quote or bars`);
      if (kind === 'cover' && !sc.title) errors.push(`${at(i)}: a cover needs a title`);
      if (kind === 'punchline' && !sc.punchline) errors.push(`${at(i)}: a punchline panel needs its punchline`);
      if (kind === 'map' && !(sc.map && sc.map.nodes)) errors.push(`${at(i)}: a map needs map.nodes`);
      if (kind === 'graph' && !(sc.graph && sc.graph.nodes)) errors.push(`${at(i)}: a graph needs graph.nodes`);
      for (const g of [sc.map, sc.graph].filter(Boolean)) {
        const ids = new Set((g.nodes || []).map((n) => n.id));
        (g.links || []).forEach(([a, b]) => { if (!ids.has(a) || !ids.has(b)) errors.push(`${at(i)}: link ${a} -> ${b} names a missing node`); });
        (g.edges || []).forEach((e) => { if (!ids.has(e.from) || !ids.has(e.to)) errors.push(`${at(i)}: edge ${e.from} -> ${e.to} names a missing node`); });
      }
    });
    return errors;
  }

  // ------------------------------------------------------------ one panel as text
  function toText(sc, cast) {
    const who = byId(cast), out = [];
    if (sc.kind === 'cover') out.push(sc.title + (sc.subtitle ? ': ' + sc.subtitle : ''));
    else if (label(sc)) out.push(label(sc) + '.');
    if (sc.punchline && sc.caption) out.push('“' + sc.punchline + '”');
    (sc.cast || []).forEach((c) => { if (c.says) out.push(`${(who[c.who] || {}).name || c.who} ${c.thinks ? 'thinks' : 'says'}: “${c.says}”`); });
    const ev = sc.evidence;
    if (ev && ev.quote) out.push('“' + ev.quote + '”' + (ev.source ? ' (' + ev.source + ')' : ''));
    if (ev && ev.bars) out.push((ev.title ? ev.title + ': ' : '') + ev.bars.map((b) => `${b.label} ${b.shown || b.value}`).join(', '));
    if (sc.stops) out.push(sc.stops.map((s) => s.label).join(' → '));
    return out.join(' ');
  }

  // ------------------------------------------------------------ markdown: the script
  const md = (t) => String(t == null ? '' : t).replace(/([\\`*_[\]<>|])/g, '\\$1');
  function toMarkdown(sb, cast, opts) {
    opts = opts || {};
    const who = byId(cast), L = [];
    L.push(`# ${md(sb.title)}`, '');
    if (sb.subtitle) L.push(`> ${md(sb.subtitle)}`, '');
    const meta = [sb.status && `Status: ${md(sb.status)}`, sb.by && `By: ${md(sb.by)}`, sb.series && `Series: ${md(sb.series)}`, `${(sb.scenes || []).length} panels`].filter(Boolean);
    L.push(meta.join(' · '), '');
    if (opts.url) L.push(`*Drawn at <${opts.url}>; the data is [storyboard.json](storyboard.json), the cast [cast.json](${opts.castHref || 'cast.json'}).*`, '');
    if (sb.rule) L.push(`*${md(sb.rule)}*`, '');
    (sb.scenes || []).forEach((sc, i) => {
      L.push(`## ${i + 1}. ${md(label(sc)) || md(sc.kind || 'scene')}`, '');
      L.push(`*${md(sc.kind || 'scene')}${sc.setting && sc.setting !== 'none' ? ', setting: ' + md(sc.setting) : ''}*`, '');
      if (sc.kind === 'cover' && sc.subtitle) L.push(md(sc.subtitle), '');
      if (sc.punchline && sc.caption) L.push(`> **${md(sc.punchline)}**`, '');
      else if (sc.kind === 'punchline' && sc.punchline) L.push(`> **${md(sc.punchline)}**`, '');
      (sc.cast || []).forEach((c) => {
        const name = md((who[c.who] || {}).name || c.who), how = `(${md(c.pose || 'stand')}, ${md(c.mood || 'neutral')})`;
        L.push(c.says ? `- **${name}** ${how} ${c.thinks ? 'thinks' : 'says'}: “${md(c.says)}”` : `- **${name}** ${how}`);
      });
      if ((sc.cast || []).length) L.push('');
      const ev = sc.evidence;
      if (ev && ev.quote) L.push(`> “${md(ev.quote)}”`, ...(ev.source ? ['>', `> Source: ${md(ev.source)}`] : []), '');
      if (ev && ev.bars) {
        L.push(ev.title ? `**${md(ev.title)}**` : '', '', '| | |', '|---|---|');
        ev.bars.forEach((b) => L.push(`| ${md(b.label)} | ${md(b.shown || b.value)} |`));
        L.push('');
      }
      if (sc.stops) L.push(sc.stops.map((s) => md(s.label) + (s.note ? ` (${md(s.note)})` : '')).join(' → '), '');
      const g = sc.map || sc.graph;
      if (g && g.nodes) L.push(`${sc.kind === 'map' ? 'Map' : 'Graph'}: ${g.nodes.map((n) => md(n.label)).join(', ')}`, '');
      const props = (sc.props || []).map((p) => md(p.kind) + (p.lines ? ` (${p.lines.map(md).join(' / ')})` : p.label ? ` (${md(p.label)})` : ''));
      if (props.length) L.push(`Props: ${props.join(', ')}`, '');
      if (sc.note) L.push(md(sc.note), '');
      if (sc.source) L.push(`*Source: ${md(sc.source)}${sc.not_a_quote ? ' (not a quote)' : ''}*`, '');
    });
    return L.join('\n').replace(/\n{3,}/g, '\n\n').trimEnd() + '\n';
  }

  // ------------------------------------------------------------ the semantic graph
  // Nodes are things (the storyboard, its panels, the characters, the props, the sources, the shelf); edges carry the
  // meaning, each a verb a reader can say aloud: "panel 3 features Noor", "Noor says 'Two ways'".
  function toGraph(sb, cast, opts) {
    opts = opts || {};
    const who = byId(cast), nodes = [], edges = [], seen = new Set();
    const node = (id, type, lbl, extra) => { if (!seen.has(id)) { seen.add(id); nodes.push(Object.assign({ id, type, label: lbl }, extra || {})); } return id; };
    const edge = (from, type, to, extra) => edges.push(Object.assign({ from, type, to }, extra || {}));
    const S = node(`storyboard:${sb.slug}`, 'storyboard', sb.title, { subtitle: sb.subtitle || '', status: sb.status || '', url: opts.url || '' });
    if (sb.series) edge(S, 'part_of', node(`series:${sb.series}`, 'series', opts.seriesTitle || sb.series));
    if (sb.shelf) edge(S, 'on_shelf', node(`shelf:${sb.shelf}`, 'shelf', sb.shelf));
    if (sb.by) edge(S, 'made_by', node(`author:${sb.by.split(',')[0].trim()}`, 'author', sb.by.split(',')[0].trim()));
    let prev = null;
    (sb.scenes || []).forEach((sc, i) => {
      const P = node(`panel:${sb.slug}/${i + 1}`, 'panel', label(sc) || `${sc.kind || 'scene'} ${i + 1}`, { n: i + 1, kind: sc.kind || 'scene', text: toText(sc, cast) });
      edge(S, 'has_panel', P, { n: i + 1 });
      if (prev) edge(prev, 'next', P);
      prev = P;
      (sc.cast || []).forEach((c) => {
        const C = node(`character:${c.who}`, (who[c.who] || {}).kind === 'agent' ? 'agent' : 'character', (who[c.who] || {}).name || c.who);
        edge(P, 'features', C, { pose: c.pose || 'stand', mood: c.mood || 'neutral' });
        if (c.says) edge(C, c.thinks ? 'thinks' : 'says', P, { text: c.says });
      });
      (sc.props || []).forEach((p) => edge(P, 'shows', node(`prop:${p.kind}`, 'prop', p.kind)));
      if (sc.source) edge(P, sc.not_a_quote ? 'drawn_from' : 'quotes', node(`source:${sc.source}`, 'source', sc.source));
      if (sc.evidence && sc.evidence.source) edge(P, 'cites', node(`source:${sc.evidence.source}`, 'source', sc.evidence.source));
      if (sc.setting && sc.setting !== 'none') edge(P, 'set_in', node(`setting:${sc.setting}`, 'setting', sc.setting));
    });
    return { what: 'A storyboard as a semantic graph: nodes are things, edges carry the meaning. Generated by formats.js ' + VERSION + ' from the storyboard and its cast.', format: 'storyboards.sgit.ai/graph/v1', storyboard: sb.slug, nodes, edges };
  }

  function stats(sb) {
    const kinds = {}, cast = new Set();
    let words = 0;
    (sb.scenes || []).forEach((sc) => {
      kinds[sc.kind || 'scene'] = (kinds[sc.kind || 'scene'] || 0) + 1;
      (sc.cast || []).forEach((c) => { cast.add(c.who); if (c.says) words += c.says.split(/\s+/).length; });
    });
    return { panels: (sb.scenes || []).length, kinds, cast: [...cast].sort(), words };
  }

  return Object.freeze({ VERSION, VOCAB, PACKS, validate, toText, toMarkdown, toGraph, stats, label });
});
