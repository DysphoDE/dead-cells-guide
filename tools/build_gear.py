"""Baut data/gear.json + assets/items/<id>.png aus deadcells.wiki.gg (Dead Cells 3.5).

Aufruf:  python -I tools/build_gear.py            (baut + prüft)
         python -I tools/build_gear.py --check    (nur Prüfung der vorhandenen gear.json)

Quellen (alles gecacht in research/cache/gear/):
  * Cargo-Tabelle "Items" (dieselben Daten wie die Infoboxen der Item-Seiten)
  * Wikitext der Item-Seiten (Tags, u. a. DualWeaponBase = zweihändig)
  * Wikitext der Gegner-/Boss-Seiten (EnemyInfobox: Biome + BSC-Stufen)
  * imageinfo der Icon-Dateien
Redaktionelle deutsche Texte: tools/gear_texts_de.py
"""
import hashlib
import html
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gear_fetch as gf  # noqa: E402
from gear_texts_de import TEXTS, BLUEPRINT_SPECIAL, NOTES  # noqa: E402

ROOT = gf.ROOT
OUT = ROOT / "data" / "gear.json"
ICON_DIR = ROOT / "assets" / "items"
ALT = ROOT / "_alt-openai" / "research-gear.json"
WIKI = "https://deadcells.wiki.gg/wiki/"
PNG_SIG = b"\x89PNG\r\n\x1a\n"

TYPE_MAP = {
    "melee weapon": ("melee", "weapon"), "ranged weapon": ("ranged", "weapon"), "shield": ("shield", "weapon"),
    "deployable": ("trap", "skill"), "grenade": ("grenade", "skill"), "power": ("power", "skill"),
}
COLOR_MAP = {"brut": "brutality", "tact": "tactics", "surv": "survival"}
DLC_MAP = {"rotg": "Rise of the Giant", "tbs": "The Bad Seed", "ff": "Fatal Falls",
           "tqats": "The Queen and the Sea", "qats": "The Queen and the Sea", "rtc": "Return to Castlevania"}
VALID_TYPES = {"melee", "ranged", "shield", "grenade", "trap", "power"}
VALID_COLORS = {"brutality", "tactics", "survival", "colorless"}
VALID_SOURCES = {"start", "enemy", "boss", "lore", "secret", "challenge", "shop", "collector", "quest",
                 "achievement", "other"}
# Seiten in der Cargo-Tabelle, die keine eigenständige Ausrüstung sind
SKIP_PAGES = {"Health Flask", "Map Part", "Balanced Blade/fr", "Blueprint Extractor"}
# Biome, die nur mit 5 BSC erreichbar sind
BIOME_MIN_BC = {"Astrolab": 5, "Observatory": 5}
BOSSES = {"Concierge", "The Concierge", "Conjunctivius", "Giant", "The Giant", "Hand of the King",
          "The Hand of the King", "Time Keeper", "The Time Keeper", "Mama Tick", "Queen", "The Queen",
          "Scarecrow", "The Scarecrow", "The Collector (5 BSC)", "Death", "Dracula - Final Form",
          "Kleio", "Calliope", "Euterpe"}
# Korrekturen, wo die Gegner-Infobox eine BSC-Angabe nicht eindeutig einem Biom zuordnet
MINBC_OVERRIDE = {
    "tornado": (0, "Guardian Knights erscheinen in High Peak Castle ab 0 BC; die Angabe 3+ BSC gilt nur für Dracula's Castle (Tiefe 3)."),
}
TAG_REMOVE = {"emergency-door": ("explosive",)}  # Wiki-Tag passt hier nicht zur Spielmechanik


def de_raw(t):
    """Englische Einheiten/Zusätze in Wiki-Rohwerten eindeutschen (für notes)."""
    for a, b in ((" seconds", " s"), (" second", " s"), ("Direct Hits", "Direkttreffer"), ("AoE", "Fläche"),
                 ("Attached", "angeheftet"), ("Floating", "schwebend"), ("per hit", "pro Treffer"),
                 ("enemy debuff", "Schwächung des Gegners"), ("bleeding", "Blutung"), ("single biter", "je Beißer"),
                 ("instant if parry is successful", "sofort bei erfolgreicher Parade"), ("per ammo", "pro Ladung")):
        t = t.replace(a, b)
    return t


