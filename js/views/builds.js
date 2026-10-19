import { html, matches, $ } from '../util.js';
import { db, rankBuilds, buildFitsBc, buildDlcOk, buildReadiness, COLOR_LABEL, findByName, L } from '../data.js';
import { profile } from '../store.js';
import { buildCard, pageHead, empty } from '../components.js';

export const title = () => 'Builds';

const state = { color: 'all', phase: 'all', mutation: 'all', q: '', fitOnly: true, readyOnly: false, favOnly: false };
const PHASES = { all: 'Alle Phasen', early: 'Früh im Run', mid: 'Mitte', late: 'Endgame', any: 'Immer' };

function filtered() {
  return rankBuilds(db.builds.filter((b) =>
    (state.color === 'all' || b.color === state.color || b.secondaryColor === state.color) &&
    (state.phase === 'all' || b.phase === state.phase) &&
    (!state.fitOnly || (buildFitsBc(b) && buildDlcOk(b))) &&
    (!state.readyOnly || buildReadiness(b).ratio >= 0.999) &&
    (!state.favOnly || profile.favorites.includes(b.id)) &&
    (state.mutation === 'all' || b.core.mutations.includes(state.mutation) || b.alternatives.mutations?.includes(state.mutation)) &&
    matches(state.q, b.name, b.tagline, b.archetype, b.whyItWorks, Object.values(b.core).flat(), Object.values(b.alternatives).flat())));
}

const list = () => {
  const l = filtered();
  return html`<p class="result-count">${l.length} von ${db.builds.length} Builds</p>${l.length ? html`<div class="grid auto">${l.map(buildCard)}</div>` : empty('Kein Build passt zu diesen Filtern. Tipp: „Nur passend zu meiner BC“ ausschalten.')}`;
};

export function render() {
  const colors = ['all', 'brutality', 'tactics', 'survival', 'hybrid'];
  return html`
  ${pageHead('Ausrüsten · Kombinieren · Überleben', 'Builds, die tragen', `Kuratiert aus Community-Konsens (Steam-Foren und -Guides, Video-Guides, Tierlisten) und Wiki-Mechaniken. Sortiert nach deiner BC und deinen Freischaltungen – oben steht, was du jetzt sofort spielen kannst.`)}
  <div class="toolbar">
    <input class="input" id="b-q" type="search" placeholder="Build, Waffe oder Mutation suchen …" value="${state.q}" aria-label="Builds durchsuchen">
    <select class="select" id="b-mut" aria-label="Mutation"><option value="all">Alle Mutationen</option>${[...new Set(db.builds.flatMap((b) => [...b.core.mutations, ...(b.alternatives.mutations ?? [])]))].sort().map((n) => { const m = findByName(n); return html`<option value="${n}" ${state.mutation === n ? 'selected' : ''}>${m ? L(m) : n} (${db.builds.filter((b) => b.core.mutations.includes(n)).length})</option>`; })}</select>
    <select class="select" id="b-phase" aria-label="Phase">${Object.entries(PHASES).map(([k, v]) => html`<option value="${k}" ${state.phase === k ? 'selected' : ''}>${v}</option>`)}</select>
  </div>
  <div class="toolbar">
    <div class="chips">${colors.map((c) => html`<button class="chip ${c}" data-color="${c}" aria-pressed="${state.color === c}">${c !== 'all' ? html`<span class="dot"></span>` : ''}${c === 'all' ? 'Alle Farben' : COLOR_LABEL[c]}</button>`)}</div>
    <span class="spacer"></span>
    <label class="switch"><input type="checkbox" id="b-fit" ${state.fitOnly ? 'checked' : ''}><span class="track"></span>Nur passend zu ${profile.bc} BC &amp; DLCs</label>
    <label class="switch"><input type="checkbox" id="b-ready" ${state.readyOnly ? 'checked' : ''}><span class="track"></span>Nur komplett freigeschaltet</label>
    ${profile.favorites.length ? html`<label class="switch"><input type="checkbox" id="b-fav" ${state.favOnly ? 'checked' : ''}><span class="track"></span>Favoriten</label>` : ''}
  </div>
  <div id="b-list">${list()}</div>`;
}

export function mount(root) {
  const refresh = () => { $('#b-list', root).innerHTML = String(list()); };
  $('#b-q', root).addEventListener('input', (e) => { state.q = e.target.value; refresh(); });
  $('#b-phase', root).addEventListener('change', (e) => { state.phase = e.target.value; refresh(); });
  $('#b-mut', root).addEventListener('change', (e) => { state.mutation = e.target.value; refresh(); });
  $('#b-fit', root).addEventListener('change', (e) => { state.fitOnly = e.target.checked; refresh(); });
  $('#b-ready', root).addEventListener('change', (e) => { state.readyOnly = e.target.checked; refresh(); });
  $('#b-fav', root)?.addEventListener('change', (e) => { state.favOnly = e.target.checked; refresh(); });
  root.querySelectorAll('[data-color]').forEach((btn) => btn.addEventListener('click', () => {
    state.color = btn.dataset.color;
    root.querySelectorAll('[data-color]').forEach((b) => b.setAttribute('aria-pressed', b === btn));
    refresh();
  }));
}
