"""Baut data/world.json (Biome, Bosse, Runen, Boss Cells, Zeittüren, Sonderbereiche) für Dead Cells 3.5.

Quellen: deadcells.wiki.gg (MediaWiki-API, gecacht unter research/cache/world/).
Strukturdaten (Gegnerlisten, Schriftrollen, Elite-Chancen, Bilder) werden aus dem Wiki geparst,
Übergänge/Bedingungen und alle deutschen Texte sind kuratiert (siehe CURATED-Abschnitte) und
gegen die Wiki-Seiten "Biomes", die Einzelseiten der Biome, "Runes", "Boss Stem Cells" und
"Time, killstreak and no-hit doors" geprüft.

Aufruf:  python -I tools/build_world.py   (aus der Projektwurzel oder von überall)
"""
import io
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import wikiapi  # noqa: E402

CACHE = ROOT / "research" / "cache" / "world"
IMGCACHE = CACHE / "img"
OUT = ROOT / "data" / "world.json"
WIKI = "https://deadcells.wiki.gg/wiki/"

RTC, TBS, FF, TQATS, ROTG = "Return to Castlevania", "The Bad Seed", "Fatal Falls", "The Queen and the Sea", "Rise of the Giant"


def wiki_url(title):
    return WIKI + urllib.parse.quote(title.replace(" ", "_"), safe="'()/,:")


# ---------------------------------------------------------------------------
# Wiki-Parsing
# ---------------------------------------------------------------------------

def infobox(w, name):
    i = w.find("{{" + name)
    if i < 0:
        return {}
    depth, j = 0, i
    while j < len(w):
        if w.startswith("{{", j):
            depth += 1; j += 2; continue
        if w.startswith("}}", j):
            depth -= 1; j += 2
            if depth == 0:
                break
            continue
        j += 1
    body = w[i + 2 + len(name):j - 2]
    parts, depth, cur, k = [], 0, "", 0
    while k < len(body):
        two = body[k:k + 2]
        if two in ("{{", "[["):
            depth += 1; cur += two; k += 2; continue
        if two in ("}}", "]]"):
            depth -= 1; cur += two; k += 2; continue
        if body[k] == "|" and depth == 0:
            parts.append(cur); cur = ""; k += 1; continue
        cur += body[k]; k += 1
    parts.append(cur)
    d = {}
    for p in parts:
        if "=" in p:
            a, b = p.split("=", 1)
            d[a.strip()] = b.strip()
    return d


ENEMY_FIX = {"Pirate Captains": "Pirate Captain", "Impaler (Enemy)": "Impaler", "Cleaver (Enemy)": "Cleaver",
             "inquisitor": "Inquisitor", "Giant": "The Giant"}


