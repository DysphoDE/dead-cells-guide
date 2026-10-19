// Liest ein Dead-Cells-Savegame (user_N.dat) direkt im Browser – nur lesend, nichts verlässt das Gerät.
//
// Aufbau (PC/Steam, Version 3.x):
//   Kopf "DE AD CE 11" + Version + Build-Hash + Build-Datum, danach ein zlib-Block.
//   Der Block ist hxbit-serialisiert (Kennung "HXS", Feldnamen im Schema). Für den Guide relevant:
//   - ItemMetaManager.itemProgress: Liste von { itemId, investedCells, isNew, unlocked }
//   - ItemMetaManager.permanentItems: Liste interner IDs (Runen, Boss-Cell-Stufen, Komfort-Freischaltungen)
// Statt eines vollständigen hxbit-Decoders werden genau diese beiden Strukturen über ihr festes
// Byte-Muster gesucht. Das ist robust gegenüber Änderungen an anderen Teilen des Spielstands.

const ZLIB_SECOND = new Set([0x01, 0x5e, 0x9c, 0xda]);
const IDENT = /^[A-Za-z_][A-Za-z0-9_]*$/;

async function inflate(bytes) {
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('deflate'));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

/** Sucht den zlib-Block im Kopf und entpackt ihn. */
async function unpack(buf) {
  for (let o = 0; o < Math.min(256, buf.length - 2); o++) {
    if (buf[o] !== 0x78 || !ZLIB_SECOND.has(buf[o + 1]) || ((buf[o] << 8) | buf[o + 1]) % 31 !== 0) continue;
    try {
      const out = await inflate(buf.subarray(o));
      if (out.length > 1000) return out;
    } catch { /* nächster Kandidat */ }
  }
  return null;
}

class Reader {
  constructor(d) { this.d = d; this.view = new DataView(d.buffer, d.byteOffset, d.byteLength); }
  /** hxbit-Int: 1 Byte (0–127) oder 0x80 + int32 little-endian. */
  int(p) {
    const c = this.d[p];
    if (c === undefined) return null;
    if (c === 0x80) return p + 5 <= this.d.length ? [this.view.getInt32(p + 1, true), p + 5] : null;
    return c < 0x80 ? [c, p + 1] : null;
  }
  /** hxbit-String: Länge+1 als Int, dann Bytes. Nur einfache Bezeichner werden akzeptiert. */
  ident(p) {
    const n = this.int(p);
    if (!n || n[0] < 2 || n[0] > 64) return null;
    const len = n[0] - 1;
    const start = n[1];
    if (start + len > this.d.length) return null;
    let s = '';
    for (let i = start; i < start + len; i++) s += String.fromCharCode(this.d[i]);
    return IDENT.test(s) ? [s, start + len] : null;
  }
  /** Ein itemProgress-Eintrag: Objekt-ID, itemId, investedCells, isNew, unlocked. */
  progress(p) {
    const id = this.int(p); if (!id) return null;
    const name = this.ident(id[1]); if (!name) return null;
    const cells = this.int(name[1]); if (!cells) return null;
    const q = cells[1];
    const isNew = this.d[q], unlocked = this.d[q + 1];
    if (isNew > 1 || unlocked > 1) return null;
    return { obj: id[0], itemId: name[0], investedCells: cells[0], isNew: isNew === 1, unlocked: unlocked === 1, end: q + 2 };
  }
}

/** Erste lange Folge von itemProgress-Einträgen mit fortlaufenden Objekt-IDs. */
function findProgress(r) {
  const d = r.d;
  for (let p = 0; p < d.length - 8; p++) {
    const first = r.progress(p);
    if (!first) continue;
    const rows = [first];
    let cur = first;
    while (true) {
      const next = r.progress(cur.end);
      if (!next || next.obj <= cur.obj || next.obj > cur.obj + 4) break;
      rows.push(next);
      cur = next;
    }
    if (rows.length >= 20) return { rows, end: cur.end };
  }
  return null;
}

/** permanentItems: kurz nach der Liste ein Array (Länge+1) aus internen Bezeichnern. */
function findPermanent(r, from, known) {
  for (let p = from; p < Math.min(from + 200, r.d.length); p++) {
    const n = r.int(p);
    if (!n || n[0] < 2 || n[0] > 200) continue;
    const list = [];
    let q = n[1];
    for (let i = 0; i < n[0] - 1; i++) {
      const s = r.ident(q);
      if (!s) break;
      list.push(s[0]);
      q = s[1];
    }
    if (list.length === n[0] - 1 && list.every((x) => known(x))) return list;
  }
  return [];
}

/**
 * @param {ArrayBuffer} buffer Inhalt von user_N.dat
 * @param {{ids: Object<string, string|string[]>, bossCells: Object<string, number>}} map aus data/save-ids.json
 */
export async function readSavegame(buffer, map) {
  const buf = new Uint8Array(buffer);
  const magicOk = buf[0] === 0xde && buf[1] === 0xad && buf[2] === 0xce && buf[3] === 0x11;
  const data = (await unpack(buf)) ?? (magicOk ? null : buf);
  if (!data) throw new Error('Die Datei ließ sich nicht entpacken. Ist das eine user_N.dat vom PC?');
  const r = new Reader(data);
  const progress = findProgress(r);
  if (!progress) throw new Error('Keine Freischaltungen im Spielstand gefunden. Dieses Format wird (noch) nicht unterstützt.');

  const keysFor = (id) => { const v = map.ids[id]; return v ? (Array.isArray(v) ? v : [v]) : []; };
  const permanent = findPermanent(r, progress.end, (x) => x in map.ids || x in map.bossCells || /(Key|Unlock|Rune\d)$/.test(x));

  const unlocked = new Set();
  const found = new Map();       // Entwurf vorhanden, aber nicht freigeschaltet → investierte Zellen
  const unknown = [];
  for (const row of progress.rows) {
    const keys = keysFor(row.itemId);
    if (!keys.length) { unknown.push(row.itemId); continue; }
    for (const k of keys) {
      if (row.unlocked) { unlocked.add(k); found.delete(k); }
      else if (!unlocked.has(k)) found.set(k, Math.max(found.get(k) ?? 0, row.investedCells > 0 ? row.investedCells : 0));
    }
  }
  const runes = new Set();
  const collector = new Set();
  const aspects = new Set();
  let bc = 0;
  for (const id of permanent) {
    if (id in map.bossCells) bc = Math.max(bc, map.bossCells[id]);
    for (const k of keysFor(id)) {
      if (k.startsWith('rune:')) runes.add(k.slice(5));
      else if (k.startsWith('collector:')) collector.add(k.slice(10));
      else unlocked.add(k);
    }
  }
  for (const k of [...unlocked]) {
    if (k.startsWith('collector:')) { collector.add(k.slice(10)); unlocked.delete(k); }
    else if (k.startsWith('aspect:')) { aspects.add(k.slice(7)); unlocked.delete(k); }
  }
  for (const k of [...found.keys()]) if (!/^(gear|mutation|outfit):/.test(k)) found.delete(k);

  return { unlocked, found, runes, collector, aspects, bc, unknown, entries: progress.rows.length, magicOk };
}
