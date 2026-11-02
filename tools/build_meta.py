"""Erzeugt data/builds.json und data/meta.json aus den redaktionellen Modulen meta_*.py
und prueft alle Eigennamen gegen die gecachten Wiki-Daten (research/cache)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import meta_builds, meta_tiers, meta_synergies, meta_routes, meta_tips  # noqa: E402
import importlib

CHECK_ONLY = "--check" in sys.argv

# Zusätzliche Build-Module (tools/meta_builds_more_*.py): je BUILDS (neue Builds), PATCHES (Ergänzungen
# bestehender Builds, id -> Felder) und optional SRC (weitere Quellen-Kürzel).
EXTRA = [importlib.import_module(f.stem) for f in sorted(Path(__file__).resolve().parent.glob("meta_builds_more_*.py"))]
ALL_SRC = dict(meta_builds.SRC)
ALL_BUILDS = list(meta_builds.BUILDS)
for mod in EXTRA:
    ALL_SRC.update(getattr(mod, "SRC", {}))
    ALL_BUILDS.extend(getattr(mod, "BUILDS", []))
_by_id = {b["id"]: b for b in ALL_BUILDS}
for mod in EXTRA:
    for bid, patch in getattr(mod, "PATCHES", {}).items():
        if bid not in _by_id:
            print(f"PATCH {mod.__name__}: unbekannter Build {bid!r}"); sys.exit(1)
        tgt = _by_id[bid]
        for k, v in patch.items():
            if k in ("core", "alternatives"):
                tgt[k] = {**tgt[k], **v}
            else:
                tgt[k] = v

TODAY = "2026-10-14"

# ---------- kanonische Namen ----------
# Quelle: gecachte Wiki-Cargo-Daten (research/cache). Fehlt der Cache (er ist gitignored),
# dienen die daraus erzeugten data/gear.json und data/mutations.json als Ersatz.
CACHE_ITEMS = ROOT / "research/cache/gear/cargo_items.json"
CACHE_MUTS = ROOT / "research/cache/mutations/api_4021ccef5a60d5e5.json"
if CACHE_ITEMS.exists() and CACHE_MUTS.exists():
    items_raw = json.loads((ROOT / "research/cache/gear/cargo_items.json").read_text(encoding="utf-8"))["cargoquery"]
    ITEM_TYPE = {}
    for x in items_raw:
        t = x["title"]
        name = t["_pageName"] if t["Name"] in ("Barricade", "Whip Sword, sword form") else t["Name"]
        if t["Name"] in ("Transformation", "Balanced Blade/fr", "Map Part", "Health Flask"):
            continue
        if t.get("RemovedContent") not in ("", "0", None):
            continue
        ITEM_TYPE[name] = t["Type"]
    DLC_MAP = {"tqats": "The Queen and the Sea", "RTC": "Return to Castlevania", "rotg": "Rise of the Giant", "RotG": "Rise of the Giant",
               "ff": "Fatal Falls", "tbs": "The Bad Seed", "": None}
    ITEM_DLC = {}
    for x in items_raw:
        t = x["title"]
        name = t["_pageName"] if t["Name"] in ("Barricade", "Whip Sword, sword form") else t["Name"]
        ITEM_DLC[name] = DLC_MAP.get(t["DLCExclusive"])
    ITEM_DLC["Toothpick"] = None  # kein DLC-Exklusiv laut Wiki-Hauptseite (Cargo-Feld inkonsistent)

    muts_raw = json.loads((ROOT / "research/cache/mutations/api_4021ccef5a60d5e5.json").read_text(encoding="utf-8"))["data"]["cargoquery"]
    MUTS = {m["title"]["Name"] for m in muts_raw if not m["title"].get("RemoveVersion")}
else:
    TYPE_FROM_DATA = {"melee": "melee weapon", "ranged": "ranged weapon", "shield": "shield",
                      "trap": "deployable", "power": "power", "grenade": "grenade"}
    _gear = json.loads((ROOT / "data/gear.json").read_text(encoding="utf-8"))["items"]
    ITEM_TYPE = {g["name"]: TYPE_FROM_DATA[g["type"]] for g in _gear}
    ITEM_DLC = {g["name"]: g.get("dlc") for g in _gear}
    MUTS = {m["name"] for m in json.loads((ROOT / "data/mutations.json").read_text(encoding="utf-8"))["mutations"]}
    ITEM_DLC["Toothpick"] = None  # wie oben: kein DLC-Exklusiv laut Wiki-Hauptseite

BIOMES = {"Prisoners' Quarters", "Promenade of the Condemned", "Toxic Sewers", "Dilapidated Arboretum", "Castle's Outskirts",
          "Prison Depths", "Corrupted Prison", "Ramparts", "Ancient Sewers", "Ossuary", "Morass of the Banished", "Dracula's Castle",
          "Black Bridge", "Insufferable Crypt", "Nest", "Defiled Necropolis", "Stilt Village", "Slumbering Sanctuary", "Graveyard",
          "Fractured Shrines", "Clock Tower", "Forgotten Sepulcher", "Cavern", "Undying Shores", "Clock Room", "Guardian's Haven",
          "Mausoleum", "High Peak Castle", "Derelict Distillery", "Infested Shipwreck", "Throne Room", "Lighthouse", "Master's Keep",
          "Astrolab", "Observatory", "The Crown", "The Bank"}
RUNES = {"Vine Rune", "Teleportation Rune", "Ram Rune", "Spider Rune", "Homunculus Rune", "Explorer's Rune"}
DLCS = {"Rise of the Giant", "The Bad Seed", "Fatal Falls", "The Queen and the Sea", "Return to Castlevania"}

errors = []
def chk_item(n, where, kinds=None):
    if n not in ITEM_TYPE:
        errors.append(f"{where}: unbekanntes Item {n!r}")
    elif kinds and ITEM_TYPE[n] not in kinds:
        errors.append(f"{where}: {n!r} ist {ITEM_TYPE[n]}, erwartet {kinds}")
def chk_mut(n, where):
    if n not in MUTS:
        errors.append(f"{where}: unbekannte Mutation {n!r}")
def chk_any(n, where):
    if n not in ITEM_TYPE and n not in MUTS:
        errors.append(f"{where}: unbekannter Name {n!r}")

WEAP = {"melee weapon", "ranged weapon", "shield"}
SKILL = {"deployable", "power", "grenade"}

# ---------- Builds ----------
TWO_HANDED = {i["name"] for i in json.loads((ROOT / "data/gear.json").read_text(encoding="utf-8"))["items"] if i.get("twoHanded")}
builds = []
used_src = set()
_ids = [b["id"] for b in ALL_BUILDS]
for dup in {x for x in _ids if _ids.count(x) > 1}:
    errors.append(f"build {dup}: ID doppelt")
for b in ALL_BUILDS:
    w = f"build {b['id']}"
    cw, cs, cm = b["core"]["weapons"], b["core"]["skills"], b["core"]["mutations"]
    if len(cm) != 3: errors.append(f"{w}: genau 3 Kern-Mutationen nötig, hat {len(cm)}")
    if len(cs) != 2: errors.append(f"{w}: genau 2 Kern-Skills nötig, hat {len(cs)}")
    if not (len(cw) == 2 or (len(cw) == 1 and cw[0] in TWO_HANDED)):
        errors.append(f"{w}: 2 Kern-Waffen nötig (oder 1 Zweihänder), hat {cw}")
    for n in b.get("mutationWhy", {}):
        if n not in cm: errors.append(f"{w}: mutationWhy für {n!r}, ist keine Kern-Mutation")
    for n in cm:
        if n not in b.get("mutationWhy", {}): errors.append(f"{w}: mutationWhy fehlt für {n!r}")
    for n in b.get("bossMutations", []): chk_mut(n, w + " bossMutations")
    for part in ("core", "alternatives"):
        for n in b[part]["weapons"]: chk_item(n, w, WEAP)
        for n in b[part]["skills"]: chk_item(n, w, SKILL)
        for n in b[part]["mutations"]: chk_mut(n, w)
    # DLC automatisch aus Kern-Items ableiten
    need = set(b["dlc"])
    for n in b["core"]["weapons"] + b["core"]["skills"]:
        if ITEM_DLC.get(n): need.add(ITEM_DLC[n])
    if need != set(b["dlc"]):
        errors.append(f"{w}: dlc {b['dlc']} != aus Kern-Items abgeleitet {sorted(need)}")
    for d in b["dlc"]:
        if d not in DLCS: errors.append(f"{w}: DLC {d!r}")
    srcs = []
    for s in b["sources"]:
        if s not in ALL_SRC: errors.append(f"{w}: Quelle {s!r} fehlt")
        else:
            srcs.append(ALL_SRC[s]); used_src.add(ALL_SRC[s])
    out = dict(b); out["sources"] = srcs
    assert out["color"] in ("brutality", "tactics", "survival", "colorless", "hybrid")
    assert out["tier"] in ("S", "A", "B") and out["phase"] in ("early", "mid", "late", "any")
    builds.append({k: out[k] for k in ["id", "name", "tagline", "color", "secondaryColor", "archetype", "difficulty", "bcMin", "bcMax",
                                        "phase", "tier", "dlc", "core", "alternatives", "statFocus", "affixes", "whyItWorks",
                                        "howToPlay", "strengths", "weaknesses", "sources"]}
                  | {k: out[k] for k in ("mutationWhy", "bossMutations", "bossMutationsWhy") if out.get(k)})

# ---------- Tiers ----------
def tierlist(rows, kinds, where, is_mut=False):
    seen, res = set(), []
    for name, tier, conf, why in rows:
        if name in seen: errors.append(f"{where}: doppelt {name}")
        seen.add(name)
        (chk_mut(name, where) if is_mut else chk_item(name, where, kinds))
        assert tier in "SABCD" and conf in ("hoch", "mittel", "niedrig"), name
        res.append({"name": name, "tier": tier, "confidence": conf, "why": why})
    return res, seen

tw, sw = tierlist(meta_tiers.WEAPONS, {"melee weapon", "ranged weapon"}, "tiers.weapons")
ts, ss = tierlist(meta_tiers.SHIELDS, {"shield"}, "tiers.shields")
tk, sk = tierlist(meta_tiers.SKILLS, SKILL, "tiers.skills")
tm, sm = tierlist(meta_tiers.MUTATIONS, None, "tiers.mutations", is_mut=True)
covered = sw | ss | sk
missing_items = sorted(n for n, t in ITEM_TYPE.items() if n not in covered and n != "Blueprint Extractor")
missing_muts = sorted(MUTS - sm)

# ---------- Synergien ----------
syn = []
for items, kind, why in meta_synergies.SYNERGIES:
    for n in items: chk_any(n, f"synergy {items}")
    syn.append({"items": items, "kind": kind, "why": why})
msets = []
for m in meta_synergies.MUTATION_SETS:
    for n in m["mutations"]: chk_mut(n, f"mutset {m['name']}")
    msets.append(m)

# Zusätzliche Kombi-Module (tools/meta_synergies_more_*.py): SYNERGIES und MUTATION_SETS als Dicts,
# jeder Eintrag mit "sources" = Liste von Community-URLs (Wiki allein zählt nicht).
def chk_sources(srcs, where):
    if not srcs or not all(isinstance(u, str) and u.startswith("http") for u in srcs):
        errors.append(f"{where}: 'sources' braucht mindestens eine URL"); return
    if all("wiki.gg" in u or "fandom.com" in u for u in srcs):
        errors.append(f"{where}: nur Wiki-Quellen – Community-Quelle fehlt")

pair_key = lambda items: tuple(sorted(n.lower() for n in items))
seen_pairs = {pair_key(x["items"]): f"meta_synergies" for x in syn}
seen_sets = {m["name"].lower() for m in msets}
seen_trios = {tuple(sorted(m["mutations"])) for m in msets}
for f in sorted(Path(__file__).resolve().parent.glob("meta_synergies_more_*.py")):
    mod = importlib.import_module(f.stem)
    for x in getattr(mod, "SYNERGIES", []):
        where = f"{f.stem}: synergy {x.get('items')}"
        if len(x.get("items", [])) < 2: errors.append(f"{where}: mindestens 2 Items"); continue
        for n in x["items"]: chk_any(n, where)
        if not x.get("why"): errors.append(f"{where}: 'why' fehlt")
        chk_sources(x.get("sources"), where)
        k = pair_key(x["items"])
        if k in seen_pairs: errors.append(f"{where}: doppelt (schon in {seen_pairs[k]})"); continue
        seen_pairs[k] = f.stem
        syn.append({"items": x["items"], "kind": x["kind"], "why": x["why"], "sources": x["sources"]})
    for m in getattr(mod, "MUTATION_SETS", []):
        where = f"{f.stem}: mutset {m.get('name')}"
        if len(m.get("mutations", [])) != 3: errors.append(f"{where}: genau 3 Mutationen"); continue
        for n in m["mutations"]: chk_mut(n, where)
        chk_sources(m.get("sources"), where)
        if m["name"].lower() in seen_sets: errors.append(f"{where}: Name doppelt")
        if tuple(sorted(m["mutations"])) in seen_trios: errors.append(f"{where}: gleiches Trio existiert schon")
        seen_sets.add(m["name"].lower()); seen_trios.add(tuple(sorted(m["mutations"])))
        msets.append(m)

# ---------- Routen ----------
for r in meta_routes.ROUTES:
    for b in r["path"]:
        if b not in BIOMES: errors.append(f"route {r['id']}: Biom {b!r}")
    for rn in r["runesNeeded"]:
        if rn not in RUNES: errors.append(f"route {r['id']}: Rune {rn!r}")
    for d in r["dlc"]:
        if d not in DLCS: errors.append(f"route {r['id']}: DLC {d!r}")

if errors:
    print("\n".join(errors)); sys.exit(1)
if CHECK_ONLY:
    print(f"OK (--check): {len(builds)} Builds, {len(syn)} Synergien, {len(msets)} Mutations-Sets, nichts geschrieben"); sys.exit(0)

SOURCES_META = [
    {"title": "Dead Cells Wiki (wiki.gg): Item-/Mutationsseiten inkl. History, Biomes, Curse, Stats, Boss Stem Cells", "url": "https://deadcells.wiki.gg/", "date": TODAY, "kind": "wiki"},
    {"title": "Offizielle Patchnotes 3.0–3.5 (Motion Twin)", "url": "https://deadcells.com/patchnotes", "date": "2022-08 bis 2024-08 (35.9: 2026-06)", "kind": "patchnotes"},
    {"title": "Steam: What's your favorite build?", "url": "https://steamcommunity.com/app/588650/discussions/0/3196993316881133865", "date": "2022-01", "kind": "community"},
    {"title": "Steam: How to abuse and beat 5BC Difficulty, Survival Build", "url": "https://steamcommunity.com/app/588650/discussions/5/3844431603849506591", "date": "2023-06", "kind": "community"},
    {"title": "Steam: Tips for 5bc?", "url": "https://steamcommunity.com/app/588650/discussions/0/3196992771953380337", "date": "2022-01", "kind": "community"},
    {"title": "Steam: Just beat the game on 5BC", "url": "https://steamcommunity.com/app/588650/discussions/0/4408466785409709597", "date": "2022-03", "kind": "community"},
    {"title": "Steam-Guide: A guide to cheesing 5 Boss Cells (V35)", "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=3323424572", "date": "2024-09-02", "kind": "guide"},
    {"title": "Gamersdecide: Best Builds / Melee / Ranged / Skills / Mutations / Routes", "url": "https://gamersdecide.com/articles/dead-cells-best-builds", "date": "2021–2024", "kind": "tierlist (schwach)"},
    {"title": "Choost Games: Weapon Tier List (Final Update)", "url": "https://choostgames.com/blog/dead-cells-weapon-tier-list/", "date": "2026-04-30", "kind": "tierlist (schwach)"},
    {"title": "PocketGamer: Weapon Tier List (v3.5.9, nach Grundschaden)", "url": "https://www.pocketgamer.com/dead-cells/weapon-tier-list", "date": "2026-10-08", "kind": "tierlist (schwach)"},
    {"title": "ScreenRant: 10 Best Weapons", "url": "https://screenrant.com/dead-cells-best-weapons/", "date": "2024-01-05", "kind": "tierlist (schwach)"},
    {"title": "AllClash: Melee Tier List", "url": "https://www.allclash.com/the-best-weapons-tier-list-in-dead-cells/", "date": "2022-08-06", "kind": "tierlist (schwach)"},
    {"title": "YouTube VeeDotMe: Mutations Tier List (The Final Update) – nur Titel/Beschreibung", "url": "https://youtu.be/6okDiuQAiUw", "date": "2024-06-10", "kind": "video"},
]

meta_out = {
    "meta": {
        "researchedAt": TODAY,
        "gameVersion": "3.5 'The End is Near' (35.8 live 2024-08; 35.9 ohne Balance-Änderungen)",
        "language": "de", "namesLanguage": "en",
        "method": "Konsens aus Community-Quellen (Steam-Foren/Guides, Videotitel), Tier-Listen-Seiten (schwach gewichtet), Patchnotes 3.0–3.5 und Wiki-Mechanik. Reddit war technisch nicht abrufbar.",
        "tierNote": "Tiers gelten für hohe BC (3–5), sofern 'why' nichts anderes sagt. Feld 'confidence': hoch = mehrere unabhängige Quellen; mittel = 1–2 Quellen plus Patch-/Mechaniklage; niedrig = redaktionelle Einordnung.",
        "coverage": {"weapons": len(tw), "shields": len(ts), "skills": len(tk), "mutations": len(tm),
                     "notRated": missing_items + missing_muts},
        "sources": SOURCES_META,
    },
    "tiers": {"weapons": tw, "shields": ts, "skills": tk, "mutations": tm},
    "synergies": syn,
    "mutationSets": msets,
    "routes": meta_routes.ROUTES,
    "generalTips": meta_tips.TIPS,
}

builds_out = {
    "meta": {
        "researchedAt": TODAY,
        "gameVersion": "3.5 'The End is Near'",
        "count": len(builds),
        "fields": "tier: S/A/B (Konsensstärke + Stärke auf hohen BC); difficulty: 1 leicht – 3 schwer; bcMin/bcMax: empfohlener Bereich; dlc: für Kern-Items nötige DLCs (automatisch geprüft).",
        "notes": [
            "Build-Kerne stammen aus Community-Quellen; Ergänzungen (Alternativen, Affixe) sind redaktionell und mechanisch begründet.",
            "Wo nur eine Quelle existiert, steht das in 'weaknesses'.",
            "Rise of the Giant ist kostenlos, wird aber als DLC-Inhalt geführt."
        ],
        "sources": sorted(used_src),
    },
    "builds": builds,
}

def dump(obj, path):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

dump(builds_out, ROOT / "data/builds.json")
dump(meta_out, ROOT / "data/meta.json")
from collections import Counter
print("builds", len(builds), Counter(b["color"] for b in builds), Counter(b["tier"] for b in builds))
print("tiers", len(tw), len(ts), len(tk), len(tm), "total items", len(tw) + len(ts) + len(tk))
print("synergies", len(syn), "mutsets", len(msets), "routes", len(meta_routes.ROUTES), "tips", len(meta_tips.TIPS))
print("not rated:", missing_items, missing_muts)
