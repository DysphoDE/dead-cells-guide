// Lädt alle JSON-Daten, normalisiert sie und baut Indizes für schnelle Nachschlagewerke.
import { norm, slug, uniq } from './util.js';
import { profile, hasDlc } from './store.js';

const FILES = ['gear', 'mutations', 'world', 'builds', 'meta', 'mechanics', 'outfits', 'names-de'];

export const db = {
  gear: [], mutations: [], outfits: [], biomes: [], bosses: [], runes: [], builds: [],
  bossCells: [], timedDoors: [], otherAreas: [], worldFlags: {},
  tiers: {}, synergies: [], mutationSets: [], routes: [], tips: [],
  mechanics: {}, meta: {}, namesDe: {},
  byKey: new Map(), byName: new Map(), biomeIndex: new Map(), blueprintsByBiome: new Map(),
};

export const TYPE_LABEL = { melee: 'Nahkampf', ranged: 'Fernkampf', shield: 'Schild', grenade: 'Granate', trap: 'Falle & Geschütz', power: 'Kraft', mutation: 'Mutation', outfit: 'Outfit' };
export const TYPE_PLURAL = { melee: 'Nahkampfwaffen', ranged: 'Fernkampfwaffen', shield: 'Schilde', grenade: 'Granaten', trap: 'Fallen & Geschütze', power: 'Kräfte' };
export const COLOR_LABEL = { brutality: 'Brutalität', tactics: 'Taktik', survival: 'Überleben', colorless: 'Farblos', hybrid: 'Hybrid' };
export const COLORS = ['brutality', 'tactics', 'survival'];
export const TIERS = ['S', 'A', 'B', 'C', 'D'];
export const SOURCE_LABEL = {
  start: 'Startausrüstung', enemy: 'Gegner-Drop', boss: 'Boss-Drop', lore: 'Lore-Raum', secret: 'Geheimbereich',
  challenge: 'Herausforderung', shop: 'Händler', collector: 'Collector', quest: 'Quest', achievement: 'Erfolg', other: 'Sonstiges',
};

