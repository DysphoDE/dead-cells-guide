// Wiederverwendbare UI-Bausteine (geben html``-Fragmente zurück).
import { html, raw } from './util.js';
import { COLOR_LABEL, TYPE_LABEL, SOURCE_LABEL, findByName, isOwned, isFound, cellsLeft, isTrackable, bpAvailable, biome, buildItems, buildReadiness, buildFitsBc, buildDlcOk, L } from './data.js';
import { profile } from './store.js';

export const CHECK = raw('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>');

export const colorClass = (e) => {
  const c = (e?.colors ?? []).filter((x) => x !== 'colorless');
  return c.length > 1 ? 'multi' : c[0] ?? 'colorless';
};

const initials = (name) => String(name ?? '?').split(/\s+/).map((w) => w[0]).join('').slice(0, 2).toUpperCase();

export function icon(e, size = '', { showOwned = false } = {}) {
  const cls = `ico ${size} ${colorClass(e)}`;
  const src = e?.icon ?? e?.image;
  const owned = showOwned && isTrackable(e) && isOwned(e) ? html`<span class="owned-dot" title="Freigeschaltet"></span>` : '';
  if (!src) return html`<span class="${cls}" aria-hidden="true"><span class="fallback">${initials(e?.name)}</span>${owned}</span>`;
  return html`<span class="${cls}" aria-hidden="true"><img src="${src}" alt="" loading="lazy" decoding="async" data-fallback="${initials(e?.name)}">${owned}</span>`;
}

/** Link-Pille für einen Namen oder ein Entity. Unbekannte Namen werden als neutrale Pille gezeigt. */
export function itemLink(ref, { owned = true } = {}) {
  const e = typeof ref === 'string' ? findByName(ref) : ref;
  if (!e) return html`<span class="item-link unknown" title="Kein eigener Eintrag">${icon({ name: ref })}<span>${ref}</span></span>`;
  const missing = owned && isTrackable(e) && !isOwned(e);
  const title = missing ? `${L(e)} – noch nicht freigeschaltet` : e.name;
  return html`<a class="item-link ${missing ? 'missing' : ''}" href="${e.url}" title="${title}">${icon(e)}<span>${L(e)}</span></a>`;
}

export const colorTag = (c) => html`<span class="tag ${c}">${COLOR_LABEL[c] ?? c}</span>`;
export const colorTags = (colors = []) => colors.map(colorTag);
export const typeTag = (e) => html`<span class="tag">${TYPE_LABEL[e.type] ?? e.type}</span>`;
export const dlcTag = (dlc) => (dlc ? (Array.isArray(dlc) ? dlc : [dlc]).map((d) => html`<span class="tag dlc" title="DLC">${d}</span>`) : '');
export const bcTag = (bc, suffix = '+') => html`<span class="tag bc" title="Boss Cells">${bc}${suffix} BC</span>`;
export const tierBadge = (tier, title = '') => (tier ? html`<span class="tier ${tier}" title="${title || `Tier ${tier}`}">${tier}</span>` : '');
export const difficulty = (n = 1) => html`<span class="diff" title="Schwierigkeit ${n}/3">${[1, 2, 3].map((i) => html`<i class="${i <= n ? 'on' : ''}"></i>`)}</span>`;

/** Hinweis „Entwurf schon im Gepäck“ inkl. restlicher Zellen. */
export const foundTag = (e) => {
  if (!isFound(e)) return '';
  const left = cellsLeft(e);
  return html`<span class="tag found" title="Entwurf eingesammelt, beim Collector noch nicht freigeschaltet">Entwurf da${left != null ? ` · noch ${left} Zellen` : ''}</span>`;
};

export const ownToggle = (e) => {
  if (!isTrackable(e)) return '';
  if (e.blueprint?.default) return html`<span class="tag ok">Von Anfang an verfügbar</span>`;
  const on = isOwned(e);
  return html`<button class="own-toggle" data-own="${e.key}" aria-pressed="${on}"><span class="box"></span>${on ? 'Freigeschaltet' : 'Als freigeschaltet markieren'}</button>`;
};

export const tick = (e) => {
  if (e.blueprint?.default) return html`<span class="tick" aria-pressed="true" title="Startausrüstung">${CHECK}</span>`;
  const on = isOwned(e);
  return html`<button class="tick" data-own="${e.key}" aria-pressed="${on}" aria-label="${L(e)} ${on ? 'freigeschaltet' : 'nicht freigeschaltet'}">${CHECK}</button>`;
};

