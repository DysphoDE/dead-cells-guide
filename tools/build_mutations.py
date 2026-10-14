"""Baut data/mutations.json + assets/mutations/<id>.png aus dem Dead Cells Wiki (wiki.gg).

Quellen:
  - Cargo-Tabelle "Mutations" (Name, Icon, Scaling, Blueprint-Ort/-Chance/-Kosten, RemoveVersion)
  - Einzelseiten der Kategorie "Category:Mutations" (Wikitext, für Details/Notes – Grundlage der
    kuratierten deutschen Texte unten)
  - Gegnerseiten (Infobox "location") für die Biomlisten der Blueprint-Drops
Alle API-Antworten werden in research/cache/mutations/ gecacht.

Aufruf:  python -I tools/build_mutations.py
"""
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wikiapi as w  # noqa: E402

ROOT = HERE.parent
CACHE = ROOT / "research" / "cache" / "mutations"
ICON_CACHE = CACHE / "icons"
OUT_JSON = ROOT / "data" / "mutations.json"
OUT_ICONS = ROOT / "assets" / "mutations"

COLORS = {"brut": "brutality", "tact": "tactics", "surv": "survival", "colorless": "colorless", "": "colorless"}
SOURCE_TYPES = {"start", "enemy", "boss", "lore", "secret", "challenge", "shop", "collector", "quest", "achievement", "other"}
DLCS = {None, "Rise of the Giant", "The Bad Seed", "Fatal Falls", "The Queen and the Sea", "Return to Castlevania"}

# Biome, die nur mit einem DLC existieren (für Hinweise in meta / Validierung)
DLC_BIOMES = {
    "Cavern": "Rise of the Giant", "Guardian's Haven": "Rise of the Giant", "Astrolab": "Rise of the Giant",
    "Observatory": "Rise of the Giant",
    "Dilapidated Arboretum": "The Bad Seed", "Morass of the Banished": "The Bad Seed", "Nest": "The Bad Seed",
    "Fractured Shrines": "Fatal Falls", "Undying Shores": "Fatal Falls", "Mausoleum": "Fatal Falls",
    "Infested Shipwreck": "The Queen and the Sea", "Lighthouse": "The Queen and the Sea", "The Crown": "The Queen and the Sea",
    "Castle's Outskirts": "Return to Castlevania", "Dracula's Castle": "Return to Castlevania",
    "Defiled Necropolis": "Return to Castlevania",
}


def slug(s):
    s = s.lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


# ---------------------------------------------------------------------------
# Kuratierte Daten (eigene deutsche Formulierungen auf Basis der Wiki-Seiten, Stand 3.5).
# "Stufe" = Stat-Level (Start = 1). Werte in Klammern "Basis" = bei Stufe 1.
# bp: sourceType, from, biomes, text  (cells / dropChance / minBC kommen aus Cargo und werden geprüft)
# ---------------------------------------------------------------------------
C = {}


def m(page, effect, numbers, notes, tags, bp):
    C[page] = dict(effect=effect, numbers=numbers, notes=notes, tags=tags, bp=bp)


def start():
    return dict(sourceType="start", **{"from": None}, biomes=[], text="Von Beginn an freigeschaltet.")


# ----- Brutality -----
m("Combo",
  "Jeder Treffer in Folge erhöht deinen Schaden um einen weiteren Stapel. Die Kette endet nach 2,5 s ohne Treffer oder sobald du Schaden nimmst.",
  "ca. +2 % Schaden pro Treffer-Stapel (+0,1 Prozentpunkte je Brutality-Stufe); jeder Treffer frischt das 2,5-s-Fenster auf.",
  "Seit 3.4 trefferbasiert (vorher Bonus nach Kills). Laut Wiki nur durch Nahkampftreffer ausgelöst – ideal für schnell schlagende Waffen (z. B. Balanced Blade).",
  ["melee", "damage", "combo"], start())
m("Vengeance",
  "Nachdem du Schaden genommen hast, verursachst du 8 s lang +60 % Schaden und erleidest 3 s lang 30 % weniger Schaden.",
  "+60 % Schaden (+1 Prozentpunkt je Brutality-Stufe) für 8 s; −30 % erlittener Schaden für 3 s.",
  None, ["damage", "defense", "on-hit-taken"], start())
m("Killer Instinct",
  "Jeder Kill durch einen Nahkampfangriff verkürzt die laufenden Skill-Abklingzeiten um 0,4 s (max. 3 s).",
  "0,4 s + 0,11 s je weiterer Brutality-Stufe, Maximum 3 s.",
  "Zählt nur, wenn der tödliche Treffer ein Nahkampfangriff ist – Kills durch Projektile oder Statuseffekte zählen nicht.",
  ["melee", "on-kill", "skill-cooldown"], start())
m("Melee (Mutation)",
  "Nahkampftreffer verlangsamen Gegner (2 Verlangsamungs-Stapel pro Treffer) für 0,4 s (max. 1,6 s).",
  "0,4 s × 1,15^(Stufe−1), Maximum 1,6 s (bei 11 Brutality-Stufen).",
  "Wiki-Seite heißt „Melee (Mutation)“. Die Verlangsamung macht Gegner leichter zu treffen und kombiniert gut mit Frostbite und Heart of Ice.",
  ["melee", "slow", "control"],
  dict(sourceType="boss", **{"from": "The Concierge"}, biomes=["Black Bridge"],
       text="Drop beim 5. Sieg über The Concierge."))
m("Open Wounds",
  "Jeder Nahkampftreffer fügt einen zusätzlichen Blutungsstapel zu (18 DPS Basis für 1,5 s).",
  "18 DPS × 1,15^(Stufe−1) pro Stapel, 1,5 s Dauer.",
  "Skaliert laut Wiki faktisch mit Schriftrollen und Stufe der auslösenden Waffe statt mit Brutality – funktioniert daher auch off-color. Hilft, die 5 Stapel für Blut-Bursts zu erreichen; auch Paraden, Phaser und Sturzangriffe lösen aus.",
  ["melee", "bleed", "dot"],
  dict(sourceType="enemy", **{"from": "Lacerator"},
       biomes=["Prison Depths", "Derelict Distillery", "Graveyard", "Slumbering Sanctuary", "Throne Room"],
       text="Seltener Drop (0,4 %) von Lacerators."))
