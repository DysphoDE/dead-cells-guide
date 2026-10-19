// Persönliches Profil (BC, DLCs, Freischaltungen, Runen, Werkstatt) in localStorage.

export const DLCS = [
  { id: 'Rise of the Giant', short: 'RotG', note: 'kostenlos' },
  { id: 'The Bad Seed', short: 'TBS' },
  { id: 'Fatal Falls', short: 'FF' },
  { id: 'The Queen and the Sea', short: 'TQatS' },
  { id: 'Return to Castlevania', short: 'RtC' },
];

const KEY = 'prisoners-guide:v2';
const listeners = new Set();

const defaults = () => ({
  version: 2,
  bc: 0,
  dlcs: DLCS.map((d) => d.id),
  owned: {},        // "gear:rusty-sword": true
  found: {},        // Entwurf im Besitz, noch nicht freigeschaltet: "gear:punishment": investierte Zellen
  collector: {},    // Collector-Upgrades aus dem Savegame (normalisierter Name): true
  aspects: [],      // freigeschaltete Aspekte (englische Namen)
  importedAt: null, // Zeitpunkt des letzten Savegame-Imports
  runes: {},        // "vine-rune": true
  favorites: [],    // Build-IDs
  workshop: { weapons: [null, null], skills: [null, null], mutations: [null, null, null] },
  prefs: { names: 'en' },
});

function load() {
  try {
    const parsed = JSON.parse(localStorage.getItem(KEY) || 'null');
    return sanitize(parsed) ?? defaults();
  } catch {
    return defaults();
  }
}

function sanitize(p) {
  if (!p || typeof p !== 'object') return null;
  const d = defaults();
  const obj = (v) => (v && typeof v === 'object' && !Array.isArray(v) ? v : {});
  const bools = (v) => Object.fromEntries(Object.entries(obj(v)).filter(([k, x]) => typeof k === 'string' && x === true));
  const strArr = (v, len) => (Array.isArray(v) ? v.slice(0, len).map((x) => (typeof x === 'string' ? x : null)) : null);
  const ws = obj(p.workshop);
  return {
    ...d,
    bc: Number.isInteger(p.bc) && p.bc >= 0 && p.bc <= 5 ? p.bc : 0,
    dlcs: Array.isArray(p.dlcs) ? p.dlcs.filter((x) => DLCS.some((d) => d.id === x)) : d.dlcs,
    owned: bools(p.owned),
    found: Object.fromEntries(Object.entries(obj(p.found)).filter(([, v]) => Number.isFinite(v) && v >= 0)),
    collector: bools(p.collector),
    aspects: Array.isArray(p.aspects) ? p.aspects.filter((x) => typeof x === 'string') : [],
    importedAt: typeof p.importedAt === 'string' ? p.importedAt : null,
    runes: bools(p.runes),
    favorites: Array.isArray(p.favorites) ? p.favorites.filter((x) => typeof x === 'string') : [],
    workshop: {
      weapons: pad(strArr(ws.weapons, 2), 2),
      skills: pad(strArr(ws.skills, 2), 2),
      mutations: pad(strArr(ws.mutations, 3), 3),
    },
    prefs: { names: obj(p.prefs).names === 'de' ? 'de' : 'en' },
  };
}
const pad = (arr, n) => Array.from({ length: n }, (_, i) => (arr && arr[i]) || null);

export const profile = load();

export function save() {
  try {
    localStorage.setItem(KEY, JSON.stringify(profile));
  } catch {
    /* Privater Modus o. Ä. – Profil gilt dann nur für diese Sitzung. */
  }
}

export function update(mutator, { silent = false } = {}) {
  mutator(profile);
  save();
  if (!silent) listeners.forEach((fn) => fn(profile));
}

export const subscribe = (fn) => { listeners.add(fn); return () => listeners.delete(fn); };

export const hasDlc = (dlc) => {
  if (!dlc || (Array.isArray(dlc) && dlc.length === 0)) return true;
  if (Array.isArray(dlc)) return dlc.every(hasDlc);
  if (dlc === 'Rise of the Giant' && !DLCS.some((d) => d.id === dlc)) return true;
  return profile.dlcs.includes(dlc);
};

export function exportProfile() {
  return JSON.stringify({ app: 'prisoners-guide', exportedAt: new Date().toISOString(), profile }, null, 2);
}

export function importProfile(text) {
  const parsed = JSON.parse(text);
  const clean = sanitize(parsed?.profile ?? parsed);
  if (!clean) throw new Error('Unbekanntes Format');
  update((p) => Object.assign(p, clean));
}

export function resetProfile() {
  update((p) => Object.assign(p, defaults()));
}
