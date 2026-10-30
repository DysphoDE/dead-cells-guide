import { html, $, matches } from '../util.js';
import { db, depthLabel, biome, L } from '../data.js';
import { profile, hasDlc, update } from '../store.js';
import { pageHead, empty, bcTag, dlcTag, CHECK, IC } from '../components.js';

export const title = () => 'Biome & Bosse';

const state = { tab: 'biomes', q: '' };
const TABS = [['biomes', 'Biome'], ['bosses', 'Bosse'], ['runes', 'Runen'], ['doors', 'Zeittüren & Geheimes']];

const diffBar = (n) => html`<span class="diff" title="Schwierigkeit ${n}/5">${[1, 2, 3, 4, 5].map((i) => html`<i class="${i <= n ? 'on' : ''}"></i>`)}</span>`;

function biomeCard(b) {
  const bps = (db.blueprintsByBiome.get(b.id) ?? []).filter((e) => e.kind !== 'outfit').length;
  return html`<a class="card biome-card" href="${b.url}">
    <div class="thumb" style="${b.image ? `background-image:url('${b.image}')` : ''}"></div>
    <div class="body">
      <h3>${L(b)}</h3>
      <div class="row" style="gap:6px"><span class="tag ${b.kind === 'arena' ? 'warn' : ''}">${depthLabel(b)}</span>${(b.minBC ?? 0) > 0 ? bcTag(b.minBC) : ''}${dlcTag(b.dlc)}</div>
      <p class="small" style="color:var(--text-2)">${b.description}</p>
      <div class="row small muted" style="gap:14px">${b.difficulty ? diffBar(b.difficulty) : ''}${b.scrolls?.power != null ? html`<span>${b.scrolls.power} Rollen</span>` : ''}${b.timedDoor ? html`<span>${IC.clock} ${b.timedDoor.minutes} min</span>` : ''}${bps ? html`<span>${bps} Entwürfe</span>` : ''}</div>
    </div>
  </a>`;
}