m("Tainted Flask",
  "Ein Schluck aus dem Heiltrank gibt 20 s lang +20 % Schaden. Fehlt mindestens eine Trankladung, füllen Elite-Kills (12, mit Skalierung bis 4) eine Ladung nach; zudem erscheint pro Biom ein zusätzlicher Elite.",
  "+20 % Schaden (+2,5 Prozentpunkte je Brutality-Stufe) für 20 s; benötigte Elite-Kills 12 × 0,96^(Stufe−1), min. 4.",
  "Erlaubt das Trinken bei voller Gesundheit. Der Elite-Zähler läuft nur, solange eine Ladung fehlt; auch Elites aus Hunter's Grenade oder Malaise zählen.",
  ["flask", "damage", "elite"],
  dict(sourceType="boss", **{"from": "The Time Keeper"}, biomes=["Clock Room"],
       text="Drop beim 6. Sieg über The Time Keeper."))
m("Scheme",
  "Der erste Nahkampfangriff nach dem Einsatz eines Skills verursacht +200 Schaden (Basis).",
  "200 × 1,15^(Stufe−1) Zusatzschaden; der Bonus verfällt 8 s nach dem Skill.",
  None, ["melee", "skill", "burst"],
  dict(sourceType="enemy", **{"from": "Sweeper"}, biomes=["Ramparts"], text="Drop (10 %) von Sweepers in den Ramparts."))
m("Predator",
  "Ein Kill per Nahkampf macht dich 1 s lang unsichtbar (max. 2,8 s); ein neuer Angriff beendet die Unsichtbarkeit.",
  "1 s × 1,055^(Stufe−1), Maximum 2,8 s (bei 21 Brutality-Stufen).",
  "Sehr gute Kombination mit dem Aspekt Assassin.",
  ["melee", "on-kill", "stealth", "defense"],
  dict(sourceType="enemy", **{"from": "Automaton"}, biomes=["Clock Tower"], text="Drop (10 %) von Automatons im Clock Tower."))
m("Frenzy",
  "Solange ein Tempo-Buff aktiv ist, heilen dich Nahkampftreffer abhängig vom Grundschaden des Angriffs.",
  "0,0012 % Max-HP je Grundschadenspunkt × 1,055^(Stufe−1), Maximum 0,008 % (37 Stufen).",
  "Gerechnet wird mit dem Grundschaden der Waffe ohne Schriftrollen-/Qualitätsboni. Synergie: Velocity, Aspekt Gotta Go Fast, Tempo-Affixe, Masochist.",
  ["melee", "heal", "speed"],
  dict(sourceType="challenge", **{"from": None}, biomes=["Toxic Sewers"],
       text="Hinter der 2-Minuten-Zeittür im Übergang (Passage) vor den Toxic Sewers."))
m("Adrenaline",
  "Nach einem Ausweichen im letzten Moment heilen dich Nahkampftreffer 5 s lang abhängig vom Grundschaden.",
  "0,0015 % Max-HP je Grundschadenspunkt × 1,085^(Stufe−1), Maximum 0,015 % (30 Stufen); Fenster 5 s.",
  "Wie bei Frenzy zählt nur der Grundschaden; schwach mit Waffen mit wenig Nahkampfschaden (z. B. Spartan Sandals).",
  ["melee", "heal", "dodge"],
  dict(sourceType="enemy", **{"from": "Rampager"},
       biomes=["Prisoners' Quarters", "Toxic Sewers", "Dilapidated Arboretum", "Prison Depths", "Ramparts",
               "Morass of the Banished", "Stilt Village", "Slumbering Sanctuary", "Clock Tower", "High Peak Castle",
               "Undying Shores", "Infested Shipwreck"],
       text="Seltener Drop (1,7 %) von Rampagers, die erst ab 3 Boss-Zellen auftauchen."))
m("Initiative",
  "Der erste Nahkampftreffer gegen jeden Gegner verursacht +100 Schaden (Basis).",
  "100 × 1,15^(Stufe−1) Zusatzschaden, einmal pro Gegner.",
  "Gilt nicht für Fernkampfangriffe.",
  ["melee", "burst"],
  dict(sourceType="enemy", **{"from": "Royal Guard"}, biomes=["High Peak Castle"],
       text="Drop (10 %) von Royal Guards im High Peak Castle."))
m("Porcupack",
  "Rollst du durch Gegner, greift die Nahkampfwaffe im Rucksack sie mit 75 % ihres normalen Schadens an; danach 3 s Abklingzeit.",
  "75 % (+1 Prozentpunkt je Brutality-Stufe) des Waffenschadens; 3 s interne Abklingzeit, kann mehrere Gegner treffen.",
  "Es wird immer der erste Combo-Schlag genutzt (Rapier/Bladed Tonfas treffen so kritisch). Effekte und Affixe der Rucksackwaffe wirken, negative Affix-Effekte entfallen.",
  ["backpack", "roll", "melee"],
  dict(sourceType="enemy", **{"from": "Rancid Rat"},
       biomes=["Toxic Sewers", "Corrupted Prison", "Graveyard", "Derelict Distillery", "Infested Shipwreck",
               "Prisoners' Quarters", "Undying Shores"],
       text="Seltener Drop (0,4 %) von Rancid Rats."))

# ----- Tactics -----
m("Support",
  "Du verursachst +35 % Schaden, solange du dich in der Nähe eines aufgestellten Skills (Fallen & Geschütze) befindest.",
  "+35 % (+0,5 Prozentpunkte je Tactics-Stufe); Reichweite ca. 9 Felder um den Skill.",
  "Mehrere aufgestellte Skills stapeln nicht. Nur Skills der Kategorie „Traps & Turrets“ zählen.",
  ["deployable", "turret", "damage"], start())
