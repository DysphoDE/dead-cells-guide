"""Baut data/outfits.json (alle Outfits/Skins, Dead Cells 3.5 inkl. DLCs) aus dem wiki.gg-Artikel "Outfits".

Ablauf:
  1. Wikitext von "Outfits" laden, {{OutfitTable}}-Blöcke parsen (150 Einträge).
  2. Für Drop-Quellen die Gegner-/Boss-Seiten laden (EnemyInfobox | location) und Biome ableiten,
     gefiltert nach BC-Bereich (Biom nur, wenn der Gegner dort auf >= minBC vorkommt).
  3. Deutsche Quellsätze aus Vorlagen bzw. handgeschriebenen Overrides erzeugen.
  4. Icons (24 px) nach assets/outfits/<id>.png laden.
  5. Validieren und schreiben.

Aufruf:  python -I tools/build_outfits.py
Alle API-Antworten werden unter research/cache/outfits/ gecacht.
"""
import json, re, sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import wikiapi  # noqa: E402

CACHE = ROOT / "research" / "cache" / "outfits"
IMGCACHE = CACHE / "img"
OUT = ROOT / "data" / "outfits.json"
ASSETS = ROOT / "assets" / "outfits"
WIKI = "https://deadcells.wiki.gg/wiki/"

DLC = {"rotg": "Rise of the Giant", "tbs": "The Bad Seed", "ff": "Fatal Falls",
       "tqats": "The Queen and the Sea", "rtc": "Return to Castlevania"}


def slug(s):
    s = s.replace("'", "").replace("’", "").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def parse_blocks(text):
    out = []
    for b in re.findall(r"\{\{OutfitTable\n(.*?)\n\}\}\n", text, re.S):
        d = {}
        for m in re.finditer(r"^\| *(\w+) *=(.*?)(?=^\| *\w+ *=|\Z)", b, re.S | re.M):
            d[m.group(1)] = m.group(2).strip()
        out.append(d)
    return out


def links(s):
    """[[Target|Text]] -> Target (ohne #Anker)."""
    res = []
    for m in re.finditer(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]", s or ""):
        t = m.group(1).strip()
        if not t.lower().startswith(("wikipedia:", "file:")):
            res.append(t)
    return res


def plain(s):
    s = re.sub(r"\{\{efn\|(?:name=[^|}]*\|)?", "", s or "")
    s = re.sub(r"<ref>.*?</ref>", "", s)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\{\{Item\|([^}|]*)[^}]*\}\}", r"\1", s)
    s = s.replace("'''", "").replace("''", "").replace("<br>", " ")
    return re.sub(r"\s+", " ", s).strip(" }")


# --------------------------------------------------------------------------- Gegner/Boss-Seiten
_page_cache = {}


def infobox(title):
    """Liefert (name, location-Wikitext) der EnemyInfobox oder None."""
    if title in _page_cache:
        return _page_cache[title]
    t = wikiapi.wikitext(CACHE, title)
    res = None
    if t and "{{EnemyInfobox" in t:
        nm = re.search(r"\|\s*name\s*=\s*(.*?)\n", t)
        loc = re.search(r"\|\s*location\s*=(.*?)\n\|", t, re.S)
        res = (nm.group(1).strip() if nm else title, loc.group(1) if loc else "")
    _page_cache[title] = res
    return res


def biomes_from_location(loc, biome_set, min_bc):
    found = []
    for line in loc.split("\n"):
        if "summoned" in line.lower():
            continue
        l2 = line.replace("[[BSC]]", "BSC")
        mx = None
        m = re.search(r"\((\d)\s*[-–—]\s*(\d)\s*BSC\)", l2)
        if m:
            mx = int(m.group(2))
        else:
            m = re.search(r"\((\d)\s*BSC\)", l2)
            if m:
                mx = int(m.group(1))
        if mx is not None and mx < min_bc:
            continue
        for b in links(line):
            if b in biome_set and b not in found:
                found.append(b)
    return found


