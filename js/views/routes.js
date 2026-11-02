import { html, $, $$ } from '../util.js';
import { db, biome, isOwned, bpAvailable, depthLabel, L } from '../data.js';
import { profile, hasDlc } from '../store.js';
import { pageHead, empty, icon, blueprintSummary, IC } from '../components.js';

export const title = () => 'Routenplaner';

const START = 'prisoners-quarters';
const state = { path: [START], routeId: null, respectRunes: false };
let resizeObs = null;

const runeOwned = (name) => {
  const r = db.runes.find((x) => x.name === name || x.id === name);
  return !r || !!profile.runes[r.id];
};

function exitState(exit) {
  const target = biome(exit.to);
  if (!target) return { ok: false, why: 'unbekannt' };
  if (!hasDlc(target.dlc)) return { ok: false, why: `${target.dlc} nicht aktiviert` };
  if ((exit.minBC ?? 0) > profile.bc || (target.minBC ?? 0) > profile.bc) return { ok: false, why: `ab ${Math.max(exit.minBC ?? 0, target.minBC ?? 0)} BC` };
  if (state.respectRunes && exit.rune && !runeOwned(exit.rune)) return { ok: false, why: `${exit.rune} fehlt` };
  return { ok: true };
}

function routeList() {
  return db.routes
    .map((r) => ({ ...r, ids: r.path.map((n) => biome(n)?.id).filter(Boolean) }))
    .filter((r) => r.ids.length > 1);
}
const routeFits = (r) => (r.bcMin ?? 0) <= profile.bc && profile.bc <= (r.bcMax ?? 5) && hasDlc(r.dlc ?? []);

function stages() {
  const visible = db.biomes.filter((b) => hasDlc(b.dlc) && b.stage != null);
  const by = new Map();
  for (const b of visible) { if (!by.has(b.stage)) by.set(b.stage, []); by.get(b.stage).push(b); }
  return [...by.entries()].sort((a, b) => a[0] - b[0]);
}

function graph() {
  const path = state.path;
  const last = path.at(-1);
  const lastBiome = biome(last);
  const nextIds = new Set((lastBiome?.exits ?? []).filter((x) => exitState(x).ok).map((x) => biome(x.to)?.id));
  return html`<div class="route-graph-wrap" id="r-wrap"><div class="route-graph" id="r-graph">
    <svg class="route-svg" id="r-svg" aria-hidden="true"></svg>
    ${stages().map(([stage, list]) => html`<div class="route-col"><div class="route-col-label">${list.every((b) => b.kind === 'arena') ? 'Boss' : list.find((b) => b.depth != null) ? `Ebene ${list.find((b) => b.depth != null).depth}` : 'Abzweig'}</div>
      ${list.map((b) => {
        const inPath = path.includes(b.id);
        const cls = [b.kind === 'arena' ? 'boss' : '', inPath ? 'in-path' : '', b.id === last ? 'current' : '', nextIds.has(b.id) ? 'next' : '', (b.minBC ?? 0) > profile.bc ? 'locked' : '', !inPath && !nextIds.has(b.id) ? 'dimmed' : ''].join(' ');
        const badges = [b.scrolls?.power ? html`<span title="Schriftrollen der Macht">${b.scrolls.power}× Rolle</span>` : '', b.timedDoor ? html`<span title="Zeittür">${IC.clock} ${b.timedDoor.minutes}′</span>` : '', (b.minBC ?? 0) > 0 ? html`<span class="bcb">${b.minBC} BC</span>` : '', b.runeHere ? html`<span class="rune" title="${b.runeHere}">Rune</span>` : ''];
        return html`<button class="node ${cls}" data-node="${b.id}" title="${L(b)}">${L(b)}<small>${b.kind === 'arena' ? 'Bossarena' : b.kind === 'secret' ? 'Geheimbiom' : (b.dlc ?? 'Basisspiel')}</small><span class="badges">${badges}</span></button>`;
      })}</div>`)}
  </div></div>`;
}