m("Tranquility",
  "Du verursachst +25 % Schaden, solange kein Gegner im Umkreis von 5 Feldern ist.",
  "+25 % (+1 Prozentpunkt je Tactics-Stufe).",
  "Verstärkt anders als Point Blank auch indirekt gesetzte Statuseffekte und Nahkampfwaffen mit großer Reichweite (z. B. Valmont's Whip).",
  ["ranged", "damage", "distance"], start())
m("Ripper",
  "Nahkampftreffer reißen bis zu 6 im Gegner steckende Projektile heraus; jedes verursacht 118 Schaden (Basis) und die Munition kehrt zurück.",
  "118 × 1,15^(Stufe−1) pro Projektil, max. 6 pro Treffer (die ältesten zuerst).",
  "Funktioniert mit allen steckenbleibenden Geschossen (Bögen, Throwing Knife, Blowgun, The Boy's Axe, Hemorrhage, Killing Deck …). Sturzangriffe und Phaser zählen als Nahkampf.",
  ["ranged", "melee", "ammo", "burst"],
  dict(sourceType="secret", **{"from": None}, biomes=["Promenade of the Condemned"],
       text="Geheimbereich hoch über dem Eingang der Promenade of the Condemned; benötigt die Spider Rune."))
m("Parting Gift",
  "Gegner, die nicht durch einen Nahkampfangriff sterben, hinterlassen eine Bombe, die nach 0,7 s für 75 Schaden (Basis) explodiert.",
  "75 × 1,15^(Stufe−1) Flächenschaden, Radius ca. 6 Felder.",
  None, ["on-kill", "ranged", "aoe"],
  dict(sourceType="secret", **{"from": None}, biomes=["Graveyard"],
       text="Geheimbereich am rechten Ende der Oberfläche im Graveyard (Schalter in einer versteckten Decke)."))
m("Networking",
  "Fernkampftreffer markieren Gegner 8 s lang; markierte Gegner teilen 35 % (max. 75 %) des Schadens, den einer von ihnen erleidet.",
  "35 % × 1,05^(Stufe−1), Maximum 75 %; geteilter Schaden höchstens alle 0,2 s.",
  "Seit 3.4 mit allen Fernkampf-Schadensquellen. Stark mit durchdringenden oder mehrere Ziele treffenden Waffen (Boomerang, Cross, Fire Blast, War Javelin …).",
  ["ranged", "aoe", "mark"],
  dict(sourceType="enemy", **{"from": "Swarm Zombie"}, biomes=["Graveyard"], text="Drop (10 %) von Swarm Zombies im Graveyard."))
m("Hunter's Instinct",
  "Jeder Kill ohne Nahkampfangriff verkürzt die laufenden Skill-Abklingzeiten um 0,3 s (max. 2,5 s).",
  "0,3 s + 0,12 s je Tactics-Stufe, Maximum 2,5 s.",
  "Zählt Fernkampfwaffen, parierte Projektile sowie Bomben/Pfeile aus Affixen; Skills und Nahkampf zählen nicht.",
  ["ranged", "on-kill", "skill-cooldown"], start())
m("Ranger's Gear",
  "Der erste Fernkampfangriff nach dem Einsatz eines Skills verursacht +180 Schaden (Basis).",
  "180 × 1,15^(Stufe−1) Zusatzschaden; der Bonus verfällt nach 8 s.",
  "Bei Mehrfachschüssen (Magic Bow, Multiple-nocks Bow, Heavy Crossbow …) erhält jedes Projektil dieses Schusses den Bonus.",
  ["ranged", "skill", "burst"],
  dict(sourceType="enemy", **{"from": "Dancer"}, biomes=["Slumbering Sanctuary"],
       text="Drop (10 %) von Dancers im Slumbering Sanctuary."))
m("Crow's Foot",
  "Jede Rolle hinterlässt 3 Krähenfüße (max. 9 gleichzeitig), die 50 Schaden (Basis) verursachen und Gegner 1,5 s verlangsamen.",
  "50 × 1,15^(Stufe−1) pro Krähenfuß; Verlangsamung 1,5 s (jeder Krähenfuß frischt sie auf).",
  None, ["roll", "slow", "trap"],
  dict(sourceType="challenge", **{"from": None}, biomes=[],
       text="In der Truhe am Anfang eines Challenge Rift (zufällig auftauchendes Bodensymbol)."))
m("Tactical Retreat",
  "Ausweichen im letzten Moment verlangsamt alle Gegner in der Nähe (2 Stapel) für 1 s (max. 3 s).",
  "1 s × 1,048^(Stufe−1), Maximum 3 s; Radius ca. 15 Felder.",
  None, ["dodge", "slow", "control"],
  dict(sourceType="enemy", **{"from": "Slammer"}, biomes=["Corrupted Prison", "Cavern", "Undying Shores", "Astrolab"],
       text="Drop (10 %) von Slammers."))
m("Barbed Tips",
  "Jedes im Gegner steckende Projektil verursacht Dauerschaden: 40 DPS (Basis) für das erste, jedes weitere 15 % weniger als das vorige.",
  "40 × 1,15^(Stufe−1) DPS für das erste Projektil, n-tes × 0,85^(n−1); Tick alle 0,4 s.",
  "Profitiert von Support, Tranquility und Point Blank. Synergie mit Ripper und schnell feuernden Bögen.",
  ["ranged", "dot"],
  dict(sourceType="enemy", **{"from": "Toxic Miasma"}, biomes=["Corrupted Prison", "Undying Shores"],
       text="Drop (10 %) von Toxic Miasmas."))
m("Point Blank",
  "Fernkampfangriffe verursachen auf kurze Distanz +30 % Schaden.",
  "+30 % (+1 Prozentpunkt je Tactics-Stufe), Maximum 60 % (31 Stufen).",
  "Entscheidend ist deine Position beim Auftreffen. Verstärkt auch Barbed Tips und reflektierte Projektile, nicht aber reflektierte Bomben.",
  ["ranged", "damage", "close-range"],
  dict(sourceType="enemy", **{"from": "Corpulent Zombie"}, biomes=["Forgotten Sepulcher"],
       text="Drop (10 %) von Corpulent Zombies im Forgotten Sepulcher."))