def links(text):
    out = []
    for m in re.finditer(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", text):
        t = m.group(1).strip()
        if t.startswith("File:") or t in ("Boss Stem Cells", "BSC"):
            continue
        out.append(ENEMY_FIX.get(t, t))
    return out


def parse_biomes_overview():
    """Liefert {Biomname: [Abschnitt, ...]} aus der Seite "Biomes" (Dracula's Castle kommt doppelt vor)."""
    w = wikiapi.wikitext(CACHE, "Biomes")
    heads = list(re.finditer(r"(?:^===\s*\[\[([^\]|]+)[^\n]*===\s*$|fake heading\|sub=3\|\[\[([^\]|]+))", w, re.M))
    secs = {}
    for n, m in enumerate(heads):
        name = m.group(1) or m.group(2)
        end = heads[n + 1].start() if n + 1 < len(heads) else len(w)
        secs.setdefault(name, []).append(w[m.end():end])
    return secs


def bsc_level(line):
    m = re.search(r"BSC(IV|III|II|I) Icon", line)
    return {"I": 1, "II": 2, "III": 3, "IV": 4}[m.group(1)] if m else 0


def parse_section(sec):
    lines = sec.split("\n")
    res = {"scrollLine": None, "base": [], "bc": []}
    in_enemies = False
    for ln in lines:
        s = ln.strip()
        if s.startswith("* '''Scrolls:'''"):
            res["scrollLine"] = s.split("'''Scrolls:'''", 1)[1].strip()
        if s.startswith("* '''Enemies:'''"):
            in_enemies = True
            res["base"] += links(re.sub(r"\([^)]*\)", "", s.split("'''Enemies:'''", 1)[1]))
            continue
        if in_enemies:
            if s.startswith("* '''") or not s.startswith("**"):
                in_enemies = False
                continue
            if "summoned by" in s:
                continue
            lvl = bsc_level(s)
            names = links(re.sub(r"\([^)]*\)", "", re.sub(r"\[\[File:[^\]]*\]\]", "", s)))
            if lvl == 0:
                res["base"] += names
            else:
                res["bc"] += [{"name": n, "fromBC": lvl} for n in names]
    # Duplikate entfernen, Reihenfolge behalten
    seen = set(); base = []
    for n in res["base"]:
        if n not in seen:
            seen.add(n); base.append(n)
    res["base"] = base
    return res


def scroll_info(line, cursed_pct):
    """Wandelt die Wiki-Zeile 'Scrolls:' in {power, dual, cursedChest, notes} um."""
    if not line:
        return {"power": 0, "dual": 0, "cursedChest": False, "notes": None}
    plain = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", line)
    power = 0
    m = re.match(r"(\d+)\s+(?:Scrolls? of )?Power", plain, re.I)
    if m:
        power = int(m.group(1))
    contained = "contained in" in plain
    if contained:
        power = 0
    dual = sum(int(x) for x in re.findall(r"(\d+)\s+Dual", plain))
    cursed = ("Cursed chest" in plain) or (cursed_pct is not None and cursed_pct >= 100)
    notes = []
    m = re.search(r"(\d+) extra [Pp]ower \((\d)\+", plain)
    if m:
        notes.append(f"+{m.group(1)} Schriftrolle der Macht ab {m.group(2)} BC")
    if contained:
        notes.append("Die einzige Schriftrolle der Macht liegt in der verfluchten Truhe am Eingang")
    elif cursed:
        notes.append("+1 Schriftrolle der Macht in der garantierten verfluchten Truhe")
    f3 = re.search(r"(\d+) Scroll Fragments? \(3 BSC\)", plain)
    f4 = re.search(r"(\d+) Scroll Fragments? \(4/5 BSC\)", plain)
    if f3 or f4:
        notes.append("Scroll Fragments: " + " / ".join(
            x for x in [f"{f3.group(1)} auf 3 BC" if f3 else None, f"{f4.group(1)} auf 4–5 BC" if f4 else None] if x))
    return {"power": power, "dual": dual, "cursedChest": cursed, "notes": "; ".join(notes) or None}


def pct(v):
    if not v:
        return None
    m = re.search(r"(\d+)\s*%", v)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# CURATED: Fortschritts-Flags (für Routenplaner maschinenlesbar)
# ---------------------------------------------------------------------------
FLAGS = {
    "hubUnlocked": "Startbereich im Prisoners' Quarters zum Hub ausgebaut (Tutorial Knight in zwei Läufen angesprochen oder ersten Lauf gewonnen).",
    "arboretumOpened": "Dilapidated Arboretum einmal mit dem Dilapidated Arboretum Key geöffnet (Schlüssel liegt im Prisoners' Quarters nahe dem Ausgang; danach dauerhaft offen).",
    "draculaDefeated": "Dracula (Master's Keep) mindestens einmal besiegt.",
    "deathDefeated": "Death (Defiled Necropolis) mindestens einmal besiegt.",
    "throneReached": "Throne Room mindestens einmal erreicht (Hand of the King getroffen).",
    "hotkDefeated": "The Hand of the King mindestens einmal besiegt (gibt die Homunculus Rune).",
    "cavernOpened": "Cavern-Portal im Graveyard einmal mit dem Cavern Key geöffnet (Schlüssel im Prisoners' Quarters, nur mit Homunculus Rune erreichbar).",
    "giantDefeated": "The Giant mindestens einmal besiegt.",
    "shoresOpened": "Undying Shores einmal von den Fractured Shrines aus mit angelegtem Cultist Outfit betreten.",
    "mausoleumVisited": "Mausoleum einmal über die Undying Shores erreicht.",
    "shipwreckOpened": "Infested Shipwreck einmal mit dem Crowned Key geöffnet (Fisherman in den Toxic Sewers → Michels Haus im Stilt Village).",
    "lighthouseVisited": "Lighthouse einmal über das Infested Shipwreck erreicht.",
}

RULES = [
    "Pro Stufe wird genau ein Biom besucht; optionale Biome (Prison Depths, Corrupted Prison) schieben sich zwischen Stufe 2 und 3.",
    "Dracula's Castle kann pro Lauf nur einmal besucht werden – entweder früh (Stufe 3) oder spät (Stufe 6).",
    "Run-interne Schlüssel (Village Key, Graveyard Key, Clockmaker's Key, Castle Keys, Distillery Key, Petrified Key, Astrolab-Schlüssel) sind im jeweiligen Biom selbst zu finden und stehen nur im Feld 'condition'.",
    "Mit 'firstTimeOnly: true' markierte Bedingungen müssen nur beim allerersten Durchgang erfüllt werden (danach bleibt der Weg offen) und können im selben Lauf erledigt werden.",
    "The Bank ersetzt bei aktivierter Goldtruhe das nächste Nicht-Boss-Biom und ist deshalb kein fester Knoten im Graphen (siehe otherAreas).",
]


def ex(to, rune=None, minBC=0, condition=None, flags=None, firstTimeOnly=False, note=None):
    d = {"to": to, "rune": rune, "minBC": minBC, "condition": condition, "flags": flags or []}
    if firstTimeOnly:
        d["firstTimeOnly"] = True
    if note:
        d["notes"] = note
    return d


# ---------------------------------------------------------------------------
# CURATED: Biome
#   wiki:   Titel der Wiki-Seite;  ov: Index des Abschnitts auf der Seite "Biomes" (für Dracula's Castle)
#   depth:  Spiel-interne Ebene (1–7), None bei Bossarenen/optionalen Biomen
# ---------------------------------------------------------------------------
B = []


def biome(**kw):
    B.append(kw)


biome(id="prisoners-quarters", name="Prisoners' Quarters", kind="biome", stage=1, depth=1, dlc=None, minBC=0, difficulty=1,
      description="Startbiom jedes Laufs: lange, fackelbeleuchtete Kerkergänge mit leichten Gegnern. Davor liegt der Hub mit Sammler-Fortschritt, BC-Röhre, Doktor (Aspekte), Schneider und Trainingsraum.",
      exits=[ex("promenade-of-the-condemned"),
             ex("toxic-sewers", rune="Vine Rune"),
             ex("dilapidated-arboretum", rune="Teleportation Rune", condition="Beim ersten Mal den Dilapidated Arboretum Key mitnehmen (liegt in diesem Biom nahe dem Ausgang).", flags=["arboretumOpened"], firstTimeOnly=True),
             ex("castles-outskirts", condition="Erst wenn der Startbereich zum Hub ausgebaut ist (Tutorial Knight zweimal angesprochen oder ersten Lauf gewonnen).", flags=["hubUnlocked"])],
      timedDoor={"minutes": 2, "to": ["promenade-of-the-condemned", "toxic-sewers", "dilapidated-arboretum", "castles-outskirts"],
                 "notes": "Zeittür im Übergang zu jedem Stufe-2-Biom; Richtung Promenade mit Assault Shield-, Richtung Toxic Sewers mit Frenzy-Entwurf."},
      tips=["Für die 2-Minuten-Zeittür direkt zum Ausgang laufen und nur Gegner im Weg erledigen.",
            "Nach dem ersten Sieg über die Hand of the King mit der Homunculus Rune den Cavern Key hinter der großen Tür am Anfang holen (öffnet die Cavern).",
            "Den Dilapidated Arboretum Key einmal mit Teleportation Rune zum Arboretum-Ausgang tragen – danach ist der Weg dauerhaft offen.",
            "Specialist's Showroom (Sammler-Upgrade) bietet Hunter's Grenade und Forgotten Map gegen Gold."])

biome(id="promenade-of-the-condemned", name="Promenade of the Condemned", kind="biome", stage=2, depth=2, dlc=None, minBC=0, difficulty=1,
      description="Weitläufiges, grünes Außengelände mit Höhlen darunter und das Biom mit den meisten Ausgängen. Hier wartet der Elite-Wächter der Vine Rune.",
      exits=[ex("ramparts", rune="Vine Rune", condition="Ohne Vine Rune geht es in der Promenade nicht weiter; die Rune bekommst du hier selbst."),
             ex("prison-depths", rune="Spider Rune"),
             ex("ossuary", rune="Teleportation Rune"),
             ex("morass-of-the-banished", rune="Teleportation Rune")],
      timedDoor={"minutes": 8, "to": ["ramparts", "ossuary"], "notes": "8-Minuten-Tür im Übergang zu Ramparts bzw. Ossuary; Richtung Ossuary mit Marksman's Bow-Entwurf."},
      fixedElites="Elite Undead Archer (Wächter der Vine Rune, nur bis zum ersten Sieg)",
      tips=["Zuerst die Vine Rune holen: der Elite Undead Archer sitzt in einer Halle unter einer Überführung.",
            "Drei Gardener's Keys sammeln → Explosive Crossbow-Entwurf; ab 3 BC tauschst du sie gegen Moonflower Keys (Acceptance-Entwurf in High Peak Castle).",
            "Mit Spider Rune hoch über dem Eingang nach Geheimräumen suchen (Assassin's Dagger, Ripper).",
            "Ossuary- und Morass-Ausgang liegen hinter Teleportationsmonolithen (Teleportation Rune)."])

biome(id="toxic-sewers", name="Toxic Sewers", kind="biome", stage=2, depth=2, dlc=None, minBC=0, difficulty=2,
      description="Enge, giftgrüne Kanalisation voller Würmer, Skorpione und Kamikaze-Fledermäuse. Fundort der Teleportation Rune.",
      exits=[ex("ramparts"),
             ex("ancient-sewers", rune="Ram Rune"),
             ex("corrupted-prison", rune="Spider Rune"),
             ex("draculas-castle-early", condition="Erst nach dem ersten Sieg über Dracula.", flags=["draculaDefeated"])],
      timedDoor={"minutes": 8, "to": ["ramparts"], "notes": "Nur im Übergang zu den Ramparts."},
      fixedElites="Elite Slasher (Wächter der Teleportation Rune, nur bis zum ersten Sieg)",
      tips=["Elite Slasher besiegen → Teleportation Rune (öffnet Ossuary, Morass, Arboretum und Forgotten Sepulcher).",
            "Giftbecken meiden; Skorpione vergiften mit Schwanzhieb und Giftschuss.",
            "Disgusting Worms lassen beim Tod mehrere Bomben fallen – nach dem Kill Abstand nehmen.",
            "Den Fisherman ansprechen: Start der Questreihe zum Infested Shipwreck (The Queen and the Sea)."])

biome(id="dilapidated-arboretum", name="Dilapidated Arboretum", kind="biome", stage=2, depth=2, dlc=TBS, minBC=0, difficulty=2,
      description="Überwucherter Schlossgarten mit Pilzgegnern, Dornen und fleischfressenden Pflanzen. Einstieg in die Bad-Seed-Route über Morass und Nest.",
      exits=[ex("morass-of-the-banished"), ex("ramparts"), ex("prison-depths", rune="Spider Rune")],
      timedDoor={"minutes": 8, "to": ["ramparts"], "notes": "Nur im Übergang zu den Ramparts."},
      tips=["Erstzugang: Dilapidated Arboretum Key im Prisoners' Quarters aufheben und mit Teleportation Rune herbringen – danach dauerhaft offen.",
            "Yeeter werfen Steine und schleudern Jerkshrooms auf dich – sie zuerst ausschalten.",
            "Jerkshrooms ducken sich in ihren Panzer; nach ihrem Ansturm zuschlagen.",
            "Exklusive Entwürfe: Flashing Fans (Yeeter), Mushroom Boi! (Jerkshroom)."])

biome(id="castles-outskirts", name="Castle's Outskirts", kind="biome", stage=2, depth=2, dlc=RTC, minBC=0, difficulty=2,
      description="Blau leuchtendes Vorgelände von Draculas Schloss mit Burggraben und langem Aufzugsschacht; hier triffst du Richter, Alucard und Maria.",
      exits=[ex("draculas-castle-early"),
             ex("corrupted-prison", rune="Spider Rune", condition="Erst nach dem ersten Sieg über Dracula.", flags=["draculaDefeated"]),
             ex("ossuary", condition="Erst nach dem ersten Sieg über Dracula.", flags=["draculaDefeated"])],
      timedDoor={"minutes": 8, "to": ["draculas-castle-early"], "notes": "8-Minuten-Tür im Übergang zu Dracula's Castle."},
      tips=["Die Zugbrücke öffnest du über einen Geheimtunnel im Burggraben; sie bleibt danach dauerhaft unten.",
            "Die herumlaufende Katze fangen → Ribonned Key für Marias Zelle (Maria Renard Outfit, Maria's Cat).",
            "Anfangs führt nur der Weg nach Dracula's Castle weiter; Ossuary und Corrupted Prison öffnen sich nach dem ersten Dracula-Sieg.",
            "Mermen spucken Feuerbälle, Vampire Bats und Harpies stürzen sich auf dich – Fernkampf hilft."])

biome(id="prison-depths", name="Prison Depths", kind="biome", optional=True, stage=3, depth=None, dlc=None, minBC=0, difficulty=3,
      description="Optionaler, düsterer Kerkerabschnitt zwischen Stufe 2 und 3: kurz, aber mit gefährlichen Gegnern (Slasher, Lacerator, Hammer). Die verfluchte Truhe am Anfang enthält die einzige Schriftrolle.",
      exits=[ex("ossuary"), ex("morass-of-the-banished"), ex("ancient-sewers", minBC=1, condition="Tür ab 1 BC.")],
      tips=["Nur mit Spider Rune über Promenade oder Arboretum erreichbar.",
            "Die verfluchte Truhe am Eingang lohnt sich nur, wenn du 10 Kills ohne Treffer schaffst (sonst Tod durch Fluch).",
            "Iron Cells Key (Drop eines zufälligen Gegners) öffnet am Ende eine von zwei Zellen mit 2er-Item-Altar.",
            "Hammers beschwören Fliegenschwärme – zügig ausschalten."])

biome(id="corrupted-prison", name="Corrupted Prison", kind="biome", optional=True, stage=3, depth=None, dlc=None, minBC=0, difficulty=3,
      description="Optionaler, stark verseuchter Gefängnistrakt hinter den Toxic Sewers mit Slammern und Toxic Miasma; ebenfalls mit verfluchter Truhe am Anfang.",
      exits=[ex("ancient-sewers"),
             ex("ramparts", minBC=1, condition="Tür ab 1 BC."),
             ex("draculas-castle-early", condition="Erst nach dem ersten Sieg über Dracula.", flags=["draculaDefeated"])],
      tips=["Zugang über die Toxic Sewers mit Spider Rune, nach dem ersten Dracula-Sieg auch aus Castle's Outskirts.",
            "Slammer-Angriffe lassen sich nicht parieren – Abstand halten.",
            "Toxic Miasmas tauchen ab und erscheinen neben dir; nicht in Gruppen hineinrollen.",
            "Iron Cells Key öffnet wie in den Prison Depths eine von zwei Item-Zellen am Ende."])

biome(id="ramparts", name="Ramparts", kind="biome", stage=4, depth=3, dlc=None, minBC=0, difficulty=2,
      description="Hohe Festungsmauern mit Türmen und tiefen Abgründen – der Standardweg zur Black Bridge. Sweeper, Inquisitoren und Buzzcutter prägen das Biom.",
      exits=[ex("black-bridge"), ex("insufferable-crypt", minBC=3, condition="Tür ab 3 BC (Weg zu Conjunctivius ohne Ram Rune).")],
      fixedElites="Elite Zombie nahe dem Eingang (Wächter der Customization Rune, nur bis zum ersten Sieg)",
      tips=["Elite Zombie nahe dem Eingang besiegen → Customization Rune (schaltet den Custom Mode frei).",
            "Ausgangs-Hinweis: Steht an der Oberfläche eine Holzplattform, liegt der Ausgang unten in einem Turm rechts – sonst ganz am rechten Ende.",
            "Inquisitoren schießen durch Wände; Sweeper legen Flammenspuren.",
            "Ab 2 BC Food Shop hinter der BC-Tür, ab 3 BC Tür zur Insufferable Crypt."])

biome(id="ancient-sewers", name="Ancient Sewers", kind="biome", stage=4, depth=3, dlc=None, minBC=0, difficulty=3,
      description="Enge, gelbliche Abwasserkanäle mit Giftbecken, Kamikaze-Schwärmen und Tentakeln aus dem Boden. Einziger Ausgang: Conjunctivius in der Insufferable Crypt.",
      exits=[ex("insufferable-crypt")],
      tips=["Aus den Toxic Sewers nur mit Ram Rune erreichbar.",
            "Old Service Keys (3 Stück, Gegnerdrops) öffnen 3 von 8 Belohnungen am Ende.",
            "Mit Homunculus Rune das Labyrinth zum Gold Reserves V-Entwurf lösen.",
            "Auf 3–5 BC viele Scroll Fragments – lohnende Route für Hochstufen-Läufe."])

biome(id="ossuary", name="Ossuary", kind="biome", stage=4, depth=3, dlc=None, minBC=0, difficulty=2,
      description="Dunkles, rot glühendes Knochenhaus voller Leichenberge mit Shockern, Thornies und Spawnern. Fundort der Ram Rune.",
      exits=[ex("black-bridge"),
             ex("defiled-necropolis", condition="Seit 3.5; erst nach dem ersten Sieg über Dracula (der Master's-Keep-Ausgang führt zur Necropolis).", flags=["draculaDefeated"])],
      fixedElites="Elite Slasher (Wächter der Ram Rune, nur bis zum ersten Sieg)",
      tips=["Elite Slasher besiegen → Ram Rune (Zugang zu den Ancient Sewers).",
            "Garantierte verfluchte Truhe: zusätzliche Schriftrolle der Macht gegen 10 Kills unter Fluch.",
            "Spawner zuerst töten, sonst erzeugen sie ständig neue Corpse Juices.",
            "Thornies nicht von hinten mit Nahkampf schlagen – die Stacheln verletzen dich."])

biome(id="morass-of-the-banished", name="Morass of the Banished", kind="biome", stage=4, depth=3, dlc=TBS, minBC=0, difficulty=3,
      description="Feuchter Sumpf der Verbannten mit Giant Ticks, Blasrohrschützen und Speerkämpfern. Einziger Weg zum Nest.",
      exits=[ex("nest")],
      tips=["Giant Ticks verhalten sich wie Mini-Bosse; auf ihre Sprungattacke mit Giftgeschossen achten.",
            "Blowgunner aus der Distanz zuerst ausschalten.",
            "Garantierte verfluchte Truhe; ab 2 BC Food Shop hinter der BC-Tür.",
            "Erreichbar über Arboretum, Prison Depths oder die Promenade (Teleportation Rune)."])

biome(id="draculas-castle-early", name="Dracula's Castle", variant="early", wiki_title="Dracula's Castle", ov=0, kind="biome", stage=4, depth=3, dlc=RTC, minBC=0, difficulty=3,
      description="Draculas rotes, verschachteltes Schloss auf Ebene 3 – das erste Biom, das sich in sich selbst schleift. Der scheinbare Ausgang zum Master's Keep wird anfangs zur Falle Richtung Defiled Necropolis.",
      exits=[ex("defiled-necropolis", condition="Der Ausgang zeigt Master's Keep, magische Ketten ziehen dich aber zur Defiled Necropolis."),
             ex("black-bridge", condition="Erst nach dem ersten Sieg über Dracula.", flags=["draculaDefeated"])],
      tips=["Pro Lauf nur einmal betretbar – entweder hier oder in der späten Variante auf Stufe 6.",
            "Garantierte verfluchte Truhe und viele Schriftrollen (ab 2 BC eine zusätzliche).",
            "Axe Armors werfen ihre Äxte im Bogen; Buer stürmen auf dich zu.",
            "Nach dem ersten Dracula-Sieg auch über Toxic Sewers und Corrupted Prison erreichbar."])

biome(id="black-bridge", name="Black Bridge", kind="boss", stage=5, depth=None, dlc=None, minBC=0, difficulty=2,
      description="Brennende Brücke vor der Burg, auf der The Concierge wartet – der klassische erste Bosskampf.",
      exits=[ex("stilt-village"), ex("slumbering-sanctuary", rune="Spider Rune"), ex("fractured-shrines")],
      timedDoor={"minutes": 15, "to": ["stilt-village", "slumbering-sanctuary", "fractured-shrines"], "notes": "Mit Root Grenade-Entwurf."},
      tips=["Der erste Sieg über den Concierge gibt die Challenger's Rune (Daily Run).",
            "Für die 15-Minuten-Zeittür (Root Grenade) die ersten Biome zügig spielen.",
            "Slumbering Sanctuary ist von hier nur mit Spider Rune erreichbar."])

biome(id="insufferable-crypt", name="Insufferable Crypt", kind="boss", stage=5, depth=None, dlc=None, minBC=0, difficulty=3,
      description="Unterirdische Gruft mit Plattformen, in der Conjunctivius angekettet ist.",
      exits=[ex("slumbering-sanctuary"), ex("graveyard", rune="Spider Rune")],
      timedDoor={"minutes": 19.5, "to": ["graveyard"], "notes": "Nur im Übergang zum Graveyard (19:30 Minuten)."},
      tips=["Erreichbar über die Ancient Sewers (Ram Rune) oder ab 3 BC über die Ramparts.",
            "Fallen (Wolf Trap) und Frost gegen die Tentakel einpacken.",
            "Graveyard nur mit Spider Rune; dorthin gibt es eine 19:30-Zeittür."])

biome(id="nest", name="Nest", kind="boss", stage=5, depth=None, dlc=TBS, minBC=0, difficulty=3,
      description="Sumpfiges Nest der Mama Tick, die halb im Wasser verborgen kämpft.",
      exits=[ex("stilt-village"), ex("fractured-shrines"), ex("graveyard", rune="Spider Rune")],
      timedDoor={"minutes": 15, "to": ["stilt-village", "fractured-shrines", "graveyard"], "notes": None},
      tips=["Frost- und Schockwaffen mitnehmen, Feuer ist im Wasser nutzlos.",
            "Graveyard nur mit Spider Rune.",
            "15-Minuten-Zeittür im Übergang nach dem Kampf."])

biome(id="defiled-necropolis", name="Defiled Necropolis", kind="boss", stage=5, depth=None, dlc=RTC, minBC=0, difficulty=3,
      description="Entweihte Totenstadt, in der Death als erster Boss der Castlevania-Route kämpft.",
      exits=[ex("slumbering-sanctuary"), ex("stilt-village"),
             ex("graveyard", rune="Spider Rune", note="Seit 3.5 ersetzt der Graveyard hier den früheren Ausgang zu den Fractured Shrines.")],
      timedDoor={"minutes": 15, "to": ["slumbering-sanctuary", "stilt-village", "graveyard"],
                 "notes": "Laut Wiki-Übersichten 15 Minuten; in der Zeittür-Tabelle und der Biomseite nicht aufgeführt (unsicher)."},
      tips=["Seit 3.5 auch über die Ossuary erreichbar (nach dem ersten Dracula-Sieg).",
            "Nach dem ersten Death-Sieg öffnet sich in späteren Läufen Dracula's Castle über den Clock Room.",
            "No-Hit-Tür mit legendärem Item nach makellosem Kampf."])

biome(id="stilt-village", name="Stilt Village", kind="biome", stage=6, depth=4, dlc=None, minBC=0, difficulty=3,
      description="Pfahldorf über dem Wasser mit zerfallenen Hütten und vielen Wandergegnern; Village Keys öffnen die Ausgänge.",
      exits=[ex("clock-tower", condition="Village Key nötig (zwei Schlüsselräume im Biom)."),
             ex("forgotten-sepulcher", rune="Teleportation Rune", condition="Village Key nötig."),
             ex("undying-shores", condition="Village Key nötig; erst nachdem die Undying Shores über die Fractured Shrines geöffnet wurden.", flags=["shoresOpened"])],
      timedDoor={"minutes": 26, "to": ["forgotten-sepulcher"], "notes": "Zeittür vor dem Forgotten Sepulcher (laut Wiki 'before Forgotten Sepulcher'; Herkunftsbiome nicht eindeutig belegt)."},
      fixedElites="Elite Armored Shrimp in Michels Haus (droppt den Crowned Key, The Queen and the Sea)",
      tips=["Beide Village Keys einsammeln: Sie öffnen Ausgänge oder den Parry Shield-Entwurf.",
            "In Michels Haus den Elite Armored Shrimp besiegen → Crowned Key für das Infested Shipwreck (vorher Fisherman in den Toxic Sewers sprechen).",
            "Pirate Captains feuern explodierende Kanonenkugeln.",
            "Forgotten-Sepulcher-Ausgang braucht zusätzlich die Teleportation Rune."])

biome(id="slumbering-sanctuary", name="Slumbering Sanctuary", kind="biome", stage=6, depth=4, dlc=None, minBC=0, difficulty=3,
      description="Uralter Tempel, der zunächst schläft: Viele Gegner stehen als graue Statuen herum, bis du den Ancient Temple Switch aktivierst. Fundort der Spider Rune.",
      exits=[ex("clock-tower"),
             ex("forgotten-sepulcher", rune="Teleportation Rune", note="Laut Runen-Übersicht und Infobox des Forgotten Sepulcher nötig; die Biomseite des Sanctuary nennt es nicht ausdrücklich."),
             ex("cavern", minBC=2, condition="Tür ab 2 BC, erst nachdem der Giant einmal besiegt wurde.", flags=["giantDefeated"])],
      timedDoor={"minutes": 26, "to": ["clock-tower", "forgotten-sepulcher"], "notes": "Laut Wiki 26 Minuten 'nach dem Slumbering Sanctuary' (genaue Übergänge nicht eindeutig)."},
      fixedElites="Elite Caster (Wächter der Spider Rune, nur bis zum ersten Sieg)",
      tips=["Elite Caster besiegen → Spider Rune (öffnet u. a. Prison Depths, Corrupted Prison und Graveyard).",
            "Nach dem Aktivieren des Schalters erwachen die Statuen (teils als Elite) – vorsichtig nähern.",
            "Golems ziehen dich aus der Distanz zu sich heran; Dancer halten ihre Angriffe zurück, wenn du parieren willst.",
            "Garantierte verfluchte Truhe; ab 2 BC Tür zur Cavern (nach Giant-Sieg)."])

biome(id="graveyard", name="Graveyard", kind="biome", stage=6, depth=4, dlc=None, minBC=0, difficulty=4,
      description="Nächtlicher Friedhof mit oberirdischem und unterirdischem Teil. Swarm Zombies und Catcher machen ihn zu einem der härteren Stufe-4-Biome.",
      exits=[ex("forgotten-sepulcher", rune="Teleportation Rune"),
             ex("cavern", rune="Homunculus Rune", condition="Beim ersten Mal den Cavern Key aus dem Prisoners' Quarters mitbringen (nach erstem Sieg über die Hand of the King, Homunculus Rune nötig).", flags=["hotkDefeated", "cavernOpened"], firstTimeOnly=True),
             ex("undying-shores", condition="Erst nachdem die Undying Shores über die Fractured Shrines geöffnet wurden.", flags=["shoresOpened"]),
             ex("clock-tower", condition="Nur als Notausgang, wenn keiner der anderen Ausgänge nutzbar ist.")],
      timedDoor={"minutes": 26, "to": ["forgotten-sepulcher"], "notes": "Zeittür vor dem Forgotten Sepulcher (Herkunftsbiome nicht eindeutig belegt)."},
      tips=["Den Graveyard Key suchen – er öffnet den unteren Teil mit den Ausgängen.",
            "Architect's Key (in einer Wand- oder Bodenrune unten) → Merchandise Categories-Entwurf; daneben Parting Gift.",
            "Catcher ziehen dich mit einem Haken heran und schlagen dann zu – dem Haken ausweichen.",
            "Swarm Zombies umgeben sich mit einer Fliegen-Elektrobarriere."])

biome(id="fractured-shrines", name="Fractured Shrines", kind="biome", stage=6, depth=4, dlc=FF, minBC=0, difficulty=3,
      description="Zerbrochene Schreine auf Felsinseln im Regen mit tiefen Abgründen; Stone Wardens bewachen Schatzräume.",
      exits=[ex("undying-shores", condition="Beim ersten Mal das Cultist Outfit tragen (Entwurf bei den Kultistenleichen im Biom).", flags=["shoresOpened"], firstTimeOnly=True),
             ex("clock-tower"),
             ex("forgotten-sepulcher", rune="Teleportation Rune", condition="Teleporter im Übergang zum Clock Tower.")],
      timedDoor={"minutes": 26, "to": ["forgotten-sepulcher"], "notes": "Zeittür vor dem Forgotten Sepulcher (unsicher, ob auch auf diesem Weg)."},
      fixedElites="Stone Wardens (Mini-Bosse vor den Schatzraumtüren)",
      tips=["Cultist Outfit von einer Kultistenleiche holen und anlegen (mit Homunculus Rune sofort möglich), um die Tür zu den Undying Shores zu öffnen.",
            "Myopic Crows fliegen geradlinig quer durchs Biom – beim Springen über Abgründe beachten.",
            "Stone Wardens besiegen öffnet Schatzräume, u. a. mit legendärem Item-Altar.",
            "Food Shop ist hier auf jeder BC-Stufe garantiert."])

biome(id="clock-tower", name="Clock Tower", kind="biome", stage=7, depth=5, dlc=None, minBC=0, difficulty=4,
      description="Vertikaler Aufstieg durch den Uhrturm mit Zahnrädern, Automatons und Cannibals. Der Clockmaker's Key öffnet den Weg zur Time Keeper.",
      exits=[ex("clock-room", condition="Clockmaker's Key nötig (oben in einem der Türme).")],
      tips=["Clockmaker's Key liegt in einem Raum oben auf einem der Türme – ohne ihn kein Ausgang.",
            "Glockenrätsel: die vier Hintergrundglocken von tief nach hoch anschlagen → Bell Tower Key → Punishment-Entwurf.",
            "Automatons dashen zweimal über die Plattform; Bombardiers decken Flächen mit Streubomben ein.",
            "Vier Schriftrollen der Macht (+1 ab 4 BC)."])

biome(id="forgotten-sepulcher", name="Forgotten Sepulcher", kind="biome", stage=7, depth=5, dlc=None, minBC=0, difficulty=4,
      description="Stockdunkle Katakomben, in denen die Dunkelheit Leben frisst, wenn du zu lange ohne Licht bist. Fundort der Explorer's Rune.",
      exits=[ex("clock-room"),
             ex("guardians-haven", minBC=2, condition="Tür ab 2 BC nahe dem Clock-Room-Ausgang, erst nachdem der Giant einmal besiegt wurde.", flags=["giantDefeated"])],
      fixedElites="Zwei Elite Dark Trackers am Ende (Crypt Keys → Explorer's Rune, nur bis zum Erhalt der Rune)",
      tips=["Nach 12 Sekunden ohne Licht beginnt Dunkelheitsschaden; Lichtquellen anlaufen, jeder Kill senkt die Dunkelheit.",
            "Die zwei Elite Dark Trackers am Ende droppen die Crypt Keys zum Raum mit der Explorer's Rune.",
            "Corpulent Zombies springen dich an und stampfen – Abstand halten.",
            "Garantierte verfluchte Truhe und 26-Minuten-Zeittür auf dem Weg hierher."])

biome(id="cavern", name="Cavern", kind="biome", stage=7, depth=5, dlc=ROTG, minBC=0, difficulty=4,
      description="Lava-Höhle unter der Burg mit sehr hoher Ausrüstungsstufe; führt zum Giant.",
      exits=[ex("guardians-haven"),
             ex("mausoleum", condition="Erst nachdem das Mausoleum einmal über die Undying Shores besucht wurde.", flags=["mausoleumVisited"])],
      tips=["Erstzugang: Cavern Key im Prisoners' Quarters (Homunculus Rune) holen und im Graveyard das Portal öffnen.",
            "Ground Shaker lassen Steine von der Decke regnen – nicht darunter stehen bleiben.",
            "Garland Key (Rankenpassage in der Decke) öffnet die 4-BC-Tür mit dem Festive Outfit.",
            "Gear-Level 7: ideale Stelle, um starke Items aufzusammeln."])

biome(id="undying-shores", name="Undying Shores", kind="biome", stage=7, depth=5, dlc=FF, minBC=0, difficulty=4,
      description="Nebelige Küste der Apostaten, die besiegte Gegner wiederbeleben; Gegner aus vorher besuchten Biomen tauchen erneut auf. Führt zum Mausoleum.",
      exits=[ex("mausoleum")],
      tips=["Apostaten zuerst töten – sie beleben die Seelen besiegter Gegner wieder.",
            "Je nach zuvor besuchten Biomen erscheinen zusätzliche Gegnertypen (z. B. Runner nach der Promenade).",
            "Runen-Türen: Symbole auf violetten Wandteppichen zeigen die richtige Tür (Cocoon-Entwurf); eine falsche Tür sperrt alle drei.",
            "Vier Schriftrollen der Macht plus zwei Dual-Schriftrollen – lohnend für den Stat-Aufbau."])

biome(id="clock-room", name="Clock Room", kind="boss", stage=8, depth=None, dlc=None, minBC=0, difficulty=4,
      description="Zifferblatt-Arena im Uhrturm, in der The Time Keeper kämpft.",
      exits=[ex("high-peak-castle"),
             ex("derelict-distillery", condition="Erst nachdem der Throne Room einmal erreicht wurde.", flags=["throneReached"]),
             ex("infested-shipwreck", condition="Beim ersten Mal ist der Crowned Key nötig.", flags=["shipwreckOpened"], firstTimeOnly=True),
             ex("draculas-castle-late", condition="Erst nach dem ersten Sieg über Death; nicht, wenn Dracula's Castle in diesem Lauf schon besucht wurde.", flags=["deathDefeated"])],
      tips=["Schild mitnehmen – fast alle Angriffe der Time Keeper sind parierbar.",
            "Derelict Distillery erscheint erst nach dem ersten Erreichen des Throne Room.",
            "Dracula's Castle (spät) nur, wenn du es in diesem Lauf nicht schon auf Stufe 3 besucht hast."])

biome(id="guardians-haven", name="Guardian's Haven", kind="boss", stage=8, depth=None, dlc=ROTG, minBC=0, difficulty=4,
      description="Lavaarena am Burgtor, in der The Giant wacht.",
      exits=[ex("high-peak-castle"),
             ex("derelict-distillery", condition="Erst nachdem der Throne Room einmal erreicht wurde.", flags=["throneReached"]),
             ex("infested-shipwreck", condition="Beim ersten Mal ist der Crowned Key nötig.", flags=["shipwreckOpened"], firstTimeOnly=True),
             ex("throne-room", condition="Überspringt Stufe 6 und gibt dafür 2 Schriftrollen der Macht."),
             ex("draculas-castle-late", condition="Erst nach dem ersten Sieg über Dracula.", flags=["draculaDefeated"])],
      tips=["Der Ausgang direkt zum Throne Room überspringt Stufe 6 und gibt 2 Schriftrollen der Macht.",
            "Auf 4 BC droppt der Giant die 5. Boss Cell.",
            "Nicht am Rand blocken – Rückstoß schiebt dich in die Lava."])

biome(id="mausoleum", name="Mausoleum", kind="boss", stage=8, depth=None, dlc=FF, minBC=0, difficulty=4,
      description="Dach einer Gruft, auf dem The Scarecrow mit Sense, Schaufel und Pilzen kämpft.",
      exits=[ex("high-peak-castle"),
             ex("derelict-distillery", condition="Erst nachdem der Throne Room einmal erreicht wurde.", flags=["throneReached"]),
             ex("infested-shipwreck", condition="Beim ersten Mal ist der Crowned Key nötig.", flags=["shipwreckOpened"], firstTimeOnly=True),
             ex("draculas-castle-late", condition="Erst nach dem ersten Sieg über Dracula.", flags=["draculaDefeated"])],
      tips=["Aus der Cavern erst erreichbar, nachdem du einmal über die Undying Shores hier warst.",
            "Explosive Pilze früh auslösen und Abstand halten.",
            "Mit 3.5 wurde die Skalierung des Mausoleums korrigiert (vorher hatte der Scarecrow auf 3 BC weniger Leben als auf 2 BC)."])

biome(id="high-peak-castle", name="High Peak Castle", kind="biome", stage=9, depth=6, dlc=None, minBC=0, difficulty=4,
      description="Das Schloss des Königs mit prunkvollen Hallen; Elite-Wächter in drei farbigen Räumen halten die Castle Keys.",
      exits=[ex("throne-room", condition="Zwei Castle Keys nötig (von den Elite-Wächtern in den farbigen Räumen)."),
             ex("masters-keep", condition="Erst nach dem ersten Sieg über Dracula.", flags=["draculaDefeated"])],
      fixedElites="Elite Slasher, Elite Thorny und zwei Elite Dark Trackers in den farbigen Räumen (je ein Castle Key)",
      tips=["Zwei der drei Castle Keys öffnen den Weg zum Throne Room.",
            "Der dritte Schlüssel öffnet einen Raum mit Schriftrolle der Macht, zwei Items und dem Boomerang-Entwurf.",
            "Lancer stechen durch Plattformen nach oben und unten; Guardian Knights saugen dich mit einem Tornado an.",
            "Moonflower-Rätsel (Schlüssel aus Ramparts, Graveyard, Sepulcher) → Acceptance-Entwurf ab 3 BC."])

biome(id="derelict-distillery", name="Derelict Distillery", kind="biome", stage=9, depth=6, dlc=None, minBC=0, difficulty=4,
      description="Verlassene Destillerie voller explodierender, springender Fässer – Alternative zu High Peak Castle und zweiter Weg zum Lighthouse.",
      exits=[ex("throne-room", condition="Distillery Key nötig (hinter einer brüchigen Wand) und eine weitere brüchige Wand vor dem Ausgang sprengen."),
             ex("lighthouse", condition="Erst nachdem das Lighthouse einmal über das Infested Shipwreck erreicht wurde.", flags=["lighthouseVisited"])],
      tips=["Getroffene Fässer leuchten weiß und schaden nur noch Gegnern – damit Wände und Gegner sprengen.",
            "Distillery Key liegt hinter einer brüchigen Wand: Fass dagegen schlagen oder Barrel Launcher nutzen.",
            "Vor dem Ausgang einen Infected Worker ein Fass gegen die Wand werfen lassen.",
            "Living Barrels tarnen sich als Fässer und explodieren nach Treffern."])

biome(id="infested-shipwreck", name="Infested Shipwreck", kind="biome", stage=9, depth=6, dlc=TQATS, minBC=0, difficulty=4,
      description="Verfallene Schiffswracks am Fuß des Leuchtturms mit brüchigen Holzplanken; einziger Erstzugang zum Lighthouse.",
      exits=[ex("lighthouse")],
      tips=["Freischaltung: Fisherman in den Toxic Sewers ansprechen, dann den Crowned Key aus Michels Haus im Stilt Village holen.",
            "Mutineers schleudern Anker durch brüchige Böden – Plattformen können unter dir wegbrechen.",
            "Forked Key (mit der Mysterious Map ausgraben) öffnet einen Lore Room mit dem Abyssal Trident.",
            "Armored Shrimps verstecken sich in Wänden und rammen dich."])

biome(id="draculas-castle-late", name="Dracula's Castle", variant="late", wiki_title="Dracula's Castle", ov=1, kind="biome", stage=9, depth=6, dlc=RTC, minBC=0, difficulty=5,
      description="Die späte, deutlich härtere Variante von Draculas Schloss auf Ebene 6. Medusa bewacht den Petrified Key zum Master's Keep, und Dracula stört dich zwischendurch persönlich.",
      exits=[ex("masters-keep", condition="Petrified Key nötig (Truhe neben Medusas Arena).")],
      fixedElites="Medusa (Mini-Boss, bewacht den Petrified Key)",
      tips=["Medusas Blick versteinert dich, wenn du ihr zugewandt bist – beim Aufladen umdrehen.",
            "Nach Medusa die Truhe neben ihrer Arena öffnen: Petrified Key + Item.",
            "Dracula erscheint zeitweise, verflucht Essen oder spiegelt den Bildschirm.",
            "Richter aus seinem Käfig befreien schaltet den Richter Mode für spätere Läufe frei."])

biome(id="throne-room", name="Throne Room", kind="boss", stage=10, depth=None, dlc=None, minBC=0, difficulty=4,
      description="Thronsaal des Königs, Arena der Hand of the King und Ende der Hauptroute.",
      exits=[ex("astrolab", minBC=5, condition="Nur mit 5 aktiven Boss Cells.")],
      tips=["Der erste Sieg gibt die Homunculus Rune; danach verlässt du den Thronsaal per Brunnen zurück zum Prisoners' Quarters.",
            "Auf 5 BC ist der Brunnen gesperrt – es geht weiter ins Astrolab.",
            "Ab dem ersten Erreichen: Derelict Distillery als Stufe-6-Alternative und Goldtruhen zur Bank."])

biome(id="lighthouse", name="Lighthouse", kind="boss", stage=10, depth=None, dlc=TQATS, minBC=0, difficulty=4,
      description="Leuchtturm, den du unter Verfolgung der drei Servants hinaufkletterst; gekämpft wird unterwegs und in Arenen.",
      exits=[ex("the-crown")],
      tips=["Zwischen Servants und Queen liegt nur noch eine Passage – kein Biom mehr zum Aufrüsten, also gut ausgerüstet hineingehen.",
            "An einem Seilzug hängend bist du unverwundbar.",
            "Unter 5 Minuten besiegt → Delayed Hedgehog Outfit."])

biome(id="masters-keep", name="Master's Keep", kind="boss", stage=10, depth=None, dlc=RTC, minBC=0, difficulty=5,
      description="Draculas Turm – Finale der Castlevania-Route mit Dracula und seiner Final Form.",
      exits=[],
      tips=["Zugang über Dracula's Castle (spät) mit Petrified Key, nach dem ersten Sieg auch direkt aus High Peak Castle.",
            "Zwei Kämpfe ohne Pause – Flask-Ladungen für die Final Form aufheben.",
            "Erst Dracula - Final Form zählt für die Boss Cells."])

biome(id="astrolab", name="Astrolab", kind="secret", stage=11, depth=7, dlc=ROTG, minBC=5, difficulty=5,
      description="Sternwarte über dem Throne Room, nur auf 5 BC erreichbar: extrem hohe Gegnerstufen und eine Schlüsseljagd über mehrere Elitegegner.",
      exits=[ex("observatory", minBC=5, condition="Zwei Guardian's Keys nötig (von zwei Elite Slammern), vorher Elevator Key und Allen Key.")],
      fixedElites="Elite Failed Experiment (Elevator Key), Elite Slammer (Allen Key), zwei Elite Slammer (Guardian's Keys)",
      tips=["Reihenfolge: Elite Failed Experiment (Elevator Key) und Elite Slammer (Allen Key), dann zwei Elite Slammer für die Guardian's Keys.",
            "Apex Key am Ende eines Hindernisparcours → Sonic Carbine-Entwurf.",
            "Food Shop vorhanden – auf 5 BC gibt es dort Cough Syrup gegen die Malaise.",
            "Magistrates of Death beschwören Screaming Skulls mit großer vertikaler Reichweite."])

biome(id="the-crown", name="The Crown", kind="boss", stage=11, depth=None, dlc=TQATS, minBC=0, difficulty=5,
      description="Spitze des Leuchtturms – Duell mit der Queen.",
      exits=[],
      tips=["Ab 3 BC gibt es nach dem Lighthouse eine der drei Flask-Aufladungen.",
            "Ausrüstung auf ihre Konter abstimmen (Feuer/Öl/Gift, Begleiter, häufiges Parieren)."])

biome(id="observatory", name="Observatory", kind="boss", stage=12, depth=None, dlc=ROTG, minBC=5, difficulty=5,
      description="Kuppel des Observatoriums: Der Collector entpuppt sich als Alchemist und wird zum wahren Endboss auf 5 BC.",
      exits=[],
      tips=["Der Collector nimmt dir vor dem Kampf Zellen und Gold ab – gold- oder zellenbasierte Items sind hier schwach.",
            "Crusher und Wolf Trap kontrollieren ihn gut.",
            "Mehrphasiger Kampf über mehrere Räume; in der Endphase haben die Wände Stacheln."])

BIOME_IMAGE_FALLBACK = {}  # id -> Dateiname, falls Infobox-Bild fehlt

# ---------------------------------------------------------------------------
# CURATED: Bosse
# ---------------------------------------------------------------------------
BOSSES = [
    dict(id="concierge", name="The Concierge", wiki="The Concierge", biome="black-bridge", dlc=None, minBC=0, tier=1,
         description="Riesiger, brennender Wärter auf der Black Bridge und der klassische erste Boss: langsam, aber mit großer Reichweite und Flächenschaden.",
         tips=["Stab und Leap haben lange, gut sichtbare Ausholbewegungen – beide lassen sich parieren und betäuben ihn kurz.",
               "Über die Feuerwelle (Fire strike) springen oder sie blocken; Rollen hilft nicht.",
               "Nah dranbleiben: In Nahkampfreichweite bevorzugt er den Stich, auf Abstand wirft er die Aura of Laceration an.",
               "Wolf Trap (ideal mit Heart of Ice) hält ihn lange fest; Fernkampf trifft auch während der Aura."],
         dangers=["Aura of Laceration: kurze Vorwarnung (rote Partikel), mehrfacher Schaden bei Kontakt",
                  "Leap in späteren Phasen mit aktiver Aura – Ducken oder Parieren schützt dann nicht vollständig",
                  "Shout beim Phasenwechsel: weder blockbar noch parierbar, nur Abstand hilft"],
         rewards="Challenger's Rune (1. Sieg); Entwürfe: Flint (1.), Heavy Crossbow (3.), Impaler (4.), Melee (5.), Ammo (6.), Alienation (7. Sieg); Concierge-Outfits je BC-Stufe und für einen makellosen Sieg."),
    dict(id="conjunctivius", name="Conjunctivius", wiki="Conjunctivius", biome="insufferable-crypt", dlc=None, minBC=0, tier=1,
         description="Angekettetes Augen-Ungetüm, das durch die Gruft schwebt und Tentakel aus dem Boden schickt. Erreichbar über die Ancient Sewers (Ram Rune) oder ab 3 BC über die Ramparts.",
         tips=["Body slam wird durch eine rote Linie angekündigt: an die Wand stellen, Wolf Trap legen, zur Wand rollen – sie bleibt in der Falle hängen.",
               "Magische Geschosse lassen sich parieren und zurückschicken; zum Ausweichen am Arenarand gegen die Wand rollen.",
               "Tentakel mit Fallen oder Frost fixieren; die Area Sweep kommt immer von der weiter entfernten Wand.",
               "Ab 1 BC beginnt der Kampf direkt in Phase 2."],
         dangers=["Rain of bolts (viele Geschosse gleichzeitig)", "Area Sweep der Tentakel quer durch die Arena", "Aura of Laceration bei Nahkontakt"],
         rewards="Entwürfe: Tentacle (1.), Cursed Sword (3.), Gastronomy (4.), Recovery (5.), Advanced Forge I (6. Sieg); Conjunctivius-Outfits."),
    dict(id="mama-tick", name="Mama Tick", wiki="Mama Tick", biome="nest", dlc=TBS, minBC=0, tier=1,
         description="Gigantische Zecke, die halb im Wasser des Nests verborgen kämpft und zwischen sichtbaren und abgetauchten Phasen wechselt.",
         tips=["Das Wasser macht sie anfällig: Frost und Verlangsamung wirken stark, Schock-Schaden und Ice Shards treffen immer kritisch.",
               "Feuer ist nutzlos – sie ist immun gegen Brand und brennendes Öl.",
               "Bei den Quick stabs an eine Arenawand stellen und nur bei nahen Stichen zur Wand rollen.",
               "Die Spit bombs landen weit von ihr entfernt – nah bei ihr bist du sicher."],
         dangers=["Slasher: schnelle Klauenserie über drei Viertel der Arena", "Lightspeed claws (gelbe Linien als Vorwarnung)", "Quick stabs an zufälligen Stellen"],
         rewards="Entwurf Scythe Claw (1. Sieg); Giant-Tick-Outfits (je BC-Stufe, makelloser Sieg, Opfern des Mushroom Boi!)."),
    dict(id="death", name="Death", wiki="Death", biome="defiled-necropolis", dlc=RTC, minBC=0, tier=1,
         description="Der Tod persönlich als erster Boss der Castlevania-Route; schwebt zwischen den Plattformen und sammelt Seelen für eine Hinrichtung.",
         tips=["Sensen-Angriffe erzeugen Seelen, die Death einsammelt; bei sechs Seelen folgt die Execution – Sensentreffer konsequent vermeiden.",
               "Die kleinen Sensen (Deathscythe) lassen sich mit Nahkampfangriffen zerstören.",
               "Sprungangriffe durch seinen Kopf richten viel Schaden an und unterbrechen ihn.",
               "Disengagement oder Ygdar Orus Li Ox lassen dich die Hinrichtung überleben.",
               "Ab 1 BC beginnt er direkt in Phase 2."],
         dangers=["Execution: 85 % der max. HP, ignoriert den One-Shot-Schutz", "Scythe flurry mit anschließendem Sensenwurf", "Spirit wave (per Rolle ausweichen; parierbar nur mit Cocoon)"],
         rewards="Entwurf Death's Scythe (1. Sieg); Death-Outfits; schaltet in späteren Läufen Dracula's Castle (spät) über den Clock Room und damit den Weg zu Dracula frei."),
    dict(id="time-keeper", name="The Time Keeper", wiki="The Time Keeper", biome="clock-room", dlc=None, minBC=0, tier=2,
         description="Schnelle Schwertkämpferin im Uhrturm mit Kombos, Shuriken und Kettenhaken, die über drei Phasen immer aggressiver wird.",
         tips=["Fast alle Angriffe sind parierbar – Schilde wie Ice Shield, Rampart oder Punishment machen den Kampf deutlich leichter.",
               "Parierte Shuriken fliegen mit hohem Schaden zurück; beim Springen zielt sie nach.",
               "Nach einem Teleport folgt immer ein Fernangriff (Haken, Shuriken, Lightspeed).",
               "Frost, Wurzeln und Verlangsamung wirken, werden bei Wiederholung aber kürzer."],
         dangers=["Sword Rain (Masochist senkt den Schaden)", "Hook and slash: Haken fesselt dich, dann folgt ein Hieb", "Lightspeed-Dash über die ganze Arena"],
         rewards="Entwürfe: Lightspeed (1.), Ice Shards (3.), Ice Crossbow (4.), Velocity (5.), Tainted Flask (6.), Emergency Triage (7. Sieg); Temporal-Outfits."),
    dict(id="giant", name="The Giant", wiki="The Giant", biome="guardians-haven", dlc=ROTG, minBC=0, tier=2,
         description="Der riesige Torwächter der Burg; kämpft mit zwei Fäusten in einer Lavaarena und ist nur an den Augen verwundbar.",
         tips=["Erst die Fäuste zerstören: Fällt eine, springt das Auge auf dieser Seite für etwa 3 Sekunden heraus und ist verwundbar.",
               "Den Punch am besten parieren – Blocken schiebt dich in die Lava.",
               "Bei den Augenlasern sofort in die Arenamitte; dort lässt sich auch die Energy salvo gut handhaben.",
               "Giantkiller trifft alle Teile kritisch; Kontrolleffekte wirken an den Händen nicht."],
         dangers=["Aufgeladene Faustangriffe", "Crystal collapse (fallende Kristalle, nicht parierbar)", "Lava am Arenarand"],
         rewards="Entwürfe: Giantkiller (1.), Giant Whistle (3. Sieg); auf 4 BC die 5. Boss Cell; Giant-Outfits; nach dem ersten Sieg öffnen sich die 2-BC-Wege Slumbering Sanctuary → Cavern und Forgotten Sepulcher → Guardian's Haven."),
    dict(id="scarecrow", name="The Scarecrow", wiki="The Scarecrow", biome="mausoleum", dlc=FF, minBC=0, tier=2,
         description="Vogelscheuche auf dem Mausoleumsdach, die mit Sense, Schaufel, Sicheln und explosiven Pilzen kämpft.",
         tips=["Sensenschwünge parieren oder abwechselnd weg- und durch ihn hindurchrollen.",
               "Pilze aus Seed planting früh auslösen und Abstand halten – nach der Schaufelattacke fliegen sie dir entgegen.",
               "Bei der Shovel swing hinter ihn rollen, sobald er auftaucht – gute Konterchance.",
               "Während Acid rain nicht angreifen, sondern ruhig ausweichen; er bewegt sich in der Luft langsam."],
         dangers=["Acid rain (hoher Schaden)", "Flying sickles, die zu ihm zurückkehren", "Phase 2 ab 50 %: schneller, Pitchfork jab erzeugt Jerkshrooms"],
         rewards="Entwurf Scarecrow's Sickles (1. Sieg); Scarecrow-Outfits."),
    dict(id="hand-of-the-king", name="The Hand of the King", wiki="The Hand of the King", biome="throne-room", dlc=None, minBC=0, tier=3,
         description="Leibwächter des Königs und Endboss der Hauptroute: schwerer Lanzenkämpfer mit Granaten, Bodenstößen und beschworenem Gefolge.",
         tips=["Viel in der Luft bleiben: Springen und Rollen weicht vielen Bodenangriffen und Kombos aus.",
               "Seine Granatensalve mit Shovel, Flashing Fans, Wave of Denial, Magnetic Grenade oder Tornado zurückwerfen.",
               "Die enge Arena begünstigt Flächenschaden: Feuer/Öl, Blutung, Giftwolken.",
               "Rampart oder Parieren gegen die Zwei- und Dreifachkombos; den Super Telluric Shock auf der Eisplattform aussitzen.",
               "Sein Frontschild schwächt Projektile ab, solange er nicht angreift."],
         dangers=["Super Telluric Shock", "Zwei- und Dreifach-Hiebkombos", "Beschworene Gegner (teils Elite)"],
         rewards="Entwürfe Symmetrical Lance und Telluric Shock (1. Sieg), Recycling Tubes (1. Sieg auf 1 BC); Homunculus Rune (1. Sieg); 1. bis 4. Boss Cell; Outfits."),
    dict(id="servants", name="The Servants", wiki="The Servants", biome="lighthouse", dlc=TQATS, minBC=0, tier=3,
         description="Die drei Dienerinnen der Königin – Calliope (Abrissbirnen), Euterpe (Bogen) und Kleio (Tonfas) – jagen dich den Leuchtturm hinauf und stellen sich dann in Arenen.",
         tips=["Beim Aufstieg in Bewegung bleiben; nach 30 % Schaden zieht sich eine Dienerin in die nächste Arena zurück (der Schaden bleibt).",
               "An einem Seilzug hängend bist du unverwundbar – nützlich gegen Euterpe.",
               "Ihr Schadenslimit pro Treffer liegt bei 40 % der max. HP: schwere, langsame Waffen sind sehr effektiv.",
               "Geschütze wie Great Owl of War schießen auch während des Aufstiegs weiter."],
         dangers=["Euterpes Pfeile (teils durch Wände und Böden)", "Calliopes Würfe von oben und schräg", "Feuer im Leuchtturm"],
         rewards="Entwürfe: Wrecking Ball, Gilded Yumi, Bladed Tonfas; Servant-Outfits; Delayed Hedgehog Outfit bei einem Sieg unter 5 Minuten."),
    dict(id="dracula", name="Dracula", wiki="Dracula", biome="masters-keep", dlc=RTC, minBC=0, tier=3,
         description="Der Schlossherr aus Castlevania; teleportiert sich durch die Arena und verwandelt sich nach seiner Niederlage in Dracula - Final Form.",
         tips=["Nach jedem Teleport startet sofort ein Angriff – auf das Wiedererscheinen achten.",
               "Soul Steal (Sturzflug-Griff ab Phase 2) unbedingt wegrollen: Er heilt sich dabei.",
               "Fire pillars (Phase 3) lassen sich nicht durchrollen – auf die glühenden Bodenstellen achten.",
               "Ab 1 BC beginnt er direkt in Phase 2."],
         dangers=["Soul Steal (Schaden und Selbstheilung)", "Fire pillars", "Bat volley beim Phasenwechsel"],
         rewards="Direkt keine Entwürfe; der Kampf geht nahtlos in Dracula - Final Form über."),
    dict(id="dracula-final-form", name="Dracula - Final Form", wiki="Dracula - Final Form", biome="masters-keep", dlc=RTC, minBC=0, tier=3,
         description="Zweite Hälfte des Dracula-Kampfs: ein riesiges Monster, das Plattformen zerstört und die Arena mit Lasern, Meteoren und Fledermäusen füllt.",
         tips=["Laser breath combo: zwei Schwenks über die Arena, dann ein gezielter, besonders gefährlicher Strahl – rechtzeitig rollen oder springen.",
               "Beim Big meteor über die entstehende Treppe nach oben ausweichen, bis die neue Mittelplattform erscheint.",
               "Fledermauswellen (Summon bats) erreichen dich auf der Mittelplattform nicht.",
               "Flask-Ladungen aus dem ersten Kampfteil hierfür aufsparen."],
         dangers=["Laser breath combo", "Side swipe zerstört Plattformen", "Big meteor im Phasenübergang"],
         rewards="Entwurf Vampire Killer (1. Sieg); 1. bis 4. Boss Cell; Dracula-Outfits; nach dem ersten Sieg zusätzliche Castlevania-Übergänge (z. B. Toxic Sewers → Dracula's Castle, High Peak Castle → Master's Keep)."),
    dict(id="queen", name="The Queen", wiki="The Queen", biome="the-crown", dlc=TQATS, minBC=0, tier=4,
         description="Die Königin der Insel: extrem schnelle Fechterin mit Rapier, Feuerangriffen und Konterattacken – Endboss der Queen-and-the-Sea-Route.",
         tips=["Normale Kombos: von ihr weglaufen und im Moment des Angriffs rollen, oder gezielt parieren.",
               "Sie kontert deine Ausrüstung: Feuer, Öl oder Giftwolken vor ihr lösen einen Fire Tornado aus, zu häufiges Parieren den Down-Strike.",
               "Wird sie zu wenig getroffen, zu oft pariert oder unterbrochen, gerät sie in Rage – dann nur noch ausweichen.",
               "Reality Slashes sind die beste Schadensphase; dabei sparsam bewegen, sonst geht der Platz aus."],
         dangers=["Grab and Throw (nicht parierbar, wirkt durch Schutzschilde)", "Down-Strike ignoriert Schilde", "Fire Aura (weder roll- noch parierbar)"],
         rewards="Entwurf Queen's Rapier (1. Sieg); 1. bis 4. Boss Cell; Queen-Outfits."),
    dict(id="collector", name="The Collector", wiki="The Collector/5 BSC", biome="observatory", dlc=ROTG, minBC=5, tier=4,
         description="Der Sammler offenbart sich als Alchemist, trinkt sein Panacea und wird auf 5 BC zum wahren Endboss; der Kampf läuft über mehrere Phasen und Räume.",
         tips=["Crusher verlangsamt ihn stark und unterbricht Angriffe wie den Tornado; Wolf Trap fixiert ihn.",
               "Spritzen-Ausfall, Bodenstampfer und Bomben weichst du an der Wand hängend (Spider Rune) aus – nicht in der Endphase, dort haben die Wände Stacheln.",
               "Doppeltornado: durch jede Säule rollen, dann wegspringen.",
               "Strahlangriff: kaum sichtbar, auf das Tonsignal achten und beim gelben Hinweis rollen."],
         dangers=["Strahlangriff (schnell, massiver Schaden)", "Doppeltornado", "Nimmt dir zu Kampfbeginn Zellen und Gold ab und heilt sich mit dem Panacea"],
         rewards="Entwurf Collector's Syringe (1. Sieg), Fallen Collector Outfit (2. Sieg), King- und White-King-Outfit unter Sonderbedingungen; wahres Ende des Spiels."),
]

# ---------------------------------------------------------------------------
# CURATED: Runen
# ---------------------------------------------------------------------------
RUNES = [
    dict(id="vine-rune", name="Vine Rune", icon="Vine Rune Icon.png", where="promenade-of-the-condemned", guardian="Undead Archer",
         effect="Lässt an markierten Stellen Kletterranken wachsen.",
         how="Elite Undead Archer in einer Halle unter einer Überführung der Promenade besiegen; die Rune droppt.",
         unlocks=["toxic-sewers", "ramparts"]),
    dict(id="teleportation-rune", name="Teleportation Rune", icon="Teleportation Rune Icon.png", where="toxic-sewers", guardian="Slasher",
         effect="Erlaubt die Nutzung von Teleportationsmonolithen.",
         how="Elite Slasher in einem Sonderraum der Toxic Sewers besiegen.",
         unlocks=["dilapidated-arboretum", "ossuary", "morass-of-the-banished", "forgotten-sepulcher"]),
    dict(id="ram-rune", name="Ram Rune", icon="Ram Rune Icon.png", where="ossuary", guardian="Slasher",
         effect="Durchbricht markierte Böden mit einem Sturzangriff (verstärkt außerdem lange Sturzangriffe).",
         how="Elite Slasher in einem Sonderraum der Ossuary besiegen.",
         unlocks=["ancient-sewers"]),
    dict(id="spider-rune", name="Spider Rune", icon="Spider Rune Icon.png", where="slumbering-sanctuary", guardian="Caster",
         effect="Erlaubt das Festhalten und Klettern an Wänden.",
         how="Elite Caster im Slumbering Sanctuary besiegen. Ohne Spider Rune erreichst du das Sanctuary über Ancient Sewers → Insufferable Crypt (Ram Rune), ab 3 BC über Ramparts → Crypt oder über die Defiled Necropolis (Return to Castlevania).",
         unlocks=["prison-depths", "corrupted-prison", "slumbering-sanctuary", "graveyard"]),
    dict(id="challengers-rune", name="Challenger's Rune", icon="Challenger Rune Icon.png", where="black-bridge", guardian="The Concierge",
         effect="Schaltet den Daily Run (tägliche Herausforderung) im Prisoners' Quarters frei.",
         how="The Concierge auf der Black Bridge zum ersten Mal besiegen.",
         unlocks=["daily-run"]),
    dict(id="customization-rune", name="Customization Rune", icon="Customization Rune Icon.png", where="ramparts", guardian="Zombie",
         effect="Schaltet den Custom Mode frei.",
         how="Einzigartigen Elite Zombie in einem Raum nahe dem Eingang der Ramparts besiegen (Runen-Übersicht nennt alternativ einen Undead Archer).",
         unlocks=["custom-mode"]),
    dict(id="explorers-rune", name="Explorer's Rune", icon="Explorer's Rune Icon.png", where="forgotten-sepulcher", guardian="Dark Tracker",
         effect="Deckt die ganze Karte samt Schriftrollen, Händlern usw. auf, sobald etwa 80 % eines Bioms erkundet sind.",
         how="Am Ende des Forgotten Sepulcher zwei Elite Dark Trackers besiegen; ihre Crypt Keys öffnen den Raum mit der Rune.",
         unlocks=[]),
    dict(id="homunculus-rune", name="Homunculus Rune", icon="Homunculus Rune Icon.png", where="throne-room", guardian="The Hand of the King",
         effect="Löst den Kopf vom Körper: Er kann Gegner anspringen und schädigen, Items und Pickups heranholen und unbegrenzt Wände hochklettern (nicht unter Fluch).",
         how="Wird automatisch nach dem ersten Sieg über The Hand of the King verliehen.",
         unlocks=["cavern"]),
]

# ---------------------------------------------------------------------------
# CURATED: Boss-Cell-Stufen
# ---------------------------------------------------------------------------
BOSS_CELLS = [
    dict(bc=0, title="Normal",
         howToGet="Ausgangszustand jedes Spielstands.",
         changes=["Jede Passage enthält einen Gesundheitsbrunnen, der Leben und alle Flask-Ladungen auffüllt.",
                  "Keine BC-Türen, keine Scroll Fragments, keine Malaise.",
                  "Zeittür-Altäre mit mindestens '+'-Qualität."],
         tips=["Auf 0 BC alle Runen einsammeln (Vine → Teleportation → Ram → Spider), damit spätere Routen offen sind.",
               "Hand of the King, Queen oder Dracula - Final Form besiegen, um die erste Boss Cell zu erhalten."]),
    dict(bc=1, title="Hard",
         howToGet="Hand of the King, The Queen oder Dracula - Final Form mit 0 aktiven Boss Cells besiegen (ohne Aspekt).",
         changes=["Gesundheitsbrunnen nur noch in jeder zweiten Passage; in den übrigen liegt stattdessen eine Flask-Aufladung.",
                  "Bosse ändern ihre frühen Phasen; u. a. Conjunctivius, Death, Scarecrow und Dracula beginnen direkt in Phase 2.",
                  "1-BC-Türen: zusätzliche Shops und Truhen sowie die Wege Prison Depths → Ancient Sewers und Corrupted Prison → Ramparts.",
                  "+1 Schriftrolle der Macht in den Stufe-2-Biomen; Food Shop hinter der 1-BC-Tür in der Ossuary.",
                  "Neue Gegner, z. B. Rancid Rats und Knife Throwers im Prisoners' Quarters, Kamikazes in der Promenade.",
                  "Legendary Forge: ++-Häufigkeit bis 100 % steigerbar; Recycling Tubes-Entwurf beim ersten 1-BC-Sieg über die Hand of the King."],
         tips=["Flask-Ladungen sparsamer einsetzen – nicht jede Passage heilt mehr voll.",
               "Die neuen 1-BC-Türen lohnen sich fast immer (Truhen, Shops)."]),
    dict(bc=2, title="Very Hard",
         howToGet="Einen der BC-Bosse (Hand of the King, The Queen, Dracula - Final Form) mit 1 aktiven Boss Cell besiegen.",
         changes=["Keine Gesundheitsbrunnen mehr; jede Passage enthält nur noch eine Flask-Aufladung.",
                  "Gegner lassen mehr Zellen fallen (Wiki: ×2).",
                  "2-BC-Türen, u. a. Food Shops (Ramparts, Morass, Graveyard, Dracula's Castle) sowie Slumbering Sanctuary → Cavern und Forgotten Sepulcher → Guardian's Haven (nach Giant-Sieg).",
                  "+1 Schriftrolle der Macht in den Stufe-3-Biomen.",
                  "Weitere Gegner wie Oven Knights, Dark Trackers und Bombers in frühen Biomen.",
                  "Legendary Forge: S-Häufigkeit bis 25 %; Zeittür-Altäre mit mindestens '++'-Qualität."],
         tips=["Heilung kommt jetzt hauptsächlich aus Essen und Flask-Aufladungen – Food Shops einplanen.",
               "Survival-Punkte oder Heil-Mutationen werden wichtiger."]),
    dict(bc=3, title="Expert",
         howToGet="Einen der BC-Bosse mit 2 aktiven Boss Cells besiegen.",
         changes=["Nur noch drei Flask-Aufladungen pro Lauf: nach dem ersten Boss, vor dem zweiten Boss und nach dem Lighthouse.",
                  "Scroll Fragments erscheinen (4 Fragmente = +1 Wertpunkt), dazu 3 zufällig verteilte Fragmente pro Lauf.",
                  "Item-Level +1; farblose Items aus verfluchten Truhen erhalten S-Qualität.",
                  "3-BC-Tür in den Ramparts zur Insufferable Crypt; +1 Schriftrolle der Macht in Stufe-4-Biomen.",
                  "Rampagers in vielen Biomen.",
                  "Legendary Forge: S-Häufigkeit bis 50 %."],
         tips=["Route über Biome mit vielen Fragmenten planen (z. B. Ancient Sewers, Cavern).",
               "Die Flask-Aufladung nach dem ersten Boss bewusst einplanen – danach gibt es lange keine."]),
    dict(bc=4, title="Nightmare",
         howToGet="Einen der BC-Bosse mit 3 aktiven Boss Cells besiegen.",
         changes=["Keine Flask-Aufladungen mehr in den Passagen.",
                  "Gegner haben größere Erkennungsreichweite und teleportieren sich zu dir.",
                  "Mehr Scroll Fragments; Item-Level +3; Zellen-Drops weiter erhöht (Wiki: ×3).",
                  "Failed Experiments ersetzen in vielen Biomen andere Gegner; Demons auch außerhalb der Cavern.",
                  "+1 Schriftrolle der Macht in Stufe-5-Biomen; 4-BC-Türen (u. a. Festive Outfit in der Cavern).",
                  "Zeittür-Altäre mit S-Qualität; Legendary Forge: S-Häufigkeit bis 100 %.",
                  "The Giant gibt auf dieser Stufe die 5. Boss Cell."],
         tips=["Heilung nur noch über Essen, Mutationen und Item-Effekte – Gold für Food Shops sparen.",
               "Für die 5. BC muss der Giant auf 4 BC besiegt werden (Route über Cavern oder Forgotten Sepulcher → Guardian's Haven)."]),
    dict(bc=5, title="Hell",
         howToGet="The Giant mit 4 aktiven Boss Cells besiegen (ohne Aspekt).",
         changes=["Die Malaise ist aktiv: Ein Infektionsbalken steigt mit der Zeit, stärkt Gegner und sinkt durch Kills, Flask oder Cough Syrup.",
                  "Gefundenes Essen ist teils infiziert; Food Shops verkaufen Cough Syrup statt kleiner Mahlzeit.",
                  "Der Collector wird in den Passagen durch seinen Assistenten (The Collector's Intern) ersetzt.",
                  "Der Brunnen-Ausgang im Throne Room ist gesperrt; stattdessen geht es ins Astrolab und zum Observatory (Collector-Bosskampf).",
                  "Alle Effekte von 4 BC bleiben (keine Flask-Aufladungen, teleportierende Gegner, Item-Level +3)."],
         tips=["Biome zügig räumen: Bei 90 % besiegter Gegner endet der Malaise-Anstieg im Biom.",
               "Im Astrolab den Food Shop für Cough Syrup nutzen.",
               "Ein Kill-starker Build (Flächenschaden) hält die Malaise niedrig."]),
]

TIMED_REWARD = "Gold/Edelsteine, 20 Zellen und ein Altar mit 3 Items (bzw. 2 Items + Amulett)"
TIMED_DOORS = [
    dict(biome="prisoners-quarters", to=["promenade-of-the-condemned"], minutes=2, reward=TIMED_REWARD + "; zusätzlich Assault Shield-Entwurf."),
    dict(biome="prisoners-quarters", to=["toxic-sewers"], minutes=2, reward=TIMED_REWARD + "; zusätzlich Frenzy-Entwurf."),
    dict(biome="prisoners-quarters", to=["dilapidated-arboretum", "castles-outskirts"], minutes=2, reward=TIMED_REWARD + "."),
    dict(biome="promenade-of-the-condemned", to=["ramparts"], minutes=8, reward=TIMED_REWARD + "."),
    dict(biome="toxic-sewers", to=["ramparts"], minutes=8, reward=TIMED_REWARD + "."),
    dict(biome="dilapidated-arboretum", to=["ramparts"], minutes=8, reward=TIMED_REWARD + "."),
    dict(biome="promenade-of-the-condemned", to=["ossuary"], minutes=8, reward=TIMED_REWARD + "; zusätzlich Marksman's Bow-Entwurf (nur beim Weg aus der Promenade)."),
    dict(biome="castles-outskirts", to=["draculas-castle-early"], minutes=8, reward=TIMED_REWARD + "."),
    dict(biome="black-bridge", to=["stilt-village", "slumbering-sanctuary", "fractured-shrines"], minutes=15, reward=TIMED_REWARD + "; zusätzlich Root Grenade-Entwurf."),
    dict(biome="nest", to=["stilt-village", "fractured-shrines", "graveyard"], minutes=15, reward=TIMED_REWARD + "."),
    dict(biome="defiled-necropolis", to=["slumbering-sanctuary", "stilt-village", "graveyard"], minutes=15, reward=TIMED_REWARD + ".",
         notes="Nur in Übersichtsseiten des Wikis genannt, nicht in der Zeittür-Tabelle – unsicher."),
    dict(biome="insufferable-crypt", to=["graveyard"], minutes=19.5, reward=TIMED_REWARD + "."),
    dict(biome="slumbering-sanctuary", to=["clock-tower", "forgotten-sepulcher"], minutes=26, reward=TIMED_REWARD + ".",
         notes="Wiki: 'nach dem Slumbering Sanctuary' bzw. 'vor dem Forgotten Sepulcher' – genaue Übergänge nicht eindeutig."),
    dict(biome="stilt-village", to=["forgotten-sepulcher"], minutes=26, reward=TIMED_REWARD + ".", notes="Wiki: 'vor dem Forgotten Sepulcher' – Herkunft nicht eindeutig."),
    dict(biome="graveyard", to=["forgotten-sepulcher"], minutes=26, reward=TIMED_REWARD + ".", notes="Wiki: 'vor dem Forgotten Sepulcher' – Herkunft nicht eindeutig."),
    dict(biome="fractured-shrines", to=["forgotten-sepulcher"], minutes=26, reward=TIMED_REWARD + ".", notes="Wiki: 'vor dem Forgotten Sepulcher' – Herkunft nicht eindeutig."),
]

OTHER_AREAS = [
    dict(id="the-bank", name="The Bank", wiki="The Bank", image_file="The Bank.png",
         description="Goldthemen-Biom mit Taschendieben, Gold Gorgers, Golden Kamikazes und Mimics; drei Stockwerke werden mit farbigen Pässen (rot, blau, grün) geöffnet. Gegner, Item-Level und Schriftrollen richten sich nach dem ersetzten Biom (eine Schriftrolle weniger als das beste ersetzte Biom, dafür eine verfluchte Truhe).",
         how="Nachdem Throne Room, The Crown oder Master's Keep einmal erreicht wurden, kann in einer Passage vor einem Nicht-Boss-Biom eine goldene Truhe stehen. Hineinspringen ersetzt das nächste Biom durch die Bank; ignoriert man sie, erscheint sie in diesem Lauf nicht mehr."),
    dict(id="passage", name="Passage", wiki="Passage", image_file="Passage.png",
         description="Übergangsbereich zwischen zwei Biomen mit Collector (bei Castlevania-Biomen Shanoa, auf 5 BC der Assistent), Schmied-Lehrling, Guillain (Mutationen) und je nach BC-Stufe Gesundheitsbrunnen oder Flask-Aufladung; dazu Zeit-, Killstreak- und nach Bossen No-Hit-Türen.",
         how="Automatisch nach jedem Biom."),
    dict(id="challenge-rift", name="Challenge Rift", wiki="Challenge Rift", image_file="Challenge Rift 1.png",
         description="Optionale Fallen-Parcours hinter einem ovalen Bodensymbol. Die Truhe am Anfang enthält Crow's Foot-Entwurf, eine Schriftrolle der Macht, ein Amulett und Zellen; danach schließt sich der Ausgang und der Parcours muss bewältigt werden.",
         how="20 % Chance pro Nicht-Boss-Biom; Bodensymbol (oval, im Gegensatz zu Wandrunen) anspielen."),
    dict(id="daily-run", name="Daily Run", wiki="Daily Run", image_file=None,
         description="Tägliche Herausforderung mit fester Karte und Bestenliste; ein Lauf dauert begrenzte Zeit und endet mit einem Boss. Abschlüsse belohnen mit Swift Sword (1.), Lacerating Aura (5.) und Meat Skewer (10.).",
         how="Challenger's Rune (Concierge) erhalten; Tür neben dem Scribe im Prisoners' Quarters."),
    dict(id="custom-mode", name="Custom Mode", wiki="Custom Mode", image_file=None,
         description="Frei konfigurierbarer Spielmodus: Item-/Mutationspools, Startausrüstung, Flask-Ladungen, Malaise, Timer usw. Manche Optionen deaktivieren Erfolge.",
         how="Customization Rune in den Ramparts erhalten; Auswahl im Hauptmenü."),
    dict(id="training-room", name="Training Room", wiki="Training Room", image_file=None,
         description="Übungsraum, in dem du beliebige freigeschaltete Waffen/Skills testen und gegen Gegner sowie Bosse trainieren kannst (z. B. die dritte Servants-Arena).",
         how="Schlüssel von der Leiche des Tutorial Knight (ab dem vierten Lauf) nehmen; Tür im Startbereich des Prisoners' Quarters."),
    dict(id="boss-rush", name="Boss Rush", wiki="Boss Rush", image_file=None,
         description="Spielmodus mit Bosskämpfen am Stück und vorgegebenen Builds; vier Prüfungen, seit 3.4 auch mit Castlevania-Bossen und eigener Konfiguration.",
         how="Mindestens drei Bosse (je einen der Stufen 1, 2 und 3) besiegt haben; Zugang im Startbereich des Prisoners' Quarters. Prüfung 3 und 4 benötigen fünf besiegte Bosse."),
    dict(id="richter-mode", name="Richter Mode", wiki="Richter Mode", image_file=None,
         description="Castlevania-Sondermodus mit Richter als Spielfigur auf einer festen Karte; Dash und High Jump werden unterwegs auf Sockeln gefunden, Endgegnerin ist Medusa.",
         how="Richter in Dracula's Castle (Ebene 6) aus seinem Käfig befreien; in einem späteren Lauf über den Käfig starten (einmal pro Lauf)."),
    dict(id="specialists-showroom", name="Specialist's Showroom", wiki="Prisoners' Quarters", image_file=None,
         description="Sonderladen im Prisoners' Quarters mit Hunter's Grenade, Forgotten Map und Golden Outfit-Entwurf hinter goldenen Türen.",
         how="Für 150 Zellen beim Collector freischalten (nach 20 Freischaltungen)."),
    dict(id="lore-rooms", name="Lore Rooms", wiki="Lore", image_file=None,
         description="Kleine Räume mit Hintergrundgeschichte der Insel; teils mit Nahrung, Zellen oder Entwürfen (z. B. Gardener's Outfit im Arboretum, Simon Outfit in Dracula's Castle, Abyssal Trident im Shipwreck).",
         how="Zufällig in vielen Biomen; manche brauchen Schlüssel oder Runen."),
    dict(id="repository-of-the-architects", name="Repository of the Architects", wiki="Repository of the Architects", image_file=None,
         description="Ungenutztes, im Spiel nicht erreichbares Biom (Prototyp des Forgotten Sepulcher) hinter einer früheren 5-BC-Tür im Graveyard.",
         how="Nicht regulär zugänglich (nur über Fremdtools)."),
]


# ---------------------------------------------------------------------------
# Bilder
# ---------------------------------------------------------------------------

def fetch_image(filenames, dest, max_bytes=400_000, max_w=960, upscale_small=False):
    """Lädt die erste verfügbare Wiki-Datei nach dest (PNG); verkleinert >400 KB auf max. 960 px Breite."""
    from PIL import Image
    IMGCACHE.mkdir(parents=True, exist_ok=True)
    for fn in [f for f in filenames if f]:
        info = wikiapi.imageurl(CACHE, fn)
        if not info:
            continue
        raw_path = IMGCACHE / re.sub(r"[^A-Za-z0-9._-]+", "_", fn)
        if not raw_path.exists():
            raw_path.write_bytes(wikiapi.get(info["url"], binary=True))
        data = raw_path.read_bytes()
        dest.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(io.BytesIO(data))
        is_png = im.format == "PNG"
        if len(data) <= max_bytes and is_png:
            dest.write_bytes(data)
        else:
            if getattr(im, "n_frames", 1) > 1:
                im.seek(0)
            im = im.convert("RGBA") if im.mode in ("P", "LA", "RGBA") else im.convert("RGB")
            if im.width > max_w:
                im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "PNG", optimize=True)
            if buf.tell() > max_bytes and im.mode == "RGB":
                buf = io.BytesIO()
                im.quantize(colors=256, method=Image.Quantize.MEDIANCUT).save(buf, "PNG", optimize=True)
            dest.write_bytes(buf.getvalue())
        return fn
    return None