async function fetchJson(name) {
  try {
    const res = await fetch(`data/${name}.json`, { cache: 'no-cache' });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

function normBlueprint(bp, fallbackText) {
  if (!bp || typeof bp !== 'object') {
    return { default: false, sourceType: null, from: null, biomes: [], dropChance: null, minBC: 0, cells: null, text: typeof bp === 'string' ? bp : fallbackText ?? null };
  }
  return {
    default: !!bp.default,
    sourceType: bp.sourceType ?? null,
    from: bp.from ?? null,
    biomes: Array.isArray(bp.biomes) ? bp.biomes : bp.location ? [bp.location] : [],
    dropChance: typeof bp.dropChance === 'number' ? bp.dropChance : parseFloat(bp.dropChance) || null,
    minBC: Number.isFinite(+bp.minBC) ? +bp.minBC : 0,
    cells: Number.isFinite(+bp.cells) && bp.cells !== null ? +bp.cells : null,
    text: bp.text ?? bp.location ?? null,
  };
}

function register(entity, ...names) {
  db.byKey.set(entity.key, entity);
  for (const n of names) {
    if (!n) continue;
    const k = norm(n);
    if (!db.byName.has(k)) db.byName.set(k, entity);
  }
}

export async function loadAll() {
  const [gear, mutations, world, builds, meta, mechanics, outfits, namesDe] = await Promise.all(FILES.map(fetchJson));
  db.namesDe = namesDe && typeof namesDe === 'object' ? (namesDe.names ?? namesDe) : {};
  const de = (name, given) => given || db.namesDe[name] || null;

  // --- Ausrüstung
  db.gear = (gear?.items ?? []).filter((i) => i.trackable !== false).map((i) => {
    const colors = uniq(i.colors ?? [i.color ?? 'colorless']);
    return {
      ...i,
      kind: 'gear',
      key: `gear:${i.id}`,
      nameDe: de(i.name, i.nameDe),
      colors: colors.length ? colors : ['colorless'],
      slot: i.slot ?? (['melee', 'ranged', 'shield'].includes(i.type) ? 'weapon' : 'skill'),
      blueprint: normBlueprint(i.blueprint, i.blueprint),
      icon: i.icon ?? `assets/items/${i.id}.png`,
      url: `#/item/${i.id}`,
      tags: i.tags ?? [],
    };
  });
  db.gear.forEach((i) => register(i, i.name, i.nameDe, i.id));

  // --- Mutationen
  db.mutations = (mutations?.mutations ?? []).map((m) => ({
    ...m,
    kind: 'mutation',
    type: 'mutation',
    key: `mutation:${m.id}`,
    nameDe: de(m.name, m.nameDe),
    colors: [m.color ?? 'colorless'],
    blueprint: normBlueprint(m.blueprint),
    icon: m.icon ?? `assets/mutations/${m.id}.png`,
    url: `#/mutation/${m.id}`,
    tags: m.tags ?? [],
  }));
  db.mutations.forEach((m) => register(m, m.name, m.nameDe, m.id));

  // --- Outfits
  db.outfits = (outfits?.outfits ?? []).map((o) => ({
    ...o,
    kind: 'outfit',
    type: 'outfit',
    key: `outfit:${o.id}`,
    nameDe: de(o.name, o.nameDe),
    colors: ['colorless'],
    blueprint: normBlueprint({ default: o.sourceType === 'start', sourceType: o.sourceType, biomes: o.biomes, minBC: o.minBC, cells: o.cells, text: o.source }),
    icon: o.image ?? null,
    url: `#/outfits?q=${encodeURIComponent(o.name)}`,
  }));
  db.outfits.forEach((o) => db.byKey.set(o.key, o));

  // --- Welt
  db.biomes = (world?.biomes ?? []).map((b) => ({ ...b, kind: b.kind === 'boss' ? 'arena' : 'biome', entityKind: 'biome', key: `biome:${b.id}`, nameDe: de(b.name, b.nameDe), url: `#/biome/${b.id}`, exits: b.exits ?? [] }));
  db.biomes.forEach((b) => {
    db.biomeIndex.set(b.id, b);
    db.biomeIndex.set(norm(b.name), b);
    if (b.nameDe) db.biomeIndex.set(norm(b.nameDe), b);
    db.byKey.set(b.key, b);
  });
  db.bosses = (world?.bosses ?? []).map((b) => ({ ...b, kind: 'boss', key: `boss:${b.id}`, nameDe: de(b.name, b.nameDe), url: `#/boss/${b.id}` }));
  db.bosses.forEach((b) => register(b, b.name, b.nameDe, b.name.replace(/^The /, '')));
  db.runes = (world?.runes ?? []).map((r) => ({ ...r, kind: 'rune', key: `rune:${r.id}`, nameDe: de(r.name, r.nameDe), url: `#/world?tab=runes#${r.id}` }));
  db.runes.forEach((r) => register(r, r.name, r.nameDe));
  db.bossCells = world?.bossCells ?? [];
  db.worldFlags = world?.meta?.flags ?? {};
  db.timedDoors = world?.timedDoors ?? [];
  db.otherAreas = world?.otherAreas ?? [];

  // --- Builds & Meta
  db.builds = (builds?.builds ?? []).map((b) => ({ ...b, kind: 'build', key: `build:${b.id}`, url: `#/build/${b.id}`, core: { weapons: [], skills: [], mutations: [], ...(b.core ?? {}) }, alternatives: { weapons: [], skills: [], mutations: [], ...(b.alternatives ?? {}) } }));
  db.builds.forEach((b) => db.byKey.set(b.key, b));
  db.meta = { builds: builds?.meta ?? {}, meta: meta?.meta ?? {} };
  db.tiers = meta?.tiers ?? {};
  db.synergies = meta?.synergies ?? [];
  db.mutationSets = meta?.mutationSets ?? [];
  db.routes = meta?.routes ?? [];
  db.tips = meta?.generalTips ?? [];
  db.mechanics = mechanics ?? {};

  // Tier-Werte an Items hängen
  for (const [cat, list] of Object.entries(db.tiers)) {
    for (const t of list ?? []) {
      const e = findByName(t.name);
      if (e && !e.tier) { e.tier = t.tier; e.tierWhy = t.why; e.tierCategory = cat; }
    }
  }

  // Entwürfe je Biom
  for (const e of [...db.gear, ...db.mutations, ...db.outfits]) {
    for (const bName of e.blueprint.biomes) {
      const b = biome(bName);
      if (!b) continue;
      if (!db.blueprintsByBiome.has(b.id)) db.blueprintsByBiome.set(b.id, []);
      db.blueprintsByBiome.get(b.id).push(e);
    }
  }

  return db;
}

export const findByName = (name) => (name ? db.byName.get(norm(name)) ?? null : null);
export const biome = (ref) => (ref ? db.biomeIndex.get(ref) ?? db.biomeIndex.get(norm(ref)) ?? db.biomeIndex.get(slug(ref)) ?? null : null);
export const boss = (id) => db.bosses.find((b) => b.id === id) ?? null;
/** Kurzlabel für die Position eines Bioms im Run. */
export const depthLabel = (b) => (b.kind === 'arena' ? 'Bossarena' : b.kind === 'secret' ? 'Geheimbiom' : b.depth != null ? `Ebene ${b.depth}` : 'Abzweig');

// ---------- Profilbezogene Ableitungen ----------
export const isOwned = (e) => !!e && (e.blueprint?.default || profile.owned[e.key] === true);
export const isTrackable = (e) => e && (e.kind === 'gear' || e.kind === 'mutation' || e.kind === 'outfit');
export const dlcOk = (e) => hasDlc(e?.dlc);
export const bpAvailable = (e) => dlcOk(e) && (e.blueprint?.minBC ?? 0) <= profile.bc;

export function buildItems(b, { withAlternatives = false } = {}) {
  const pick = (src) => [...(src.weapons ?? []), ...(src.skills ?? []), ...(src.mutations ?? [])];
  const names = withAlternatives ? [...pick(b.core), ...pick(b.alternatives)] : pick(b.core);
  return names.map((n) => ({ name: n, entity: findByName(n) }));
}

export function buildReadiness(b) {
  const items = buildItems(b).filter((x) => x.entity && isTrackable(x.entity));
  const owned = items.filter((x) => isOwned(x.entity)).length;
  return { owned, total: items.length, missing: items.filter((x) => !isOwned(x.entity)).map((x) => x.entity), ratio: items.length ? owned / items.length : 1 };
}

export const buildFitsBc = (b) => (b.bcMin ?? 0) <= profile.bc && profile.bc <= (b.bcMax ?? 5);
export const buildDlcOk = (b) => hasDlc(b.dlc ?? []) && buildItems(b).every((x) => !x.entity || dlcOk(x.entity));

const TIER_SCORE = { S: 5, A: 4, B: 3, C: 2, D: 1 };

/** Sortiert Builds: passend zu BC/DLC zuerst, dann Freischalt-Grad, dann Tier. */
export function rankBuilds(list = db.builds) {
  return [...list]
    .map((b) => ({ b, fit: buildFitsBc(b) && buildDlcOk(b) ? 1 : 0, ready: buildReadiness(b).ratio, tier: TIER_SCORE[b.tier] ?? 0 }))
    .sort((x, y) => y.fit - x.fit || (y.ready >= 0.999) - (x.ready >= 0.999) || y.tier - x.tier || y.ready - x.ready || x.b.name.localeCompare(y.b.name))
    .map((x) => x.b);
}
export const tierScore = (e) => TIER_SCORE[e?.tier] ?? 0;

/** Empfehlung, welche Entwürfe sich als Nächstes lohnen: Tier, Nutzung in Builds, Erreichbarkeit bei aktueller BC. */
export function nextUnlocks(limit = 8, kinds = ['gear', 'mutation']) {
  const usage = new Map();
  for (const b of db.builds) for (const { entity } of buildItems(b)) if (entity) usage.set(entity.key, (usage.get(entity.key) ?? 0) + 1);
  return [...db.gear, ...db.mutations]
    .filter((e) => kinds.includes(e.kind) && !isOwned(e) && bpAvailable(e))
    .map((e) => ({ e, score: tierScore(e) * 3 + Math.min(usage.get(e.key) ?? 0, 4) * 2 + (e.blueprint.dropChance && e.blueprint.dropChance >= 5 ? 1 : 0) + (['lore', 'secret', 'boss'].includes(e.blueprint.sourceType) ? 1 : 0) }))
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score || a.e.name.localeCompare(b.e.name))
    .slice(0, limit)
    .map((x) => x.e);
}

/** Anzeigename je nach Einstellung (englische Wiki-Namen oder deutsche Spielnamen). */
export const L = (e) => (e && profile.prefs.names === 'de' && e.nameDe) || e?.name || '';
/** Der jeweils andere Name (für Untertitel/Tooltips), falls abweichend. */
export const altName = (e) => {
  const other = profile.prefs.names === 'de' ? e?.name : e?.nameDe;
  return other && other !== L(e) ? other : null;
};
