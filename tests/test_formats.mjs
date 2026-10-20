// formats.js in Node, against the real storyboards in tests/fixtures (a gen-z board and a pki board), no mocks.
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
const require = createRequire(import.meta.url);
const F = require(process.env.SB_SRC ? process.env.SB_SRC + '/formats.js' : '../src/formats.js');
const load = (n) => JSON.parse(readFileSync(new URL(`fixtures/${n}.bundle.json`, import.meta.url), 'utf8'));
let n = 0;
const t = (name, fn) => { fn(); n++; console.log('ok', name); };

for (const name of ['gen-z', 'pki']) {
  const { storyboard: sb, cast, packs } = load(name);
  const props = packs.flatMap((p) => F.PACKS[p]);
  t(`${name}: validates clean`, () => assert.deepEqual(F.validate(sb, cast, { props }), []));
  t(`${name}: markdown has a heading per panel`, () => {
    const md = F.toMarkdown(sb, cast);
    assert.equal((md.match(/^## \d+\. /gm) || []).length, sb.scenes.length);
    assert.ok(md.startsWith(`# ${sb.title}`));
    assert.equal(F.toMarkdown(sb, cast), md, 'deterministic');
  });
  t(`${name}: graph is connected and well formed`, () => {
    const g = F.toGraph(sb, cast);
    const ids = new Set(g.nodes.map((x) => x.id));
    assert.equal(ids.size, g.nodes.length, 'unique ids');
    for (const e of g.edges) assert.ok(ids.has(e.from) && ids.has(e.to), `${e.from} -> ${e.to}`);
    assert.equal(g.edges.filter((e) => e.type === 'has_panel').length, sb.scenes.length);
    assert.equal(g.edges.filter((e) => e.type === 'next').length, sb.scenes.length - 1);
    const speakers = new Set(sb.scenes.flatMap((s) => (s.cast || []).filter((c) => c.says).map((c) => 'character:' + c.who)));
    for (const s of speakers) assert.ok(g.edges.some((e) => e.from === s && (e.type === 'says' || e.type === 'thinks')), s);
  });
}
t('negative control: a broken storyboard fails, naming each fault', () => {
  const { storyboard: sb, cast } = load('pki');
  const broken = JSON.parse(JSON.stringify(sb));
  broken.scenes[1].cast[0].who = 'nobody';
  broken.scenes[1].cast[0].mood = 'furious';
  broken.scenes[2].kind = 'collage';
  const errs = F.validate(broken, cast, { props: F.PACKS.security });
  assert.ok(errs.some((e) => e.includes('"nobody" is not in the cast')), errs.join('\n'));
  assert.ok(errs.some((e) => e.includes('unknown mood "furious"')));
  assert.ok(errs.some((e) => e.includes('unknown kind "collage"')));
  // without the pack, the pki props are unknown
  assert.ok(F.validate(sb, cast).some((e) => e.includes('unknown prop "vault"')));
});
console.log(`test_formats: ${n} passed`);
