// Synergie-Engine: kombiniert recherchierte Kombos (meta.json) mit einer Mechanik-Heuristik
// (welcher Gegenstand erzeugt einen Zustand, welcher profitiert davon per Krit-Bedingung).
import { db, findByName, COLOR_LABEL, TYPE_LABEL, L } from './data.js';
import { norm, uniq } from './util.js';

export const EFFECTS = {
  bleed: { label: 'Blutung', re: /blut(?!dürst)|bleed/i },
  poison: { label: 'Gift', re: /gift|vergift|poison/i },
  burn: { label: 'Feuer', re: /brenn(?!bar)|(?<![a-zäöüß])feuer(?!rate)|entz[üu]nd|in brand|flamme|\bburn|\bfire\b/i },
  oil: { label: 'Öl', re: /(^|[^a-zäöüß])öl(?![a-zäöüß])|ölt|ölig|\boil(ed)?\b/i },
  freeze: { label: 'Frost', re: /einfr|friert|gefror|frost|\beis(?!en)|freez/i },
  slow: { label: 'Verlangsamung', re: /verlangsam|\bslow/i },
  stun: { label: 'Betäubung', re: /bet[äa]ub|\bstun/i },
  root: { label: 'Verwurzeln', re: /verwurzel|wurzel|\broot/i },
  electric: { label: 'Elektrizität', re: /elektr|blitz|electric|\bshock/i },
  curse: { label: 'Fluch', re: /fluch|curse/i },
};

const text = (e) => [e.description, e.effect].filter(Boolean).join(' ');

/** Welche Zustände erzeugt ein Gegenstand? Tags mischen „erzeugt“ und „profitiert“, daher wird für
 *  Effekte aus der Krit-Bedingung nur der Text ohne „gegen …“/„für …-Builds“-Phrasen gewertet. */
export function applies(e) {
  if (!e) return [];
  const tags = (e.tags ?? []).map((t) => t.toLowerCase());
  const ben = benefits(e);
  const full = text(e);
  const stripped = full.replace(/gegen [^.;]*/gi, '').replace(/für [^.;]*builds/gi, '');
  return Object.entries(EFFECTS)
    .filter(([k, v]) => (ben.includes(k)
      ? v.re.test(stripped)
      : tags.includes(k) || (k === 'burn' && tags.includes('fire')) || v.re.test(full)))
    .map(([k]) => k);
}

/** Von welchen Zuständen profitiert ein Gegenstand (Krit-Bedingung)? */
export function benefits(e) {
  if (!e?.crit) return [];
  return Object.entries(EFFECTS).filter(([, v]) => v.re.test(e.crit)).map(([k]) => k);
}

const key = (a, b) => [norm(a), norm(b)].sort().join('|');
let pairIndex = null;
function pairs() {
  if (pairIndex) return pairIndex;
  pairIndex = new Map();
  for (const s of db.synergies) {
    const items = s.items ?? [];
    for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) pairIndex.set(key(items[i], items[j]), s);
  }
  return pairIndex;
}

