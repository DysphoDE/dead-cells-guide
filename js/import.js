// Dialog für den Savegame-Import: Datei wählen/ziehen → Vorschau → übernehmen.
import { html } from './util.js';
import { db, L, isOwned } from './data.js';
import { profile, update } from './store.js';
import { readSavegame } from './savegame.js';
import { openDialog, closeDialog, toast } from './ui.js';
import { icon } from './components.js';

let idMap = null;
const loadMap = async () => (idMap ??= await fetch('data/save-ids.json', { cache: 'no-cache' }).then((r) => r.json()));

const PATHS = [
  ['Steam (Cloud, Standard)', 'C:\\Program Files (x86)\\Steam\\userdata\\<deine-ID>\\588650\\remote\\user_0.dat'],
  ['Steam (ohne Cloud)', '<Spielordner>\\Dead Cells\\save\\user_0.dat'],
  ['Andere PC-Versionen', 'Ordner „save“ im Installationsverzeichnis des Spiels'],
];

const head = (sub) => html`<div class="dialog-head"><div><div class="eyebrow">Savegame-Import</div><h2 id="dialog-title">${sub}</h2></div><button class="icon-btn" data-close aria-label="Schließen">✕</button></div>`;

export function openImport() {
  const d = openDialog(html`${head('Spielstand einlesen')}
    <p style="color:var(--text-2)">Lade deine <b>user_0.dat</b> hoch (bzw. user_1/2.dat für weitere Spielstände). Die Datei wird nur in deinem Browser gelesen – sie wird nirgendwohin geschickt und nicht verändert.</p>
    <label class="drop" id="drop">
      <input type="file" id="save-file" accept=".dat,application/octet-stream">
      <b>Datei hier ablegen</b><span class="muted small">oder klicken zum Auswählen</span>
    </label>
    <details class="faq" style="margin-top:14px"><summary>Wo finde ich die Datei?</summary><div>
      <ul class="clean stack small" style="gap:8px">${PATHS.map(([k, v]) => html`<li><b>${k}</b><br><code>${v}</code></li>`)}</ul>
      <p class="small muted" style="margin-top:10px">Tipp: Im Datei-Dialog den Pfad oben in die Adresszeile einfügen. Steam-Ordner „userdata“ enthält einen Unterordner mit deiner Steam-ID – bei nur einem Konto gibt es genau einen. Konsolen- und Handy-Spielstände werden nicht unterstützt.</p>
    </div></details>
    <p class="small" id="save-error" style="color:var(--brutality);margin-top:10px" hidden></p>`);

  const input = d.querySelector('#save-file');
  const drop = d.querySelector('#drop');
  const handle = async (file) => {
    if (!file) return;
    const err = d.querySelector('#save-error');
    err.hidden = true;
    drop.classList.add('busy');
    try {
      if (file.size > 20_000_000) throw new Error('Die Datei ist zu groß für einen Dead-Cells-Spielstand.');
      const [map, buf] = await Promise.all([loadMap(), file.arrayBuffer()]);
      preview(await readSavegame(buf, map), file.name);
    } catch (e) {
      err.textContent = e.message || 'Die Datei konnte nicht gelesen werden.';
      err.hidden = false;
    } finally {
      drop.classList.remove('busy');
    }
  };
  input.addEventListener('change', () => handle(input.files?.[0]));
  drop.addEventListener('dragover', (e) => { e.preventDefault(); drop.classList.add('over'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('over'));
  drop.addEventListener('drop', (e) => { e.preventDefault(); drop.classList.remove('over'); handle(e.dataTransfer?.files?.[0]); });
}

function preview(save, fileName) {
  const tracked = (k) => db.byKey.get(k);
  const unlocked = [...save.unlocked].map(tracked).filter(Boolean);
  const found = [...save.found.keys()].map(tracked).filter(Boolean);
  const count = (list, kind) => list.filter((e) => e.kind === kind).length;
  const added = unlocked.filter((e) => !isOwned(e));
  const removed = Object.keys(profile.owned).filter((k) => !save.unlocked.has(k)).map(tracked).filter(Boolean);
  const runes = db.runes.filter((r) => save.runes.has(r.id));

  const d = openDialog(html`${head('Das steht in deinem Spielstand')}
    <p class="small muted" style="margin-top:-6px">${fileName} · ${save.entries} Einträge gelesen</p>
    <div class="grid cols-3" style="gap:8px;margin:14px 0">
      ${[['Waffen & Skills', count(unlocked, 'gear'), db.gear.length], ['Mutationen', count(unlocked, 'mutation'), db.mutations.length], ['Outfits', count(unlocked, 'outfit'), db.outfits.length]]
        .map(([k, n, t]) => html`<div class="panel tight"><b style="font:800 26px var(--font-display)">${n}<span class="dim" style="font-size:16px"> / ${t}</span></b><div class="muted small">${k} freigeschaltet</div></div>`)}
    </div>
    <ul class="clean stack small" style="gap:8px">
      <li><b>${found.length}</b> Entwürfe gefunden, aber noch nicht beim Collector freigeschaltet</li>
      <li><b>${runes.length}</b> von ${db.runes.length} Runen${runes.length ? html`: <span class="muted">${runes.map((r) => L(r)).join(', ')}</span>` : ''}</li>
      <li>Höchste freigeschaltete Stufe: <b>${save.bc} Boss Cell${save.bc === 1 ? '' : 's'}</b></li>
      <li><b>${save.collector.size}</b> Collector-Upgrades${save.aspects.size ? html` · <b>${save.aspects.size}</b> Aspekte` : ''}</li>
    </ul>
    ${added.length ? html`<div class="field-label" style="margin:16px 0 8px">Neu für den Guide (${added.length})</div><div class="row" style="gap:4px">${added.slice(0, 40).map((e) => html`<span title="${L(e)}">${icon(e, 'sm')}</span>`)}${added.length > 40 ? html`<span class="dim small">+${added.length - 40}</span>` : ''}</div>` : ''}
    <div class="stack" style="gap:10px;margin-top:18px">
      <label class="check"><input type="radio" name="mode" value="replace" checked> Spielstand übernehmen – ersetzt deine bisherigen Haken${removed.length ? html` <span class="tag warn">${removed.length} würden entfernt</span>` : ''}</label>
      <label class="check"><input type="radio" name="mode" value="merge"> Nur ergänzen – bisherige Haken bleiben</label>
      <label class="check"><input type="checkbox" id="set-bc" checked> Boss-Cell-Regler auf ${save.bc} BC stellen</label>
    </div>
    <div class="row" style="margin-top:20px;justify-content:flex-end"><button class="btn ghost" data-close>Abbrechen</button><button class="btn primary" id="apply-save">Übernehmen</button></div>`);

  d.querySelector('#apply-save').addEventListener('click', () => {
    const replace = d.querySelector('input[name="mode"]:checked').value === 'replace';
    const setBc = d.querySelector('#set-bc').checked;
    update((p) => {
      if (replace) { p.owned = {}; p.found = {}; p.runes = {}; p.collector = {}; p.aspects = []; }
      for (const e of unlocked) { p.owned[e.key] = true; delete p.found[e.key]; }
      for (const e of found) if (!p.owned[e.key]) p.found[e.key] = save.found.get(e.key) ?? 0;
      for (const r of runes) p.runes[r.id] = true;
      for (const c of save.collector) p.collector[c] = true;
      p.aspects = [...new Set([...p.aspects, ...save.aspects])];
      if (setBc) p.bc = save.bc;
      p.importedAt = new Date().toISOString();
    });
    closeDialog();
    toast(`Spielstand übernommen: ${unlocked.length} Freischaltungen, ${runes.length} Runen, ${save.bc} BC.`);
  });
}
