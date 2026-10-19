import { html, matches, $ } from '../util.js';
import { db, COLOR_LABEL, TIERS, isOwned, dlcOk, tierScore, findByName, L } from '../data.js';
import { icon, pageHead, empty, tierBadge, colorTag, itemLink, blueprintSummary } from '../components.js';

export const title = () => 'Mutationen';

const state = { color: 'all', tier: 'all', own: 'all', q: '', tab: 'all' };

function card(m) {
  return html`<a class="card ${m.colors[0]}" href="${m.url}" style="gap:10px">
    <div class="row" style="flex-wrap:nowrap;gap:12px">${icon(m, '', { showOwned: true })}<div style="flex:1;min-width:0"><h3 style="font-size:20px">${L(m)}</h3><div class="row" style="gap:6px;margin-top:4px">${colorTag(m.colors[0])}${m.dlc ? html`<span class="tag dlc">${m.dlc}</span>` : ''}</div></div>${tierBadge(m.tier)}</div>
    <p>${m.effect}</p>
    <div class="card-foot"><span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${blueprintSummary(m)}</span></div>
  </a>`;
}

function list() {
  const l = db.mutations
    .filter((m) => dlcOk(m) && (state.color === 'all' || m.colors[0] === state.color) && (state.tier === 'all' || m.tier === state.tier) &&
      (state.own === 'all' || (state.own === 'owned') === isOwned(m)) && matches(state.q, m.name, m.nameDe, m.effect, m.notes, m.tags))
    .sort((a, b) => tierScore(b) - tierScore(a) || a.name.localeCompare(b.name));
  return html`<p class="result-count">${l.length} Mutationen</p>${l.length ? html`<div class="grid auto">${l.map(card)}</div>` : empty('Keine Mutation passt zu diesen Filtern.')}`;
}

function sets() {
  const fromBuilds = db.builds.filter((b) => b.core.mutations.length === 3)
    .sort((a, b) => tierScore(b) - tierScore(a) || a.name.localeCompare(b.name));
  if (!db.mutationSets.length && !fromBuilds.length) return empty('Noch keine Kombis hinterlegt.');
  return html`
  ${db.mutationSets.length ? html`<div class="section-head"><div><h2 style="font-size:24px">Klassische Dreier-Kombis</h2><p>Bewährte Sets, die zu vielen Builds passen.</p></div></div>
  <div class="grid auto">${db.mutationSets.map((s) => html`<article class="card ${s.color}">
    <div class="row" style="gap:6px">${colorTag(s.color)}</div>
    <h3>${L(s)}</h3>
    <div class="stack" style="gap:6px">${s.mutations.map((n) => itemLink(n))}</div>
    ${s.forWhat ? html`<p><b style="color:var(--text)">Wofür:</b> ${s.forWhat}</p>` : ''}
    <p>${s.why}</p>
    <div class="card-foot"><a class="link-btn" href="#/workshop" data-set="${s.mutations.join('|')}">In der Werkstatt öffnen →</a></div>
  </article>`)}</div>` : ''}
  ${fromBuilds.length ? html`<div class="section-head" style="margin-top:34px"><div><h2 style="font-size:24px">Mutationen aus den Builds (${fromBuilds.length})</h2><p>Jedes Build-Set mit Begründung pro Mutation – und was du vor dem Boss tauschst.</p></div></div>
  <div class="grid auto">${fromBuilds.map((b) => html`<article class="card ${b.color}">
    <div class="row" style="gap:6px">${tierBadge(b.tier)}${colorTag(b.color)}<span class="tag">${b.archetype}</span></div>
    <h3><a href="${b.url}" style="color:var(--text)">${L(b)}</a></h3>
    <div class="stack" style="gap:8px">${b.core.mutations.map((n) => html`<div>${itemLink(n)}${b.mutationWhy?.[n] ? html`<p class="small" style="margin-top:4px">${b.mutationWhy[n]}</p>` : ''}</div>`)}</div>
    ${b.bossMutations?.length ? html`<p class="small"><b style="color:var(--text)">Vor Bossen:</b> ${b.bossMutations.map((n) => L(findByName(n) ?? { name: n })).join(', ')}</p>` : ''}
    <div class="card-foot"><a class="link-btn" href="${b.url}">Zum Build →</a><span class="spacer"></span><a class="link-btn" href="#/workshop?build=${b.id}">Werkstatt</a></div>
  </article>`)}</div>` : ''}`;
}

export function render() {
  return html`
  ${pageHead('Drei Plätze · viele Möglichkeiten', 'Mutationen', 'Jede Mutation mit genauen Werten, Entwurf-Fundort und Einschätzung – plus bewährte Dreier-Kombinationen. Tipp: Vor Bossen lohnt sich oft ein Mutations-Respec beim Händler.')}
  <div class="tabs" role="tablist">
    <button role="tab" data-tab="all" aria-selected="${state.tab === 'all'}">Alle Mutationen</button>
    <button role="tab" data-tab="sets" aria-selected="${state.tab === 'sets'}">Bewährte Kombis</button>
  </div>
  <div id="m-body">${body()}</div>`;
}

function body() {
  if (state.tab === 'sets') return sets();
  return html`<div class="toolbar">
      <input class="input" id="m-q" type="search" placeholder="Mutation oder Effekt suchen …" value="${state.q}" aria-label="Mutationen durchsuchen">
      <select class="select" id="m-color" aria-label="Farbe"><option value="all">Alle Farben</option>${['brutality', 'tactics', 'survival', 'colorless'].map((c) => html`<option value="${c}" ${state.color === c ? 'selected' : ''}>${COLOR_LABEL[c]}</option>`)}</select>
      <select class="select" id="m-tier" aria-label="Tier"><option value="all">Alle Tiers</option>${TIERS.map((t) => html`<option value="${t}" ${state.tier === t ? 'selected' : ''}>Tier ${t}</option>`)}</select>
      <select class="select" id="m-own" aria-label="Freischaltung"><option value="all">Freigeschaltet &amp; fehlend</option><option value="owned" ${state.own === 'owned' ? 'selected' : ''}>Nur freigeschaltet</option><option value="missing" ${state.own === 'missing' ? 'selected' : ''}>Nur fehlend</option></select>
    </div><div id="m-list">${list()}</div>`;
}

export function mount(root) {
  const bindFilters = () => {
    const refresh = () => { $('#m-list', root).innerHTML = String(list()); };
    $('#m-q', root)?.addEventListener('input', (e) => { state.q = e.target.value; refresh(); });
    for (const k of ['color', 'tier', 'own']) $(`#m-${k}`, root)?.addEventListener('change', (e) => { state[k] = e.target.value; refresh(); });
  };
  bindFilters();
  root.querySelectorAll('[data-tab]').forEach((btn) => btn.addEventListener('click', () => {
    state.tab = btn.dataset.tab;
    root.querySelectorAll('[data-tab]').forEach((b) => b.setAttribute('aria-selected', b === btn));
    $('#m-body', root).innerHTML = String(body());
    bindFilters();
  }));
  root.addEventListener('click', (ev) => {
    const a = ev.target.closest('[data-set]');
    if (!a) return;
    ev.preventDefault();
    const names = a.dataset.set.split('|').filter((n) => findByName(n));
    location.hash = `#/workshop?${names.map((n) => `add=${encodeURIComponent(n)}`).join('&')}`;
  });
}