# --------------------------------------------------------------------------- handgepflegte Daten
START = {
    "Classic Outfit": "Standard-Outfit, von Anfang an getragen.",
    "Galaxy Outfit": "Immer beim Tailor verfügbar (Geschenk aus Update 1.3, sobald ein weiteres Outfit freigeschaltet ist).",
    "Baguette Outfit": "Immer beim Tailor verfügbar (Geschenk zum 14. Juli aus Update 1.3, sobald ein weiteres Outfit freigeschaltet ist).",
    "Retro Outfit": "Immer beim Tailor verfügbar (kam mit Update 2.0 zusammen mit dem 8-Bit-Soundtrack).",
    "Reverse Burglar's Outfit": "Immer beim Tailor verfügbar (Weihnachtsgeschenk aus Update 2.1).",
    "Winter Outfit": "Immer beim Tailor verfügbar (Wintergeschenk aus Update 2.1).",
}

# id -> (sourceType, deutscher Satz)
OVERRIDE = {
    "golden-outfit": ("shop", "Im Specialist Shop der Prisoners' Quarters für 10.000 Gold oder einen 50-Kill-Fluch kaufen."),
    "festive-outfit": ("secret", "Hinter der 4-BC-Tür im Cavern, die sich nur mit dem Garland Key öffnen lässt."),
    "gardeners-outfit": ("lore", "Im Lore-Raum des Dilapidated Arboretum."),
    "the-royal-gardeners-outfit": ("secret", "An der Leiche des Royal Gardener in den Prisoners' Quarters."),
    "hev-outfit": ("lore", "Im Lore-Raum der Prisoners' Quarters."),
    "flying-alcoholic-outfit": ("enemy", "Garantierter Drop (100 %) von Skeletons im Cavern."),
    "cultist-outfit": ("secret", "An einer der Leichen auf den großen schwebenden Inseln der Fractured Shrines; wird zum Betreten der Undying Shores benötigt und kann per Homunculus Rune sofort angezogen werden."),
    "vessels-outfit": ("challenge", "Mit dem Pure Nail 8-mal hintereinander abprallen (Pogo), ohne den Boden zu berühren."),
    "penitents-outfit": ("challenge", "Den Face Flask bei niedrigen Lebenspunkten benutzen."),
    "luchadors-outfit": ("challenge", "Einen Corpulent Zombie mit Spartan Sandals, Spiked Boots, Hayabusa Boots oder Hayabusa Gauntlets töten."),
    "little-bones-outfit": ("secret", "Per Bodenstampfer einen besonderen Grabstein nahe dem Eingang zum unterirdischen Teil des Graveyard zerschlagen."),
    "the-magicians-outfit": ("secret", "Das Hard Light Sword aufheben, während man das Drifter Outfit trägt."),
    "explorers-outfit": ("challenge", "Einen kompletten Run beenden, ohne Schaden durch Fallen zu nehmen."),
    "knights-outfit": ("lore", "Im Lore-Raum der Prisoners' Quarters."),
    "commando-outfit": ("challenge", "An einem zufälligen Altar in einem Biom (ohne Gegner in der Nähe) die zwei Schatten-Imps beschwören und töten."),
    "familiar-outfit": ("secret", "Mit der Homunculus Rune einen Gegenstand in Lava fallen lassen (z. B. hinter der Cavern-Key-Tür in den Prisoners' Quarters, im Cavern oder in Guardian's Haven)."),
    "ironclad-outfit": ("quest", "Drei Schlüssel sammeln (Emerald Key aus einem Elite-Raum, Sapphire Key von einem Wahl-Altar, Ruby Key aus einem Shop); auch über mehrere Biome verteilt möglich."),
    "modernized-bomber-outfit": ("challenge", "Einen Gegner mit dem Baseball Bat töten, nachdem er durch eine aufgebrochene Tür oder herabfallende Trümmer betäubt wurde."),
    "zero-outfit": ("challenge", "15 Gegner in Folge mit dem Dash-Angriff von Hattori's Katana töten, ohne getroffen zu werden."),
    "shovel-knight-outfit": ("secret", "Das Shovel-Knight-Gemälde im High Peak Castle mit der Shovel zerschlagen."),
    "delayed-hedgehog-outfit": ("challenge", "Den Lighthouse in unter 300 Sekunden abschließen (ab Ende der Zwischensequenz bis zum letzten Servant-Kill)."),
    "gentlemans-outfit": ("challenge", "Am Ende einer Plattform-Herausforderung in The Bank."),
    "trailer-bobby-outfit": ("lore", "Im Lore-Raum der Prisoners' Quarters."),
    "simon-outfit": ("lore", "Im Lore-Raum von Dracula's Castle."),
    "alucard-outfit": ("quest", "Alucard im Master's Keep treffen."),
    "richter-outfit": ("quest", "Den Richter-Modus in Dracula's Castle abschließen."),
    "sypha-outfit": ("lore", "Im Lore-Raum des Master's Keep vor dem Kampf gegen Dracula."),
    "trevor-outfit": ("lore", "Im Lore-Raum des Master's Keep vor dem Kampf gegen Dracula."),
    "maria-renard-outfit": ("quest", "Mit Maria Renard in Castle's Outskirts sprechen."),
    "sacrificial-tick-outfit": ("quest", "Den Mushroom Boi! im Lore-Raum am Ende des Morass of the Banished opfern und danach das Nest betreten."),
    "king-outfit": ("quest", "Auf 5 BC den Collector besiegen, nachdem man den König übernommen hat: Collector einmal besiegen, dann mit der Symmetrical Lance der Hand of the King den Schild zerschlagen und den König mit der Homunculus Rune übernehmen."),
    "white-king-outfit": ("boss", "Den Collector (5 BC) ohne Schaden besiegen; erst möglich, wenn das King Outfit bereits freigeschaltet ist."),
    "flawless-servant-outfit": ("boss", "Den Lighthouse (Kampf gegen The Servants) ohne erlittenen Schaden abschließen (Flawless, ohne Aspekte)."),
    "fallen-collector-outfit": ("boss", "Drop des Collector (5 BC) beim zweiten Sieg."),
}