/** Partner für ein Item: recherchierte Kombos zuerst, dann Mechanik-Treffer. */
export function partnersFor(e, limit = 14) {
  const out = new Map();
  const add = (partner, why, source, refs = []) => {
    if (!partner || partner.key === e.key || out.has(partner.key)) return;
    out.set(partner.key, { e: partner, why, source, refs });
  };
  for (const s of db.synergies) {
    if (!(s.items ?? []).some((n) => norm(n) === norm(e.name))) continue;
    for (const n of s.items) if (norm(n) !== norm(e.name)) add(findByName(n), s.why, 'community', s.sources ?? []);
  }
  for (const set of db.mutationSets) {
    if (!(set.mutations ?? []).some((n) => norm(n) === norm(e.name))) continue;
    for (const n of set.mutations) if (norm(n) !== norm(e.name)) add(findByName(n), `Teil der Kombi „${L(set)}“: ${set.forWhat ?? set.why ?? ''}`, 'set', set.sources ?? []);
  }
  const myBenefits = benefits(e);
  const myApplies = applies(e);
  const pool = [...db.gear, ...db.mutations];
  if (myBenefits.length) {
    for (const p of pool) {
      if (p.slot === e.slot && p.kind === 'gear' && e.kind === 'gear' && p.type === e.type) continue;
      const hit = applies(p).find((x) => myBenefits.includes(x));
      if (hit) add(p, `${L(p)} erzeugt ${EFFECTS[hit].label} – genau die Krit-Bedingung von ${L(e)}.`, 'mechanic');
    }
  }
  if (myApplies.length && e.kind === 'gear') {
    for (const p of db.gear) {
      const hit = benefits(p).find((x) => myApplies.includes(x));
      if (hit) add(p, `${L(e)} erzeugt ${EFFECTS[hit].label}; ${L(p)} trifft dann kritisch.`, 'mechanic');
    }
  }
  const rank = { community: 0, set: 1, mechanic: 2 };
  return [...out.values()].sort((a, b) => rank[a.source] - rank[b.source] || (b.e.tier ? 1 : 0) - (a.e.tier ? 1 : 0)).slice(0, limit);
}

export const knownPair = (a, b) => pairs().get(key(a.name, b.name)) ?? null;

/** Analyse eines Loadouts für die Werkstatt. */
export function analyze(loadout) {
  const gear = [...loadout.weapons, ...loadout.skills].map(findByName).filter(Boolean);
  const muts = loadout.mutations.map(findByName).filter(Boolean);
  const all = [...gear, ...muts];
  const insights = [];
  let score = 0;

  if (!gear.length) return { insights, score: 0, color: null, matches: [] };

  // Farben / Skalierung
  const colorCount = {};
  for (const g of gear) for (const c of g.colors) if (c !== 'colorless') colorCount[c] = (colorCount[c] ?? 0) + 1 / g.colors.filter((x) => x !== 'colorless').length;
  const sorted = Object.entries(colorCount).sort((a, b) => b[1] - a[1]);
  const main = sorted[0]?.[0] ?? null;
  const offColor = gear.filter((g) => g.colors.some((c) => c !== 'colorless') && !g.colors.includes(main));
  if (main && !offColor.length) {
    insights.push({ type: 'good', title: `Alles skaliert mit ${COLOR_LABEL[main]}`, text: 'Jede Schriftrolle in diese Farbe verstärkt dein komplettes Loadout.' });
    score += 25;
  } else if (main) {
    insights.push({ type: 'warn', title: 'Gemischte Farben', text: `${offColor.map((g) => g.name).join(', ')} skaliert nicht mit ${COLOR_LABEL[main]}. Mehrfarbige Items nutzen automatisch deine höhere Farbe – reine Fremdfarben werden mit der Zeit schwächer, außer du splittest die Schriftrollen bewusst.` });
    score += 8;
  }

  // Bekannte Kombos
  const found = [];
  for (let i = 0; i < all.length; i++) for (let j = i + 1; j < all.length; j++) {
    const s = knownPair(all[i], all[j]);
    if (s && !found.includes(s)) { found.push(s); insights.push({ type: 'good', title: `${all[i].name} + ${all[j].name}`, text: s.why }); score += 16; }
  }

  // Mechanik: Zustand erzeugen → Krit nutzen
  for (const g of gear) {
    const ben = benefits(g);
    if (!ben.length) continue;
    const enablers = all.filter((x) => x !== g && applies(x).some((a) => ben.includes(a)));
    if (enablers.length) {
      const eff = ben.find((b) => enablers.some((x) => applies(x).includes(b)));
      if (!found.some((s) => s.items?.some((n) => norm(n) === norm(g.name)) && s.items?.some((n) => enablers.some((x) => norm(x.name) === norm(n))))) {
        insights.push({ type: 'good', title: `${L(g)} trifft kritisch`, text: `${enablers.map((x) => x.name).join(' und ')} ${enablers.length > 1 ? 'erzeugen' : 'erzeugt'} ${EFFECTS[eff].label} – die Krit-Bedingung von ${L(g)}.` });
        score += 14;
      }
    } else {
      insights.push({ type: 'info', title: `${L(g)} will ${ben.map((b) => EFFECTS[b].label).join(' / ')}`, text: `Krit-Bedingung: ${g.crit} Ein Skill, der das auslöst, würde den Schaden stark erhöhen.` });
    }
  }

  // Mutationsfarbe
  if (main && muts.length) {
    const off = muts.filter((m) => m.colors[0] !== 'colorless' && m.colors[0] !== main);
    if (off.length) insights.push({ type: 'info', title: 'Mutationen anderer Farbe', text: `${off.map((m) => m.name).join(', ')} skaliert mit einer anderen Farbe als dein Loadout. Ihr Effekt hängt teils von den Stats dieser Farbe ab.` });
    else score += 10;
  }

  // Zweihänder
  const twoHanded = gear.find((g) => g.twoHanded);
  if (twoHanded && loadout.weapons.filter(Boolean).length > 1) insights.push({ type: 'warn', title: `${L(twoHanded)} ist zweihändig`, text: 'Diese Waffe belegt beide Waffenplätze – die zweite Waffe kannst du nicht zusätzlich tragen.' });

  // Kein Schild / keine Defensive
  const hasShield = gear.some((g) => g.type === 'shield');
  const hasDefMut = muts.some((m) => (m.tags ?? []).some((t) => ['defense', 'heal', 'parry'].includes(t)));
  if (!hasShield && !hasDefMut && gear.length >= 3) insights.push({ type: 'info', title: 'Wenig Defensive', text: 'Kein Schild und keine Schutz-/Heil-Mutation. Auf höheren BC kann eine Überlebens-Mutation oder ein Schild Runs retten.' });

  // Fernkampf Munition
  const ranged = gear.filter((g) => g.type === 'ranged');
  if (ranged.length && muts.some((m) => norm(m.name) === 'ammo')) { score += 6; }

  score = Math.max(0, Math.min(100, score + Math.min(gear.length, 4) * 5));

  const names = new Set(all.map((x) => norm(x.name)));
  const matchesBuilds = db.builds
    .map((b) => ({ b, n: [...b.core.weapons, ...b.core.skills, ...b.core.mutations].filter((n) => names.has(norm(n))).length }))
    .filter((x) => x.n >= 1)
    .sort((a, b) => b.n - a.n)
    .slice(0, 4);

  return { insights, score, color: main, matches: matchesBuilds };
}

