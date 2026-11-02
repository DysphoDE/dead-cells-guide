import { html } from '../util.js';
import { db, biome, L } from '../data.js';
import { empty, bcTag, dlcTag, IC } from '../components.js';

const get = (id) => db.bosses.find((b) => b.id === id);
export const title = (ctx) => L(get(ctx.param)) || 'Boss';

export function render(ctx) {
  const b = get(ctx.param);
  if (!b) return empty('Diesen Boss gibt es nicht.');
  const arena = biome(b.biome);
  const before = arena ? db.biomes.filter((x) => x.exits.some((e) => biome(e.to)?.id === arena.id)) : [];
  const drops = [...db.gear, ...db.mutations, ...db.outfits].filter((e) => e.blueprint.from && (e.blueprint.from === b.name || e.blueprint.from === b.name.replace(/^The /, '')));
  return html`
  <a class="back" href="#/world?tab=bosses">← Alle Bosse</a>
  <section class="detail-hero">
    ${b.image ? html`<span class="ico xl" style="overflow:hidden"><img src="${b.image}" alt="" style="width:100%;height:100%;object-fit:cover;image-rendering:auto"></span>` : html`<span class="ico xl"><span class="fallback">${b.name[0]}</span></span>`}
    <div>
      <h1>${L(b)}</h1>
      <p class="lead">${b.description}</p>
      <div class="row" style="gap:8px"><span class="tag">Boss</span>${(b.minBC ?? 0) > 0 ? bcTag(b.minBC) : ''}${dlcTag(b.dlc)}</div>
      <div class="row">${arena ? html`<a class="tag" href="${arena.url}">Arena: ${L(arena)}</a>` : ''}${b.wiki ? html`<a class="btn sm ghost" href="${b.wiki}" target="_blank" rel="noopener">Im Wiki ${IC.ext}</a>` : ''}</div>
    </div>
  </section>
  <div class="detail-grid">
    <div class="stack">
      ${b.tips?.length ? html`<section class="panel"><h3>Taktik</h3><ol class="steps" style="margin-top:12px">${b.tips.map((t) => html`<li><span>${t}</span></li>`)}</ol></section>` : ''}
      ${b.dangers?.length ? html`<section class="panel"><h3>Gefährlichste Angriffe</h3><ul class="bullets">${b.dangers.map((t) => html`<li>${t}</li>`)}</ul></section>` : ''}
    </div>
    <aside class="stack">
      ${b.rewards ? html`<section class="panel"><h3>Belohnung</h3><p style="color:var(--text-2)">${b.rewards}</p></section>` : ''}
      ${drops.length ? html`<section class="panel"><h3>Entwürfe als Belohnung</h3><div class="row" style="gap:6px;margin-top:8px">${drops.map((e) => html`<a class="tag" href="${e.url}">${L(e)}</a>`)}</div></section>` : ''}
      ${before.length ? html`<section class="panel"><h3>Zugang über</h3><div class="row" style="gap:6px;margin-top:8px">${before.map((x) => html`<a class="tag" href="${x.url}">${L(x)}</a>`)}</div></section>` : ''}
    </aside>
  </div>`;
}