REFERENCE = {
    "legendary-warriors-outfit": "Son Goku aus Dragon Ball",
    "donatello-outfit": "Donatello aus Teenage Mutant Ninja Turtles",
    "carduus-outfit": "Anspielung auf Carduus, den Haupt-Artist von Dead Cells (Vorliebe für Lila)",
    "aphrodite-outfit": "Griechische Göttin Aphrodite",
    "cloud-outfit": "Cloud Strife aus Final Fantasy VII",
    "drifter-outfit": "Der Drifter aus Hyper Light Drifter",
    "a-thousand-and-one-nights-outfit": "Aladdin (Zeichentrickfilm)",
    "dictator-outfit": "M. Bison (Dictator) aus Street Fighter",
    "mage-outfit": "Farbschema des Schwarzmagiers aus Final Fantasy",
    "trailer-bobby-outfit": "Der Beheaded aus den animierten Dead-Cells-Trailern (mit Flammenkopf)",
    "robin-hood-outfit": "Robin Hood",
    "desert-dweller-outfit": "Vault-Overall aus der Fallout-Reihe",
    "galaxy-outfit": "Farbschema von GOG.com / GOG Galaxy",
    "baguette-outfit": "Französischer Nationalfeiertag (14. Juli)",
    "retro-outfit": "Monochromer grüner Bildschirm des ersten Game Boy",
    "hev-outfit": "HEV-Anzug von Gordon Freeman aus Half-Life",
    "blade-masters-outfit": "Beatrix Kiddo aus Kill Bill",
    "reverse-burglars-outfit": "Weihnachtsmann",
    "rocky-outfit": "Name/Text spielen auf The Rocky Horror Picture Show an",
    "vessels-outfit": "Der Knight (Vessel) aus Hollow Knight",
    "penitents-outfit": "Der Büßer (Penitent One) aus Blasphemous",
    "luchadors-outfit": "Juan Aguacate aus Guacamelee!",
    "little-bones-outfit": "Skul aus Skul: The Hero Slayer",
    "the-magicians-outfit": "Hyper Light Drifter (Drifter-Variante)",
    "explorers-outfit": "Caradog McCallister aus Curse of the Dead Gods",
    "knights-outfit": "Der Knight aus Soul Knight",
    "commando-outfit": "Commando aus Risk of Rain",
    "familiar-outfit": "Standard-Spielfigur aus Terraria",
    "ironclad-outfit": "Ironclad aus Slay the Spire",
    "modernized-bomber-outfit": "Jacket aus Hotline Miami",
    "zero-outfit": "Zero aus Katana ZERO",
    "shovel-knight-outfit": "Shovel Knight aus Shovel Knight",
    "delayed-hedgehog-outfit": "Sonic the Hedgehog",
    "luminous-boss-knight-outfit": "Anspielung auf TRON",
    "bisonnica-triumph-outfit": "M. Bison (Dictator) aus Street Fighter",
    "piccolo-concierge-outfit": "Piccolo aus Dragon Ball",
    "frozen-queen-outfit": "Disney-Film Die Eiskönigin (Frozen)",
    "simon-outfit": "Simon Belmont aus Castlevania",
    "alucard-outfit": "Alucard aus Castlevania",
    "richter-outfit": "Richter Belmont aus Castlevania",
    "sypha-outfit": "Sypha Belnades aus Castlevania",
    "trevor-outfit": "Trevor Belmont aus Castlevania",
    "maria-renard-outfit": "Maria Renard aus Castlevania",
    "hector-outfit": "Hector aus Castlevania",
    "haunted-armor-outfit": "Castlevania-Reihe",
    "death-outfit": "Der Tod aus Castlevania",
    "cold-death-outfit": "Der Tod aus Castlevania (Farbvariante)",
    "red-death-outfit": "Der Tod aus Castlevania; Name nach Poes Die Maske des Roten Todes",
    "edgy-death-outfit": "Der Tod aus Castlevania (Farbvariante)",
    "spectral-death-outfit": "Der Tod aus Castlevania (Farbvariante)",
    "flawless-death-outfit": "Der Tod aus Castlevania (Flawless-Variante)",
    "dracula-outfit": "Dracula aus Castlevania",
    "mathias-cronqvist-outfit": "Mathias Cronqvist (Draculas früheres Ich) aus Castlevania",
    "doctor-dracula-outfit": "Dracula aus Castlevania im Stil von Doctor Strange (Marvel)",
    "pompous-dracula-outfit": "Dracula aus Castlevania (Farbvariante)",
    "vigilante-dracula-outfit": "Dracula aus Castlevania im Stil von Batman (DC)",
    "flawless-dracula-outfit": "Dracula aus Castlevania (Flawless-Variante)",
}

