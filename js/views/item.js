// Detailseite für Ausrüstung (#/item/<id>) und Mutationen (#/mutation/<id>).
import { html } from '../util.js';
import { db, TYPE_LABEL, buildItems, bpAvailable, L, altName } from '../data.js';
import { profile } from '../store.js';
import { icon, colorTags, dlcTag, tierBadge, foundTag, ownToggle, blueprintFacts, kv, itemLink, empty } from '../components.js';
import { partnersFor, applies, benefits, EFFECTS } from '../synergy.js';

const find = (ctx) => (ctx.path === 'mutation' ? db.mutations : db.gear).find((x) => x.id === ctx.param);
export const title = (ctx) => L(find(ctx)) || 'Eintrag';

const SOURCE_TAG = { community: 'Community', set: 'Mutations-Kombi', mechanic: 'Mechanik' };

export function render(ctx) {
  const e = find(ctx);
  const isMut = ctx.path === 'mutation';
  if (!e) return empty('Diesen Eintrag gibt es nicht.');
  const usedIn = db.builds.filter((b) => buildItems(b, { withAlternatives: true }).some((x) => x.entity === e));
  const partners = partnersFor(e);
  const app = applies(e);
  const ben = benefits(e);
  const stats = [];
  if (!isMut) {
    stats.push(['Typ', TYPE_LABEL[e.type] ?? e.type]);
    if (e.twoHanded) stats.push(['Hände', 'Zweihändig – belegt beide Waffenplätze']);
    if (e.baseDps != null) stats.push(['Basis-DPS', html`<b>${e.baseDps}</b>${e.dps2 != null ? html` <span class="muted">(Krit/Alt: ${e.dps2})</span>` : ''}`]);
    if (e.cooldown != null) stats.push(['Abklingzeit', `${String(e.cooldown).replace('.', ',')} s`]);
  }
  if (e.crit) stats.push(['Krit-Bedingung', e.crit]);
  if (app.length) stats.push(['Erzeugt', html`<span class="row" style="gap:6px">${app.map((a) => html`<span class="tag">${EFFECTS[a].label}</span>`)}</span>`]);
  if (ben.length) stats.push(['Profitiert von', html`<span class="row" style="gap:6px">${ben.map((a) => html`<span class="tag">${EFFECTS[a].label}</span>`)}</span>`]);
  if (isMut && e.numbers) stats.push(['Werte', e.numbers]);

  return html`
  <a class="back" href="${isMut ? '#/mutations' : '#/arsenal'}">← ${isMut ? 'Alle Mutationen' : 'Arsenal'}</a>
  <section class="detail-hero ${e.colors[0]}">
    ${icon(e, 'xl')}
    <div>
      <div class="row" style="gap:6px">${tierBadge(e.tier)}${colorTags(e.colors)}<span class="tag">${isMut ? 'Mutation' : TYPE_LABEL[e.type]}</span>${dlcTag(e.dlc)}</div>
      <h1 style="margin-top:10px">${L(e)}</h1>
      ${altName(e) ? html`<p class="sub">${profile.prefs.names === 'de' ? 'Englisch' : 'Im deutschen Spiel'}: ${altName(e)}</p>` : ''}
      <p class="lead">${isMut ? e.effect : e.description}</p>
      <div class="row">${ownToggle(e)}${foundTag(e)}${!bpAvailable(e) ? html`<span class="tag warn">Bei ${profile.bc} BC / deinen DLCs nicht erhältlich</span>` : ''}${e.wiki ? html`<a class="btn sm ghost" href="${e.wiki}" target="_blank" rel="noopener">Im Wiki ↗</a>` : ''}</div>
    </div>
  </section>

  <div class="detail-grid">
    <div class="stack">
      ${stats.length ? html`<section class="panel"><h3>Mechanik</h3>${kv(stats)}${e.notes ? html`<p class="note" style="margin-top:14px">${e.notes}</p>` : ''}</section>` : ''}
      ${e.tierWhy ? html`<section class="panel"><div class="row" style="gap:10px;margin-bottom:8px">${tierBadge(e.tier)}<h3 style="margin:0">Einschätzung</h3></div><p style="color:var(--text-2)">${e.tierWhy}</p></section>` : ''}
      <section class="panel">
        <h3>Passt gut zu</h3>
        <p class="muted small" style="margin-bottom:12px">Community-Kombos zuerst, danach Partner, die mechanisch passen (Zustand erzeugen → Krit auslösen).</p>
        ${partners.length ? html`<div class="stack" style="gap:10px">${partners.map((p) => html`<div class="row" style="flex-wrap:nowrap;align-items:flex-start;gap:12px">${itemLink(p.e)}<span class="small" style="color:var(--text-2);flex:1;padding-top:6px">${p.why} <span class="dim">· ${SOURCE_TAG[p.source]}</span></span></div>`)}</div>` : html`<p class="muted">Keine besonderen Partner bekannt – ein solides Allround-Item.</p>`}
        <a class="btn sm" style="margin-top:16px" href="#/workshop?add=${encodeURIComponent(e.name)}">In der Werkstatt ausprobieren</a>
      </section>
      ${usedIn.length ? html`<section class="panel"><h3>In diesen Builds</h3><div class="stack" style="gap:8px;margin-top:10px">${usedIn.map((b) => html`<a href="${b.url}" class="row" style="justify-content:space-between;color:var(--text)"><b>${L(b)}</b><span class="row" style="gap:6px">${tierBadge(b.tier)}<span class="tag">${b.archetype}</span></span></a>`)}</div></section>` : ''}
    </div>
    <aside class="stack">
      <section class="panel">
        <h3>Entwurf</h3>
        ${e.blueprint.text ? html`<p style="color:var(--text-2);margin-bottom:14px">${e.blueprint.text}</p>` : ''}
        ${kv(blueprintFacts(e))}
      </section>
    </aside>
  </div>`;
}
