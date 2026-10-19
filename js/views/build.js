import { html } from '../util.js';
import { db, buildReadiness, buildFitsBc, buildDlcOk, findByName, COLOR_LABEL, L } from '../data.js';
import { profile, update } from '../store.js';
import { itemLink, tierBadge, colorTag, difficulty, dlcTag, blueprintSummary, icon, empty } from '../components.js';
import { toast } from '../ui.js';

const get = (id) => db.builds.find((b) => b.id === id);
export const title = (ctx) => get(ctx.param)?.name ?? 'Build';

const slotBlock = (label, names) => (names?.length ? html`<div class="slot"><span class="slot-label">${label}</span><div class="stack" style="gap:6px">${names.map((n) => itemLink(n))}</div></div>` : '');
const host = (u) => { try { return new URL(u).hostname.replace(/^www\./, ''); } catch { return u; } };

export function render(ctx) {
  const b = get(ctx.param);
  if (!b) return empty('Diesen Build gibt es nicht. ← Zurück zu den Builds');
  const r = buildReadiness(b);
  const fav = profile.favorites.includes(b.id);
  const fits = buildFitsBc(b);
  const related = db.builds.filter((x) => x.id !== b.id && (x.color === b.color || x.archetype === b.archetype)).slice(0, 3);

  return html`
  <a class="back" href="#/builds">← Alle Builds</a>
  <section class="detail-hero ${b.color}">
    <div class="row" style="gap:6px;align-self:start">${b.core.weapons.slice(0, 2).map((n) => icon(findByName(n) ?? { name: n }, 'lg'))}</div>
    <div>
      <div class="row" style="gap:6px">${tierBadge(b.tier, `Build-Tier ${b.tier}`)}${colorTag(b.color)}${b.secondaryColor ? colorTag(b.secondaryColor) : ''}<span class="tag">${b.archetype}</span>${dlcTag(b.dlc)}</div>
      <h1 style="margin-top:10px">${L(b)}</h1>
      <p class="lead">${b.tagline}</p>
      <div class="row">
        <span class="tag bc">${b.bcMin}–${b.bcMax} BC</span>
        <span class="tag">Schwierigkeit ${difficulty(b.difficulty)}</span>
        ${!fits ? html`<span class="tag warn">Nicht für ${profile.bc} BC empfohlen</span>` : ''}
        ${!buildDlcOk(b) ? html`<span class="tag warn">Benötigt nicht aktivierte DLCs</span>` : ''}
        <span class="spacer"></span>
        <button class="btn sm" data-fav aria-pressed="${fav}">${fav ? '★ Favorit' : '☆ Merken'}</button>
        <a class="btn sm" href="#/workshop?build=${b.id}">In der Werkstatt öffnen</a>
      </div>
    </div>
  </section>

  <div class="detail-grid">
    <div class="stack">
      <section class="panel">
        <h3>Loadout</h3>
        <div class="slot-grid" style="margin-top:12px">
          ${slotBlock('Waffen', b.core.weapons)}
          ${slotBlock('Skills', b.core.skills)}
          ${slotBlock('Mutationen', b.core.mutations)}
        </div>
        ${Object.values(b.alternatives).some((x) => x?.length) ? html`
          <h3 style="margin-top:22px;font-size:18px">Gute Alternativen</h3>
          <div class="slot-grid" style="margin-top:10px">
            ${slotBlock('Waffen', b.alternatives.weapons)}${slotBlock('Skills', b.alternatives.skills)}${slotBlock('Mutationen', b.alternatives.mutations)}
          </div>` : ''}
      </section>
      ${b.mutationWhy ? html`<section class="panel">
        <h3>Die Mutationen im Detail</h3>
        <div class="stack" style="gap:12px;margin-top:12px">${b.core.mutations.map((n) => html`<div class="row" style="flex-wrap:nowrap;align-items:flex-start;gap:12px">${itemLink(n)}<span class="small" style="color:var(--text-2);flex:1;padding-top:6px">${b.mutationWhy[n] ?? ''}</span></div>`)}</div>
        ${b.bossMutations?.length ? html`<div class="note" style="margin-top:16px"><b>Vor dem Boss tauschen:</b> <span class="row" style="gap:6px;margin:8px 0">${b.bossMutations.map((n) => itemLink(n))}</span>${b.bossMutationsWhy ?? ''}</div>` : ''}
      </section>` : ''}
      ${b.whyItWorks ? html`<section class="panel"><h3>Warum es funktioniert</h3><p class="muted" style="color:var(--text-2)">${b.whyItWorks}</p></section>` : ''}
      ${b.howToPlay?.length ? html`<section class="panel"><h3>So spielst du ihn</h3><ol class="steps" style="margin-top:12px">${b.howToPlay.map((s) => html`<li><span>${s}</span></li>`)}</ol></section>` : ''}
      <div class="grid cols-2">
        ${b.strengths?.length ? html`<section class="panel"><h3 style="color:var(--survival)">Stärken</h3><ul class="bullets">${b.strengths.map((s) => html`<li>${s}</li>`)}</ul></section>` : ''}
        ${b.weaknesses?.length ? html`<section class="panel"><h3 style="color:var(--brutality)">Schwächen</h3><ul class="bullets">${b.weaknesses.map((s) => html`<li>${s}</li>`)}</ul></section>` : ''}
      </div>
    </div>

    <aside class="stack">
      <section class="panel">
        <h3>Dein Stand</h3>
        <div class="row" style="margin:8px 0 10px"><b style="font:800 30px var(--font-display)">${r.owned}/${r.total}</b><span class="muted">Kern-Items freigeschaltet</span></div>
        <div class="progress"><i style="--p:${r.total ? (r.owned / r.total) * 100 : 100}%"></i></div>
        ${r.missing.length ? html`<div class="stack" style="gap:10px;margin-top:16px">${r.missing.map((e) => html`<a href="${e.url}" class="row" style="flex-wrap:nowrap;gap:10px;color:var(--text)">${icon(e, 'sm')}<span style="min-width:0"><b>${L(e)}</b><small class="muted" style="display:block">${blueprintSummary(e)}</small></span></a>`)}</div>` : html`<p class="muted small" style="margin-top:12px">Du hast alles für diesen Build. Viel Spaß!</p>`}
      </section>
      ${b.statFocus || b.affixes?.length ? html`<section class="panel">
        <h3>Schriftrollen &amp; Affixe</h3>
        ${b.statFocus ? html`<p class="small" style="color:var(--text-2)">${b.statFocus}</p>` : ''}
        ${b.affixes?.length ? html`<div class="field-label" style="margin:14px 0 8px">Gesuchte Affixe</div><ul class="bullets small">${b.affixes.map((a) => html`<li>${a}</li>`)}</ul>` : ''}
      </section>` : ''}
      ${b.sources?.length ? html`<section class="panel tight"><div class="field-label" style="margin-bottom:8px">Quellen</div><ul class="clean stack small" style="gap:4px">${b.sources.map((s) => html`<li><a href="${s}" target="_blank" rel="noopener">${host(s)} ↗</a></li>`)}</ul></section>` : ''}
      ${related.length ? html`<section class="panel tight"><div class="field-label" style="margin-bottom:8px">Ähnliche Builds</div><ul class="clean stack" style="gap:6px">${related.map((x) => html`<li><a href="${x.url}">${L(x)}</a> <span class="dim small">· ${COLOR_LABEL[x.color] ?? ''}</span></li>`)}</ul></section>` : ''}
    </aside>
  </div>`;
}

export function mount(root, ctx) {
  root.querySelector('[data-fav]')?.addEventListener('click', () => {
    const id = ctx.param;
    const on = !profile.favorites.includes(id);
    update((p) => { p.favorites = on ? [...p.favorites, id] : p.favorites.filter((x) => x !== id); });
    toast(on ? 'Als Favorit gemerkt.' : 'Favorit entfernt.');
  });
}