WIKI_TAG_MAP = {"Bleed": "bleed", "Fire": "fire", "Poison": "poison", "Ice": "freeze", "Electric": "electric",
                "Oil": "oil", "Stun": "stun", "Explosive": "explosive", "Pet": "summon", "Heal": "heal",
                "LimitedAmmo": "ammo", "VeryFewAmmo": "ammo", "ManualAmmoRefill": "ammo"}


# ------------------------------------------------------------------ Hilfen
def slug(s):
    s = s.replace("'", "").replace("’", "")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def legacy_slug(s):  # Schema der Vorarbeit in _alt-openai (Apostroph -> "-")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def clean(s):
    s = s or ""
    s = re.sub(r"\[\[File:[^\]]*\]\]", "", s)
    s = re.sub(r"<br\s*/?>", " / ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = html.unescape(s).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip(" /")


def num(x):
    f = float(x)
    return int(f) if f.is_integer() else f


def parse_dps(raw):
    t = clean(raw)
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(?:\s*\((\d+(?:\.\d+)?)\))?", t)
    return (num(m.group(1)), t) if m else (None, t)


def parse_cooldown(raw):
    t = clean(raw)
    if not t or t.upper() == "N/A":
        return None, t
    m = re.match(r"(\d+(?:\.\d+)?)(?!\s*[-–])(?:\s*seconds?)?(?:\s|$|\()", t + " ")
    return (num(m.group(1)) if m else None), t


def wiki_url(title):
    return WIKI + title.replace(" ", "_").replace("'", "%27")


def canon_file(n):
    n = unquote(n or "").replace("_", " ").strip()
    n = re.sub(r"\?.*$", "", n)
    n = n.split("/")[-1]
    return n[:1].upper() + n[1:] if n else n


def links(text):
    return [(m.group(1).strip(), (m.group(2) or m.group(1)).strip())
            for m in re.finditer(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]", text or "")]


def infobox_field(text, field, box="EnemyInfobox"):
    m = re.search(r"\{\{" + box + r"(.*?)\n\}\}", text or "", re.S)
    if not m:
        return None
    body = m.group(1)
    fm = re.search(r"\n\|\s*" + field + r"\s*=(.*?)(?=\n\|\s*[a-z_0-9]+\s*=|\Z)", body, re.S)
    return fm.group(1) if fm else None


def parse_bsc(s):
    """Mindest-BSC aus Texten wie '(2+ BSC)', '(0-3 BSC)', '(1 BSC)', '(0BC+)', '3+ [[BSC]]'."""
    s = (s or "").replace("[[BSC]]", "BSC").replace("BCS", "BSC")
    m = re.search(r"(\d)\s*(?:\+|[-–�]\s*\d)?\s*(?:BSC|BC)", s)
    return int(m.group(1)) if m else None


# ------------------------------------------------------------------ Laden
def load_cargo():
    f = gf.CACHE / "cargo_items.json"
    if not f.exists():
        fields = gf.api({"action": "cargofields", "table": "Items"})["cargofields"]
        data = gf.http_get(gf.API, {"action": "cargoquery", "tables": "Items",
                                     "fields": ",".join(list(fields) + ["_pageName"]),
                                     "limit": "500", "format": "json"})
        f.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return [r["title"] for r in json.loads(f.read_text(encoding="utf-8"))["cargoquery"]]


def select_rows(rows):
    out, seen = [], set()
    for r in rows:
        if r["Type"] not in TYPE_MAP or r["RemovedContent"] == "1" or r["_pageName"] in SKIP_PAGES:
            continue
        if r["_pageName"] == "Whip Sword" and r["Name"] == "Transformation":
            continue  # Hilfseintrag (Formwechsel) – kein eigenes Item
        if r["_pageName"] in seen:
            raise SystemExit("doppelte Seite in Cargo: " + r["_pageName"])
        seen.add(r["_pageName"])
        out.append(r)
    return out


def item_name(page):
    return re.sub(r"\s*\((Weapon|Skill)\)$", "", page)


# ------------------------------------------------------------------ Gegner-/Boss-Orte
def parse_location_groups(loc):
    """Liste (linkziele, min_bsc|None, roh) je Absatz; beschworene Gegner werden ignoriert."""
    if not loc:
        return []
    loc = re.sub(r"\{\{(?:spt|SpoilerTag)\|", "", loc)
    loc = re.sub(r"\{\{(?:DLC|dlc|efn)\|[^}]*\}\}", "", loc)
    groups = []
    for part in re.split(r"\n|;\s*(?=\[\[)", loc):
        part = part.strip()
        if not part or "summoned" in part.lower():
            continue
        tg = [t for t, _ in links(part) if t.lower() not in ("bsc", "curse")]
        groups.append((tg, parse_bsc(part), part))
    return groups


def main_build():
    rows = select_rows(load_cargo())
    pages = gf.wikitexts([r["_pageName"] for r in rows])
    alt = {it["id"]: it for it in json.loads(ALT.read_text(encoding="utf-8"))["items"]} if ALT.exists() else {}

    # Gegner/Bosse aus "Drops from …"
    drop_links = {}
    for r in rows:
        loc = r["BlueprintLocation"]
        if loc.startswith("Drops from") and "lore room" not in loc:
            drop_links[r["_pageName"]] = links(loc)
    enemy_pages = gf.wikitexts(sorted({t for ls in drop_links.values() for t, _ in ls}), sub="enemies")

    # Biome: Namen aus der Gear-Tabelle + The Bank, kanonisiert über Redirects
    gear_wt = gf.api({"action": "parse", "page": "Gear", "prop": "wikitext"})["parse"]["wikitext"]
    table = gear_wt.split("== Gear level ==")[1].split("|}")[0]
    biome_names = set(re.findall(r"\n\|\s*([A-Z][^\n{|]+?)(?:\{\{DLC\|[^}]*\}\})?\s*\n", table))
    biome_names |= set(re.findall(r"content = ([A-Z][^\n{]+?)\{\{DLC", table))
    biome_names = {b.strip() for b in biome_names if not b.strip().isdigit()} | {"The Bank", "Infested Shipwreck"}
    biome_names.discard("Shipwreck")  # Tabellenkurzform; Seite heißt "Infested Shipwreck"
    all_link_targets = set(biome_names)
    for _, (fin, txt) in enemy_pages.items():
        for tg, _, _ in parse_location_groups(infobox_field(txt, "location")):
            all_link_targets.update(tg)
    for r in rows:
        all_link_targets.update(t for t, _ in links(r["BlueprintLocation"]))
    canon = gf.resolve_titles(sorted(all_link_targets))
    biome_set = {canon[b] for b in biome_names if canon.get(b)}

    def to_biomes(targets):
        out = []
        for t in targets:
            c = canon.get(t)
            if c in biome_set and c not in out:
                out.append(c)
        return out

    # Icons
    cand = {}
    for r in rows:
        name = item_name(r["_pageName"])
        c = [f"{name} Icon.png", canon_file(r["Image"])]
        cand[r["_pageName"]] = [x for x in dict.fromkeys(c) if x]
    infos = gf.imageinfos(sorted({x for cs in cand.values() for x in cs}))

    # Deutsche Spielnamen: data/names-de.json (von tools/names_de.py aus den Lokalisierungsdateien des Spiels erzeugt)
    nd = ROOT / "data" / "names-de.json"
    names_de = json.loads(nd.read_text(encoding="utf-8")) if nd.exists() else {}

    items, problems = [], []
    for r in rows:
        page = r["_pageName"]
        name = item_name(page)
        iid = slug(name)
        typ, slot = TYPE_MAP[r["Type"]]
        wt = pages[page][1] or ""
        tag_line = ",".join(re.findall(r"^\|\s*tags\s*=(.*)$", wt, re.M))
        wtags = {t.strip() for t in tag_line.split(",") if t.strip()}

        sc = r["Scaling"]
        colors = ["colorless"] if sc == "colorless" else [COLOR_MAP[p] for p in re.findall(r"brut|tact|surv", sc)]
        dlc = DLC_MAP.get(r["DLCExclusive"].lower()) if r["DLCExclusive"] else None

        base_dps, dps_raw = parse_dps(r["BaseDPS"])
        dps2, dps2_raw = parse_dps(r["BaseDPS2"])
        cooldown, cd_raw = (None, "")
        if slot == "skill" or typ == "shield":
            cooldown, cd_raw = parse_cooldown(r["Recharge"])
        if iid in ("mushroom-boi", "diverse-deck"):
            cooldown = None  # mehrere Werte (Beschwören/Opfern bzw. Kartenwechsel)

        if iid not in TEXTS:
            problems.append(f"kein deutscher Text für {iid}")
            desc, crit, extra = None, None, []
        else:
            desc, crit, extra = TEXTS[iid]
        tags = []
        if crit:
            tags.append("crit")
        tags += [WIKI_TAG_MAP[t] for t in sorted(wtags) if t in WIKI_TAG_MAP]
        if typ == "shield":
            tags.append("parry")
        if "Deployable" in wtags and iid not in ("night-light", "emergency-door", "wolf-trap", "cleaver", "crusher",
                                                 "explosive-decoy"):
            tags.append("turret")
        tags += extra
        tags = [t for t in dict.fromkeys(tags) if t not in TAG_REMOVE.get(iid, ())]

        # ---------------- Entwurf
        loc, chance_raw = r["BlueprintLocation"], r["BlueprintChance"]
        cells = int(r["BlueprintCost"]) if r["BlueprintCost"] else None
        bp = {"default": False, "sourceType": "other", "from": None, "biomes": [], "dropChance": None,
              "minBC": 0, "cells": cells, "text": None}
        notes = [NOTES[iid]] if iid in NOTES else []
        if loc.startswith("Always unlocked"):
            bp.update(default=True, sourceType="start", cells=None,
                      text=("Startausrüstung – von Anfang an verfügbar." if "RustyItem" in wtags
                            else "Von Anfang an freigeschaltet, kein Entwurf nötig."))
        elif iid in BLUEPRINT_SPECIAL:
            bp.update(BLUEPRINT_SPECIAL[iid])
        elif page in drop_links:
            ls = drop_links[page]
            pm = re.search(r"([\d.]+)%", chance_raw or loc)
            bp["dropChance"] = num(pm.group(1)) if pm else None
            reward_bsc = parse_bsc(chance_raw) or 0
            kill = re.search(r"\((\d+)(?:st|nd|rd|th) kill\)", loc)
            last = "killed last" in loc
            froms, biomes, mins = [], [], []
            for tgt, disp in ls:
                fin, etxt = enemy_pages[tgt]
                nm = re.sub(r"\s*\((Enemy|5 BSC)\)$", "", tgt)
                froms.append(nm)
                groups = parse_location_groups(infobox_field(etxt, "location"))
                raw_loc = infobox_field(etxt, "location") or ""
                if not groups and "BSC" in raw_loc:
                    mins.append(parse_bsc(raw_loc) or 0)
                for tg, mb, _ in groups:
                    bl = to_biomes(tg)
                    if not bl:
                        if mb is not None:
                            mins.append(mb)
                        continue
                    biomes += [b for b in bl if b not in biomes]
                    floor = max(BIOME_MIN_BC.get(b, 0) for b in bl)
                    mins.append(max(mb or 0, floor))
            bp["from"] = ", ".join(dict.fromkeys(froms))
            bp["biomes"] = biomes
            bp["minBC"] = max(reward_bsc, min(mins) if mins else 0)
            is_boss = bool(kill or last) or any(t in BOSSES for t, _ in ls)
            bp["sourceType"] = "boss" if is_boss else "enemy"
            where = ", ".join(biomes) if biomes else "verfluchten Biomen"
            bc = f" (ab {bp['minBC']} BC)" if bp["minBC"] else ""
            if last:
                bp["text"] = (f"Fällt von {bp['from']}, wenn sie als letzte der drei Dienerinnen (The Servants) "
                              f"im {where} besiegt wird.")
            elif kill:
                bp["text"] = f"Fällt beim {kill.group(1)}. Sieg über {bp['from']} ({where}){bc}."
            elif is_boss:
                bp["text"] = f"Fällt vom Boss {bp['from']} ({where}){bc}."
            else:
                ch = str(bp["dropChance"]).replace(".", ",") if bp["dropChance"] is not None else "?"
                bp["text"] = f"Fällt mit {ch} % Chance von {bp['from']} – vorkommend in {where}{bc}."
                if not biomes:
                    bp["text"] = (f"Fällt mit {ch} % Chance von {bp['from']}, der nur in verfluchten Biomen "
                                  f"ab {bp['minBC']} BC auftaucht.")
        else:
            problems.append(f"Entwurfsquelle unbekannt: {iid}: {loc}")
        if iid in MINBC_OVERRIDE:
            bp["minBC"], why = MINBC_OVERRIDE[iid]
            notes.append(why)
        if bp["biomes"]:  # nur wenn ALLE Fundorte erst ab 5 BC existieren (Astrolab/Observatory)
            bp["minBC"] = max(bp["minBC"], min(BIOME_MIN_BC.get(b, 0) for b in bp["biomes"]))
        if typ in ("melee", "ranged", "shield") and slot == "weapon" and bp["sourceType"] == "start" and "RustyItem" not in wtags:
            pass

        if base_dps is None and dps_raw and typ in ("melee", "ranged") or (dps_raw and base_dps is None and iid == "alucards-shield"):
            notes.append(f"Basis-DPS laut Wiki: {de_raw(dps_raw)}.")
        if dps2 is None and dps2_raw:
            notes.append(f"Zweitfunktion/zweite Form laut Wiki: {de_raw(dps2_raw)} DPS.")
        if cooldown is None and cd_raw and cd_raw.upper() != "N/A" and (slot == "skill" or typ == "shield"):
            notes.append(f"Abklingzeit laut Wiki: {de_raw(cd_raw)}" + ("" if re.search(r"[a-z)]$", de_raw(cd_raw)) else " s") + ".")

        # ---------------- Icon
        chosen = next((c for c in cand[page] if infos.get(c)), None)
        if not chosen:
            problems.append(f"kein Icon im Wiki für {iid}: {cand[page]}")
        items.append({
            "id": iid, "name": name, "nameDe": names_de.get(name), "type": typ, "slot": slot, "colors": colors, "dlc": dlc,
            "twoHanded": "DualWeaponBase" in wtags,
            "description": desc, "crit": crit,
            "baseDps": base_dps, "dps2": dps2, "cooldown": cooldown,
            "tags": tags, "blueprint": bp,
            "notes": " ".join(notes) if notes else None,
            "wiki": wiki_url(page), "icon": f"assets/items/{iid}.png",
            "_icon_file": chosen, "_alt": alt.get(legacy_slug(name)),
        })

    # Icons herunterladen / wiederverwenden
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    man_f = gf.CACHE / "icons_manifest.json"
    manifest = json.loads(man_f.read_text(encoding="utf-8")) if man_f.exists() else {}
    stats = {"reused": 0, "renamed": 0, "downloaded": 0, "kept": 0}
    for it in items:
        fname = it.pop("_icon_file")
        altit = it.pop("_alt")
        if not fname:
            continue
        info = infos[fname]
        dest = ROOT / it["icon"]
        m = manifest.get(it["id"])
        legacy = ICON_DIR / (legacy_slug(it["name"]) + ".png")
        if dest.exists() and m and m["file"] == fname and hashlib.sha1(dest.read_bytes()).hexdigest() == m["sha1"]:
            stats["kept"] += 1
            # Altdatei unter dem früheren Slug (z. B. assassin-s-dagger.png) mit identischem Inhalt aufräumen
            if legacy != dest and legacy.exists() and legacy.read_bytes() == dest.read_bytes():
                legacy.unlink()
                stats["renamed"] += 1
            continue
        # Vorhandene Datei wiederverwenden, wenn sie ein PNG ist und laut Vorarbeit aus derselben Wiki-Datei stammt.
        # (Größenvergleich mit imageinfo ist nicht möglich: wiki.gg liefert optimierte, kleinere Dateien aus.)
        reuse_src = None
        for src in (dest, legacy):
            if src.exists() and src.read_bytes()[:8] == PNG_SIG and altit and \
                    canon_file(altit.get("iconSource", "")) == canon_file(fname):
                reuse_src = src
                break
        if reuse_src is not None:
            if reuse_src != dest:
                shutil.move(str(reuse_src), str(dest))
                stats["renamed"] += 1
            else:
                stats["reused"] += 1
        else:
            content, ctype = gf.download(info["url"])
            if content[:8] != PNG_SIG:
                problems.append(f"Icon kein PNG: {it['id']} ({ctype})")
                continue
            dest.write_bytes(content)
            stats["downloaded"] += 1
        manifest[it["id"]] = {"file": fname, "url": info["url"],
                              "sha1": hashlib.sha1(dest.read_bytes()).hexdigest()}
    man_f.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Icons:", stats)

    order = ["melee", "ranged", "shield", "trap", "grenade", "power"]
    items.sort(key=lambda x: (order.index(x["type"]), x["name"].lower()))
    meta = {
        "source": "https://deadcells.wiki.gg/wiki/Gear (Cargo-Tabelle 'Items', Item-Infoboxen und Gegner-Infoboxen via MediaWiki-API)",
        "researchedAt": "2026-10-14",
        "gameVersion": "3.5 – The End is Near (inkl. aller DLCs)",
        "notes": [
            "Namen exakt wie im englischen Wiki. nameDe stammt aus data/names-de.json (deutsche Lokalisierung des Spiels, per tools/names_de.py extrahiert); null, wo dort kein Eintrag existiert.",
            "Beschreibungen/Krit-Bedingungen sind eigene deutsche Kurzfassungen der Wiki-Angaben.",
            "Nicht enthalten: entfernte Items (Temporal Distortion), Hilfs-/Unterformen (Blueprint Extractor der Hunter's Grenade, Transformation des Whip Sword, die vier Karten des Diverse Deck), Health Flask und Map Part.",
            "baseDps/dps2: Basis-DPS ohne Krit aus der Wiki-Basiswerttabelle (Gear-Level I, ohne Stats). null, wenn der Wert eine Spanne/mehrdeutig ist – Rohwert dann in notes.",
            "cooldown: Abklingzeit in Sekunden (nur Skills/Schilde), null wenn nicht vorhanden oder mehrdeutig.",
            "twoHanded: laut Wiki-Tag DualWeaponBase (belegt beide Waffenslots).",
            "blueprint.dropChance: Prozent (0.4 = 0,4 %). blueprint.minBC: niedrigste Boss-Cell-Stufe, auf der der Entwurf erreichbar ist (aus Item- und Gegner-Infobox; Astrolab/Observatory = 5).",
            "blueprint.biomes: Biome, in denen der Entwurfsträger bzw. Fundort vorkommt (beschworene Gegner ausgenommen; BSC-Einschränkungen einzelner Biome siehe Wiki-Gegnerseite).",
            "blueprint.cells: Zellen-Kosten beim Collector; null, wenn das Item beim Aufheben sofort freigeschaltet wird oder von Anfang an verfügbar ist.",
            "blueprint.sourceType 'start' = von Anfang an freigeschaltet; die eigentliche Startausrüstung (Rusty Sword, Beginner's Bow, Old Wooden Shield) ist in notes vermerkt.",
            "Rise of the Giant ist kostenlos, wird aber als DLC-Inhalt geführt.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"meta": meta, "items": items}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"geschrieben: {OUT} ({len(items)} Items)")
    for p in problems:
        print("PROBLEM:", p)
    return not problems


def check():
    d = json.loads(OUT.read_text(encoding="utf-8"))
    errs, ids = [], set()
    from collections import Counter
    cnt = Counter()
    for it in d["items"]:
        i = it["id"]
        if i in ids:
            errs.append(f"doppelte ID {i}")
        ids.add(i)
        cnt[it["type"]] += 1
        if it["type"] not in VALID_TYPES:
            errs.append(f"{i}: ungültiger Typ {it['type']}")
        if not it["colors"] or any(c not in VALID_COLORS for c in it["colors"]):
            errs.append(f"{i}: ungültige Farben {it['colors']}")
        if it["slot"] != ("weapon" if it["type"] in ("melee", "ranged", "shield") else "skill"):
            errs.append(f"{i}: Slot passt nicht")
        if it["dlc"] not in (None, *set(DLC_MAP.values())):
            errs.append(f"{i}: DLC {it['dlc']}")
        if it["blueprint"]["sourceType"] not in VALID_SOURCES:
            errs.append(f"{i}: sourceType {it['blueprint']['sourceType']}")
        if not it["description"] or not it["blueprint"]["text"]:
            errs.append(f"{i}: Text fehlt")
        if i != slug(it["name"]):
            errs.append(f"{i}: ID passt nicht zum Namen")
        p = ROOT / it["icon"]
        if not p.exists():
            errs.append(f"{i}: Icon fehlt ({p})")
        elif p.read_bytes()[:8] != PNG_SIG:
            errs.append(f"{i}: Icon ist kein PNG")
    print("Anzahl je Typ:", dict(cnt), "gesamt", len(d["items"]))
    print("zweihändig:", [it["id"] for it in d["items"] if it["twoHanded"]])
    for e in errs:
        print("FEHLER:", e)
    print("Prüfung:", "OK" if not errs else f"{len(errs)} Fehler")
    return not errs


if __name__ == "__main__":
    ok = True
    if "--check" not in sys.argv:
        ok = main_build()
    ok = check() and ok
    sys.exit(0 if ok else 1)
