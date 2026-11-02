import { html } from '../util.js';
import { db, biome, rankBuilds, buildFitsBc, buildDlcOk, L } from '../data.js';
import { profile } from '../store.js';
import { pageHead, empty } from '../components.js';

export const title = () => 'Boss Cells';

export function render() {
  const levels = db.bossCells;
  if (!levels.length) return html`${pageHead('Schwierigkeit', 'Boss Cells', '')}${empty('BC-Daten werden noch recherchiert.')}`;
  const builds = rankBuilds(db.builds.filter((b) => buildFitsBc(b) && buildDlcOk(b) && (b.bcMin ?? 0) >= Math.max(0, profile.bc - 1))).slice(0, 4);
  return html`
  ${pageHead('0 bis 5 · jede Stufe ändert das Spiel', 'Boss Cells', 'Was sich auf jeder Stufe ändert – Heilung, Gegner, Malaise, neue Wege – und worauf du dich einstellen musst. Deine aktuelle Stufe stellst du oben rechts ein.')}
  <div class="stack">
    ${levels.map((l) => {
      const active = l.bc === profile.bc;
      return html`<section class="panel" style="${active ? 'border-top-color:var(--ch)' : ''}">
        <div class="bc-hero">
          <button class="bc-orb" data-bc="${l.bc}" style="${active ? '' : 'filter:grayscale(.75) brightness(.7);'}border:0" title="${l.bc} BC einstellen">${l.bc}</button>
          <div>
            <h3 style="font-size:28px">${l.title}</h3>
            ${active ? html`<div class="row" style="gap:8px;margin-top:6px"><span class="tag bc">Deine Stufe</span></div>` : ''}
            ${l.howToGet ? html`<p class="small muted" style="margin-top:4px"><b style="color:var(--text-2)">Freischalten:</b> ${l.howToGet}</p>` : ''}
          </div>
        </div>
        <div class="grid cols-2" style="margin-top:16px">
          <div><div class="field-label" style="margin-bottom:8px">Was sich ändert</div><ul class="bullets small">${(l.changes ?? []).map((c) => html`<li>${c}</li>`)}</ul></div>
          <div class="stack" style="gap:16px">
            ${l.tips?.length ? html`<div><div class="field-label" style="margin-bottom:8px">Tipps</div><ul class="bullets small">${l.tips.map((c) => html`<li>${c}</li>`)}</ul></div>` : ''}
            ${l.newEnemies?.length ? html`<div><div class="field-label" style="margin-bottom:8px">Neue Gegner</div><ul class="clean stack small" style="gap:4px">${l.newEnemies.map((x) => html`<li><b>${x.enemy}</b> <span class="muted">· ${x.biomes.map((id) => L(biome(id) ?? { name: id })).join(', ')}</span></li>`)}</ul></div>` : ''}
          </div>
        </div>
      </section>`;
    })}
  </div>
  ${builds.length ? html`<section class="section"><div class="section-head"><div><h2>Builds für ${profile.bc} BC</h2><p>Speziell für diese Stufe gebaut.</p></div><a class="link-btn" href="#/builds">Alle Builds →</a></div>
    <div class="grid auto">${builds.map((b) => html`<a class="card ${b.color}" href="${b.url}"><h3>${L(b)}</h3><p>${b.tagline}</p></a>`)}</div></section>` : ''}`;
}
