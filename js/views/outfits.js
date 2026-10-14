import { html, matches, $, pct } from '../util.js';
import { db, isOwned, dlcOk, SOURCE_LABEL, L } from '../data.js';
import { pageHead, empty, icon, tick, ring } from '../components.js';

export const title = () => 'Outfits';

const state = { q: '', status: 'all', source: 'all', lastParam: null };

function list() {
  const l = db.outfits.filter((o) => dlcOk(o) &&
    (state.status === 'all' || (state.status === 'owned') === isOwned(o)) &&
    (state.source === 'all' || o.sourceType === state.source) &&
    matches(state.q, o.name, o.nameDe, o.source, o.reference, o.enemy, o.biomes));
  if (!l.length) return empty('Kein Outfit gefunden.');
  return html`<p class="result-count">${l.length} Outfits</p><div class="track-list">${l.map((o) => html`<div class="track-row ${isOwned(o) ? 'owned' : ''}">${tick(o)}${icon(o)}<span class="meta"><b style="display:block">${L(o)}</b><small title="${o.source}">${o.source}</small>${o.reference ? html`<small class="dim" title="${o.reference}">↳ ${o.reference}</small>` : ''}</span>${o.dlc ? html`<span class="tag dlc" title="${o.dlc}">DLC</span>` : ''}</div>`)}</div>`;
}

export function render(ctx) {
  if (ctx.params.q && ctx.params.q !== state.lastParam) state.q = state.lastParam = ctx.params.q;
  const avail = db.outfits.filter(dlcOk);
  const owned = avail.filter(isOwned).length;
  const sources = [...new Set(db.outfits.map((o) => o.sourceType).filter(Boolean))];
  return html`
  ${pageHead('Für die Optik', 'Outfits', 'Alle Outfits mit Fundort und Herkunft – viele davon Crossover aus anderen Spielen. Abhaken, was du schon hast.', html`<div class="stat" style="padding:10px 14px">${ring(pct(owned, avail.length), `${pct(owned, avail.length)}%`)}<span><b>${owned} / ${avail.length}</b><small>gesammelt</small></span></div>`)}
  ${!db.outfits.length ? empty('Outfit-Daten fehlen noch.') : html`
  <div class="toolbar">
    <input class="input" id="o-q" type="search" placeholder="Outfit, Gegner, Boss oder Spiel …" value="${state.q}" aria-label="Outfits durchsuchen">
    <select class="select" id="o-status" aria-label="Status"><option value="all">Alle</option><option value="missing" ${state.status === 'missing' ? 'selected' : ''}>Fehlt mir</option><option value="owned" ${state.status === 'owned' ? 'selected' : ''}>Habe ich</option></select>
    <select class="select" id="o-source" aria-label="Quelle"><option value="all">Alle Quellen</option>${sources.map((s) => html`<option value="${s}" ${state.source === s ? 'selected' : ''}>${SOURCE_LABEL[s] ?? s}</option>`)}</select>
  </div>
  <div id="o-list">${list()}</div>`}`;
}

export function mount(root) {
  const refresh = () => { const l = $('#o-list', root); if (l) l.innerHTML = String(list()); };
  $('#o-q', root)?.addEventListener('input', (e) => { state.q = e.target.value; refresh(); });
  $('#o-status', root)?.addEventListener('change', (e) => { state.status = e.target.value; refresh(); });
  $('#o-source', root)?.addEventListener('change', (e) => { state.source = e.target.value; refresh(); });
}