m("Acrobatipack",
  "Nach einer Rolle feuert dein nächster Angriff mit einer Fernkampfwaffe zusätzlich ein Projektil der Fernkampfwaffe im Rucksack ab (25 % Schaden); 3 s Abklingzeit.",
  "25 % (+1 Prozentpunkt je Tactics-Stufe) des Waffenschadens; 3 s interne Abklingzeit.",
  "Löst nur mit echten Fernkampfwaffen aus (nicht z. B. Shrapnel Axes). Verbraucht keine Rucksack-Munition; Pfeile aus dem Rucksack bleiben nicht stecken (kein Ripper/Barbed Tips).",
  ["backpack", "roll", "ranged"],
  dict(sourceType="enemy", **{"from": "Demolisher"},
       biomes=["Derelict Distillery", "Ramparts", "Stilt Village", "Prisoners' Quarters", "Castle's Outskirts", "Clock Tower"],
       text="Drop (10 %) von Demolishers (Derelict Distillery; weitere Biome erst mit höheren Boss-Zellen)."))

# ----- Survival -----
m("Armadillopack",
  "Beim Rollen pariert der Schild im Rucksack Angriffe und Projektile automatisch und verursacht dabei 50 % seines Schadens.",
  "50 % (+1,5 Prozentpunkte je Survival-Stufe); Reichweite 3 Felder vor dir; 3 s Abklingzeit.",
  "Löst auch Parade-Effekte des Schilds aus (z. B. Einfrieren beim Ice Shield). Reflektierte Projektile/Bomben starten keine Abklingzeit. Ideal für Builds ohne Schild in der Hand.",
  ["backpack", "roll", "parry", "defense", "shield"],
  dict(sourceType="enemy", **{"from": "Thorny"}, biomes=["Dilapidated Arboretum", "Ossuary", "High Peak Castle"],
       text="Seltener Drop (1,7 %) von Thornies."))
m("Gastronomy",
  "Essen heilt 65 % mehr. Recycelst du Essen stattdessen, verursachst du 300 s lang +10 % Schaden.",
  "+65 % Essensheilung; +10 % Schaden (+1 Prozentpunkt je Survival-Stufe) je recyceltem Essen, 300 s, stapelbar.",
  "In Boss Rush nicht verfügbar.",
  ["food", "heal", "damage"],
  dict(sourceType="boss", **{"from": "Conjunctivius"}, biomes=["Insufferable Crypt"],
       text="Drop beim 4. Sieg über Conjunctivius."))
m("Heart of Ice",
  "Greifst du einen eingefrorenen, betäubten, verwurzelten oder verlangsamten Gegner aus der Nähe an, sinken die Skill-Abklingzeiten um 0,6 s (max. 2 s).",
  "0,6 s + 0,06 s je Survival-Stufe, Maximum 2 s; höchstens alle 0,5 s.",
  "Wirkt mit Nah- und Fernkampf auf kurze Distanz. Verlangsamte Ziele zählen laut Wiki ebenfalls, obwohl die Spielbeschreibung das nicht nennt. Starke Synergie mit Melee, Phaser und Nutcracker.",
  ["skill-cooldown", "freeze", "root", "slow", "stun"],
  dict(sourceType="enemy", **{"from": "Pirate Captain"}, biomes=["Stilt Village", "Infested Shipwreck"],
       text="Drop (10 %) von Pirate Captains."))
m("Kill Rhythm",
  "Wechselst du zwischen deinen beiden Waffen, erhält der nächste Angriff der anderen Waffe +15 % Angriffstempo.",
  "+15 % (+1 Prozentpunkt je Survival-Stufe); hält bis zum nächsten Angriff, höchstens 2 s; stapelt nicht.",
  "Beschleunigt vor allem Aufladezeiten (z. B. Flint, Toothpick, Heavy Crossbow), nicht Animationssperren oder Abklingzeiten.",
  ["attack-speed", "weapon-swap"],
  dict(sourceType="enemy", **{"from": "Oven Knight"},
       biomes=["Prisoners' Quarters", "Clock Tower", "Cavern", "Derelict Distillery", "Ramparts"],
       text="Seltener Drop (0,4 %) von Oven Knights, nur ab 2 Boss-Zellen."))
m("What Doesn't Kill Me",
  "Eine erfolgreiche Parade gegen einen Nahkampfangriff heilt dich um 2 % deiner Max-HP (max. 6 %).",
  "2 % × 1,05^(Stufe−1), Maximum 6 %; pro Gegner höchstens alle 30 s.",
  "Funktioniert auch mit Cocoon und Iron Staff.",
  ["parry", "heal"],
  dict(sourceType="enemy", **{"from": "Disgusting Worm"},
       biomes=["Toxic Sewers", "Ancient Sewers", "Undying Shores", "Throne Room"],
       text="Garantierter Drop (100 %) des ersten Disgusting Worm, der getötet wird."))
m("Soldier's Resistance",
  "Erhöht deine maximalen Lebenspunkte um 5 % (max. 40 %).",
  "5 % × 1,11^(Stufe−1), Maximum 40 % (21 Survival-Stufen).",
  "Wirkt prozentual auf das aktuelle Maximum, wächst also mit weiteren HP-Erhöhungen; additiv mit Dead Inside.",
  ["health", "defense"],
  dict(sourceType="enemy", **{"from": "Guardian Knight"}, biomes=["High Peak Castle", "Dracula's Castle"],
       text="Drop (10 %) von Guardian Knights."))
m("Necromancy",
  "Jeder Kill heilt dich um 0,3 % deiner Max-HP (max. 3 %); zähe Gegner heilen mehr, und die Heilung sinkt, je voller deine Lebensleiste ist.",
  "0,3 % × 1,15^(Stufe−1), Maximum 3 %; multipliziert mit (Gegner-Basis-HP / 125) × (1 − aktuelle HP / Max-HP).",
  "Seit 3.4 ohne 50-%-Grenze. Dead Inside blockiert die Heilung.",
  ["heal", "on-kill"], start())