export function pageHead(eyebrow, title, text, actions = '') {
  return html`<header class="page-head"><div><div class="eyebrow">${eyebrow}</div><h1>${title}</h1>${text ? html`<p>${text}</p>` : ''}</div>${actions ? html`<div class="row">${actions}</div>` : ''}</header>`;
}

export const empty = (text) => html`<div class="empty">${text}</div>`;

export function blueprintSummary(e) {
  const bp = e.blueprint ?? {};
  if (bp.default) return 'Von Anfang an verfügbar';
  if (bp.text) return bp.text;
  const parts = [SOURCE_LABEL[bp.sourceType], bp.from, bp.biomes?.join(', ')].filter(Boolean);
  return parts.join(' · ') || 'Fundort unbekannt';
}

export function blueprintFacts(e) {
  const bp = e.blueprint ?? {};
  const rows = [];
  if (bp.default) rows.push(['Status', 'Von Anfang an verfügbar']);
  if (bp.sourceType && !bp.default) rows.push(['Quelle', SOURCE_LABEL[bp.sourceType] ?? bp.sourceType]);
  if (bp.from) rows.push(['Von', itemLink(bp.from, { owned: false })]);
  if (bp.biomes?.length) rows.push(['Wo', html`<span class="row" style="gap:6px">${bp.biomes.map((n) => { const b = biome(n); return b ? html`<a class="tag" href="${b.url}">${L(b)}</a>` : html`<span class="tag">${n}</span>`; })}</span>`]);
  if (bp.dropChance) rows.push(['Drop-Chance', `${String(bp.dropChance).replace('.', ',')} %`]);
  if (!bp.default) rows.push(['Ab Boss Cells', html`${bcTag(bp.minBC ?? 0)} ${(bp.minBC ?? 0) > profile.bc ? html`<span class="tag warn">über deiner aktuellen BC</span>` : ''}`]);
  if (bp.cells != null) rows.push(['Kosten beim Collector', html`<b style="color:var(--cell)">${bp.cells}</b> Zellen`]);
  return rows;
}

export const kv = (rows) => html`<dl class="kv">${rows.map(([k, v]) => html`<dt>${k}</dt><dd>${v}</dd>`)}</dl>`;

export function itemCard(e, { sub } = {}) {
  const available = bpAvailable(e);
  return html`<a class="card item-card ${colorClass(e)}" href="${e.url}">
    ${icon(e, '', { showOwned: true })}
    <span class="meta"><h3>${L(e)}</h3><small>${sub ?? `${TYPE_LABEL[e.type] ?? e.type} · ${e.colors.map((c) => COLOR_LABEL[c]).join(' / ')}`}</small></span>
    <span class="side">${tierBadge(e.tier)}${!available ? html`<span class="tag lock" title="Bei deiner BC/DLC-Auswahl nicht erhältlich">gesperrt</span>` : ''}</span>
  </a>`;
}

export function buildCard(b) {
  const r = buildReadiness(b);
  const fits = buildFitsBc(b) && buildDlcOk(b);
  const core = buildItems(b).slice(0, 6);
  return html`<a class="card build-card ${b.color}" href="${b.url}">
    <div class="tags-row">${tierBadge(b.tier, `Build-Tier ${b.tier}`)}${colorTag(b.color)}${b.secondaryColor ? colorTag(b.secondaryColor) : ''}<span class="tag">${b.archetype}</span></div>
    <div><h3>${L(b)}</h3><p style="margin-top:6px">${b.tagline}</p></div>
    <div class="loadout-strip">${core.map(({ name, entity }) => html`<span title="${name}${entity && isTrackable(entity) && !isOwned(entity) ? ' (fehlt dir)' : ''}" class="${entity && isTrackable(entity) && !isOwned(entity) ? 'not-owned' : ''}">${icon(entity ?? { name }, 'sm')}</span>`)}</div>
    <div class="card-foot">${difficulty(b.difficulty)}<span>${b.bcMin}–${b.bcMax} BC</span>${b.dlc?.length ? html`<span class="tag dlc">DLC</span>` : ''}
      <span class="ready">${!fits ? html`<span class="tag lock">passt nicht zu deiner BC/DLC</span>` : r.total && r.owned === r.total ? html`<span class="tag ok">Alles freigeschaltet</span>` : html`<span class="tag">${r.owned}/${r.total} freigeschaltet</span>`}</span></div>
  </a>`;
}

export function ring(p, label, color = 'var(--flame)') {
  return html`<span class="ring" style="--p:${p};--rc:${color}"><span>${label}</span></span>`;
}
