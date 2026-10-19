import { $, $$, html, debounce, download, matches } from './util.js';
import { db, loadAll, TYPE_LABEL, isOwned, L } from './data.js';
import { profile, update, subscribe, DLCS, exportProfile, importProfile, resetProfile } from './store.js';
import { icon } from './components.js';
import { toast, openDialog, closeDialog } from './ui.js';
import { openImport } from './import.js';
import * as views from './views/index.js';

// ---------- Navigation ----------
const I = {
  home: '<path d="M3 11.5 12 4l9 7.5M5.5 9.5V20h13V9.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
  builds: '<path d="M5 19 19 5m-4 0h4v4M5 5l5 5m4 4 5 5m-4 0h4v-4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
  workshop: '<path d="M14.5 6.5a4 4 0 0 0-5.3 5.3L4 17l3 3 5.2-5.2a4 4 0 0 0 5.3-5.3l-2.3 2.3-2.3-.7-.7-2.3z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
  arsenal: '<path d="M14 4h6v6L9 21l-6-6zM12 12l-4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
  mutations: '<path d="M12 3c2 3 5 4.5 5 8.5a5 5 0 0 1-10 0C7 7.5 10 6 12 3zM12 14v7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
  tiers: '<path d="M4 6h16M4 12h11M4 18h6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
  routes: '<circle cx="5" cy="6" r="2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="19" cy="18" r="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M7 6h7a3 3 0 0 1 0 6H10a3 3 0 0 0 0 6h7" fill="none" stroke="currentColor" stroke-width="1.8"/>',
  world: '<path d="M3 20h18M5 20V9l4-3 4 3v11M13 20v-7l3-2 3 2v7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
  bc: '<circle cx="12" cy="12" r="7" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="2.6" fill="currentColor"/>',
  unlocks: '<rect x="4" y="4" width="16" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="m8 12 3 3 5-6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
  outfits: '<path d="M8 4 4 7l2 4 2-1v10h8V10l2 1 2-4-4-3c-.5 1.7-2 3-4 3S8.5 5.7 8 4z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
  knowledge: '<path d="M5 4h10a4 4 0 0 1 4 4v12H9a4 4 0 0 1-4-4zM5 16a4 4 0 0 1 4-4h10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
};

const NAV = [
  ['Run vorbereiten'],
  ['', 'Übersicht', 'home'],
  ['builds', 'Builds', 'builds'],
  ['workshop', 'Was passt zusammen?', 'workshop'],
  ['routes', 'Routenplaner', 'routes'],
  ['Nachschlagen'],
  ['arsenal', 'Waffen & Skills', 'arsenal'],
  ['mutations', 'Mutationen', 'mutations'],
  ['tiers', 'Tierlisten', 'tiers'],
  ['world', 'Biome & Bosse', 'world'],
  ['bc', 'Boss Cells', 'bc'],
  ['knowledge', 'Wissen & Mechaniken', 'knowledge'],
  ['Fortschritt'],
  ['unlocks', 'Freischaltungen', 'unlocks'],
  ['outfits', 'Outfits', 'outfits'],
];

// Welche Nav-Einträge gelten für Detailseiten als aktiv
const PARENT = { build: 'builds', item: 'arsenal', mutation: 'mutations', biome: 'world', boss: 'world', about: 'knowledge' };

function renderNav(active) {
  const owned = [...db.gear, ...db.mutations].filter(isOwned).length;
  $('#nav').innerHTML = NAV.map(([path, label, ic]) => {
    if (label === undefined) return `<div class="nav-group">${path}</div>`;
    const isActive = active === path;
    const count = path === 'unlocks' ? `<span class="count">${owned}</span>` : '';
    return `<a href="#/${path}" class="${isActive ? 'active' : ''}" ${isActive ? 'aria-current="page"' : ''}><svg viewBox="0 0 24 24" aria-hidden="true">${I[ic]}</svg>${label}${count}</a>`;
  }).join('');
}

function renderLang() {
  const cur = profile.prefs.names;
  $('#lang-select').innerHTML = [['en', 'EN', 'Englische Namen (wie im Wiki)'], ['de', 'DE', 'Deutsche Namen (wie im deutschen Spiel)']]
    .map(([k, t, title]) => `<button data-lang="${k}" aria-pressed="${cur === k}" title="${title}">${t}</button>`).join('');
}