m("Berserker",
  "Jeder Nahkampf-Kill senkt 8 s lang den erlittenen Schaden um 5 % (bis 20 % pro Kill), stapelbar bis 90 %; solange ein Stapel aktiv ist, bist du immun gegen Betäubung.",
  "5 % × 1,05^(Stufe−1) pro Kill, max. 20 % pro Kill (30 Stufen); Gesamtgrenze 90 %; Dauer 8 s.",
  "Alle Stapel laufen gemeinsam ab – neue Kills verlängern die Dauer nicht. Gute Kombination mit Recovery.",
  ["melee", "on-kill", "defense"],
  dict(sourceType="enemy", **{"from": "Failed Experiment"},
       biomes=["Prisoners' Quarters", "Promenade of the Condemned", "Ancient Sewers", "Stilt Village",
               "Forgotten Sepulcher", "Cavern", "Derelict Distillery", "Undying Shores", "Astrolab"],
       text="Sehr seltener Drop (0,4 %) von Failed Experiments, nur ab 4 Boss-Zellen."))
m("Blind Faith",
  "Jede erfolgreiche Parade verkürzt die laufenden Skill-Abklingzeiten um 2,8 s (max. 6 s).",
  "2,8 s + 0,105 s je Survival-Stufe, Maximum 6 s.",
  "Besonders stark mit Skills mit kurzer Abklingzeit (z. B. Infantry Grenade).",
  ["parry", "skill-cooldown", "shield"], start())
m("Counterattack",
  "Der erste Angriff nach einer erfolgreichen Parade verursacht +210 Schaden (Basis).",
  "210 × 1,15^(Stufe−1) Zusatzschaden; muss innerhalb von 8 s nach der Parade erfolgen.",
  None, ["parry", "burst", "shield"], start())
m("Extended Healing",
  "Der Heiltrank heilt 100 % statt 60 % deiner Max-HP, verteilt über 12 s; währenddessen verursachst du +25 % Schaden.",
  "+25 % Schaden (+1 Prozentpunkt je Survival-Stufe) während der 12-s-Heilung.",
  "Mit Emergency Triage kombinierbar: weiterhin 100 % über 12 s, zusätzlich schnelles Trinken und Kraftfeld.",
  ["flask", "heal", "damage"],
  dict(sourceType="secret", **{"from": None}, biomes=["Ossuary"],
       text="Geheimbereich im Ossuary: Sarkophag in einer Wand anrollen und aktivieren, er teleportiert zum Bauplan."))
m("Spite",
  "Erfolgreiche Paraden und reflektierte Projektile verursachen +140 Schaden (Basis).",
  "140 × 1,15^(Stufe−1) pro Parade/Reflexion.",
  "Wirkt auf jede einzelne Parade, auch mit Cocoon und Iron Staff.",
  ["parry", "shield", "burst"],
  dict(sourceType="secret", **{"from": None}, biomes=["Toxic Sewers"],
       text="Geheimbereich im Übergang (Passage) zwischen Prisoners' Quarters und Toxic Sewers."))

# ----- Colorless -----
m("Disengagement",
  "Einmal pro Biom: Fallen deine HP unter 15 %, schützt dich 5 s lang ein Kraftfeld.",
  "Schwelle 15 % HP; 5 s Kraftfeld; 1× pro Biom.",
  "Challenge Rifts zählen als eigenes Biom (Schutz wird beim Betreten/Verlassen erneuert). Einige Greifangriffe (z. B. The Queen, Dracula) umgehen Kraftfelder.",
  ["defense", "death-prevention"],
  dict(sourceType="secret", **{"from": None}, biomes=["Prisoners' Quarters"],
       text="Geheimbereich über den hängenden Flaschen in den Prisoners' Quarters; benötigt die Homunculus Rune (nach dem ersten Sieg über den Hand of the King)."))
m("No Mercy",
  "Normale Gegner sterben sofort, sobald ihr Leben auf 15 % oder weniger fällt; bei Bossen liegt die Schwelle bei 7,5 %.",
  "Hinrichtung bei ≤15 % HP (Bosse ≤7,5 %).",
  "Löst ohne eigenen Treffer aus – senkt die Gegner-HP also effektiv um 15 %. Betrifft fälschlich auch verbündete Biter (Swarm, Affixe).",
  ["execute", "damage"],
  dict(sourceType="enemy", **{"from": "Slasher"},
       biomes=["Prison Depths", "Ossuary", "Morass of the Banished", "Fractured Shrines", "Ramparts", "Graveyard",
               "Undying Shores", "Toxic Sewers", "High Peak Castle", "Throne Room"],
       text="Seltener Drop (1,7 %) von Slashers."))
m("Instinct of the Master of Arms",
  "Jeder kritische Treffer verkürzt die laufenden Skill-Abklingzeiten um 0,08 s (max. 1 s), höchstens einmal alle 0,2 s.",
  "0,08 s + 0,04 s je Stufe des höchsten Stats, Maximum 1 s (24 Stufen).",
  "Farblos, skaliert aber mit deinem höchsten Stat. Schild-Paraden zählen als kritische Treffer.",
  ["crit", "skill-cooldown", "parry"], start())
m("Emergency Triage",
  "Heiltränke heilen nur 35 %, werden aber 275 % schneller getrunken und geben 2 s lang ein Kraftfeld.",
  "35 % Heilung; 275 % Trinkgeschwindigkeit; 2 s Kraftfeld (seit 3.5 mit interner Abklingzeit).",
  "Mit Extended Healing kombiniert: 100 % Heilung über 12 s plus Kraftfeld.",
  ["flask", "heal", "defense"],
  dict(sourceType="boss", **{"from": "The Time Keeper"}, biomes=["Clock Room"],
       text="Drop beim 7. Sieg über The Time Keeper."))
