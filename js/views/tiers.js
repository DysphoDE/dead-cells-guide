import { html, $ } from '../util.js';
import { db, TIERS, findByName, isOwned, isTrackable, dlcOk, L } from '../data.js';
import { pageHead, empty } from '../components.js';

export const title = () => 'Tierlisten';

const CATS = [['weapons', 'Waffen'], ['shields', 'Schilde'], ['skills', 'Skills'], ['mutations', 'Mutationen']];
const TIER_TEXT = { S: 'Trägt Runs allein', A: 'Sehr stark', B: 'Solide', C: 'Situativ', D: 'Schwach' };
const state = { cat: 'weapons', highlight: false };

function board() {
  const list = (db.tiers[state.cat] ?? []).map((t) => ({ ...t, e: findByName(t.name) })).filter((t) => !t.e || dlcOk(t.e));
  if (!list.length) return empty('Für diese Kategorie gibt es noch keine Tier-Daten.');
  return html`<div class="tier-board">${TIERS.map((tier) => {
    const items = list.filter((t) => t.tier === tier);
    if (!items.length) return '';
    return html`<div class="tier-row ${tier}"><div class="label" title="${TIER_TEXT[tier]}">${tier}</div><div class="items">${items.map((t) => {
      const e = t.e;
      const missing = state.highlight && e && isTrackable(e) && !isOwned(e);
      const tip = `${L(t.e ?? t)}${t.why ? ` – ${t.why}` : ''}`;
      return e
        ? html`<a class="tier-chip ${missing ? 'missing' : ''}" href="${e.url}" title="${tip}" aria-label="${L(t.e ?? t)}">${e.icon ? html`<img src="${e.icon}" alt="" loading="lazy" data-fallback="${t.name.slice(0, 2)}">` : html`<span class="fb">${L(t.e ?? t)}</span>`}</a>`
        : html`<span class="tier-chip" title="${tip}"><span class="fb">${L(t.e ?? t)}</span></span>`;
    })}</div></div>`;
  })}</div>`;
}

function details() {
  const list = (db.tiers[state.cat] ?? []).map((t) => ({ ...t, e: findByName(t.name) })).filter((t) => t.why && (!t.e || dlcOk(t.e)));
  if (!list.length) return '';
  return html`<section class="section"><div class="section-head"><div><h2>Begründungen</h2><p>Warum etwas wo steht – kurz und knapp.</p></div></div>
    <div class="table-wrap"><table class="table"><thead><tr><th>Name</th><th>Tier</th><th>Warum</th><th>Belege</th></tr></thead><tbody>
    ${TIERS.flatMap((tier) => list.filter((t) => t.tier === tier).map((t) => html`<tr><td>${t.e ? html`<a href="${t.e.url}" style="color:var(--text)">${L(t.e ?? t)}</a>` : t.name}</td><td><span class="tier ${tier}">${tier}</span></td><td>${t.why}</td><td>${t.confidence ? html`<span class="rating ${{ hoch: 'top', mittel: 'good', niedrig: 'meh' }[t.confidence] ?? ''}" title="Wie gut die Einstufung durch Quellen gestützt ist">${t.confidence}</span>` : ''}</td></tr>`))}
    </tbody></table></div></section>`;
}

export function render() {
  return html`
  ${pageHead('Konsens statt Bauchgefühl', 'Tierlisten', 'Zusammengeführt aus mehreren aktuellen Community-Tierlisten und Diskussionen (Stand nach den letzten Balance-Patches). Stärke hängt immer von BC, Build und Spielstil ab – nimm es als Kompass, nicht als Gesetz.')}
  <div class="row" style="justify-content:space-between;margin-bottom:6px">
    <div class="tabs" role="tablist" style="margin:0">${CATS.map(([k, v]) => html`<button role="tab" data-cat="${k}" aria-selected="${state.cat === k}">${v}</button>`)}</div>
    <label class="switch"><input type="checkbox" id="t-hl" ${state.highlight ? 'checked' : ''}><span class="track"></span>Fehlende ausgrauen</label>
  </div>
  <p class="small muted" style="margin:10px 0 16px">${Object.entries(TIER_TEXT).map(([k, v]) => `${k} = ${v}`).join(' · ')}</p>
  <div id="t-body">${board()}${details()}</div>`;
}

export function mount(root) {
  const refresh = () => { $('#t-body', root).innerHTML = String(html`${board()}${details()}`); };
  root.querySelectorAll('[data-cat]').forEach((btn) => btn.addEventListener('click', () => {
    state.cat = btn.dataset.cat;
    root.querySelectorAll('[data-cat]').forEach((b) => b.setAttribute('aria-selected', b === btn));
    refresh();
  }));
  $('#t-hl', root).addEventListener('change', (e) => { state.highlight = e.target.checked; refresh(); });
}
