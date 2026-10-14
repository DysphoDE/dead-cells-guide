import { html, matches, $ } from '../util.js';
import { db, findByName, isOwned, dlcOk, COLOR_LABEL, tierScore, L } from '../data.js';
import { profile, update } from '../store.js';
import { icon, itemLink, pageHead, tierBadge, colorTag } from '../components.js';
import { analyze, suggest, describeType } from '../synergy.js';
import { openDialog, closeDialog } from '../ui.js';

export const title = () => 'Was passt zusammen?';

const SLOT_LABEL = { weapons: ['Hauptwaffe', 'Zweitwaffe / Schild'], skills: ['Skill links', 'Skill rechts'], mutations: ['Mutation 1', 'Mutation 2', 'Mutation 3'] };
const poolFor = (kind) => (kind === 'mutations' ? db.mutations : db.gear.filter((g) => (kind === 'weapons' ? g.slot === 'weapon' : g.slot === 'skill')));

function applyParams(ctx) {
  const build = ctx.params.build;
  const adds = ctx.search?.getAll('add') ?? [];
  if (!build && !adds.length) return;
  update((p) => {
    if (build) {
      const b = db.builds.find((x) => x.id === build);
      if (b) p.workshop = { weapons: [b.core.weapons[0] ?? null, b.core.weapons[1] ?? null], skills: [b.core.skills[0] ?? null, b.core.skills[1] ?? null], mutations: [0, 1, 2].map((i) => b.core.mutations[i] ?? null) };
    }
    for (const add of adds) {
      const e = findByName(add);
      if (e) {
        const kind = e.kind === 'mutation' ? 'mutations' : e.slot === 'weapon' ? 'weapons' : 'skills';
        const slots = p.workshop[kind];
        if (!slots.includes(e.name)) { const free = slots.indexOf(null); slots[free === -1 ? 0 : free] = e.name; }
      }
    }
  }, { silent: true });
  history.replaceState(null, '', '#/workshop');
}

function slotButton(kind, i) {
  const name = profile.workshop[kind][i];
  const e = findByName(name);
  return html`<div class="slot-pick ${e ? 'filled' : ''}">
    <button class="slot-main" data-slot="${kind}:${i}" aria-label="${SLOT_LABEL[kind][i]}: ${e ? L(e) : 'leer'} – ändern">
      ${e ? icon(e, '', { showOwned: true }) : html`<span class="ico"><span class="fallback">+</span></span>`}
      <span class="meta"><small class="slot-label">${SLOT_LABEL[kind][i]}</small><b>${e ? L(e) : 'Auswählen …'}</b>${e ? html`<small>${describeType(e)} · ${e.colors.map((c) => COLOR_LABEL[c]).join(' / ')}</small>` : ''}</span>
    </button>
    ${e ? html`<a class="icon-btn" href="${e.url}" aria-label="${L(e)} ansehen" title="Details" style="width:32px;height:32px">↗</a><button class="icon-btn" data-clear="${kind}:${i}" aria-label="${L(e)} entfernen" title="Entfernen" style="width:32px;height:32px">✕</button>` : ''}
  </div>`;
}

function analysisPanel() {
  const ws = profile.workshop;
  const a = analyze(ws);
  const emptyKinds = ['weapons', 'skills', 'mutations'].filter((k) => ws[k].some((x) => !x));
  if (!a.insights.length && !a.matches.length) {
    return html`<div class="panel"><h3>Analyse</h3><p class="muted">Wähle links mindestens eine Waffe oder einen Skill. Die Werkstatt prüft Farben, Krit-Bedingungen und bekannte Kombos und schlägt passende Partner vor.</p>
    <div class="field-label" style="margin:18px 0 10px">Oder starte mit einem Build</div>
    <div class="chips">${db.builds.slice().sort((x, y) => tierScore(y) - tierScore(x)).slice(0, 8).map((b) => html`<a class="chip" href="#/workshop?build=${b.id}">${L(b)}</a>`)}</div></div>`;
  }
  return html`<div class="stack">
    <div class="panel">
      <div class="row" style="justify-content:space-between"><h3 style="margin:0">Synergie</h3>${a.color ? colorTag(a.color) : ''}</div>
      <div class="score" style="margin:12px 0 4px"><div class="score-bar"><i style="--p:${a.score}%"></i></div><b style="font:800 26px var(--font-display);min-width:52px;text-align:right">${a.score}</b></div>
      <p class="dim small">Grobe Heuristik aus Farbe, Krit-Bedingungen und recherchierten Kombos – kein exakter Schadensrechner.</p>
      <div style="margin-top:10px">${a.insights.map((x) => html`<div class="insight ${x.type}"><span class="ic">${x.type === 'good' ? '✓' : x.type === 'warn' ? '!' : 'i'}</span><span><b>${x.title}</b><br>${x.text}</span></div>`)}</div>
    </div>
    ${emptyKinds.length ? html`<div class="panel"><h3>Vorschläge für freie Plätze</h3>
      ${emptyKinds.map((k) => {
        const s = suggest(ws, k, 5);
        return s.length ? html`<div class="field-label" style="margin:14px 0 8px">${k === 'weapons' ? 'Waffen' : k === 'skills' ? 'Skills' : 'Mutationen'}</div>
          <div class="stack" style="gap:8px">${s.map((x) => html`<div class="row" style="flex-wrap:nowrap;gap:10px;align-items:flex-start"><button class="btn sm" data-put="${k}" data-name="${x.e.name}" title="In freien Platz übernehmen">+</button>${itemLink(x.e)}<span class="small muted" style="flex:1;padding-top:6px">${x.why[0] ?? ''}</span></div>`)}</div>` : '';
      })}
    </div>` : ''}
    ${a.matches.length ? html`<div class="panel"><h3>Ähnliche Builds</h3><div class="stack" style="gap:8px;margin-top:8px">${a.matches.map(({ b, n }) => html`<a class="row" href="${b.url}" style="justify-content:space-between;color:var(--text)"><span><b>${L(b)}</b> <span class="dim small">· ${n} gemeinsam</span></span>${tierBadge(b.tier)}</a>`)}</div></div>` : ''}
  </div>`;
}