m("Frostbite",
  "Gegner erleiden 30 DPS (Basis) pro Verlangsamungs-Stapel; eingefrorene Gegner zählen als volle 5 Stapel.",
  "30 × 1,15^(Stufe−1) DPS pro Stapel (Stufe = höchster Stat), max. 5 Stapel.",
  "Seit 3.4 farblos, skaliert mit dem höchsten Stat. Synergie: Melee, Tactical Retreat, Crow's Foot, Eis-Waffen und Verlangsamungs-Affixe.",
  ["slow", "freeze", "dot"],
  dict(sourceType="enemy", **{"from": "Buzzcutter"},
       biomes=["Ramparts", "Toxic Sewers", "Dilapidated Arboretum", "Undying Shores"],
       text="Drop (10 %) von Buzzcutters."))
m("Ygdar Orus Li Ox",
  "Rettet dich einmal pro Run vor dem Tod (nicht bei Fluch): Gegner in der Nähe werden eingefroren, du erhältst 25 % Max-HP zurück und Malaise wird entfernt.",
  "1× pro Run; heilt 25 % Max-HP.",
  "Nur bei der ersten Mutationswahl (nach Prisoners' Quarters) wählbar. Nach dem Auslösen bleibt der Slot für den Rest des Runs belegt; vorher kann sie entgegen der Spielbeschreibung per Reset entfernt werden. Schützt nicht vor Fluch-Tod.",
  ["death-prevention", "defense"], start())
m("Recovery",
  "Das Zeitfenster, in dem du verlorene Lebenspunkte durch eigene Angriffe zurückholen kannst, wird verdreifacht.",
  "Rückgewinnbare HP verfallen erst nach 0,24 s statt 0,08 s und mit 10 % statt 30 % Max-HP pro Sekunde.",
  "Funktioniert auch mit Dead Inside. Synergie mit Vengeance, Berserker und Spite Sword.",
  ["heal", "recovery"],
  dict(sourceType="boss", **{"from": "Conjunctivius"}, biomes=["Insufferable Crypt"],
       text="Drop beim 5. Sieg über Conjunctivius."))
m("Velocity",
  "Der Tempo-Buff aus Kill-Serien hält dreimal so lange (30 s statt 10 s).",
  "×3 Dauer (10 s → 30 s); mit Aspekt Gotta Go Fast 60 s.",
  "Synergie: Swift Sword, Frenzy, Get Rich Quick.",
  ["speed"],
  dict(sourceType="boss", **{"from": "The Time Keeper"}, biomes=["Clock Room"],
       text="Drop beim 5. Sieg über The Time Keeper."))
m("Dead Inside",
  "Verdoppelt deine maximalen Lebenspunkte, deaktiviert aber jede Heilung außer dem Zurückholen von HP (Recovery-Mechanik).",
  "+100 % Max-HP; −100 % Heilung (Trank, Essen, Necromancy usw.).",
  "Seit 3.4 in dieser Form (vorher +50 % HP / halbe Heilung). Mit Recovery und Vengeance kombinierbar.",
  ["health", "defense"],
  dict(sourceType="enemy", **{"from": "Lancer"}, biomes=["High Peak Castle", "Observatory"],
       text="Seltener Drop (1,7 %) von Lancers, nur ab 4 Boss-Zellen."))
m("Alienation",
  "Flüche brauchen 50 % mehr Kills zum Aufheben; beim Abbauen eines Fluchs mit mindestens 5 Stapeln wirst du geheilt.",
  "+50 % benötigte Kills; Heilung laut Wiki ca. 5 % HP pro fluchmindernden Kill.",
  "Die Kill-Erhöhung gilt nur für Flüche, die nach der Wahl entstehen. Die Wiki-Angaben zur genauen Heilung sind uneinheitlich (pro Kill vs. abhängig von der Stapelzahl). In Boss Rush nicht verfügbar.",
  ["curse", "heal"],
  dict(sourceType="boss", **{"from": "The Concierge"}, biomes=["Black Bridge"],
       text="Drop beim 7. Sieg über The Concierge."))
m("Acceptance",
  "Halbiert die zum Aufheben eines Fluchs nötigen Kills, aber jedes gegessene Essen verflucht dich.",
  "−50 % Fluch-Kills; Essen gibt einen 10er-Fluch, der durch den Effekt auf 5 halbiert wird.",
  "In Boss Rush nicht verfügbar. Mit Cursed Flask gibt jeder Schluck nur 10 statt 20 Stapel.",
  ["curse", "food"],
  dict(sourceType="secret", **{"from": None}, biomes=["High Peak Castle"],
       text="Ab 3 Boss-Zellen: Gardener's Keys (Promenade) gegen Moonflower Keys (Ramparts→Insufferable Crypt, Graveyard, Forgotten Sepulcher) tauschen und damit drei Türen eines Geheimgangs im High Peak Castle öffnen."))
m("Masochist",
  "Fallenschaden ist auf 10 % deiner Max-HP begrenzt; nach einem Fallentreffer läufst du 20 s lang 20 % schneller.",
  "Max. 10 % Max-HP pro Fallentreffer; +20 % Bewegungstempo für 20 s.",
  "Die Schadensgrenze greift auch bei manchen anderen Quellen (Abgrund der Ramparts, Lava/elektrische Knoten in Cavern und Guardian's Haven, bestimmte Sprengsätze) – dort ohne Tempo-Bonus. Der Tempo-Buff aktiviert Swift-Sword-Krits und Frenzy.",
  ["trap", "speed", "defense"],
  dict(sourceType="secret", **{"from": None}, biomes=["Slumbering Sanctuary"],
       text="Geheimbereich in der Wand eines engen senkrechten Schachts mit Stacheln im Slumbering Sanctuary."))
m("Ammo",
  "Verdoppelt die Munition deiner Waffen.",
  "×2 Munition.",
  "Seit 3.4 für alle munitionsbasierten Waffen außer Gilded Yumi und Laser Glaive.",
  ["ammo", "ranged"],
  dict(sourceType="boss", **{"from": "The Concierge"}, biomes=["Black Bridge"],
       text="Drop beim 6. Sieg über The Concierge."))