function bossCard(b) {
  const arena = biome(b.biome);
  return html`<a class="card biome-card" href="${b.url}">
    <div class="thumb" style="${b.image ? `background-image:url('${b.image}');background-size:contain;background-color:#120e18` : ''}"></div>
    <div class="body">
      <h3>${L(b)}</h3>
      <div class="row" style="gap:6px">${arena ? html`<span class="tag">${arena.depth != null ? `Ebene ${arena.depth}` : 'Boss'}</span>` : ''}${(b.minBC ?? 0) > 0 ? bcTag(b.minBC) : ''}${dlcTag(b.dlc)}</div>
      <p class="small" style="color:var(--text-2)">${b.description}</p>
      ${arena ? html`<p class="small dim">Arena: ${L(arena)}</p>` : ''}
    </div>
  </a>`;
}

function runes() {
  if (!db.runes.length) return empty('Noch keine Runen-Daten.');
  return html`<p class="muted small" style="margin-bottom:12px">Hake gefundene Runen ab – der Routenplaner kann dann nur Wege zeigen, die du wirklich gehen kannst.</p>
  <div class="grid auto">${db.runes.map((r) => {
    const where = biome(r.where);
    const on = !!profile.runes[r.id];
    return html`<article class="card ${on ? 'survival' : ''}" id="${r.id}">
      <div class="row" style="justify-content:space-between;flex-wrap:nowrap"><h3>${L(r)}</h3><button class="tick" data-rune="${r.id}" aria-pressed="${on}" aria-label="${L(r)} gefunden">${CHECK}</button></div>
      <p><b style="color:var(--text)">Effekt:</b> ${r.effect}</p>
      <p><b style="color:var(--text)">So bekommst du sie:</b> ${r.how}</p>
      <div class="card-foot">${where ? html`<a href="${where.url}">${L(where)}</a>` : ''}${r.guardian ? html`<span>· Wächter: ${r.guardian}</span>` : ''}</div>
    </article>`;
  })}</div>`;
}

function doors() {
  return html`
  ${db.timedDoors.length ? html`<div class="section-head"><div><h2 style="font-size:24px">Zeittüren</h2><p>Erreiche das Biom-Ende rechtzeitig für Bonus-Zellen, Gold und Ausrüstung – oft auch einen Entwurf.</p></div></div>
  <div class="table-wrap"><table class="table"><thead><tr><th>Biom</th><th>Zeitlimit</th><th>Belohnung</th></tr></thead><tbody>
    ${db.timedDoors.map((d) => { const b = biome(d.biome); return html`<tr><td>${b ? html`<a href="${b.url}" style="color:var(--text)">${L(b)}</a>` : d.biome}</td><td>${d.minutes} min</td><td>${d.reward}</td></tr>`; })}
  </tbody></table></div>` : ''}
  ${db.otherAreas.length ? html`<div class="section-head" style="margin-top:30px"><div><h2 style="font-size:24px">Besondere Orte</h2></div></div>
  <div class="grid auto">${db.otherAreas.map((o) => html`<article class="card"><h3>${L(o)}</h3><p>${o.description}</p>${o.how ? html`<p><b style="color:var(--text)">So kommst du hin:</b> ${o.how}</p>` : ''}</article>`)}</div>` : ''}`;
}

function body() {
  if (state.tab === 'runes') return runes();
  if (state.tab === 'doors') return doors();
  const isBoss = state.tab === 'bosses';
  const list = (isBoss ? db.bosses : db.biomes.filter((b) => b.kind !== 'arena'))
    .filter((b) => hasDlc(b.dlc) && matches(state.q, b.name, b.nameDe, b.description))
    .sort((a, b) => (a.stage ?? 99) - (b.stage ?? 99) || a.name.localeCompare(b.name));
  return html`<div class="toolbar"><input class="input" id="w-q" type="search" placeholder="${isBoss ? 'Boss suchen …' : 'Biom suchen …'}" value="${state.q}"></div>
  <div id="w-list">${list.length ? html`<div class="grid auto">${list.map(isBoss ? bossCard : biomeCard)}</div>` : empty('Nichts gefunden.')}</div>`;
}

export function render(ctx) {
  if (ctx.params.tab && TABS.some(([k]) => k === ctx.params.tab)) state.tab = ctx.params.tab;
  return html`
  ${pageHead('Die Insel', 'Biome & Bosse', `${db.biomes.filter((b) => b.kind !== 'arena').length} Biome, ${db.bosses.length} Bosse und ${db.runes.length} Runen – mit Ausgängen, Schriftrollen, Zeittüren und konkreten Tipps.`, html`<a class="btn" href="#/routes">Zum Routenplaner</a>`)}
  <div class="tabs" role="tablist">${TABS.map(([k, v]) => html`<button role="tab" data-tab="${k}" aria-selected="${state.tab === k}">${v}</button>`)}</div>
  <div id="w-body">${body()}</div>`;
}

export function mount(root) {
  const bind = () => $('#w-q', root)?.addEventListener('input', (e) => {
    state.q = e.target.value;
    const tmp = document.createElement('div');
    tmp.innerHTML = String(body());
    $('#w-list', root).replaceWith(tmp.querySelector('#w-list'));
  });
  bind();
  root.querySelectorAll('[data-tab]').forEach((btn) => btn.addEventListener('click', () => {
    state.tab = btn.dataset.tab;
    state.q = '';
    history.replaceState(null, '', `#/world?tab=${state.tab}`);
    root.querySelectorAll('[data-tab]').forEach((b) => b.setAttribute('aria-selected', b === btn));
    $('#w-body', root).innerHTML = String(body());
    bind();
  }));
  root.addEventListener('click', (ev) => {
    const t = ev.target.closest('[data-rune]');
    if (!t) return;
    const id = t.dataset.rune;
    update((p) => { if (p.runes[id]) delete p.runes[id]; else p.runes[id] = true; });
  });
}