function drawEdges(root) {
  const g = $('#r-graph', root);
  const svg = $('#r-svg', root);
  if (!g || !svg) return;
  const box = g.getBoundingClientRect();
  svg.setAttribute('width', box.width);
  svg.setAttribute('height', box.height);
  svg.setAttribute('viewBox', `0 0 ${box.width} ${box.height}`);
  const pos = new Map($$('[data-node]', g).map((el) => { const r = el.getBoundingClientRect(); return [el.dataset.node, { x1: r.left - box.left, x2: r.right - box.left, y: r.top - box.top + r.height / 2 }]; }));
  const onPath = new Set(state.path.slice(1).map((id, i) => `${state.path[i]}>${id}`));
  let out = '';
  for (const b of db.biomes) {
    const from = pos.get(b.id);
    if (!from) continue;
    for (const ex of b.exits) {
      const t = biome(ex.to);
      const to = t && pos.get(t.id);
      if (!to) continue;
      const on = onPath.has(`${b.id}>${t.id}`);
      const locked = !exitState(ex).ok;
      const x1 = from.x2, x2 = to.x1, dx = Math.max(24, (x2 - x1) / 2);
      out += `<path class="${on ? 'on' : ''} ${locked ? 'locked' : ''}" d="M${x1},${from.y} C${x1 + dx},${from.y} ${x2 - dx},${to.y} ${x2},${to.y}"/>`;
    }
  }
  // Pfad-Kanten zuletzt, damit sie oben liegen
  svg.innerHTML = out.split('<path').filter(Boolean).map((p) => `<path${p}`).sort((a, b) => a.includes('class="on') - b.includes('class="on')).join('');
}

function summary() {
  const ids = state.path;
  const list = ids.map((id) => biome(id)).filter(Boolean);
  const scrolls = list.reduce((s, b) => s + (b.scrolls?.power ?? 0), 0);
  const doors = list.filter((b) => b.timedDoor);
  const runesNeeded = new Set();
  for (let i = 1; i < ids.length; i++) {
    const ex = biome(ids[i - 1])?.exits.find((x) => biome(x.to)?.id === ids[i]);
    if (ex?.rune) runesNeeded.add(ex.rune);
  }
  const bosses = db.bosses.filter((bo) => ids.includes(bo.biome));
  const bps = [];
  for (const id of ids) for (const e of db.blueprintsByBiome.get(id) ?? []) if (e.kind !== 'outfit' && !isOwned(e) && bpAvailable(e) && !bps.includes(e)) bps.push(e);
  const route = routeList().find((r) => r.id === state.routeId);
  return html`<div class="panel">
    ${route ? html`<h3>${L(route)}</h3><p class="route-goal">Ziel: ${route.goal}</p><p style="color:var(--text-2)">${route.why}</p>` : html`<h3>Eigene Route</h3><p class="muted small">Klicke auf ein markiertes Biom, um weiterzugehen. Klick auf ein Biom im Pfad springt dorthin zurück.</p>`}
    <div class="path-strip" style="margin:14px 0">${list.map((b, i) => html`<span class="hop">${i ? html`<span class="arrow" aria-hidden="true">→</span>` : ''}<a class="step ${b.kind === 'arena' ? 'boss' : ''}" href="${b.url}">${L(b)}</a></span>`)}</div>
    <div class="grid cols-4" style="gap:10px">
      <div class="panel tight"><div class="field-label">Schriftrollen</div><b style="font:800 26px var(--font-display)">${scrolls}</b> <span class="dim small">der Macht (Basis)</span></div>
      <div class="panel tight"><div class="field-label">Zeittüren</div><b style="font:800 26px var(--font-display)">${doors.length}</b> <span class="dim small">${doors.map((d) => `${L(d)} ${d.timedDoor.minutes}′`).join(', ')}</span></div>
      <div class="panel tight"><div class="field-label">Runen nötig</div>${runesNeeded.size ? html`<div class="row" style="gap:4px;margin-top:4px">${[...runesNeeded].map((r) => html`<span class="tag ${runeOwned(r) ? 'ok' : 'warn'}">${r}</span>`)}</div>` : html`<b style="font:800 26px var(--font-display)">0</b>`}</div>
      <div class="panel tight"><div class="field-label">Bosse</div><div class="row" style="gap:4px;margin-top:4px">${bosses.length ? bosses.map((b) => html`<a class="tag" href="${b.url}">${L(b)}</a>`) : html`<span class="dim">–</span>`}</div></div>
    </div>
    ${route?.tips?.length ? html`<div class="field-label" style="margin:18px 0 8px">Tipps</div><ul class="bullets small">${route.tips.map((t) => html`<li>${t}</li>`)}</ul>` : ''}
    <div class="field-label" style="margin:18px 0 8px">Entwürfe auf dieser Route, die dir fehlen (${bps.length})</div>
    ${bps.length ? html`<div class="grid auto-s" style="gap:6px">${bps.slice(0, 18).map((e) => html`<a class="row" href="${e.url}" style="flex-wrap:nowrap;gap:8px;color:var(--text)" title="${blueprintSummary(e)}">${icon(e, 'sm')}<span style="min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" class="small">${L(e)}</span></a>`)}</div>${bps.length > 18 ? html`<p class="dim small" style="margin-top:8px">… und ${bps.length - 18} weitere. Details auf den Biom-Seiten.</p>` : ''}` : html`<p class="muted small">Nichts mehr zu holen – oder noch keine Fundort-Daten.</p>`}
  </div>`;
}

