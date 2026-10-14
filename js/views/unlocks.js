import { html, matches, $, pct } from '../util.js';
import { db, depthLabel, isOwned, bpAvailable, dlcOk, nextUnlocks, biome, SOURCE_LABEL, TYPE_LABEL, L } from '../data.js';
import { profile, update } from '../store.js';
import { pageHead, empty, icon, tick, blueprintSummary, ring, bcTag, tierBadge } from '../components.js';
import { toast } from '../ui.js';

export const title = () => 'Freischaltungen';

const state = { kind: 'gear', mode: 'list', status: 'missing', source: 'all', availableOnly: false, q: '' };
const KINDS = [['gear', 'Waffen & Skills'], ['mutation', 'Mutationen'], ['outfit', 'Outfits']];

const pool = () => ({ gear: db.gear, mutation: db.mutations, outfit: db.outfits }[state.kind]).filter(dlcOk);

function filtered() {
  return pool().filter((e) =>
    !e.blueprint.default &&
    (state.status === 'all' || (state.status === 'owned') === isOwned(e)) &&
    (state.source === 'all' || e.blueprint.sourceType === state.source) &&
    (!state.availableOnly || bpAvailable(e)) &&
    matches(state.q, e.name, e.nameDe, e.blueprint.text, e.blueprint.from, e.blueprint.biomes));
}

const row = (e) => html`<div class="track-row ${isOwned(e) ? 'owned' : ''}">${tick(e)}${icon(e, 'sm')}<span class="meta"><a href="${e.url}">${L(e)}</a><small title="${blueprintSummary(e)}">${blueprintSummary(e)}</small></span>${!bpAvailable(e) ? bcTag(e.blueprint.minBC) : ''}${e.blueprint.cells ? html`<span class="tag" title="Zellen-Kosten" style="color:var(--cell)">${e.blueprint.cells}</span>` : ''}</div>`;

function listView(items) {
  if (!items.length) return empty(state.status === 'missing' ? 'Nichts mehr offen in dieser Auswahl. Stark!' : 'Nichts gefunden.');
  if (state.mode === 'list') {
    return html`<div class="track-list">${items.sort((a, b) => a.name.localeCompare(b.name)).map(row)}</div>`;
  }
  // Entwurf-Atlas: nach Biom gruppiert
  const groups = new Map();
  for (const e of items) {
    const keys = e.blueprint.biomes.length ? e.blueprint.biomes.map((n) => biome(n)?.id ?? n) : ['__none'];
    for (const k of keys) { if (!groups.has(k)) groups.set(k, []); groups.get(k).push(e); }
  }
  const ordered = [...groups.entries()].sort((a, b) => (biome(a[0])?.stage ?? 99) - (biome(b[0])?.stage ?? 99) || String(a[0]).localeCompare(String(b[0])));
  return html`<div class="stack" style="gap:22px">${ordered.map(([k, list]) => {
    const b = biome(k);
    return html`<section><div class="row" style="margin-bottom:10px"><h3 style="font-size:22px">${b ? html`<a href="${b.url}" style="color:var(--text)">${L(b)}</a>` : k === '__none' ? 'Ohne festen Fundort' : k}</h3>${b ? html`<span class="tag">${depthLabel(b)}</span>` : ''}<span class="dim small">${list.length}</span></div>
      <div class="track-list">${list.sort((x, y) => x.name.localeCompare(y.name)).map(row)}</div></section>`;
  })}</div>`;
}

function progress() {
  const cat = (list) => { const l = list.filter(dlcOk); return [l.filter(isOwned).length, l.length]; };
  const weapons = cat(db.gear.filter((g) => g.slot === 'weapon'));
  const skills = cat(db.gear.filter((g) => g.slot === 'skill'));
  const muts = cat(db.mutations);
  const outfits = cat(db.outfits);
  const runes = [db.runes.filter((r) => profile.runes[r.id]).length, db.runes.length];
  const box = (label, [o, t], color) => html`<div class="stat">${ring(pct(o, t), `${pct(o, t)}%`, color)}<span><b>${o}<span class="dim" style="font-size:17px"> / ${t}</span></b><small>${label}</small></span></div>`;
  return html`<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(190px,1fr))">${box('Waffen & Schilde', weapons, 'var(--brutality)')}${box('Skills', skills, 'var(--tactics)')}${box('Mutationen', muts, 'var(--survival)')}${box('Outfits', outfits, 'var(--flame)')}${box('Runen', runes, 'var(--cell)')}</div>`;
}

