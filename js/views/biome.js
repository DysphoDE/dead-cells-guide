import { html } from '../util.js';
import { db, depthLabel, biome as getBiome, isOwned, bpAvailable, L, altName } from '../data.js';
import { profile, hasDlc } from '../store.js';
import { empty, bcTag, dlcTag, icon, tick, blueprintSummary, IC } from '../components.js';

export const title = (ctx) => L(getBiome(ctx.param)) || 'Biom';

const SOURCE_ORDER = ['lore', 'secret', 'boss', 'enemy', 'challenge', 'shop', 'quest', 'collector', 'achievement', 'other'];

export function render(ctx) {
  const b = getBiome(ctx.param);
  if (!b) return empty('Dieses Biom gibt es nicht.');
  const incoming = db.biomes.filter((x) => x.exits.some((e) => getBiome(e.to)?.id === b.id));
  const bosses = db.bosses.filter((x) => x.biome === b.id);
  const rune = b.runeHere ? db.runes.find((r) => r.name === b.runeHere) : null;
  const bps = (db.blueprintsByBiome.get(b.id) ?? []).filter((e) => e.kind !== 'outfit')
    .sort((x, y) => isOwned(x) - isOwned(y) || SOURCE_ORDER.indexOf(x.blueprint.sourceType) - SOURCE_ORDER.indexOf(y.blueprint.sourceType) || x.name.localeCompare(y.name));
  const outfits = (db.blueprintsByBiome.get(b.id) ?? []).filter((e) => e.kind === 'outfit');
  const missing = bps.filter((e) => !isOwned(e)).length;

  return html`
  <a class="back" href="#/world">← Biome &amp; Bosse</a>
  <section class="detail-hero">
    <div class="ico xl"><span class="fallback" style="font-size:30px">${b.depth ?? (b.kind === 'arena' ? 'Boss' : '?')}</span></div>
    <div>
      <h1>${L(b)}</h1>
      ${altName(b) ? html`<p class="sub">${profile.prefs.names === 'de' ? 'Englisch' : 'Im deutschen Spiel'}: ${altName(b)}</p>` : ''}
      <p class="lead">${b.description}</p>
      <div class="row" style="gap:8px"><span class="tag ${b.kind === 'arena' ? 'warn' : ''}">${depthLabel(b)}</span>${(b.minBC ?? 0) > 0 ? bcTag(b.minBC) : ''}${dlcTag(b.dlc)}</div>
      <div class="row">${b.scrolls?.power != null ? html`<span class="tag">${b.scrolls.power} Schriftrollen der Macht</span>` : ''}${b.scrolls?.dual ? html`<span class="tag">${b.scrolls.dual} Doppel-Rollen</span>` : ''}${b.scrolls?.cursedChest ? html`<span class="tag warn">Verfluchte Truhe möglich</span>` : ''}${b.timedDoor ? html`<span class="tag" title="${b.timedDoor.notes ?? ''}">${IC.clock} Zeittür ${b.timedDoor.minutes} min</span>` : ''}${b.wiki ? html`<a class="btn sm ghost" href="${b.wiki}" target="_blank" rel="noopener">Im Wiki ${IC.ext}</a>` : ''}</div>
    </div>
  </section>

  <div class="detail-grid">
    <div class="stack">
      ${b.tips?.length ? html`<section class="panel"><h3>Tipps</h3><ul class="bullets">${b.tips.map((t) => html`<li>${t}</li>`)}</ul>${b.scrolls?.notes ? html`<p class="note" style="margin-top:14px">${b.scrolls.notes}</p>` : ''}</section>` : ''}
      <section class="panel">
        <div class="row" style="justify-content:space-between"><h3 style="margin:0">Entwürfe hier</h3><span class="tag ${missing ? 'warn' : 'ok'}">${missing ? `${missing} fehlen dir` : 'alles freigeschaltet'}</span></div>
        <p class="muted small" style="margin:6px 0 14px">Gegner-Drops, Lore-Räume, Geheimbereiche und Bosse in diesem Biom. Hake ab, was du hast.</p>
        ${bps.length ? html`<div class="track-list">${bps.map((e) => html`<div class="track-row ${isOwned(e) ? 'owned' : ''}">${tick(e)}${icon(e, 'sm')}<span class="meta"><a href="${e.url}">${L(e)}</a><small>${blueprintSummary(e)}${e.blueprint.dropChance ? ` · ${String(e.blueprint.dropChance).replace('.', ',')} %` : ''}</small></span>${!bpAvailable(e) ? bcTag(e.blueprint.minBC) : ''}</div>`)}</div>` : html`<p class="muted">Keine Entwurf-Fundorte bekannt.</p>`}
      </section>
      ${outfits.length ? html`<section class="panel"><h3>Outfits hier</h3><div class="row" style="gap:6px;margin-top:8px">${outfits.map((o) => html`<a class="tag ${isOwned(o) ? 'ok' : ''}" href="${o.url}">${L(o)}</a>`)}</div></section>` : ''}
    </div>
    <aside class="stack">
      <section class="panel">
        <h3>Ausgänge</h3>
        ${b.exits.length ? html`<ul class="clean stack" style="gap:8px;margin-top:8px">${b.exits.map((e) => {
          const t = getBiome(e.to);
          const locked = (e.minBC ?? 0) > profile.bc || (t && !hasDlc(t.dlc));
          return html`<li class="row" style="justify-content:space-between;gap:8px;${locked ? 'opacity:.55' : ''}">${t ? html`<a href="${t.url}">${L(t)}</a>` : e.to}<span class="row" style="gap:4px">${e.rune ? html`<span class="tag" style="color:var(--tactics)">${e.rune}</span>` : ''}${(e.minBC ?? 0) > 0 ? bcTag(e.minBC) : ''}</span>${e.condition ? html`<small class="muted" style="flex-basis:100%">${e.condition}</small>` : ''}${(e.flags ?? []).map((f) => html`<small class="dim" style="flex-basis:100%">↳ Voraussetzung: ${db.worldFlags[f] ?? f}</small>`)}${e.firstTimeOnly ? html`<small class="dim" style="flex-basis:100%">↳ nur beim ersten Mal</small>` : ''}</li>`;
        })}</ul>` : html`<p class="muted small">Endpunkt.</p>`}
        ${incoming.length ? html`<div class="field-label" style="margin:16px 0 8px">Erreichbar von</div><div class="row" style="gap:6px">${incoming.map((x) => html`<a class="tag" href="${x.url}">${L(x)}</a>`)}</div>` : ''}
      </section>
      ${bosses.length ? html`<section class="panel"><h3>Boss</h3>${bosses.map((x) => html`<a class="row" href="${x.url}" style="gap:10px;color:var(--text);margin-top:8px"><b>${L(x)}</b><span class="muted small">→ Taktik</span></a>`)}</section>` : ''}
      ${rune ? html`<section class="panel"><h3>${L(rune)}</h3><p class="small" style="color:var(--text-2)">${rune.how}</p><p class="small muted" style="margin-top:6px">${rune.effect}</p></section>` : ''}
      ${b.bcEnemies?.length ? html`<section class="panel"><h3>Neue Gegner auf höherer BC</h3><ul class="clean stack small" style="gap:6px;margin-top:8px">${b.bcEnemies.map((x) => html`<li class="row" style="justify-content:space-between">${x.name}${bcTag(x.fromBC)}</li>`)}</ul></section>` : ''}
      ${b.notableEnemies?.length ? html`<section class="panel"><h3>Gegner</h3><div class="row" style="gap:6px;margin-top:6px">${b.notableEnemies.map((n) => html`<span class="tag">${n}</span>`)}</div>${b.elite ? html`<p class="small muted" style="margin-top:10px">${b.elite}</p>` : ''}</section>` : ''}
    </aside>
  </div>`;
}