m("Gold Plating",
  "Treffer kosten Gold statt Lebenspunkte: 550 Gold pro verhindertem Prozent Max-HP. Reicht das Gold nicht, verlierst du den Rest als HP.",
  "550 Gold je 1 % Max-HP Schaden (seit 3.4.2).",
  "Kein Schutz vor Gift, Dunkelheit oder Fluch-Tod; die Kill-Serie (Perfekt-Türen) endet trotzdem. Absorbierte Treffer lassen dich nicht zurückzucken. Eher spät im Run mit hohem Goldvorrat sinnvoll.",
  ["gold", "defense"],
  dict(sourceType="enemy", **{"from": "Mimic"}, biomes=["The Bank"],
       text="Drop (10 %) von Mimics (zuerst in The Bank, danach in jedem Biom möglich)."))
m("Get Rich Quick",
  "Kills während eines Tempo-Buffs sammeln Bonusgold (doppelte Menge), das ausgezahlt wird, wenn der Buff endet.",
  "×2 Gold je Kill unter Tempo-Buff.",
  "In Boss Rush nicht verfügbar. Synergie: Velocity, Gold Plating, Money Shooter.",
  ["gold", "speed", "on-kill"],
  dict(sourceType="enemy", **{"from": "Mimic"}, biomes=["The Bank"],
       text="Drop (10 %) von Mimics (zuerst in The Bank, danach in jedem Biom möglich)."))
m("Midas' Blood",
  "Für jeden verlorenen Lebenspunkt erhältst du 1,6 Gold.",
  "1,6 Gold pro verlorenem HP (seit 3.4.2; vorher 2 bzw. 3).",
  "In Boss Rush nicht verfügbar. Kann kurzzeitig zum Goldfarmen genommen werden; von Gold Plating absorbierter Schaden zählt nicht.",
  ["gold"],
  dict(sourceType="enemy", **{"from": "Gold Gorger"}, biomes=["The Bank"],
       text="Seltener Drop (1,7 %) von Gold Gorgers in The Bank."))
m("Wish",
  "Der nächste neu aufgenommene oder gekaufte Gegenstand wird legendär; danach ist die Mutation verbraucht und belegt ihren Slot für den Rest des Runs.",
  None,
  "Nicht entfernbar. Wirkt nicht auf bereits legendäre oder vor der Wahl schon einmal aufgehobene Items. In Boss Rush nicht verfügbar.",
  ["legendary"],
  dict(sourceType="challenge", **{"from": None}, biomes=[],
       text="Belohnung für das Abschließen von Prüfung 3 im Boss Rush."))
m("Cursed Flask",
  "Dein Heiltrank hat unbegrenzte Ladungen, aber jeder Schluck verflucht dich mit 20 Stapeln.",
  "+20 Fluchstapel pro Schluck (10 mit Acceptance).",
  "Nicht nutzbar, wenn der Trank 0 Ladungen hat. Da ein Fluch jeden Treffer tödlich macht, v. a. mit dem Aspekt Damned sinnvoll; starke Synergie mit Demonic Strength.",
  ["flask", "curse", "heal"],
  dict(sourceType="enemy", **{"from": "Curser"}, biomes=[],
       text="Drop (10 %) von Cursers, die nur in verfluchten Biomen (ab 2 Boss-Zellen) erscheinen."))
m("Damned Vigor",
  "Bei tödlichem Schaden lebst du noch 2 s weiter; tötest du in dieser Zeit einen Gegner, überlebst du mit 1 HP – sonst, oder bei einem weiteren Treffer, stirbst du ohne jeden Schutz.",
  "2 s Gnadenfrist; Rettung auf 1 HP.",
  "Greift auch bei Fluch-Tod (der Fluchzähler bleibt). Aktiviert nur, wenn du vor dem Treffer mehr als 1 HP hattest.",
  ["death-prevention", "on-kill"],
  dict(sourceType="enemy", **{"from": "Sore Loser"}, biomes=[],
       text="Drop (10 %) von Sore Losers, die nur in verfluchten Biomen (ab 2 Boss-Zellen) erscheinen."))
m("Demonic Strength",
  "Solange du verflucht bist, verursachst du +30 % Schaden, plus 2 % je Fluchstapel.",
  "+30 % + 2 % je Stapel, maximal +130 % bei 50 Stapeln.",
  "Cursed Sword zählt nur als ein Stapel. Synergie: Cursed Flask, Spite Sword.",
  ["curse", "damage"],
  dict(sourceType="enemy", **{"from": "Doom Bringer"}, biomes=[],
       text="Drop (10 %) von Doom Bringers, die nur in verfluchten Biomen (ab 2 Boss-Zellen) erscheinen."))


# ---------------------------------------------------------------------------
def parse_chance(s):
    """'3+ BSC; 1.7%' -> (1.7, 3); '10%' -> (10.0, None)."""
    if not s:
        return None, None
    pct = re.findall(r"([\d.]+)\s*%", s)
    bc = re.search(r"(\d)\+\s*BSC", s)
    return (float(pct[-1]) if pct else None), (int(bc.group(1)) if bc else None)


def fetch_icon(fname, dest):
    ICON_CACHE.mkdir(parents=True, exist_ok=True)
    cached = ICON_CACHE / fname.replace(" ", "_")
    if not cached.exists():
        info = w.imageurl(CACHE, fname)
        if not info:
            raise RuntimeError(f"kein imageinfo für {fname}")
        data = w.get(info["url"], binary=True)
        cached.write_bytes(data)
    data = cached.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"{fname} ist kein PNG")
    shutil.copyfile(cached, dest)


