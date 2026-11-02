import { html, pct } from '../util.js';
import { db, isOwned, rankBuilds, buildFitsBc, buildDlcOk, buildReadiness, nextUnlocks, biome, L } from '../data.js';
import { profile, hasDlc } from '../store.js';
import { buildCard, icon, blueprintSummary, tierBadge, IC } from '../components.js';
import { CHAPTERS } from '../chapters.js';

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

  const ledger = [
    ['#/bc', 'Boss Cells', html`${profile.bc}`, level?.title ?? 'Boss-Cell-Stufe', pct(profile.bc, 5)],
    ['#/unlocks', 'Freigeschaltet', html`${owned}<span> / ${trackable.length}</span>`, 'Waffen, Skills & Mutationen', pct(owned, trackable.length)],
    ['#/builds', 'Sofort spielbar', html`${ready}<span> / ${fitting.length}</span>`, 'Builds mit allem, was du hast', pct(ready, fitting.length)],
    ['#/world?tab=runes', 'Runen', html`${runesOwned}<span> / ${db.runes.length}</span>`, 'Gefunden', pct(runesOwned, db.runes.length)],
  ];

  return html`
  <section class="opener">
    <figure class="opener-plate"><img src="assets/hero.jpg" alt="Pixel-Art aus Dead Cells: Burgruinen der Insel im Abendrot" width="1920" height="624"></figure>
    <div class="opener-text">
      <h1>Stirb klüger. Lauf weiter.</h1>
      <div>
        <p>Builds, die wirklich tragen. Routen mit allen Schriftrollen. Jeder Entwurf mit Fundort – abgestimmt auf deine Boss Cells und das, was du schon freigeschaltet hast.</p>
        <div class="row"><a class="btn primary" href="#/builds">Build finden</a><a class="btn" href="#/routes">Route planen</a><a class="btn ghost" href="#/workshop">Was passt zusammen?</a></div>
      </div>
    </div>
  </section>

  <section class="ledger" aria-label="Dein Spielstand">
    ${ledger.map(([href, k, v, sub, p]) => html`<a href="${href}"><span class="ledger-k">${k}</span><b class="ledger-v">${v}</b><small>${sub}</small><span class="meter" aria-hidden="true"><i style="--p:${p}%"></i></span></a>`)}
  </section>

  ${!profile.importedAt ? html`<div class="import-cta">
    <div><h3>Spielst du auf dem PC?</h3><p>Lies dein Savegame ein – dann kennt der Guide sofort alle deine Freischaltungen, Runen und Boss Cells. Die Datei bleibt in deinem Browser.</p></div>
    <button class="btn primary" data-save-import>Savegame importieren</button>
  </div>` : ''}

  <section class="section">
    <div class="section-head"><div><h2>Für deinen nächsten Run</h2><p>Passend zu ${profile.bc} BC – mit dem, was du schon hast, zuerst.</p></div><a class="link-btn" href="#/builds">Alle ${db.builds.length} Builds →</a></div>
    ${picks.length ? html`<div class="grid cols-3">${picks.map(buildCard)}</div>` : html`<div class="empty">Noch keine Builds geladen.</div>`}
  </section>

  <section class="section split">
    <div>
      <div class="section-head"><div><h2>Diese Entwürfe lohnen sich jetzt</h2><p>Starke Items, die du bei ${profile.bc} BC bekommen kannst und noch nicht hast.</p></div></div>
      ${next.length ? html`<ol class="clean index-list">${next.map((e) => html`<li><a href="${e.url}">${icon(e, 'sm')}<span class="meta"><b>${L(e)}</b><small>${blueprintSummary(e)}</small></span>${tierBadge(e.tier)}</a></li>`)}</ol>` : html`<p class="muted">Alles Wichtige freigeschaltet – stark!</p>`}
      <a class="link-btn" href="#/unlocks">Zum Freischalt-Tracker →</a>
    </div>
    <div class="stack">
      ${level ? html`<div class="panel">
        <div class="bc-hero"><div class="bc-orb" aria-label="${profile.bc} Boss Cells">${profile.bc}</div><div><h3>${level.title}</h3>
        <ul class="bullets small">${(level.changes ?? []).slice(0, 3).map((c) => html`<li>${c}</li>`)}</ul>
        <a class="link-btn" href="#/bc">Alles zu Boss Cells →</a></div></div>
      </div>` : ''}
      ${route ? html`<div class="panel">
        <h3>${L(route)}</h3><p class="muted small">${route.why}</p>
        <div class="path-strip">${route.path.map((n, i) => { const b = biome(n); return html`<span class="hop">${i ? html`<span class="arrow" aria-hidden="true">→</span>` : ''}<span class="step ${b?.kind === 'arena' ? 'boss' : ''}">${b?.name ?? n}</span></span>`; })}</div>
        <a class="link-btn" href="#/routes?r=${route.id}">Im Routenplaner öffnen →</a>
      </div>` : ''}
      ${tip ? html`<aside class="tipbox"><h3><span class="tip-mark" aria-hidden="true">${IC.alert}</span>${tip.topic}</h3><p>${tip.tip}</p></aside>` : ''}
    </div>
  </section>

  <section class="section">
    <div class="section-head"><div><h2>Inhalt</h2></div></div>
    <div class="contents">
      ${CHAPTERS.map((c) => html`<div class="contents-ch" data-ch="${c.n}"><h3><span>${c.n}</span>${c.title}</h3><ol class="clean">${c.sections.map(([path, label, blurb], i) => html`<li><a href="#/${path}"><b>${c.n}.${i + 1}</b><span><span class="c-label">${label}</span><small>${blurb}</small></span></a></li>`)}</ol></div>`)}
    </div>
  </section>`;
}