export function render(ctx) {
  if (!db.biomes.length) return html`${pageHead('Routenplaner', 'Routen', '')}${empty('Biom-Daten werden noch recherchiert.')}`;
  if (ctx.params.r) {
    const r = routeList().find((x) => x.id === ctx.params.r);
    if (r) { state.routeId = r.id; state.path = r.ids; }
  }
  const routes = routeList();
  return html`
  ${pageHead('Jede Insel hat mehrere Wege', 'Routenplaner', 'Wähle eine empfohlene Route oder bau deine eigene. Ausgänge, die bei deiner BC, deinen DLCs oder (optional) deinen Runen nicht offen sind, werden gesperrt.')}
  <div class="section-head" style="margin-bottom:10px"><div><h2 style="font-size:24px">Empfohlene Routen</h2></div>
    <div class="row"><label class="switch"><input type="checkbox" id="r-runes" ${state.respectRunes ? 'checked' : ''}><span class="track"></span>Nur mit meinen Runen</label>
    <a class="btn sm ghost" href="#/world?tab=runes">Runen verwalten</a></div></div>
  <div class="chips scroll-x" style="margin-bottom:18px">
    <button class="chip" data-route="" aria-pressed="${!state.routeId}">${IC.edit} Eigene Route</button>
    ${routes.map((r) => html`<button class="chip" data-route="${r.id}" aria-pressed="${state.routeId === r.id}" style="${routeFits(r) ? '' : 'opacity:.5'}" title="${r.goal}${routeFits(r) ? '' : ' – passt nicht zu deiner BC/DLC'}">${L(r)}</button>`)}
  </div>
  <div id="r-sum">${summary()}</div>
  <div class="section-head" style="margin:26px 0 10px"><div><h2 style="font-size:24px">Biom-Karte</h2><p>Getönt mit gestricheltem Rahmen = nächster möglicher Schritt · schraffiert = gesperrt</p></div>
    <div class="row"><button class="btn sm" id="r-back" ${state.path.length < 2 ? 'disabled' : ''}>← Schritt zurück</button><button class="btn sm ghost" id="r-reset">Neu starten</button></div></div>
  <div id="r-graph-host">${graph()}</div>`;
}

export function mount(root) {
  const redraw = () => {
    $('#r-graph-host', root).innerHTML = String(graph());
    $('#r-sum', root).innerHTML = String(summary());
    $('#r-back', root).disabled = state.path.length < 2;
    root.querySelectorAll('[data-route]').forEach((b) => b.setAttribute('aria-pressed', (b.dataset.route || null) === state.routeId));
    requestAnimationFrame(() => drawEdges(root));
  };
  requestAnimationFrame(() => drawEdges(root));
  resizeObs = new ResizeObserver(() => drawEdges(root));
  resizeObs.observe(root);

  root.addEventListener('click', (ev) => {
    const node = ev.target.closest('[data-node]');
    if (node) {
      const id = node.dataset.node;
      const idx = state.path.indexOf(id);
      if (idx !== -1) { state.path = state.path.slice(0, idx + 1); state.routeId = null; history.replaceState(null, '', '#/routes'); redraw(); return; }
      const last = biome(state.path.at(-1));
      const ex = last?.exits.find((x) => biome(x.to)?.id === id);
      if (ex && exitState(ex).ok) { state.path = [...state.path, id]; state.routeId = null; history.replaceState(null, '', '#/routes'); redraw(); }
      else location.hash = `#/biome/${id}`;
      return;
    }
    const r = ev.target.closest('[data-route]');
    if (r) {
      const route = routeList().find((x) => x.id === r.dataset.route);
      state.routeId = route?.id ?? null;
      state.path = route ? route.ids : [START];
      history.replaceState(null, '', route ? `#/routes?r=${route.id}` : '#/routes');
      redraw();
    }
  });
  $('#r-back', root).addEventListener('click', () => { state.path = state.path.slice(0, -1); state.routeId = null; history.replaceState(null, '', '#/routes'); redraw(); });
  $('#r-reset', root).addEventListener('click', () => { state.path = [START]; state.routeId = null; history.replaceState(null, '', '#/routes'); redraw(); });
  $('#r-runes', root).addEventListener('change', (e) => { state.respectRunes = e.target.checked; redraw(); });
}

export function unmount() { resizeObs?.disconnect(); resizeObs = null; }