def main():
    rows = w.api(CACHE, {
        "action": "cargoquery", "tables": "Mutations", "limit": "500",
        "fields": "_pageName=Page,Name,Image,Image2,Id,Description,InternalName,InternalName2,Scaling,"
                  "BlueprintLocation,BlueprintChance,BlueprintCost,DLC,RemoveVersion",
    })["data"]["cargoquery"]
    rows = [r["title"] for r in rows]
    cat = [t for t in w.category(CACHE, "Category:Mutations") if not t.startswith("Category:")]
    for t in cat:  # Einzelseiten cachen (Grundlage der kuratierten Texte)
        w.wikitext(CACHE, t)

    removed, out, problems = [], [], []
    for r in sorted(rows, key=lambda r: (["brut", "tact", "surv", "colorless", ""].index(r["Scaling"]), r["Name"])):
        if r["RemoveVersion"]:
            removed.append(f'{r["Name"]} (entfernt in {r["RemoveVersion"]})')
            continue
        page = r["Page"]
        cur = C.get(page)
        if cur is None:
            problems.append(f"keine kuratierten Daten für {page}")
            continue
        mid = slug(r["Name"])
        default = not r["BlueprintLocation"].strip()
        chance, bc = parse_chance(r["BlueprintChance"])
        bp = dict(cur["bp"])
        if default != (bp["sourceType"] == "start"):
            problems.append(f"{page}: default/sourceType passt nicht zu Cargo")
        minbc = bc or 0
        if bp["sourceType"] == "secret" and "3 Boss-Zellen" in bp["text"]:
            minbc = 3
        if bp["from"] in ("Curser", "Sore Loser", "Doom Bringer"):
            minbc = 2  # verfluchte Biome erst ab 2 BSC
        blueprint = {
            "default": default,
            "sourceType": bp["sourceType"],
            "from": bp["from"],
            "biomes": bp["biomes"],
            "dropChance": chance,
            "minBC": minbc,
            "cells": int(r["BlueprintCost"]) if r["BlueprintCost"] else None,
            "text": bp["text"],
        }
        dest = OUT_ICONS / f"{mid}.png"
        OUT_ICONS.mkdir(parents=True, exist_ok=True)
        fetch_icon(r["Image"], dest)
        out.append({
            "id": mid,
            "name": r["Name"],
            "nameDe": None,
            "color": COLORS[r["Scaling"]],
            "dlc": r["DLC"] or None,
            "effect": cur["effect"],
            "numbers": cur["numbers"],
            "notes": cur["notes"],
            "tags": cur["tags"],
            "blueprint": blueprint,
            "wiki": "https://deadcells.wiki.gg/wiki/" + quote(page.replace(" ", "_"), safe="()'_"),
            "icon": f"assets/mutations/{mid}.png",
        })

    extra = set(C) - {r["Page"] for r in rows}
    if extra:
        problems.append(f"kuratierte Einträge ohne Cargo-Zeile: {sorted(extra)}")

    # ---------- Validierung ----------
    ids = [m_["id"] for m_ in out]
    if len(ids) != len(set(ids)):
        problems.append("doppelte IDs")
    if len({m_["name"] for m_ in out}) != len(out):
        problems.append("doppelte Namen")
    for m_ in out:
        if m_["color"] not in {"brutality", "tactics", "survival", "colorless"}:
            problems.append(f'{m_["id"]}: ungültige Farbe')
        if m_["dlc"] not in DLCS:
            problems.append(f'{m_["id"]}: ungültiges DLC')
        if m_["blueprint"]["sourceType"] not in SOURCE_TYPES:
            problems.append(f'{m_["id"]}: ungültiger sourceType')
        p = ROOT / m_["icon"]
        if not p.exists() or p.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            problems.append(f'{m_["id"]}: Icon fehlt/kein PNG')
        if not m_["blueprint"]["default"] and m_["blueprint"]["cells"] is None:
            problems.append(f'{m_["id"]}: Zellkosten fehlen')
    if problems:
        print("PROBLEME:\n  " + "\n  ".join(problems))
        sys.exit(1)

    counts = {c: sum(1 for m_ in out if m_["color"] == c) for c in ("brutality", "tactics", "survival", "colorless")}
    meta = {
        "title": "Dead Cells – Mutationen",
        "gameVersion": "3.5 (The End is Near), inkl. aller DLCs",
        "generated": date.today().isoformat(),
        "source": "https://deadcells.wiki.gg/wiki/Mutations (Cargo-Tabelle „Mutations“ + Einzelseiten der Category:Mutations)",
        "generator": "tools/build_mutations.py",
        "count": len(out),
        "countByColor": counts,
        "fields": {
            "numbers": "Skalierung: 'Stufe' = Stat-Level der Mutationsfarbe (Startwert 1). Formeln wie im Wiki; Basiswerte gelten bei Stufe 1.",
            "blueprint.dropChance": "Dropchance in Prozent (Zahl), null wenn kein Zufallsdrop.",
            "blueprint.cells": "Zellkosten beim Collector; null bei von Beginn an verfügbaren Mutationen.",
            "blueprint.minBC": "Minimale Boss-Zellen (BSC), ab der der Bauplan erhältlich ist.",
            "blueprint.biomes": "Biome, in denen Quelle/Gegner vorkommt (teils erst ab höheren BC); leer = zufällig/biomunabhängig.",
        },
        "notes": [
            "Entfernte Mutationen (nicht enthalten): " + ", ".join(removed) + ".",
            "Keine Mutation ist an ein DLC gebunden (dlc=null bei allen). Einige Blueprint-Gegner kommen zusätzlich in DLC-Biomen vor "
            "(z. B. Thorny in Dilapidated Arboretum), sind aber stets auch im Basisspiel erreichbar.",
            "Mutationen skalieren mit 1,15^(Stufe−1) bzw. den angegebenen Formeln; Schadensboni von Mutationen werden nicht durch Item-Affixe verstärkt.",
            "Man kann bis zu 3 Mutationen gleichzeitig tragen (eine pro abgeschlossenem Biom); ein Reset bei Guillain kostet 1.000 Gold und verdoppelt sich bis max. 8.000.",
            "Deutsche Spielnamen (nameDe) sind nicht verlässlich belegt und daher null.",
        ],
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"meta": meta, "mutations": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"OK: {len(out)} Mutationen -> {OUT_JSON}")
    print("Farben:", counts)
    print("Entfernt:", removed)


if __name__ == "__main__":
    main()
