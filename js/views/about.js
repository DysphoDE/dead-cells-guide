import { html } from '../util.js';
import { db } from '../data.js';
import { pageHead } from '../components.js';

export const title = () => 'Quellen & Datenstand';

export function render() {
  const notes = [db.meta.builds?.notes, db.meta.meta?.notes].flat().filter(Boolean);
  const sources = [...new Set([...(db.meta.builds?.sources ?? []), ...(db.meta.meta?.sources ?? [])])].filter((s) => typeof s === 'string');
  const counts = [
    ['Waffen, Schilde & Skills', db.gear.length], ['Mutationen', db.mutations.length], ['Outfits', db.outfits.length],
    ['Biome & Arenen', db.biomes.length], ['Bosse', db.bosses.length], ['Runen', db.runes.length],
    ['Builds', db.builds.length], ['Synergie-Kombos', db.synergies.length], ['Routen', db.routes.length],
  ];
  return html`
  ${pageHead('Transparenz', 'Quellen & Datenstand', 'Woher die Daten stammen und wie die Empfehlungen entstanden sind.')}
  <div class="grid cols-3">${counts.map(([k, v]) => html`<div class="panel tight"><b style="font:800 30px var(--font-display)">${v}</b><div class="muted small">${k}</div></div>`)}</div>
  <div class="grid cols-2 section">
    <section class="panel"><h3>Wie die Daten entstanden sind</h3><ul class="bullets">
      <li><b>Spieldaten</b> (Werte, Entwurf-Fundorte, Drop-Chancen, BC-Anforderungen, Biom-Übergänge) stammen aus dem <a href="https://deadcells.wiki.gg" target="_blank" rel="noopener">Dead Cells Wiki auf wiki.gg</a> (Stand Version 3.5 „The End is Near“) und den offiziellen Patchnotes.</li>
      <li><b>Builds, Tierlisten, Synergien und Routen</b> sind redaktionelle Einschätzungen, gebildet aus dem Konsens mehrerer Community-Quellen (Steam-Foren und -Guides, Video-Guides, Tierlisten-Seiten). Sie sind Orientierung, kein Naturgesetz.</li>
      <li><b>Texte</b> sind eigene deutsche Zusammenfassungen. Spielnamen kannst du oben rechts zwischen Englisch (wie im Wiki und in Videos) und Deutsch (wie im deutschen Spiel, aus den Sprachdateien des Spiels) umschalten; Erklärtexte nennen Items meist mit englischem Namen.</li>
      <li><b>Dein Fortschritt</b> wird ausschließlich lokal in deinem Browser gespeichert (localStorage). Es gibt kein Tracking und keine externen Requests.</li>
    </ul></section>
    <section class="panel"><h3>Rechtliches</h3><p style="color:var(--text-2)">Inoffizielles Fan-Projekt ohne Verbindung zu Motion Twin, Evil Empire oder Playdigious. „Dead Cells“, Spielgrafiken, Icons und Namen sind Eigentum ihrer jeweiligen Rechteinhaber. Wiki-Inhalte stehen unter CC BY-SA; Icons und Bilder wurden über das Wiki bezogen.</p>
    ${notes.length ? html`<div class="field-label" style="margin:16px 0 8px">Hinweise zur Recherche</div><ul class="bullets small">${notes.map((n) => html`<li>${n}</li>`)}</ul>` : ''}</section>
  </div>
  ${sources.length ? html`<section class="section"><div class="section-head"><div><h2>Community-Quellen</h2></div></div><div class="panel"><ul class="clean stack small" style="gap:6px">${sources.map((s) => html`<li><a href="${s}" target="_blank" rel="noopener">${s}</a></li>`)}</ul></div></section>` : ''}`;
}
