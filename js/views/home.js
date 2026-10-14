import { html, pct } from '../util.js';
import { db, isOwned, rankBuilds, buildFitsBc, buildDlcOk, buildReadiness, nextUnlocks, biome, L } from '../data.js';
import { profile, hasDlc } from '../store.js';
import { buildCard, icon, ring, blueprintSummary, tierBadge, bcTag } from '../components.js';

export const title = () => 'Übersicht';

function tipOfTheDay() {
  if (!db.tips.length) return null;
  const day = Math.floor(Date.now() / 86_400_000);
  return db.tips[day % db.tips.length];
}

export function render() {
  const trackable = [...db.gear, ...db.mutations];
  const owned = trackable.filter(isOwned).length;
  const fitting = db.builds.filter((b) => buildFitsBc(b) && buildDlcOk(b));
  const ready = fitting.filter((b) => buildReadiness(b).ratio >= 0.999).length;
  const runesOwned = db.runes.filter((r) => profile.runes[r.id]).length;
  const level = db.bossCells.find((x) => x.bc === profile.bc);
  const picks = rankBuilds(fitting).slice(0, 3);
  const next = nextUnlocks(6);
  const route = db.routes.find((r) => (r.bcMin ?? 0) <= profile.bc && profile.bc <= (r.bcMax ?? 5) && hasDlc(r.dlc ?? []));
  const tip = tipOfTheDay();

  return html`
  <section class="hero">
    <div class="hero-inner">
      <div class="eyebrow">Dein Begleiter für die Insel</div>
      <h1>Stirb klüger.<br><em>Lauf weiter.</em></h1>
      <p>Builds, die wirklich tragen. Routen mit allen Schriftrollen. Jeder Entwurf mit Fundort – abgestimmt auf deine Boss Cells und das, was du schon freigeschaltet hast.</p>
      <div class="row"><a class="btn primary" href="#/builds">Build finden</a><a class="btn" href="#/routes">Route planen</a><a class="btn ghost" href="#/workshop">Was passt zusammen?</a></div>
    </div>
  </section>

  <div class="stat-strip">
    <a class="stat" href="#/bc">${ring(pct(profile.bc, 5), `${profile.bc}`, 'var(--cell)')}<span><b>${profile.bc} BC</b><small>${level?.title ?? 'Boss-Cell-Stufe'}</small></span></a>
    <a class="stat" href="#/unlocks">${ring(pct(owned, trackable.length), `${pct(owned, trackable.length)}%`)}<span><b>${owned}<span class="dim" style="font-size:18px"> / ${trackable.length}</span></b><small>Waffen, Skills &amp; Mutationen</small></span></a>
    <a class="stat" href="#/builds">${ring(pct(ready, fitting.length), `${ready}`, 'var(--survival)')}<span><b>${ready}<span class="dim" style="font-size:18px"> / ${fitting.length}</span></b><small>Builds sofort spielbar</small></span></a>
    <a class="stat" href="#/world?tab=runes">${ring(pct(runesOwned, db.runes.length), `${runesOwned}`, 'var(--tactics)')}<span><b>${runesOwned}<span class="dim" style="font-size:18px"> / ${db.runes.length}</span></b><small>Runen gefunden</small></span></a>
  </div>

  <section class="section">
    <div class="section-head"><div><h2>Für deinen nächsten Run</h2><p>Passend zu ${profile.bc} BC – mit dem, was du schon hast, zuerst.</p></div><a class="link-btn" href="#/builds">Alle ${db.builds.length} Builds →</a></div>
    ${picks.length ? html`<div class="grid cols-3">${picks.map(buildCard)}</div>` : html`<div class="empty">Noch keine Builds geladen.</div>`}
  </section>

  <section class="section grid cols-2">
    <div class="panel">
      <div class="eyebrow">Als Nächstes freischalten</div>
      <h3>Diese Entwürfe lohnen sich jetzt</h3>
      <p class="muted small" style="margin-bottom:12px">Starke Items, die du bei ${profile.bc} BC bekommen kannst und noch nicht hast.</p>
      ${next.length ? html`<ul class="clean stack" style="gap:8px">${next.map((e) => html`<li><a class="row" href="${e.url}" style="gap:12px;color:var(--text);flex-wrap:nowrap">${icon(e, 'sm')}<span style="flex:1;min-width:0"><b>${L(e)}</b><small class="muted" style="display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${blueprintSummary(e)}</small></span>${tierBadge(e.tier)}</a></li>`)}</ul>` : html`<p class="muted">Alles Wichtige freigeschaltet – stark!</p>`}
      <a class="link-btn" href="#/unlocks" style="display:inline-block;margin-top:14px">Zum Freischalt-Tracker →</a>
    </div>
    <div class="stack">
      ${level ? html`<div class="panel">
        <div class="bc-hero"><div class="bc-orb">${profile.bc}</div><div><div class="eyebrow">Deine Stufe</div><h3>${level.title}</h3>
        <ul class="bullets small">${(level.changes ?? []).slice(0, 3).map((c) => html`<li>${c}</li>`)}</ul>
        <a class="link-btn" href="#/bc" style="display:inline-block;margin-top:10px">Alles zu Boss Cells →</a></div></div>
      </div>` : ''}
      ${route ? html`<div class="panel">
        <div class="eyebrow">Routen-Empfehlung</div><h3>${L(route)}</h3><p class="muted small" style="margin-bottom:12px">${route.why}</p>
        <div class="path-strip">${route.path.map((n, i) => { const b = biome(n); return html`${i ? html`<span class="arrow">→</span>` : ''}<span class="step ${b?.kind === 'arena' ? 'boss' : ''}">${b?.name ?? n}</span>`; })}</div>
        <a class="link-btn" href="#/routes?r=${route.id}" style="display:inline-block;margin-top:12px">Im Routenplaner öffnen →</a>
      </div>` : ''}
      ${tip ? html`<div class="panel"><div class="eyebrow">Profi-Tipp</div><h3>${tip.topic}</h3><p class="muted">${tip.tip}</p></div>` : ''}
    </div>
  </section>

  <section class="section">
    <div class="section-head"><div><h2>Alles auf einen Blick</h2></div></div>
    <div class="grid cols-4">
      ${[
        ['#/tiers', 'Tierlisten', 'Waffen, Skills, Schilde und Mutationen nach Stärke.'],
        ['#/mutations', 'Mutationen', 'Alle Mutationen plus bewährte 3er-Kombis.'],
        ['#/world', 'Biome & Bosse', 'Jedes Biom mit Ausgängen, Schriftrollen und Boss-Tipps.'],
        ['#/knowledge', 'Wissen', 'Collector-Upgrades, Affixe, Statuseffekte, Glossar.'],
      ].map(([href, t, d]) => html`<a class="card" href="${href}"><h3>${t}</h3><p>${d}</p><span class="link-btn" style="margin-top:auto">Öffnen →</span></a>`)}
    </div>
  </section>`;
}