# ---------------------------------------------------------------------------
# Aufbau
# ---------------------------------------------------------------------------

def main():
    overview = parse_biomes_overview()
    biome_ids = {b["id"] for b in B}
    boss_by_biome = {}
    for bo in BOSSES:
        boss_by_biome.setdefault(bo["biome"], []).append(bo["id"])
    rune_by_biome = {r["where"]: r["name"] for r in RUNES}
    missing_images = []

    biomes_out = []
    newenemies = {k: [] for k in range(1, 5)}
    for b in B:
        title = b.get("wiki_title", b["name"])
        w = wikiapi.wikitext(CACHE, title) or ""
        ib = infobox(w, "BiomeInfobox")
        secs = overview.get(title, [])
        sec = secs[b.get("ov", 0)] if len(secs) > b.get("ov", 0) else ""
        ps = parse_section(sec)
        cursed_pct = pct(ib.get("cursed_chests_0") or ib.get("cursed_chest_0"))
        scrolls = scroll_info(ps["scrollLine"], cursed_pct)
        if b["id"].startswith("draculas-castle"):
            scrolls["cursedChest"] = True  # Biomseite: "guaranteed Cursed chest"
            scrolls["notes"] = ("+1 Schriftrolle der Macht in der garantierten verfluchten Truhe; "
                                + ("+1 Schriftrolle der Macht ab 2 BC; Scroll Fragments: 3 auf 3 BC / 4 auf 4–5 BC"
                                   if b["variant"] == "early" else
                                   "Bonus-Schriftrolle laut Biomseite nur in der frühen Variante (Infobox nennt 3 ab 2 BC – unsicher); Scroll Fragments: 1 auf 3 BC / 2 auf 4–5 BC"))
        if b["id"] == "guardians-haven":
            scrolls["notes"] = (scrolls["notes"] + "; " if scrolls["notes"] else "") + "Ausgang zum Throne Room gibt 2 Schriftrollen der Macht"
        if b["id"] == "high-peak-castle":
            scrolls["notes"] = (scrolls["notes"] + "; " if scrolls["notes"] else "") + "Dritter Castle Key öffnet einen Raum mit einer weiteren Schriftrolle der Macht"
        if b["id"] == "forgotten-sepulcher" and scrolls["power"] == 3:
            pass
        is_boss = b["kind"] == "boss"
        boss_names = {bo["name"] for bo in BOSSES} | {"Conjunctivius's Tentacles", "The Collector (5 BSC)", "The Collector"}
        notable = [] if is_boss else [n for n in ps["base"] if n not in boss_names]
        bc_en = [] if is_boss else [e for e in ps["bc"] if e["name"] not in boss_names]
        for e in bc_en:
            newenemies[e["fromBC"]].append((e["name"], b["id"]))
        # Elite-Info
        el = []
        we, er = pct(ib.get("wandering_elite")), pct(ib.get("elite_room"))
        if b.get("fixedElites"):
            el.append(b["fixedElites"])
        if we is not None:
            el.append(f"Wandernder Elitegegner: {we} %")
        if er is not None:
            el.append(f"Eliteraum: {er} %")
        td = b.get("timedDoor")
        image_file = ib.get("image") or f"{title}.png"
        img_rel = f"assets/biomes/{b['id']}.png"
        got = fetch_image([image_file, f"{title}.png", BIOME_IMAGE_FALLBACK.get(b["id"])], ROOT / img_rel)
        if not got:
            missing_images.append(img_rel); img_rel = None
        biomes_out.append({
            "id": b["id"], "name": b["name"], "nameDe": None, "kind": b["kind"],
            **({"variant": b["variant"]} if b.get("variant") else {}),
            **({"optional": True} if b.get("optional") else {}),
            "stage": b["stage"], "depth": b["depth"], "dlc": b["dlc"], "minBC": b["minBC"],
            "description": b["description"], "difficulty": b["difficulty"],
            "exits": b["exits"],
            "scrolls": scrolls,
            "timedDoor": td,
            "runeHere": rune_by_biome.get(b["id"]),
            "bosses": boss_by_biome.get(b["id"], []),
            "notableEnemies": notable,
            "bcEnemies": bc_en,
            "elite": " · ".join(el) or None,
            "tips": b["tips"],
            "wiki": wiki_url(title),
            "image": img_rel,
        })

    bosses_out = []
    stage_of = {b["id"]: b["stage"] for b in B}
    for bo in BOSSES:
        w = wikiapi.wikitext(CACHE, bo["wiki"]) or ""
        ib = infobox(w, "EnemyInfobox")
        img = ib.get("image", "").split("|")[0].strip()
        cands = [img if img and not img.startswith("<") else None, f"{bo['name']}.png"]
        if bo["id"] == "servants":
            cands = ["The Servants.png", "Calliope.png"]
        img_rel = f"assets/bosses/{bo['id']}.png"
        if not fetch_image(cands, ROOT / img_rel):
            missing_images.append(img_rel); img_rel = None
        bosses_out.append({
            "id": bo["id"], "name": bo["name"], "biome": bo["biome"], "stage": stage_of[bo["biome"]], "tier": bo["tier"],
            "dlc": bo["dlc"], "minBC": bo["minBC"], "description": bo["description"], "tips": bo["tips"],
            "dangers": bo["dangers"], "rewards": bo["rewards"], "wiki": wiki_url(bo["wiki"]), "image": img_rel,
        })

    runes_out = []
    for r in RUNES:
        img_rel = f"assets/biomes/rune-{r['id']}.png"
        if not fetch_image([r["icon"]], ROOT / img_rel):
            missing_images.append(img_rel); img_rel = None
        runes_out.append({k: r[k] for k in ("id", "name", "effect", "where", "guardian", "how", "unlocks")}
                         | {"wiki": wiki_url("Runes") + "#" + r["name"].replace(" ", "_"), "image": img_rel})

    bc_out = []
    for c in BOSS_CELLS:
        ne = {}
        for name, bid in newenemies.get(c["bc"], []):
            ne.setdefault(name, []).append(bid)
        bc_out.append({**c, "newEnemies": [{"enemy": k, "biomes": v} for k, v in ne.items()],
                       "wiki": wiki_url("Boss Stem Cells")})

    other_out = []
    for a in OTHER_AREAS:
        img_rel = None
        if a["image_file"]:
            img_rel = f"assets/biomes/{a['id']}.png"
            if not fetch_image([a["image_file"]], ROOT / img_rel):
                missing_images.append(img_rel); img_rel = None
        other_out.append({"id": a["id"], "name": a["name"], "description": a["description"], "how": a["how"],
                          "wiki": wiki_url(a["wiki"]), "image": img_rel})

    world = {
        "meta": {
            "game": "Dead Cells", "version": "3.5 (The End is Near) inkl. aller DLCs",
            "generated": __import__("datetime").date.today().isoformat(),
            "source": "https://deadcells.wiki.gg/ (Seiten 'Biomes', Einzelseiten der Biome/Bosse, 'Runes', 'Boss Stem Cells', 'Time, killstreak and no-hit doors'); Texte eigene deutsche Zusammenfassungen.",
            "generator": "tools/build_world.py",
            "fields": {
                "stage": "Spalte im Biomgraph: 1 Start, 2 Stufe 2, 3 optionale Biome, 4 Stufe 3, 5 erste Bosse, 6 Stufe 4, 7 Stufe 5, 8 zweite Bosse, 9 Stufe 6, 10 dritte Bosse, 11 Astrolab/The Crown, 12 Observatory.",
                "depth": "Spielinterne Biom-Ebene (1–7); null bei Bossarenen und optionalen Biomen.",
                "difficulty": "Redaktionelle, grobe relative Einschätzung 1–5 (auf gleicher BC-Stufe).",
                "exits": "Gerichtete Übergänge. rune = benötigte Rune; minBC = benötigte aktive Boss Cells; flags = dauerhafte Fortschrittsbedingungen (siehe meta.flags); condition = Erklärung inkl. run-interner Schlüssel.",
                "scrolls": "Garantierte Schriftrollen auf 0 BC: power = Schriftrollen der Macht (ohne verfluchte Truhe), dual = Dual-Schriftrollen, cursedChest = garantierte verfluchte Truhe mit einer weiteren Schriftrolle; notes = BC-Boni und Scroll Fragments.",
                "timedDoor": "Zeittür im Übergang NACH diesem Biom (Gesamtlaufzeit beim Erreichen); 'to' = Übergänge, in denen sie steht.",
                "bcEnemies": "Gegner, die ab der genannten BC-Stufe hinzukommen bzw. andere ersetzen.",
                "elite": "Feste Elitegegner sowie Wiki-Chancen für wandernde Elite und Eliteraum.",
                "ids": "Slug des englischen Namens; Dracula's Castle ist in draculas-castle-early (Ebene 3) und draculas-castle-late (Ebene 6) aufgeteilt.",
            },
            "flags": FLAGS,
            "rules": RULES,
            "counts": {},
        },
        "biomes": biomes_out,
        "bosses": bosses_out,
        "runes": runes_out,
        "bossCells": bc_out,
        "timedDoors": TIMED_DOORS,
        "otherAreas": other_out,
    }

    # ------------------------------------------------------------------ Validierung
    errors = []
    other_ids = {a["id"] for a in other_out}
    for b in biomes_out:
        for e in b["exits"]:
            if e["to"] not in biome_ids:
                errors.append(f"exit {b['id']} -> {e['to']} unbekannt")
            for f in e["flags"]:
                if f not in FLAGS:
                    errors.append(f"Flag {f} unbekannt ({b['id']})")
            if e["rune"] and e["rune"] not in {r["name"] for r in RUNES}:
                errors.append(f"Rune {e['rune']} unbekannt")
        if b["runeHere"] and b["runeHere"] not in {r["name"] for r in RUNES}:
            errors.append(f"runeHere {b['runeHere']}")
        if b["timedDoor"]:
            for t in b["timedDoor"]["to"]:
                if t not in {e["to"] for e in b["exits"]}:
                    errors.append(f"timedDoor {b['id']} -> {t} ist kein Ausgang")
    for bo in bosses_out:
        if bo["biome"] not in biome_ids:
            errors.append(f"boss {bo['id']} biome {bo['biome']}")
    for r in runes_out:
        if r["where"] not in biome_ids:
            errors.append(f"rune {r['id']} where {r['where']}")
        for u in r["unlocks"]:
            if u not in biome_ids | other_ids:
                errors.append(f"rune {r['id']} unlocks {u}")
    for t in TIMED_DOORS:
        if t["biome"] not in biome_ids:
            errors.append(f"timedDoor biome {t['biome']}")
        for x in t["to"]:
            if x not in biome_ids:
                errors.append(f"timedDoor to {x}")
    # Erreichbarkeit
    adj = {b["id"]: [e["to"] for e in b["exits"]] for b in biomes_out}
    seen, stack = {"prisoners-quarters"}, ["prisoners-quarters"]
    while stack:
        for n in adj[stack.pop()]:
            if n not in seen:
                seen.add(n); stack.append(n)
    unreachable = sorted(biome_ids - seen)
    if unreachable:
        errors.append(f"nicht erreichbar: {unreachable}")
    # Stufen müssen entlang der Kanten steigen
    st = {b["id"]: b["stage"] for b in biomes_out}
    for b in biomes_out:
        for e in b["exits"]:
            if st[e["to"]] <= st[b["id"]]:
                errors.append(f"Stufe fällt: {b['id']}({st[b['id']]}) -> {e['to']}({st[e['to']]})")

    world["meta"]["counts"] = {"biomes": len(biomes_out), "exits": sum(len(b["exits"]) for b in biomes_out),
                               "bosses": len(bosses_out), "runes": len(runes_out), "bossCells": len(bc_out),
                               "timedDoors": len(TIMED_DOORS), "otherAreas": len(other_out)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(world, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("geschrieben:", OUT, world["meta"]["counts"])
    if missing_images:
        print("FEHLENDE BILDER:", missing_images)
    if errors:
        print("VALIDIERUNGSFEHLER:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("Validierung OK: alle Referenzen gültig, alle Biome von prisoners-quarters erreichbar.")


if __name__ == "__main__":
    main()
