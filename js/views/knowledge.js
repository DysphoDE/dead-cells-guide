import { html, norm } from '../util.js';
import { db, L } from '../data.js';
import { pageHead, empty, IC } from '../components.js';
import { profile } from '../store.js';

export const title = () => 'Wissen & Mechaniken';

const RATING_LABEL = { high: 'Pflicht', medium: 'Lohnt sich', low: 'Optional', top: 'Top', good: 'Gut', meh: 'Meh' };

export function render() {
  const m = db.mechanics;
  const blocks = [];
  const add = (id, label, content) => { if (content) blocks.push({ id, label, content }); };

  add('tips-beginner', 'Einsteiger-Tipps', m.beginnerTips?.length && html`<ol class="steps">${m.beginnerTips.map((t) => html`<li><span>${t}</span></li>`)}</ol>`);
  add('tips-pro', 'Profi-Tipps', (m.advancedTips?.length || db.tips.length) && html`
    ${db.tips.length ? html`<div class="grid cols-2">${db.tips.map((t) => html`<div class="panel tight"><b>${t.topic}</b><p class="small" style="color:var(--text-2);margin-top:4px">${t.tip}</p></div>`)}</div>` : ''}
    ${m.advancedTips?.length ? html`<ul class="bullets" style="margin-top:14px">${m.advancedTips.map((t) => html`<li>${t}</li>`)}</ul>` : ''}`);
  for (const s of m.sections ?? []) {
    add(`s-${s.id}`, s.title, html`${s.summary ? html`<p style="color:var(--text-2);margin-bottom:12px">${s.summary}</p>` : ''}<ul class="bullets">${(s.points ?? []).map((p) => html`<li>${p}</li>`)}</ul>${s.wiki ? html`<p class="small" style="margin-top:10px"><a href="${s.wiki}" target="_blank" rel="noopener">Mehr im Wiki ${IC.ext}</a></p>` : ''}`);
  }
  add('collector', 'Collector-Upgrades', m.collector?.length && html`<p class="muted small" style="margin-bottom:12px">Wofür sich deine Zellen lohnen – Empfehlung von oben nach unten.</p>
    <div class="table-wrap"><table class="table"><thead><tr><th>Upgrade</th><th>Kosten</th><th>Effekt</th><th>Wert</th>${Object.keys(profile.collector).length ? html`<th>Du</th>` : ''}</tr></thead><tbody>
    ${[...m.collector].sort((a, b) => ['high', 'medium', 'low'].indexOf(a.recommended) - ['high', 'medium', 'low'].indexOf(b.recommended)).map((c) => html`<tr><td>${L(c)}${c.category ? html`<br><span class="dim small">${c.category}</span>` : ''}</td><td style="white-space:nowrap;color:var(--cell)">${c.cells ?? '–'}${c.minBC ? html`<br><span class="dim small">ab ${c.minBC} BC</span>` : ''}</td><td>${c.effect}${c.why ? html`<br><span class="dim small">${c.why}</span>` : ''}</td><td>${c.recommended ? html`<span class="rating ${c.recommended}">${RATING_LABEL[c.recommended] ?? c.recommended}</span>` : ''}</td>${Object.keys(profile.collector).length ? html`<td>${profile.collector[norm(c.name)] ? html`<span class="tag ok" title="Laut Savegame gekauft">gekauft</span>` : html`<span class="dim">–</span>`}</td>` : ''}</tr>`)}
    </tbody></table></div>`);
  add('forge', 'Schmiede (Forge)', m.forge?.length && html`<div class="table-wrap"><table class="table"><thead><tr><th>Stufe</th><th>Zellen</th><th>Effekt</th></tr></thead><tbody>${m.forge.map((f) => html`<tr><td>${f.level}</td><td style="color:var(--cell)">${f.cells ?? '–'}</td><td>${f.effect}</td></tr>`)}</tbody></table></div>`);
  add('status', 'Statuseffekte', m.statusEffects?.length && html`<div class="grid cols-2">${m.statusEffects.map((s) => html`<div class="panel tight"><b>${s.nameDe ?? s.name}</b>${s.nameDe && s.nameDe !== s.name ? html` <span class="dim small">(${L(s)})</span>` : ''}<p class="small" style="color:var(--text-2);margin-top:6px">${s.effect}</p>${s.synergy ? html`<p class="small muted" style="margin-top:6px">↳ ${s.synergy}</p>` : ''}</div>`)}</div>`);
  add('affixes', 'Affixe', m.affixes?.length && html`<div class="table-wrap"><table class="table"><thead><tr><th>Affix</th><th>Für</th><th>Wert</th><th>Hinweis</th></tr></thead><tbody>${[...m.affixes].sort((a, b) => ['top', 'good', 'meh'].indexOf(a.rating) - ['top', 'good', 'meh'].indexOf(b.rating)).map((a) => html`<tr><td>${L(a)}</td><td class="small">${{ weapon: 'Waffe', skill: 'Skill', shield: 'Schild', any: 'Alles' }[a.type] ?? a.type ?? ''}</td><td><span class="rating ${a.rating}">${RATING_LABEL[a.rating] ?? a.rating}</span></td><td class="small">${a.note}</td></tr>`)}</tbody></table></div>`);
  add('farming', 'Zellen farmen', m.cellFarming?.length && html`<ul class="bullets">${m.cellFarming.map((t) => html`<li>${t}</li>`)}</ul>`);
  add('secrets', 'Geheimnisse & Extras', m.achievementsOrSecrets?.length && html`${m.achievementsOrSecrets.map((s) => html`<details class="faq"><summary>${L(s)}</summary><div>${s.how}</div></details>`)}`);
  add('glossary', 'Glossar', m.glossary?.length && html`<div class="table-wrap"><table class="table"><tbody>${[...m.glossary].sort((a, b) => a.term.localeCompare(b.term)).map((g) => html`<tr><td style="white-space:nowrap">${g.term}</td><td>${g.explanation}</td></tr>`)}</tbody></table></div>`);

  return html`
  ${pageHead('Aus Fehlern wird Erfahrung', 'Wissen & Mechaniken', 'Wie das Spiel unter der Haube funktioniert: Schriftrollen, Heilung, Collector, Affixe, Statuseffekte und die kleinen Tricks, die Runs retten.', html`<a class="btn sm ghost" href="#/about">Quellen &amp; Datenstand</a>`)}
  ${blocks.length ? html`<div class="knowledge">
    <nav class="toc" aria-label="Inhalt">${blocks.map((b) => html`<a href="#/knowledge" data-jump="${b.id}">${b.label}</a>`)}</nav>
    <div class="stack" style="gap:36px">${blocks.map((b) => html`<section class="k-section" id="${b.id}"><h2 style="font-size:32px;margin-bottom:14px">${b.label}</h2>${b.content}</section>`)}</div>
  </div>` : empty('Mechanik-Daten werden noch recherchiert.')}`;
}

export function mount(root) {
  root.addEventListener('click', (ev) => {
    const a = ev.target.closest('[data-jump]');
    if (!a) return;
    ev.preventDefault();
    document.getElementById(a.dataset.jump)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}