NOTES = {
    "bobby-outfit": "Gleicher Anzeigename wie das Trailer-Bobby-Outfit (Update 3.0); die Wiki-Fußnote zum Trailer-Look gehört laut Patchnotes zum anderen Bobby Outfit.",
    "trailer-bobby-outfit": "Im Spiel ebenfalls „Bobby Outfit“ genannt; Wiki-intern als „Trailer Bobby Outfit“ geführt (Update 3.0).",
    "cultist-outfit": "Einziges Outfit mit Spielfunktion: nötig, um die Undying Shores erstmals von den Fractured Shrines aus zu betreten.",
    "gardeners-outfit": "Im Spiel als „Gardner's Outfit“ falsch geschrieben.",
    "king-outfit": "Spoiler (Wahres Ende).",
    "white-king-outfit": "Spoiler (Wahres Ende).",
    "fallen-collector-outfit": "Spoiler.",
}


def de_num(s):
    return s.replace(".", ",").replace("%", " %")


def main():
    text = wikiapi.wikitext(CACHE, "Outfits")
    blocks = parse_blocks(text)
    biome_set = set(t for t in wikiapi.category(CACHE, "Category:Biomes")
                    if ":" not in t and "/" not in t and t != "Biomes")

    outfits = []
    for d in blocks:
        name = d["name"]
        oid = slug(d.get("showcase") or name)
        loc = d.get("location", "")
        diff = d.get("difficulty", "").strip()
        m = re.match(r"(\d)\+?\s*BSC", diff)
        min_bc = int(m.group(1)) if m else 0
        m = re.search(r"\((\d)(?:-\d)?\s*BSC\)", loc)  # Boss-Rush-Prüfungen
        if m and "Boss Rush" in loc:
            min_bc = int(m.group(1))
        cost = d.get("cost", "").strip()
        cells = int(cost) if cost.isdigit() else None
        chance = d.get("drop_chance") or (re.search(r"\((\d+(?:\.\d+)?%)\)", loc) or [None, None])[1]
        dlc = DLC.get((d.get("dlc") or "").strip().lower())
        flawless = name.startswith("Flawless ") or oid == "white-king-outfit"

        # Quelle / Biome
        enemy = None
        biomes = []
        for lk in links(loc):
            if lk in biome_set:
                biomes.append(lk) if lk not in biomes else None
                continue
            ib = infobox(lk)
            if ib:
                enemy = enemy or ib[0]
                for b in biomes_from_location(ib[1], biome_set, min_bc):
                    if b not in biomes:
                        biomes.append(b)

        is_boss_drop = bool(re.match(r"(Drops|Defeat|Clear)", loc)) and enemy and (
            "Drops from the [[" in loc or flawless or enemy in (
                "Conjunctivius", "Mama Tick", "Death", "Dracula - Final Form"))
        if name in START:
            stype, src = "start", START[name]
        elif oid in OVERRIDE:
            stype, src = OVERRIDE[oid]
        elif "Boss Rush" in loc:
            stype = "challenge"
            nr = re.search(r"(\d)(?:st|nd|rd|th)", loc).group(1)
            rng = re.search(r"\(([\d\-]+) BSC\)", loc).group(1)
            how = "ohne Treffer (flawless) abschließen" if "flawless" in loc else "abschließen"
            src = f"Die {nr}. Boss-Rush-Prüfung auf {rng} BC {how}."
        elif flawless and enemy:
            stype = "boss"
            src = f"{enemy} ohne erlittenen Schaden besiegen (Flawless, ohne Aspekte)"
            src += "; wird rückwirkend gewährt, wenn das passende Achievement schon freigeschaltet ist." if "retroactively" in d.get("note", "") else "."
        elif is_boss_drop:
            stype = "boss"
            lvl = "auf jeder BC-Stufe" if min_bc == 0 else f"ab {min_bc} BC"
            src = (f"Drop von {enemy} bei einem Sieg {lvl} (Boss-Outfits fallen nur bei Kills ohne "
                   f"geplanten Entwurf-Drop und in aufsteigender BC-Reihenfolge).")
        elif enemy and re.match(r"(Drops|Dropped) from", loc):
            stype = "enemy"
            lvl = "auf jeder BC-Stufe" if min_bc == 0 else f"ab {min_bc} BC"
            ch = f" ({de_num(chance)} Chance)" if chance else ""
            src = f"Zufallsdrop{ch} von {enemy} {lvl}."
        else:
            stype, src = "other", plain(loc)
            print("WARN: keine Klassifizierung für", name, "->", loc, file=sys.stderr)

        rec = {
            "id": oid,
            "name": name,
            "nameDe": None,
            "dlc": dlc,
            "source": src,
            "sourceType": stype,
            "biomes": biomes,
            "minBC": min_bc,
            "cells": cells,
            "reference": REFERENCE.get(oid),
            "wiki": WIKI + "Outfits#" + quote((d.get("showcase") or name).replace(" ", "_"), safe="_-.'()!"),
            "image": None,
            # Zusatzfelder für den Tracker
            "enemy": (enemy or ("The Servants" if oid == "flawless-servant-outfit" else None)) if stype in ("enemy", "boss") else None,
            "dropChance": chance if stype == "enemy" else None,
            "flawless": flawless,
            "iconFile": (d.get("icon") or f"{name} Icon") + ".png",
            "notes": NOTES.get(oid),
        }
        outfits.append(rec)

    fetch_images(outfits)
    for r in outfits:
        r.pop("iconFile")

    validate(outfits)
    meta = {
        "title": "Dead Cells – Outfits (Skins)",
        "gameVersion": "3.5 (The End is Near) inkl. aller DLCs",
        "source": WIKI + "Outfits",
        "sourceApi": "https://deadcells.wiki.gg/api.php (action=parse, Outfits + Gegner-/Boss-Seiten)",
        "generatedBy": "tools/build_outfits.py",
        "count": len(outfits),
        "fields": {
            "sourceType": "start|enemy|boss|lore|secret|challenge|achievement|shop|quest|other",
            "minBC": "Mindest-Boss-Cell-Stufe, ab der der Entwurf fallen bzw. erspielt werden kann",
            "cells": "Zellkosten beim Collector; null = kostenlos/direkt freigeschaltet bzw. unbekannt",
            "biomes": "Biome, in denen Gegner/Boss bzw. Fundort auf >= minBC vorkommt (aus Wiki-Infoboxen abgeleitet)",
            "enemy": "Englischer Name des droppenden Gegners/Bosses (nur sourceType enemy/boss)",
            "flawless": "true = Boss ohne Schaden besiegen",
        },
        "hints": [
            "Sewing Scissors erfordert 16, Giant Comb 51 freigeschaltete Outfits.",
            "Boss-Outfits droppen nur bei Kills ohne geplanten Entwurf-Drop; die niedrigste noch fehlende BC-Stufe kommt zuerst.",
            "Der Hunter's Grenade erhöht die Chance auf Gegner-Drops (auch Outfits).",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"meta": meta, "outfits": outfits}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"OK: {len(outfits)} Outfits -> {OUT}")


