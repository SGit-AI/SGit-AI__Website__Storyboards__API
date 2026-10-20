/* storyboards.sgit.ai: the page's own behaviour. The theme switch (kept in this browser only), the copy buttons, and the
 * exports on a storyboard's page, which hand the page's own data to the kit's export.js (api.storyboards.sgit.ai) so a
 * downloaded panel is the panel on the screen. */
(function () {
  'use strict';
  const KEY = 'api.storyboards.sgit.ai.theme';
  const root = document.documentElement;
  const dark = () => matchMedia('(prefers-color-scheme: dark)').matches;
  const apply = (t) => { root.dataset.theme = t || (dark() ? 'night' : 'light'); };
  let saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* the default holds */ }
  apply(saved);

  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.querySelector('.theme');
    if (btn) {
      const label = () => { btn.textContent = root.dataset.theme === 'night' ? 'light' : 'dark'; };
      label();
      btn.addEventListener('click', () => {
        const t = root.dataset.theme === 'night' ? 'light' : 'night';
        apply(t); label();
        try { localStorage.setItem(KEY, t); } catch (e) { /* this visit only */ }
      });
    }
    document.querySelectorAll('[data-copy]').forEach((b) => b.addEventListener('click', async () => {
      const text = document.querySelector(b.dataset.copy).textContent;
      try { await navigator.clipboard.writeText(text); b.textContent = 'Copied'; } catch (e) { b.textContent = 'Select and copy'; }
      setTimeout(() => { b.textContent = 'Copy'; }, 1600);
    }));
  });

})();
