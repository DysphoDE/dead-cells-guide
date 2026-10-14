"""Erzeugt data/names-de.json: englische Wiki-Namen -> deutscher Spielname.
Quelle: Lokalisierungsdateien der lokal installierten Spielversion (res.pak -> lang/main.en.mo + lang/main.de.mo).
Beide .mo-Dateien verwenden den französischen Originaltext als msgid; über diesen Schlüssel werden EN und DE verknüpft.
Englische Namen stammen aus Wiki-Kategorien (deadcells.wiki.gg)."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import wikiapi
from mo_read import read_mo

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "research" / "cache" / "mechanics"
LANG = ROOT / "research" / "cache" / "lang"

CATS = {
    "item": ["Category:Melee weapons", "Category:Ranged weapons", "Category:Shields",
             "Category:Deployable traps", "Category:Grenades", "Category:Powers"],
    "mutation": ["Category:Mutations"],
    "biome": ["Category:Biomes"],
    "boss": ["Category:Bosses"],
}
EXTRA = [
    # Mechanik-Begriffe, Runen, Upgrades, Aspekte, NPCs, Modi (in mechanics.json verwendet)
    "Brutality", "Tactics", "Survival", "Malaise", "Custom Mode", "Boss Rush", "Daily Challenge",
    "Health Flask", "Health Flask I", "Health Flask II", "Health Flask III", "Health Flask IV",
    "Gold Reserves I", "Gold Reserves II", "Gold Reserves III", "Gold Reserves IV", "Gold Reserves V",
    "Recycling I", "Recycling II", "Random Melee Weapon", "Random Starter Bow", "Random Starter Shield",
    "Restock", "Specialist's Showroom", "Hunter's Mirror", "Merchandise Categories", "Advanced Forge I",
    "Recycling Tubes", "Backpack", "Training Room Key",
    "Vine Rune", "Customization Rune", "Challenger's Rune", "Teleportation Rune", "Ram Rune",
    "Explorer's Rune", "Spider Rune", "Homunculus Rune",
    "Toxin Lover", "Firestarter", "Shatter", "Assassin", "Relentless", "Blood Drinker", "Damned",
    "Gotta Go Fast", "Grenadier", "Menagerie", "Stomper", "Superconductor", "Tinker",
    "The Collector", "The Blacksmith", "The Blacksmith's Apprentice", "Guillain", "The Tailor", "The Doctor",
    "The Bank", "Passage", "Scroll of Power", "Scroll Fragment", "Cursed Chest", "Legendary Forge",
    "Boss Stem Cell", "Boss Cell", "Cells", "Gold",
]
# Begriffe, die im Spiel nur innerhalb von Sätzen/UI-Texten vorkommen. Werte stammen ebenfalls aus main.de.mo
# (Beleg-Strings in Klammern), wurden aber von Hand aus diesen Sätzen abgeleitet.
MANUAL = {
    "Cross": "Kreuz",                    # Item; "Cross" ist auch Verb ("Durchqueren")
    "Malaise": "Siechtum",               # "Malaise cleared" -> "Siechtum beseitigt."
    "Health Flask": "Medizinphiole",     # "Health Flask I" -> "Medizinphiole I"
    "Boss Stem Cell": "Boss-Stammzelle", # "::num:: Boss Stem Cell activated" -> "::num:: Boss-Stammzelle aktiviert"
    "Boss Cell": "Bosszelle",            # "Boss Cell V" -> "Bosszelle V"
    "Cursed Chest": "Verfluchte Truhe",  # "Cursed Chest found!" -> "Eine verfluchte Truhe gefunden!"
    "The Blacksmith": "Der Schmied",     # "I'm the Blacksmith." -> "Ich bin der Schmied."
    "Minor Forge": "Gewöhnliche Schmiede",  # "MINOR FORGE" -> "GEWÖHNLICHE SCHMIEDE"
    "Legendary Forge": "Legendäre Schmiede",# "LEGENDARY FORGE" -> "LEGENDÄRE SCHMIEDE"
    "Aspects": "Aspekte",
    "Mutations": "Mutationen",
    "Tailor's Daughter": "Tochter des Schneiders",
    "Specialist's Showroom": "Spezialhändler",  # "The Specialist's Showroom" -> "Spezialhändler"
    "Epic Scroll of Power": "Episches Pergament der Macht",
    "Assassin's Scroll": "Pergament des Assassinen",
    "Minotaur's Scroll": "Pergament des Minotaurus",
    "Guardian's Scroll": "Pergament des Wächters",
    "Critical hit": "Kritischer Treffer",
    "Demonic Strength": "Dämonische Kraft",  # im Spiel EN "Demon Strength" (U35_P_DEMONICFORCE)
    "Mausoleum": "Mausoleum",               # "The Mausoleum" -> "Das Mausoleum"
}

SKIP = re.compile(r"^(Template:|File:|Category:)|/fr$|^(Biomes|Bosses)$")

def norm(s):
    return s.replace("\u2019", "'").replace("\u00a0", " ").strip().lower()

def main():
    en = read_mo(LANG / "main.en.mo")
    de = read_mo(LANG / "main.de.mo")
    rev = {}
    for k, v in en.items():
        if k in de and de[k].strip():
            rev.setdefault(norm(v), set()).add(de[k].strip())
    removed = set(wikiapi.category(CACHE, "Category:Removed content"))
    names = []
    for kind, cats in CATS.items():
        for c in cats:
            for t in wikiapi.category(CACHE, c):
                if SKIP.search(t) or t in removed:
                    continue
                names.append(t)
    names += EXTRA
    direct = {norm(k): v.strip() for k, v in de.items() if v.strip()}
    out, ambiguous, missing = {}, {}, []
    for n in dict.fromkeys(names + list(MANUAL)):
        if n in MANUAL:
            out[n] = MANUAL[n]
            continue
        cands = rev.get(norm(n))
        if not cands and norm(n) in direct:
            cands = {direct[norm(n)]}
        if not cands and n.startswith("The "):
            cands = rev.get(norm(n[4:]))
        if not cands:
            # Wiki-Seitentitel mit Klammerzusatz, z. B. "Cleaver (Skill)"
            base = re.sub(r"\s*\(.*\)$", "", n)
            if base != n:
                cands = rev.get(norm(base))
        if cands and re.search(r"\s\(.*\)$", n):
            # Disambiguierungs-Zusatz der Wiki-Seite entfernen ("Melee (Mutation)" -> "Melee")
            n = re.sub(r"\s*\(.*\)$", "", n)
        if not cands:
            missing.append(n)
        elif len(cands) == 1:
            out[n] = next(iter(cands))
        elif len({c.lower() for c in cands}) == 1:
            # nur Groß-/Kleinschreibung verschieden (z. B. "TAKTIK"/"Taktik") -> nicht-versale Form
            out[n] = sorted(cands, key=lambda c: (c.isupper(), c))[0]
        else:
            ambiguous[n] = sorted(cands)
    (ROOT / "research" / "cache" / "lang" / "names_de_report.json").write_text(
        json.dumps({"missing": missing, "ambiguous": ambiguous}, ensure_ascii=False, indent=1), encoding="utf-8", newline=chr(10))
    (ROOT / "data" / "names-de.json").write_text(json.dumps(dict(sorted(out.items())), ensure_ascii=False, indent=1), encoding="utf-8", newline=chr(10))
    print("mapped", len(out), "ambiguous", len(ambiguous), "missing", len(missing))
    print("AMBIG", ambiguous)
    print("MISSING", missing)

if __name__ == "__main__":
    main()