def fetch_images(outfits):
    ASSETS.mkdir(parents=True, exist_ok=True)
    IMGCACHE.mkdir(parents=True, exist_ok=True)
    files = sorted({r["iconFile"] for r in outfits})
    info = {}
    for i in range(0, len(files), 40):
        chunk = files[i:i + 40]
        d = wikiapi.api(CACHE, {"action": "query", "titles": "|".join("File:" + f for f in chunk),
                                "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "96"})["data"]
        norm = {n["to"]: n["from"] for n in d["query"].get("normalized", [])}
        for pg in d["query"]["pages"]:
            if pg.get("imageinfo"):
                title = norm.get(pg["title"], pg["title"])
                info[title[5:]] = pg["imageinfo"][0]
                info[pg["title"][5:]] = pg["imageinfo"][0]
    for r in outfits:
        ii = info.get(r["iconFile"]) or info.get(r["iconFile"].replace("_", " "))
        if not ii:
            print("WARN: kein Icon für", r["name"], file=sys.stderr)
            continue
        url = ii.get("thumburl") or ii["url"]
        cf = IMGCACHE / (slug(r["iconFile"][:-4]) + ".png")
        if not cf.exists():
            cf.write_bytes(wikiapi.get(url, binary=True))
        data = cf.read_bytes()
        if not data.startswith(b"\x89PNG") or len(data) > 30 * 1024:
            print("WARN: Icon ungeeignet für", r["name"], len(data), file=sys.stderr)
            continue
        (ASSETS / f"{r['id']}.png").write_bytes(data)
        r["image"] = f"assets/outfits/{r['id']}.png"


def validate(outfits):
    errs = []
    ids = [r["id"] for r in outfits]
    for i in set(ids):
        if ids.count(i) > 1:
            errs.append(f"doppelte id: {i}")
    names = [r["name"] for r in outfits]
    for n in set(names):
        if names.count(n) > 1:
            print(f"Hinweis: Name mehrfach (gewollt?): {n}", file=sys.stderr)
    req = ["id", "name", "source", "sourceType", "biomes", "minBC", "wiki"]
    types = {"start", "enemy", "boss", "lore", "secret", "challenge", "achievement", "shop", "quest", "other"}
    for r in outfits:
        for k in req:
            if r.get(k) in (None, "") and k != "biomes":
                errs.append(f"{r['id']}: Feld {k} fehlt")
        if r["sourceType"] not in types:
            errs.append(f"{r['id']}: sourceType {r['sourceType']}")
        if r["dlc"] not in (None, *DLC.values()):
            errs.append(f"{r['id']}: dlc {r['dlc']}")
        if r["image"] and not (ROOT / r["image"]).exists():
            errs.append(f"{r['id']}: Bild fehlt")
        if r["sourceType"] in ("enemy", "boss") and not r["biomes"] and r["id"] != "white-king-outfit":
            print(f"Hinweis: {r['id']} ohne Biome", file=sys.stderr)
    if errs:
        raise SystemExit("VALIDIERUNG FEHLGESCHLAGEN:\n" + "\n".join(errs))
    print("Validierung OK:", len(outfits), "Einträge,", sum(1 for r in outfits if r["image"]), "Bilder")


if __name__ == "__main__":
    main()