function body() {
  const items = filtered();
  const sources = [...new Set(pool().map((e) => e.blueprint.sourceType).filter(Boolean))];
  return html`
  <div class="tabs" role="tablist">${KINDS.map(([k, v]) => html`<button role="tab" data-kind="${k}" aria-selected="${state.kind === k}">${v}</button>`)}</div>
  <div class="toolbar">
    <input class="input" id="u-q" type="search" placeholder="Name, Gegner oder Biom …" value="${state.q}" aria-label="Freischaltungen durchsuchen">
    <select class="select" id="u-status" aria-label="Status"><option value="missing" ${state.status === 'missing' ? 'selected' : ''}>Fehlt mir</option><option value="owned" ${state.status === 'owned' ? 'selected' : ''}>Habe ich</option><option value="all" ${state.status === 'all' ? 'selected' : ''}>Alle</option></select>
    <select class="select" id="u-source" aria-label="Quelle"><option value="all">Alle Quellen</option>${sources.map((s) => html`<option value="${s}" ${state.source === s ? 'selected' : ''}>${SOURCE_LABEL[s] ?? s}</option>`)}</select>
  </div>
  <div class="toolbar">
    <div class="tabs" style="margin:0" role="tablist" aria-label="Ansicht"><button data-mode="list" role="tab" aria-selected="${state.mode === 'list'}">Liste</button><button data-mode="atlas" role="tab" aria-selected="${state.mode === 'atlas'}">Nach Biom (Entwurf-Atlas)</button></div>
    <label class="switch"><input type="checkbox" id="u-avail" ${state.availableOnly ? 'checked' : ''}><span class="track"></span>Nur bei ${profile.bc} BC erhältlich</label>
    <span class="spacer"></span>
    ${items.length ? html`<button class="btn sm ghost" data-bulk="${state.status === 'owned' ? 'off' : 'on'}">${state.status === 'owned' ? 'Alle angezeigten abwählen' : `Alle ${items.length} angezeigten abhaken`}</button>` : ''}
  </div>
  <p class="result-count">${items.length} Einträge · Startausrüstung wird automatisch als freigeschaltet gezählt</p>
  ${listView(items)}`;
}

export function render() {
  const next = nextUnlocks(6);
  return html`
  ${pageHead('Deine Sammlung', 'Freischaltungen', 'Hake ab, was du im Spiel schon freigeschaltet hast. Alle Empfehlungen auf der Seite richten sich danach. Gespeichert wird nur lokal in deinem Browser – über das Zahnrad oben kannst du exportieren.', html`<button class="btn sm" data-export>Exportieren</button><button class="btn sm" data-import>Importieren</button>`)}
  ${progress()}
  ${next.length ? html`<section class="section" style="margin-top:28px"><div class="section-head"><div><h2>Nächste Ziele</h2><p>Starke, häufig gespielte Entwürfe, die du bei ${profile.bc} BC bekommen kannst.</p></div></div>
    <div class="grid auto">${next.map((e) => html`<a class="card item-card ${e.colors[0]}" href="${e.url}">${icon(e)}<span class="meta"><h3>${L(e)}</h3><small title="${blueprintSummary(e)}">${blueprintSummary(e)}</small></span><span class="side">${tierBadge(e.tier)}<span class="tag">${e.kind === 'mutation' ? 'Mutation' : TYPE_LABEL[e.type]}</span></span></a>`)}</div></section>` : ''}
  <section class="section" id="u-body">${body()}</section>`;
}

export function mount(root) {
  const host = $('#u-body', root);
  const refresh = (keepFocus) => {
    const id = document.activeElement?.id;
    const pos = document.activeElement?.selectionStart;
    host.innerHTML = String(body());
    if (keepFocus && id) { const el = $(`#${id}`, host); el?.focus(); if (pos != null) el?.setSelectionRange?.(pos, pos); }
  };
  host.addEventListener('input', (e) => { if (e.target.id === 'u-q') { state.q = e.target.value; refresh(true); } });
  host.addEventListener('change', (e) => {
    const t = e.target;
    if (t.id === 'u-status') state.status = t.value;
    else if (t.id === 'u-source') state.source = t.value;
    else if (t.id === 'u-avail') state.availableOnly = t.checked;
    else return;
    refresh(true);
  });
  host.addEventListener('click', (e) => {
    const k = e.target.closest('[data-kind]');
    if (k) { state.kind = k.dataset.kind; state.source = 'all'; refresh(); return; }
    const m = e.target.closest('[data-mode]');
    if (m) { state.mode = m.dataset.mode; refresh(); return; }
    const bulk = e.target.closest('[data-bulk]');
    if (bulk) {
      const items = filtered();
      const on = bulk.dataset.bulk === 'on';
      if (!confirm(on ? `${items.length} Einträge als freigeschaltet markieren?` : `${items.length} Einträge als fehlend markieren?`)) return;
      update((p) => { for (const e2 of items) { if (on) p.owned[e2.key] = true; else delete p.owned[e2.key]; } });
      toast(on ? `${items.length} Einträge abgehakt.` : `${items.length} Einträge zurückgesetzt.`);
    }
  });
}
