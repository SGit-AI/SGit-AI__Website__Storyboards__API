/* export.js: a storyboard's panels as files, made in the browser from the same data and the same drawing as the deck.
 * Needs storyboard.js (and Rough.js) loaded first. Nothing leaves the browser; every function returns a string or a Blob.
 *
 *   StoryboardExport.svg(storyboard, cast, i, opts)        -> Promise<string>  one panel, standalone SVG
 *        opts.animated   true: the panel draws itself when opened (CSS inside the file, no script)
 *        opts.fonts      'link' (default: @font-face pointing at this release's fonts) | 'embed' (fonts inlined) | 'none'
 *   StoryboardExport.sheet(storyboard, cast, opts)          -> Promise<string>  every panel on one SVG, opts.cols (default 4)
 *   StoryboardExport.image(storyboard, cast, i, opts)       -> Promise<Blob>    PNG or JPEG: opts.type 'image/png' | 'image/jpeg',
 *        opts.width (default 1600; 480 makes a thumbnail), opts.quality (JPEG, default 0.86)
 *   StoryboardExport.download(blobOrString, filename, type)  saves a file
 *
 * Seeds are the deck's (11 + panel index), so an exported panel is the panel a reader saw.
 */
(function () {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const VERSION = 'v0.1.0';
  // where this file was served from: the fonts sit beside it, in the same immutable release
  const BASE = (document.currentScript && document.currentScript.src || location.href).replace(/[^/]*$/, '');
  const FONTS = [['Caveat', 700, 'fonts/caveat-700-latin.woff2'], ['Patrick Hand', 400, 'fonts/patrick-hand-400-latin.woff2']];
  const ANIM = 'path[pathLength]{stroke-dasharray:1;animation:sb-draw 1.1s ease-out both}' +
    '.actor{animation:sb-in .6s ease-out both;animation-delay:var(--d,0s)}' +
    '.pop{animation:sb-pop .45s cubic-bezier(.2,1.4,.5,1) both;animation-delay:var(--d,.5s);transform-box:fill-box;transform-origin:center}' +
    '@keyframes sb-draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}' +
    '@keyframes sb-in{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}' +
    '@keyframes sb-pop{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:none}}' +
    '@media (prefers-reduced-motion:reduce){*{animation:none!important}}';

  const kit = () => {
    if (!window.StoryboardKit) throw new Error('export.js: load storyboard.js first');
    return window.StoryboardKit;
  };
  let embedded = null;
  async function fontFaces(mode) {
    if (mode === 'none') return '';
    if (mode === 'embed') {
      if (!embedded) {
        embedded = Promise.all(FONTS.map(async ([family, weight, path]) => {
          const buf = new Uint8Array(await (await fetch(BASE + path)).arrayBuffer());
          let bin = '';
          for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
          return `@font-face{font-family:'${family}';font-weight:${weight};src:url(data:font/woff2;base64,${btoa(bin)}) format('woff2')}`;
        })).then((a) => a.join(''));
      }
      return embedded;
    }
    return FONTS.map(([family, weight, path]) => `@font-face{font-family:'${family}';font-weight:${weight};src:url(${BASE}${path}) format('woff2')}`).join('');
  }

  function drawn(storyboard, cast, i, footer) {
    const svg = document.createElementNS(NS, 'svg');
    kit().drawScene(svg, storyboard.scenes[i], cast, { seed: 11 + i, footer: footer === false ? null : `${storyboard.title} \u00b7 ${i + 1}/${storyboard.scenes.length}` });
    return svg;
  }
  function serialise(svg, css, title, w, h) {
    svg.setAttribute('xmlns', NS);
    svg.setAttribute('width', w || kit().W);
    svg.setAttribute('height', h || kit().H);
    if (title) { const t = document.createElementNS(NS, 'title'); t.textContent = title; svg.insertBefore(t, svg.firstChild); }
    if (css) { const s = document.createElementNS(NS, 'style'); s.textContent = css; svg.insertBefore(s, svg.firstChild); }
    return '<?xml version="1.0" encoding="UTF-8"?>\n<!-- drawn by api.storyboards.sgit.ai ' + VERSION + ' (storyboard.js ' + kit().VERSION + ') -->\n' + new XMLSerializer().serializeToString(svg);
  }

  async function svg(storyboard, cast, i, opts) {
    opts = opts || {};
    const s = drawn(storyboard, cast, i, opts.footer);
    const css = (await fontFaces(opts.fonts || 'link')) + (opts.animated ? ANIM : '');
    return serialise(s, css, `${storyboard.title}, panel ${i + 1}`);
  }

  async function sheet(storyboard, cast, opts) {
    opts = opts || {};
    const K = kit(), cols = opts.cols || 4, n = storyboard.scenes.length, rows = Math.ceil(n / cols), gap = 40;
    const out = document.createElementNS(NS, 'svg');
    const w = cols * K.W + (cols + 1) * gap, h = rows * K.H + (rows + 1) * gap;
    out.setAttribute('viewBox', `0 0 ${w} ${h}`);
    const bg = document.createElementNS(NS, 'rect');
    bg.setAttribute('width', w); bg.setAttribute('height', h); bg.setAttribute('fill', '#ffffff');
    out.appendChild(bg);
    storyboard.scenes.forEach((_, i) => {
      const p = drawn(storyboard, cast, i, opts.footer);
      p.setAttribute('x', gap + (i % cols) * (K.W + gap));
      p.setAttribute('y', gap + Math.floor(i / cols) * (K.H + gap));
      p.setAttribute('width', K.W); p.setAttribute('height', K.H);
      out.appendChild(p);
    });
    return serialise(out, await fontFaces(opts.fonts || 'link'), `${storyboard.title}, every panel`, w, h);
  }

  async function image(storyboard, cast, i, opts) {
    opts = opts || {};
    const K = kit(), width = opts.width || K.W, height = Math.round(width * K.H / K.W);
    // an SVG drawn into a canvas cannot fetch anything, so the fonts go inside it
    const text = await svg(storyboard, cast, i, { fonts: 'embed', footer: opts.footer });
    const url = URL.createObjectURL(new Blob([text], { type: 'image/svg+xml' }));
    try {
      const img = new Image();
      await new Promise((ok, fail) => { img.onload = ok; img.onerror = () => fail(new Error('export.js: the SVG did not load as an image')); img.src = url; });
      if (img.decode) await img.decode().catch(() => {});
      const c = document.createElement('canvas');
      c.width = width; c.height = height;
      const g = c.getContext('2d');
      g.fillStyle = K.PAPER; g.fillRect(0, 0, width, height);
      g.drawImage(img, 0, 0, width, height);
      const type = opts.type || 'image/png';
      return await new Promise((ok) => c.toBlob(ok, type, type === 'image/jpeg' ? (opts.quality || 0.86) : undefined));
    } finally {
      URL.revokeObjectURL(url);
    }
  }

  function download(data, filename, type) {
    const blob = data instanceof Blob ? data : new Blob([data], { type: type || 'application/octet-stream' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = filename;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  window.StoryboardExport = Object.freeze({ VERSION, BASE, svg, sheet, image, download });
})();
