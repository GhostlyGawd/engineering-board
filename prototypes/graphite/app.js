/* Progressive enhancements only; source pages and all records exist in HTML. */
(() => {
  const root = document.documentElement;
  const announce = message => { document.getElementById('announcement').textContent = message; };
  const themeButton = document.querySelector('.theme');
  const themeIcon = themeButton?.querySelector('img');
  function setTheme(theme) {
    root.dataset.theme = theme;
    const next = theme === 'dark' ? 'light' : 'dark';
    if (themeButton) {
      themeButton.setAttribute('aria-label', `Switch to ${next} theme`);
      themeButton.title = `Switch to ${next} theme`;
      themeIcon.src = themeIcon.src.replace(/(sun|moon)\.svg$/, `${next === 'light' ? 'sun' : 'moon'}.svg`);
    }
  }
  let savedTheme;
  try { savedTheme = localStorage.getItem('eb-graphite-theme'); } catch (_) { /* Local storage may be unavailable. */ }
  setTheme(savedTheme === 'light' ? 'light' : 'dark');
  themeButton?.addEventListener('click', () => {
    const theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    setTheme(theme);
    try { localStorage.setItem('eb-graphite-theme', theme); } catch (_) { /* Theme still works for this page. */ }
    announce(`${theme === 'dark' ? 'Dark' : 'Light'} theme selected.`);
  });
  const panels = [...document.querySelectorAll('[data-panel]')];
  const findings = [...document.querySelectorAll('.finding')];
  function select(id, focus = false) {
    const active = panels.find(panel => panel.dataset.panel === id);
    if (!active) return;
    panels.forEach(panel => { panel.hidden = panel !== active; });
    findings.forEach(link => {
      if (link.dataset.select === id) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    if (focus) { active.focus({ preventScroll: true }); active.scrollIntoView({ block: 'nearest' }); }
  }
  const selectedHash = () => /^#entry-(H001|B00[123])$/.test(location.hash) ? location.hash.slice(7) : 'H001';
  if (panels.length) {
    select(selectedHash());
    document.querySelectorAll('[data-select]').forEach(link => link.addEventListener('click', event => {
      event.preventDefault();
      const id = link.dataset.select;
      history.pushState(null, '', `#entry-${id}`);
      select(id, true);
      announce(`${id} selected. ${panels.find(panel => panel.dataset.panel === id).querySelector('h3').textContent}`);
    }));
    window.addEventListener('hashchange', () => select(selectedHash()));
    window.addEventListener('popstate', () => select(selectedHash()));
  }
  const search = document.querySelector('.search');
  const input = document.getElementById('finding-search');
  function filter() {
    const query = input.value.trim().toLocaleLowerCase();
    let count = 0;
    findings.forEach(link => { link.hidden = !link.dataset.search.toLocaleLowerCase().includes(query); if (!link.hidden) count++; });
    document.querySelector('.no-results').hidden = count !== 0;
    announce(`${count} ${count === 1 ? 'finding' : 'findings'} match${count === 1 ? 'es' : ''}${query ? ` “${input.value.trim()}”` : ''}.`);
  }
  function resetSearch() { input.value = ''; filter(); input.focus(); }
  search?.addEventListener('submit', event => event.preventDefault());
  input?.addEventListener('input', filter);
  search?.addEventListener('reset', event => { event.preventDefault(); resetSearch(); });
  document.querySelector('[data-reset]')?.addEventListener('click', resetSearch);
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const target = document.getElementById(button.dataset.copy);
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(target.textContent);
      announce(button.dataset.copy === 'install-command' ? 'Installation commands copied. Run them in your own terminal.' : 'Initialization prompt copied. Paste it in a new Codex session.');
      const original = button.innerHTML;
      button.textContent = 'Copied';
      window.setTimeout(() => { button.innerHTML = original; }, 1800);
    } catch (_) {
      const selection = window.getSelection();
      const range = document.createRange(); range.selectNodeContents(target); selection.removeAllRanges(); selection.addRange(range);
      announce('Clipboard unavailable. Text selected; use your device’s copy command.');
    }
  }));
  root.classList.add('enhanced');
})();
