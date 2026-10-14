import { html, matches, $ } from '../util.js';
import { db, TYPE_PLURAL, COLOR_LABEL, TIERS, isOwned, dlcOk, tierScore } from '../data.js';
import { itemCard, pageHead, empty } from '../components.js';

export const title = () => 'Waffen & Skills';

const state = { type: 'all', color: 'all', tier: 'all', own: 'all', sort: 'tier', q: '' };

function filtered() {
  const l = db.gear.filter((e) =>
    dlcOk(e) &&
    (state.type === 'all' || e.type === state.type || (state.type === 'weapons' && e.slot === 'weapon') || (state.type === 'skills' && e.slot === 'skill')) &&
    (state.color === 'all' || e.colors.includes(state.color)) &&
    (state.tier === 'all' || e.tier === state.tier) &&
    (state.own === 'all' || (state.own === 'owned') === isOwned(e)) &&
    matches(state.q, e.name, e.nameDe, e.description, e.crit, e.tags, e.blueprint.text, e.blueprint.from));
  const by = {
    tier: (a, b) => tierScore(b) - tierScore(a) || a.name.localeCompare(b.name),
    name: (a, b) => a.name.localeCompare(b.name),
    dps: (a, b) => (b.baseDps ?? -1) - (a.baseDps ?? -1),
  }[state.sort];
  return l.sort(by);
}

const list = () => {
  const l = filtered();
  return html`<p class="result-count">${l.length} Einträge${state.sort === 'dps' ? ' · Basis-DPS ohne Krits, Stats und Affixe' : ''}</p>${l.length ? html`<div class="grid auto">${l.map((e) => itemCard(e))}</div>` : empty('Nichts gefunden. Filter lockern?')}`;
};

export function render(ctx) {
  if (ctx.params.type) state.type = ctx.params.type;
  const types = [['all', 'Alles'], ['weapons', 'Alle Waffen'], ['melee', TYPE_PLURAL.melee], ['ranged', TYPE_PLURAL.ranged], ['shield', TYPE_PLURAL.shield], ['skills', 'Alle Skills'], ['grenade', TYPE_PLURAL.grenade], ['trap', TYPE_PLURAL.trap], ['power', TYPE_PLURAL.power]];
  return html`
  ${pageHead('Das Arsenal', 'Waffen & Skills', `Alle ${db.gear.length} Waffen, Schilde und Skills mit Krit-Bedingung, Entwurf-Fundort, Tier-Einschätzung und passenden Partnern.`)}
  <div class="tabs" role="tablist">${types.map(([k, v]) => html`<button role="tab" data-type="${k}" aria-selected="${state.type === k}">${v}</button>`)}</div>
  <div class="toolbar">
    <input class="input" id="a-q" type="search" placeholder="Name, Effekt (z. B. bleed, freeze) oder Fundort …" value="${state.q}" aria-label="Arsenal durchsuchen">
    <select class="select" id="a-color" aria-label="Farbe"><option value="all">Alle Farben</option>${['brutality', 'tactics', 'survival', 'colorless'].map((c) => html`<option value="${c}" ${state.color === c ? 'selected' : ''}>${COLOR_LABEL[c]}</option>`)}</select>
    <select class="select" id="a-tier" aria-label="Tier"><option value="all">Alle Tiers</option>${TIERS.map((t) => html`<option value="${t}" ${state.tier === t ? 'selected' : ''}>Tier ${t}</option>`)}</select>
    <select class="select" id="a-own" aria-label="Freischaltung"><option value="all">Freigeschaltet &amp; fehlend</option><option value="owned" ${state.own === 'owned' ? 'selected' : ''}>Nur freigeschaltet</option><option value="missing" ${state.own === 'missing' ? 'selected' : ''}>Nur fehlend</option></select>
    <select class="select" id="a-sort" aria-label="Sortierung"><option value="tier">Nach Tier</option><option value="name" ${state.sort === 'name' ? 'selected' : ''}>Nach Name</option><option value="dps" ${state.sort === 'dps' ? 'selected' : ''}>Nach Basis-DPS</option></select>
  </div>
  <div id="a-list">${list()}</div>`;
}

export function mount(root) {
  const refresh = () => { $('#a-list', root).innerHTML = String(list()); };
  $('#a-q', root).addEventListener('input', (e) => { state.q = e.target.value; refresh(); });
  for (const k of ['color', 'tier', 'own', 'sort']) $(`#a-${k}`, root).addEventListener('change', (e) => { state[k] = e.target.value; refresh(); });
  root.querySelectorAll('[data-type]').forEach((btn) => btn.addEventListener('click', () => {
    state.type = btn.dataset.type;
    root.querySelectorAll('[data-type]').forEach((b) => b.setAttribute('aria-selected', b === btn));
    refresh();
  }));
}