/** Vorschläge für einen leeren Slot, abgestimmt aufs aktuelle Loadout. */
export function suggest(loadout, slotKind, limit = 6) {
  const chosen = [...loadout.weapons, ...loadout.skills, ...loadout.mutations].filter(Boolean).map(findByName).filter(Boolean);
  if (!chosen.length) return [];
  const score = new Map();
  const bump = (e, s, why) => {
    if (!e || chosen.includes(e)) return;
    const okSlot = slotKind === 'mutations' ? e.kind === 'mutation' : slotKind === 'weapons' ? e.slot === 'weapon' : e.slot === 'skill';
    if (!okSlot) return;
    const cur = score.get(e.key) ?? { e, s: 0, why: [] };
    cur.s += s;
    if (why && cur.why.length < 2) cur.why.push(why);
    score.set(e.key, cur);
  };
  for (const c of chosen) for (const p of partnersFor(c, 40)) bump(p.e, p.source === 'community' ? 5 : p.source === 'set' ? 4 : 3, p.why);
  return [...score.values()].map((x) => ({ ...x, s: x.s + (x.e.tier ? { S: 3, A: 2, B: 1 }[x.e.tier] ?? 0 : 0) })).sort((a, b) => b.s - a.s).slice(0, limit);
}

export const describeType = (e) => (e.kind === 'mutation' ? 'Mutation' : TYPE_LABEL[e.type] ?? e.type);
export { uniq };