export function render(ctx) {
  applyParams(ctx);
  return html`
  ${pageHead('Synergie-Werkstatt', 'Was passt zusammen?', 'Stell dein Loadout zusammen – die Werkstatt erklärt dir, was harmoniert, was sich beißt, und was noch fehlt.', html`<button class="btn sm ghost" data-reset-ws>Leeren</button>`)}
  <div class="workshop">
    <div class="stack">
      <div class="panel"><div class="field-label" style="margin-bottom:10px">Waffen</div><div class="stack" style="gap:8px">${[0, 1].map((i) => slotButton('weapons', i))}</div></div>
      <div class="panel"><div class="field-label" style="margin-bottom:10px">Skills</div><div class="stack" style="gap:8px">${[0, 1].map((i) => slotButton('skills', i))}</div></div>
      <div class="panel"><div class="field-label" style="margin-bottom:10px">Mutationen</div><div class="stack" style="gap:8px">${[0, 1, 2].map((i) => slotButton('mutations', i))}</div></div>
    </div>
    <div id="ws-analysis">${analysisPanel()}</div>
  </div>`;
}

function setSlot(kind, i, name) {
  update((p) => {
    const slots = p.workshop[kind];
    const existing = slots.indexOf(name);
    if (name && existing !== -1 && existing !== i) slots[existing] = null;
    slots[i] = name;
  });
}

function picker(kind, i) {
  let q = '';
  let ownedOnly = false;
  const ws = profile.workshop;
  const sugg = suggest(ws, kind, 6).map((x) => x.e);
  const listHtml = () => {
    const pool = poolFor(kind).filter((e) => dlcOk(e) && (!ownedOnly || isOwned(e)) && matches(q, e.name, e.nameDe, e.tags, e.description, e.effect));
    const ordered = q ? pool.sort((a, b) => a.name.localeCompare(b.name)) : [...sugg.filter((s) => pool.includes(s)), ...pool.filter((e) => !sugg.includes(e)).sort((a, b) => tierScore(b) - tierScore(a) || a.name.localeCompare(b.name))];
    return ordered.map((e) => html`<button data-pick="${e.name}">${icon(e, 'sm', { showOwned: true })}<span style="flex:1;min-width:0"><b>${L(e)}</b>${sugg.includes(e) && !q ? html` <span class="tag ok" style="margin-left:4px">passt</span>` : ''}<small>${describeType(e)} · ${e.colors.map((c) => COLOR_LABEL[c]).join(' / ')}</small></span>${tierBadge(e.tier)}</button>`);
  };
  const d = openDialog(html`
    <div class="dialog-head"><div><div class="eyebrow">${SLOT_LABEL[kind][i]}</div><h2 id="dialog-title">Auswählen</h2></div><button class="icon-btn" data-close aria-label="Schließen">✕</button></div>
    <div class="row"><input class="input" id="pick-q" type="search" placeholder="Suchen …" style="flex:1" autocomplete="off"><label class="switch"><input type="checkbox" id="pick-own"><span class="track"></span>Nur freigeschaltet</label></div>
    <div class="picker-list" id="pick-list">${listHtml()}</div>`);
  const list = $('#pick-list', d);
  const refresh = () => { list.innerHTML = String(html`${listHtml()}`); };
  $('#pick-q', d).addEventListener('input', (ev) => { q = ev.target.value; refresh(); });
  $('#pick-own', d).addEventListener('change', (ev) => { ownedOnly = ev.target.checked; refresh(); });
  list.addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-pick]');
    if (!b) return;
    closeDialog();
    setSlot(kind, i, b.dataset.pick);
  });
  setTimeout(() => $('#pick-q', d)?.focus(), 30);
}

export function mount(root) {
  root.addEventListener('click', (ev) => {
    const clear = ev.target.closest('[data-clear]');
    if (clear) { const [k, i] = clear.dataset.clear.split(':'); setSlot(k, +i, null); return; }
    const slot = ev.target.closest('[data-slot]');
    if (slot) { const [k, i] = slot.dataset.slot.split(':'); picker(k, +i); return; }
    const put = ev.target.closest('[data-put]');
    if (put) { const k = put.dataset.put; const i = profile.workshop[k].indexOf(null); if (i !== -1) setSlot(k, i, put.dataset.name); return; }
    if (ev.target.closest('[data-reset-ws]')) update((p) => { p.workshop = { weapons: [null, null], skills: [null, null], mutations: [null, null, null] }; });
  });
}