function renderBc() {
  $('#bc-select').innerHTML = [0, 1, 2, 3, 4, 5].map((n) => `<button data-bc="${n}" aria-pressed="${profile.bc === n}" title="${n} Boss Cells">${n}</button>`).join('');
}

// ---------- Router ----------
function parseHash() {
  const h = location.hash.replace(/^#\/?/, '');
  const [pathPart, query = ''] = h.split('?');
  const [path, ...rest] = pathPart.split('/').map((x) => { try { return decodeURIComponent(x); } catch { return x; } });
  const search = new URLSearchParams(query.split('#')[0]);
  return { path: path || '', param: rest.join('/') || null, params: Object.fromEntries(search), search };
}

let current = null;

function route({ keepScroll = false } = {}) {
  const ctx = parseHash();
  const view = views.resolve(ctx.path);
  const main = $('#main');
  const focusKey = keepScroll ? document.activeElement?.dataset?.own : null;
  const scrollY = window.scrollY;

  current?.unmount?.();
  current = view;
  main.innerHTML = String(view.render(ctx));
  view.mount?.(main, ctx);

  renderNav(PARENT[ctx.path] ?? ctx.path);
  renderBc();
  renderLang();
  document.title = `${view.title?.(ctx) ?? 'Übersicht'} · Prisoner's Guide`;

  if (keepScroll) {
    window.scrollTo(0, scrollY);
    if (focusKey) main.querySelector(`[data-own="${CSS.escape(focusKey)}"]`)?.focus({ preventScroll: true });
  } else {
    window.scrollTo(0, 0);
  }
  closeMenu();
}

function rerender() { route({ keepScroll: true }); }

function profileDialog() {
  const d = openDialog(html`
    <div class="dialog-head"><div><div class="eyebrow">Dein Profil</div><h2 id="dialog-title">Einstellungen &amp; Daten</h2></div>
      <button class="icon-btn" data-close aria-label="Schließen">✕</button></div>
    <div class="stack">
      <section><div class="field-label" style="margin-bottom:10px">Spielnamen</div>
        <div class="tabs" style="margin:0"><button data-lang="en" aria-selected="${profile.prefs.names === 'en'}">Englisch (wie im Wiki)</button><button data-lang="de" aria-selected="${profile.prefs.names === 'de'}">Deutsch (wie im Spiel)</button></div>
      </section>
      <section><div class="field-label" style="margin-bottom:10px">Installierte Erweiterungen</div>
        <div class="stack" style="gap:10px">${DLCS.map((x) => html`<label class="switch"><input type="checkbox" data-dlc="${x.id}" ${profile.dlcs.includes(x.id) ? 'checked' : ''}><span class="track"></span>${x.id}${x.note ? html` <span class="dim small">(${x.note})</span>` : ''}</label>`)}</div>
        <p class="small muted" style="margin-top:10px">Builds, Items, Biome und Routen aus abgewählten DLCs werden ausgeblendet oder als gesperrt markiert.</p>
      </section>
      <section><div class="field-label" style="margin-bottom:10px">Savegame</div>
        <p class="small muted" style="margin-bottom:10px">Freischaltungen, Runen und Boss Cells direkt aus deiner user_0.dat übernehmen.${profile.importedAt ? ` Zuletzt importiert: ${new Date(profile.importedAt).toLocaleString('de-DE')}.` : ''}</p>
        <button class="btn sm primary" data-save-import>Savegame importieren</button>
      </section>
      <section><div class="field-label" style="margin-bottom:10px">Fortschritt sichern</div>
        <p class="small muted" style="margin-bottom:10px">Dein Fortschritt wird nur lokal in diesem Browser gespeichert. Exportiere ihn, um ihn auf ein anderes Gerät mitzunehmen.</p>
        <div class="row"><button class="btn sm" data-export>Exportieren</button><button class="btn sm" data-import>Importieren</button><button class="btn sm ghost" data-reset style="margin-left:auto;color:var(--brutality)">Zurücksetzen</button></div>
      </section>
    </div>`);
}

// ---------- Suche ----------
let searchIndex = [];
let searchSel = 0;

function buildSearchIndex() {
  const kindLabel = { gear: null, mutation: 'Mutation', outfit: 'Outfit', biome: 'Biom', arena: 'Bossarena', boss: 'Boss', build: 'Build', rune: 'Rune' };
  searchIndex = [
    ...db.builds.map((b) => ({ e: b, kind: 'Build', sub: b.tagline, hay: [b.name, b.tagline, b.archetype, ...Object.values(b.core).flat()] })),
    ...db.gear.map((e) => ({ e, kind: TYPE_LABEL[e.type], sub: e.description, hay: [e.name, e.nameDe, e.type, TYPE_LABEL[e.type], ...(e.tags ?? [])] })),
    ...db.mutations.map((e) => ({ e, kind: 'Mutation', sub: e.effect, hay: [e.name, e.nameDe, 'mutation', ...(e.tags ?? [])] })),
    ...db.biomes.map((e) => ({ e, kind: kindLabel[e.kind], sub: e.description, hay: [e.name, e.nameDe] })),
    ...db.bosses.map((e) => ({ e, kind: 'Boss', sub: e.description, hay: [e.name, e.nameDe, 'boss'] })),
    ...db.runes.map((e) => ({ e, kind: 'Rune', sub: e.effect, hay: [e.name, e.nameDe, 'rune'] })),
    ...db.outfits.map((e) => ({ e, kind: 'Outfit', sub: e.source, hay: [e.name, e.nameDe, 'outfit'] })),
  ];
}

function runSearch(q) {
  const list = $('#search-results');
  if (!q.trim()) {
    list.innerHTML = `<li class="hint">Tipp: Suche auch nach Effekten wie „bleed“, „parry“ oder Biomen wie „Ramparts“.</li>`;
    return;
  }
  const qq = q.toLowerCase();
  const hits = searchIndex
    .filter((x) => matches(q, x.hay))
    .map((x) => ({ ...x, rank: (x.e.name.toLowerCase().startsWith(qq) ? 0 : x.e.name.toLowerCase().includes(qq) ? 1 : 2) + (x.kind === 'Outfit' ? 0.5 : 0) }))
    .sort((a, b) => a.rank - b.rank || a.e.name.localeCompare(b.e.name))
    .slice(0, 40);
  searchSel = 0;
  list.innerHTML = hits.length
    ? hits.map((x, i) => String(html`<li role="option" aria-selected="${i === 0}"><a href="${x.e.url}">${x.e.kind === 'build' || x.e.kind === 'biome' || x.e.kind === 'arena' || x.e.kind === 'rune' || x.e.kind === 'boss' ? html`<span class="ico sm"><span class="fallback">${x.e.name[0]}</span></span>` : icon(x.e, 'sm')}<span class="meta">${L(x.e)}<small>${x.sub ?? ''}</small></span><span class="kind">${x.kind ?? ''}</span></a></li>`)).join('')
    : `<li class="hint">Nichts gefunden für „${q.replace(/[<>&]/g, '')}“.</li>`;
}

function openSearch() {
  const d = $('#search-dialog');
  if (!d.open) d.showModal();
  const input = $('#search-input');
  input.select();
  runSearch(input.value);
}

function moveSel(delta) {
  const items = $$('#search-results li[role="option"]');
  if (!items.length) return;
  searchSel = (searchSel + delta + items.length) % items.length;
  items.forEach((li, i) => li.setAttribute('aria-selected', i === searchSel));
  items[searchSel].scrollIntoView({ block: 'nearest' });
}

// ---------- Menü (mobil) ----------
function openMenu() { document.body.classList.add('menu-open'); $('#scrim').hidden = false; $('#menu-btn').setAttribute('aria-expanded', 'true'); }
function closeMenu() { document.body.classList.remove('menu-open'); $('#scrim').hidden = true; $('#menu-btn').setAttribute('aria-expanded', 'false'); }

// ---------- Globale Events ----------
function bindGlobal() {
  window.addEventListener('hashchange', () => {
    const d = $('#search-dialog');
    if (d.open) d.close();
    if ($('#dialog').open) closeDialog();
    route();
  });

  document.addEventListener('click', (ev) => {
    const t = ev.target.closest('[data-bc],[data-lang],[data-own],[data-export],[data-import],[data-reset],[data-save-import]');
    if (!t) return;
    if (t.dataset.saveImport !== undefined) {
      openImport();
    } else if (t.dataset.bc !== undefined) {
      const bc = +t.dataset.bc;
      if (bc === profile.bc) return;
      update((p) => { p.bc = bc; });
      toast(`${bc} Boss Cells aktiv – Empfehlungen angepasst.`);
    } else if (t.dataset.lang) {
      if (t.dataset.lang === profile.prefs.names) return;
      update((p) => { p.prefs.names = t.dataset.lang; });
      if ($('#dialog').open) $$('#dialog [data-lang]').forEach((b) => b.setAttribute('aria-selected', b.dataset.lang === t.dataset.lang));
      toast(t.dataset.lang === 'de' ? 'Spielnamen jetzt auf Deutsch.' : 'Spielnamen jetzt auf Englisch (wie im Wiki).');
    } else if (t.dataset.own) {
      const key = t.dataset.own;
      const on = !profile.owned[key];
      update((p) => { if (on) { p.owned[key] = true; delete p.found[key]; } else delete p.owned[key]; });
      const e = db.byKey.get(key);
      if (on && e) toast(`${L(e)} freigeschaltet.`);
    } else if (t.dataset.export !== undefined) {
      download(`dead-cells-fortschritt-${new Date().toISOString().slice(0, 10)}.json`, exportProfile());
      toast('Fortschritt exportiert.');
    } else if (t.dataset.import !== undefined) {
      $('#import-file').click();
    } else if (t.dataset.reset !== undefined) {
      if (confirm('Wirklich alles zurücksetzen? Freischaltungen, BC und Einstellungen gehen verloren.')) { resetProfile(); closeDialog(); toast('Profil zurückgesetzt.'); }
    }
  });

  document.addEventListener('change', (ev) => {
    const t = ev.target;
    if (t.dataset.dlc) {
      update((p) => { p.dlcs = t.checked ? [...new Set([...p.dlcs, t.dataset.dlc])] : p.dlcs.filter((x) => x !== t.dataset.dlc); });
    }
  });

  $('#import-file').addEventListener('change', async (ev) => {
    const f = ev.target.files?.[0];
    ev.target.value = '';
    if (!f) return;
    try {
      if (f.size > 2_000_000) throw new Error('zu groß');
      importProfile(await f.text());
      closeDialog();
      toast('Fortschritt importiert.');
    } catch {
      toast('Import fehlgeschlagen – ist das eine exportierte Fortschrittsdatei?');
    }
  });

  // Bild-Fallback (z. B. fehlendes Icon) → Initialen anzeigen
  document.addEventListener('error', (ev) => {
    const img = ev.target;
    if (img.tagName !== 'IMG' || !img.dataset.fallback) return;
    const span = document.createElement('span');
    span.className = 'fallback';
    span.textContent = img.dataset.fallback;
    img.replaceWith(span);
  }, true);

  $('#profile-btn').addEventListener('click', profileDialog);
  $('#menu-btn').addEventListener('click', () => (document.body.classList.contains('menu-open') ? closeMenu() : openMenu()));
  $('#scrim').addEventListener('click', closeMenu);
  $('#search-btn').addEventListener('click', openSearch);
  $('#dialog').addEventListener('click', (ev) => { if (ev.target.id === 'dialog') closeDialog(); });
  $('#search-dialog').addEventListener('click', (ev) => { if (ev.target.id === 'search-dialog') ev.target.close(); });

  const input = $('#search-input');
  input.addEventListener('input', debounce(() => runSearch(input.value), 60));
  input.addEventListener('keydown', (ev) => {
    if (ev.key === 'ArrowDown') { ev.preventDefault(); moveSel(1); }
    else if (ev.key === 'ArrowUp') { ev.preventDefault(); moveSel(-1); }
    else if (ev.key === 'Enter') {
      const a = $$('#search-results li[role="option"]')[searchSel]?.querySelector('a');
      if (a) { ev.preventDefault(); location.hash = a.getAttribute('href'); $('#search-dialog').close(); }
    }
  });

  document.addEventListener('keydown', (ev) => {
    const typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName);
    if ((ev.key === 'k' && (ev.ctrlKey || ev.metaKey)) || (ev.key === '/' && !typing)) { ev.preventDefault(); openSearch(); }
  });

  subscribe(() => { buildSearchIndex(); rerender(); });
}

// ---------- Start ----------
(async function boot() {
  try {
    await loadAll();
  } catch (err) {
    console.error(err);
    $('#main').innerHTML = '<div class="empty">Die Daten konnten nicht geladen werden. Bitte Seite neu laden.</div>';
    return;
  }
  buildSearchIndex();
  bindGlobal();
  route();
})();
