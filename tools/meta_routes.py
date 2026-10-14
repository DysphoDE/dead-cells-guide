"""Routen-Daten fuer data/meta.json (redaktionell, Biome/Exits gegen deadcells.wiki.gg/wiki/Biomes geprueft)."""

W = "https://deadcells.wiki.gg/wiki/"

ROUTES = [
    {
        "id": "einsteiger-klassiker",
        "name": "Der Klassiker für den ersten Sieg",
        "goal": "Einsteiger: erster Sieg über die Hand des Königs",
        "bcMin": 0, "bcMax": 1,
        "path": ["Prisoners' Quarters", "Promenade of the Condemned", "Ramparts", "Black Bridge", "Stilt Village",
                 "Clock Tower", "Clock Room", "High Peak Castle", "Throne Room"],
        "runesNeeded": ["Vine Rune"],
        "dlc": [],
        "why": "Braucht nur die Vine Rune (liegt selbst in der Promenade), alle Biome sind gut lesbar und die Bosse (Concierge, Time Keeper, Hand of the King) haben klar erlernbare Muster. Clock Tower bietet 4 Schriftrollen der Macht.",
        "tips": [
            "In der Promenade den Elite-Bogenschützen für die Vine Rune legen – ohne sie geht es dort nicht weiter.",
            "Concierge: Schild oder Rolle gegen den Sprung, nicht in die Ecke drängen lassen.",
            "High Peak Castle: die Schlüssel-Elites töten – zwei Castle Keys öffnen den Weg, der dritte gibt Boomerang-Entwurf und eine Schriftrolle.",
            "Flask nicht horten: lieber früh trinken und Zeit für Erholungstreffer (Rally) nutzen."
        ],
        "sources": [W + "Biomes", W + "Runes"]
    },
    {
        "id": "runen-reihenfolge",
        "name": "Runen in der richtigen Reihenfolge",
        "goal": "Freischaltung: alle Bewegungsrunen (Vine → Teleportation → Ram → Spider → Homunculus)",
        "bcMin": 0, "bcMax": 0,
        "path": ["Prisoners' Quarters", "Toxic Sewers", "Ancient Sewers", "Insufferable Crypt", "Slumbering Sanctuary",
                 "Forgotten Sepulcher", "Clock Room", "High Peak Castle", "Throne Room"],
        "runesNeeded": ["Vine Rune", "Teleportation Rune", "Ram Rune"],
        "dlc": [],
        "why": "Die Runen bauen aufeinander auf: Vine (Promenade) öffnet die Toxic Sewers, dort liegt die Teleportation Rune; mit ihr erreicht man das Ossuary (Ram Rune); mit Ram geht es von den Toxic Sewers in die Ancient Sewers → Insufferable Crypt → Slumbering Sanctuary (Spider Rune). Homunculus gibt es nach dem ersten Sieg über die Hand of the King.",
        "tips": [
            "Lauf 1: Promenade (Vine). Lauf 2: Toxic Sewers (Teleportation). Lauf 3: Promenade → Ossuary (Ram). Lauf 4: diese Route für die Spider Rune.",
            "Rune-Räume sind Elite-Kämpfe – vorher Flask auffüllen und Skills bereit halten.",
            "Explorer's Rune liegt am Ende des Forgotten Sepulcher hinter zwei Elite Dark Trackers – praktisch für alle späteren Läufe."
        ],
        "sources": [W + "Runes", W + "Biomes"]
    },
    {
        "id": "max-schriftrollen-cavern",
        "name": "Maximale Schriftrollen (Cavern-Route)",
        "goal": "Max. Schriftrollen / stärkster Build für 3–5 BC",
        "bcMin": 2, "bcMax": 5,
        "path": ["Prisoners' Quarters", "Toxic Sewers", "Corrupted Prison", "Ancient Sewers", "Insufferable Crypt",
                 "Slumbering Sanctuary", "Cavern", "Guardian's Haven", "High Peak Castle", "Throne Room"],
        "runesNeeded": ["Vine Rune", "Spider Rune"],
        "dlc": ["Rise of the Giant"],
        "why": "Kombiniert die schriftrollenreichsten Biome jeder Stufe: Ancient Sewers (3+1 Macht, 5 Fragmente auf 4/5 BC), Slumbering Sanctuary (inkl. garantierter Fluchkiste) und Cavern (4+1 Macht, 5 Fragmente). Auf 4/5 BC kommen so rund 20 Schriftrollen der Macht, 9 Doppelrollen und ca. 7 Rollen aus Fragmenten zusammen – deutlich mehr als jeder andere Pfad.",
        "tips": [
            "Cavern aus der Slumbering Sanctuary braucht 2+ BC und einen ersten Sieg über The Giant; alternativ Graveyard mit Cavern Key.",
            "Nach Guardian's Haven lieber High Peak Castle statt direkt Throne Room: der Direktweg gibt nur 2 Schriftrollen, High Peak 2 Macht + 2 Doppelrollen + Fragmente.",
            "Corrupted Prison lohnt nur, wenn du die Fluchkiste sicher abarbeiten kannst – sonst direkt Toxic Sewers → Ancient Sewers (Ram Rune).",
            "Der Giant ist ein DPS-Check: genug Schaden für Phase 3 mitnehmen, sonst lieber Clock Tower → Clock Room.",
            "Auf 5 BC geht es nach dem Throne Room weiter ins Astrolab (2 Doppelrollen) und zum Observatory."
        ],
        "sources": [W + "Biomes", W + "Scrolls", W + "Cavern", "https://steamcommunity.com/sharedfiles/filedetails/?id=3323424572"]
    },
    {
        "id": "max-schriftrollen-ohne-dlc",
        "name": "Viele Schriftrollen ohne DLC",
        "goal": "Max. Schriftrollen im Basisspiel",
        "bcMin": 0, "bcMax": 5,
        "path": ["Prisoners' Quarters", "Toxic Sewers", "Ancient Sewers", "Insufferable Crypt", "Slumbering Sanctuary",
                 "Clock Tower", "Clock Room", "High Peak Castle", "Throne Room"],
        "runesNeeded": ["Vine Rune", "Ram Rune"],
        "dlc": [],
        "why": "Ancient Sewers und Clock Tower sind die schriftrollenstärksten Basisspiel-Biome ihrer Stufe (je 3–4 Macht + Extra ab höherer BC). Die Slumbering Sanctuary hat eine garantierte Fluchkiste mit zusätzlicher Rolle.",
        "tips": [
            "Forgotten Sepulcher statt Clock Tower ist gleichwertig (3 + 1 in Fluchkiste), aber durch die Dunkelheit riskanter.",
            "Die drei Old Service Keys in den Ancient Sewers öffnen Belohnungen am Biom-Ende – Schlüsselträger nicht übersehen.",
            "Auf 3+ BC kannst du statt Toxic Sewers → Ancient Sewers auch Ramparts → Insufferable Crypt nehmen (BC-Tür)."
        ],
        "sources": [W + "Biomes", W + "Scrolls"]
    },
    {
        "id": "bc5-sicher",
        "name": "5 BC: sicher statt gierig",
        "goal": "BC5 / Hell schaffen (Stabilität vor Maximalwerten)",
        "bcMin": 4, "bcMax": 5,
        "path": ["Prisoners' Quarters", "Promenade of the Condemned", "Ramparts", "Black Bridge", "Stilt Village",
                 "Clock Tower", "Clock Room", "High Peak Castle", "Throne Room", "Astrolab", "Observatory"],
        "runesNeeded": ["Vine Rune"],
        "dlc": ["Rise of the Giant"],
        "why": "Auf 5 BC entscheiden Heilung und Malaise. Kurze, offene Biome mit vielen Schriftrollen der Macht (Ramparts 3+1, Stilt Village 3+1, Clock Tower 4+1) sind leichter zu kontrollieren als dunkle oder verwinkelte Biome. Nach der Hand of the King führt der Weg auf 5 BC weiter ins Astrolab und zum Collector.",
        "tips": [
            "Ab 4 BC gibt es in Passagen keine Flask-Aufladungen mehr – Heilung kommt aus Essen, Mutationen (Necromancy, Gastronomy) oder Lebensraub.",
            "Malaise durch zügiges Töten niedrig halten; Essen auf 5 BC ist (bis auf ein sauberes Stück pro Biom) infiziert.",
            "Fluchkisten nur öffnen, wenn das Biom danach noch genug Gegner zum Abarbeiten hat.",
            "Astrolab braucht Allen-, Elevator- und zwei Guardian's Keys von Elites – vorher Gesundheit sichern.",
            "Steam-Spieler nennen Stilt Village die leichteste 4. Stufe und den Concierge den leichtesten ersten Boss; die Derelict Distillery (Fallen + Zeitdruck) meiden viele auf 5 BC."
        ],
        "sources": [W + "Biomes", W + "Boss_Stem_Cells", W + "Astrolab", "https://steamcommunity.com/app/588650/discussions/0/3196992771953380337", "https://steamcommunity.com/app/588650/discussions/0/4408466785409709597"]
    },
    {
        "id": "speedrun-zeittueren",
        "name": "Zeittüren-Sprint",
        "goal": "Speedrun: Zeittüren (Promenade 2 Min, Ramparts 8 Min, Black Bridge→Stilt 15 Min) mit Bonus-Items",
        "bcMin": 0, "bcMax": 5,
        "path": ["Prisoners' Quarters", "Promenade of the Condemned", "Ramparts", "Black Bridge", "Stilt Village",
                 "Clock Tower", "Clock Room", "High Peak Castle", "Throne Room"],
        "runesNeeded": ["Vine Rune"],
        "dlc": [],
        "why": "Zeittüren liegen in den Übergängen nach Promenade (2 Min, Assault-Shield-Entwurf), Ramparts (8 Min) und nach der Black Bridge (15 Min, Root-Grenade-Entwurf). Sie enthalten Gold, 20 Zellen und eine Itemauswahl (auf 4–5 BC in S-Qualität).",
        "tips": [
            "Schnelle Lauf-Items (Velocity, Speed-Affixe, Swift Sword/Frenzy) helfen, Gegner auf dem Weg zu ignorieren.",
            "Die 2-Minuten-Tür gibt es auch nach Toxic Sewers (Frenzy-Entwurf) – gleiche Logik.",
            "Shops und Schatzräume mit der Standard-Zeiteinstellung ausnutzen: Zeit in Shops/Übergängen zählt nicht.",
            "Wer Schriftrollen braucht, nimmt sie im Vorbeilaufen mit – Fragment-Sockel auf 3+ BC liegen oft am Weg."
        ],
        "sources": [W + "Time_doors", W + "Biomes", "https://gamersdecide.com/articles/dead-cells-best-routes"]
    },
    {
        "id": "zellen-farmen",
        "name": "Zellen- und Entwurfs-Farm",
        "goal": "Zellen-Farmen und Entwürfe sammeln (Freischaltungen voranbringen)",
        "bcMin": 2, "bcMax": 4,
        "path": ["Prisoners' Quarters", "Promenade of the Condemned", "Ossuary", "Black Bridge", "Slumbering Sanctuary",
                 "Forgotten Sepulcher", "Clock Room", "High Peak Castle", "Throne Room"],
        "runesNeeded": ["Vine Rune", "Teleportation Rune", "Spider Rune"],
        "dlc": [],
        "why": "Ab 2 BC droppen Gegner doppelt so viele Zellen (ab 4 BC dreifach). Gründliches Abgrasen vieler Biome mit vielen Gegnern bringt Zellen und Entwurf-Drops; Mutationen wie Tainted Flask erhöhen zudem die Zahl der Elites.",
        "tips": [
            "Für reines Zellen-Farmen die höchste BC wählen, die du sicher überlebst – der Multiplikator lohnt sich mehr als Tempo.",
            "Zeit-, Killstreak- und No-Hit-Türen geben feste 20 Zellen zusätzlich.",
            "Hunter's Grenade + Blueprint Extractor (Specialist's Showroom) holt gezielt Entwürfe aus Gegnern.",
            "Eine Lore-Room- oder Biom-spezifische Entwurfsliste mitlaufen lassen und gezielt Biome wechseln."
        ],
        "sources": [W + "Boss_Stem_Cells", W + "Biomes", "https://youtu.be/iHY19it-L2s"]
    },
    {
        "id": "bad-seed",
        "name": "Durch den Garten (The Bad Seed)",
        "goal": "DLC-Inhalte: Dilapidated Arboretum, Morass, Mama Tick",
        "bcMin": 0, "bcMax": 5,
        "path": ["Prisoners' Quarters", "Dilapidated Arboretum", "Morass of the Banished", "Nest", "Stilt Village",
                 "Clock Tower", "Clock Room", "High Peak Castle", "Throne Room"],
        "runesNeeded": ["Teleportation Rune"],
        "dlc": ["The Bad Seed"],
        "why": "Ersetzt Stufe 2–3.5 durch die DLC-Biome; Mama Tick ist ein guter Lernboss für Positionierung. Morass hat eine garantierte Fluchkiste mit Zusatzrolle.",
        "tips": [
            "Für das Arboretum braucht es Teleportation Rune plus den Arboretum-Schlüssel aus dem Prisoners' Quarters (nahe dem Ausgang).",
            "Mama Tick: auf die Tentakel-Angriffe achten, nicht unter dem Auge stehen bleiben.",
            "Scythe Claw (Mama-Tick-Entwurf) ist eine starke Survival-Waffe für spätere Läufe."
        ],
        "sources": [W + "Biomes", W + "Dilapidated_Arboretum"]
    },
    {
        "id": "fatal-falls",
        "name": "Tempel über den Wolken (Fatal Falls)",
        "goal": "DLC-Inhalte: Fractured Shrines, Undying Shores, Scarecrow",
        "bcMin": 0, "bcMax": 5,
        "path": ["Prisoners' Quarters", "Promenade of the Condemned", "Ramparts", "Black Bridge", "Fractured Shrines",
                 "Undying Shores", "Mausoleum", "High Peak Castle", "Throne Room"],
        "runesNeeded": ["Vine Rune"],
        "dlc": ["Fatal Falls"],
        "why": "Undying Shores hat 4 Schriftrollen der Macht und ist damit eine gute Stufe-5-Alternative; der Scarecrow im Mausoleum ist ein fairer Boss.",
        "tips": [
            "Der erste Zugang zu den Undying Shores aus den Fractured Shrines erfordert das Cultist Outfit (ausgerüstet).",
            "Die Fractured Shrines haben nur 1 Macht-Rolle (+1 in Fluchkiste) – Schriftrollen holst du in den Undying Shores nach."
        ],
        "sources": [W + "Biomes", W + "Undying_Shores"]
    },
    {
        "id": "queen",
        "name": "Zur Königin (The Queen and the Sea)",
        "goal": "Alternatives Finale: The Queen (BC-Quelle wie die Hand of the King)",
        "bcMin": 0, "bcMax": 5,
        "path": ["Prisoners' Quarters", "Toxic Sewers", "Ancient Sewers", "Insufferable Crypt", "Slumbering Sanctuary",
                 "Clock Tower", "Clock Room", "Infested Shipwreck", "Lighthouse", "The Crown"],
        "runesNeeded": ["Vine Rune", "Ram Rune"],
        "dlc": ["The Queen and the Sea"],
        "why": "The Queen gibt wie die Hand of the King eine Boss Stem Cell. Der Shipwreck hat ab 3 BC eine Extra-Rolle; auf 3 BC gibt es nach dem Lighthouse noch eine Flask-Aufladung.",
        "tips": [
            "Die Queen bestraft Gier: Parieren lohnt sich gegen ihre Stichserien, Schild mitnehmen.",
            "Lighthouse ist ein Kletter-Biom mit Servants als Boss – Fernkampf oder Fallen sind dort sehr bequem."
        ],
        "sources": [W + "Biomes", W + "The_Queen"]
    },
    {
        "id": "castlevania",
        "name": "Draculas Schloss (Return to Castlevania)",
        "goal": "DLC-Inhalte: Castle's Outskirts, Dracula's Castle, Death und Dracula",
        "bcMin": 0, "bcMax": 5,
        "path": ["Prisoners' Quarters", "Castle's Outskirts", "Dracula's Castle", "Defiled Necropolis", "Stilt Village",
                 "Clock Tower", "Clock Room", "Dracula's Castle", "Master's Keep"],
        "runesNeeded": [],
        "dlc": ["Return to Castlevania"],
        "why": "Seit 3.5 kann man beide Castlevania-Biome in einem Lauf besuchen. Death (Defiled Necropolis) und Dracula (Master's Keep) sind die Bosse; Dracula - Final Form gibt ebenfalls eine Boss Stem Cell.",
        "tips": [
            "Der späte Zugang zu Dracula's Castle aus dem Clock Room setzt voraus, dass Death mindestens einmal besiegt wurde.",
            "Castlevania-Waffen (Vampire Killer, Alucard's Sword, Bible) sind starke Fundstücke auf dieser Route.",
            "Dracula's Castle (früh) hat 3 Macht + Extra ab 2 BC – gute Rollenausbeute."
        ],
        "sources": [W + "Biomes", W + "Version_3.5"]
    },
    {
        "id": "cavern-giant",
        "name": "Die fünfte Boss-Zelle (The Giant)",
        "goal": "BC5 freischalten: The Giant mit 4 BC besiegen",
        "bcMin": 4, "bcMax": 4,
        "path": ["Prisoners' Quarters", "Toxic Sewers", "Ancient Sewers", "Insufferable Crypt", "Graveyard",
                 "Cavern", "Guardian's Haven", "High Peak Castle", "Throne Room"],
        "runesNeeded": ["Vine Rune", "Ram Rune", "Spider Rune", "Homunculus Rune"],
        "dlc": ["Rise of the Giant"],
        "why": "Die fünfte Boss Stem Cell droppt nur The Giant in Guardian's Haven bei 4 aktiven BC. Der Weg über Graveyard → Cavern braucht beim ersten Mal den Cavern Key (Prisoners' Quarters, Homunculus Rune).",
        "tips": [
            "Den Cavern Key gibt es hinter der großen Tür am Start der Prisoners' Quarters – nur mit Homunculus Rune.",
            "Alternativ (nach erstem Giant-Kill) Slumbering Sanctuary → Cavern über die 2-BC-Tür.",
            "Für den Giant-Kampf Schaden priorisieren: in Phase 3 entscheidet DPS, nicht Ausweichen allein."
        ],
        "sources": [W + "Boss_Stem_Cells", W + "Biomes", W + "Guardian's_Haven"]
    },
    {
        "id": "fluch-gier",
        "name": "Fluchkisten-Pfad",
        "goal": "Extra-Rollen und S-Qualität-Items aus Fluchkisten (risikoreich)",
        "bcMin": 3, "bcMax": 5,
        "path": ["Prisoners' Quarters", "Toxic Sewers", "Corrupted Prison", "Ancient Sewers", "Insufferable Crypt",
                 "Slumbering Sanctuary", "Forgotten Sepulcher", "Clock Room", "High Peak Castle", "Throne Room"],
        "runesNeeded": ["Vine Rune", "Spider Rune", "Teleportation Rune"],
        "dlc": [],
        "why": "Corrupted Prison, Slumbering Sanctuary und Forgotten Sepulcher haben je eine garantierte Fluchkiste mit Schriftrolle der Macht. Ab 3 BC liefern Fluchkisten farblose Items in S-Qualität.",
        "tips": [
            "Fluch (10 Stapel) baut sich durch Kills ab; jeder Treffer tötet sofort – vorher Raum mit vielen schwachen Gegnern suchen.",
            "Acceptance halbiert die nötigen Kills, verflucht aber beim Essen.",
            "Im Forgotten Sepulcher lieber erst nach dem Abbau des Fluchs ins Dunkle laufen: Dunkelheit-Schaden tötet zwar nicht sofort, Gegner aber schon."
        ],
        "sources": [W + "Biomes", W + "Curse", W + "Boss_Stem_Cells"]
    },
    {
        "id": "ossuary-schriftrollen",
        "name": "Schriftrollen über das Ossuary",
        "goal": "Max. Schriftrollen mit leichteren Gegnern (Alternative zur Kanalisation)",
        "bcMin": 2, "bcMax": 5,
        "path": ["Prisoners' Quarters", "Promenade of the Condemned", "Prison Depths", "Ossuary", "Black Bridge",
                 "Slumbering Sanctuary", "Cavern", "Guardian's Haven", "High Peak Castle", "Throne Room"],
        "runesNeeded": ["Vine Rune", "Spider Rune"],
        "dlc": ["Rise of the Giant"],
        "why": "Prison Depths (Fluchkiste mit Rolle) und Ossuary (2 + 1 in Fluchkiste) ersetzen die Kanalisation; mit dem Concierge als erstem Boss und Cavern auf Stufe 5 bleibt die Rollenausbeute hoch. Gamersdecide (Max-Stats-Route) und TrueAchievements (5-BC-Walkthrough) nennen sehr ähnliche Pfade.",
        "tips": [
            "Prison Depths erreichst du aus der Promenade nur mit der Spider Rune.",
            "Die Fluchkisten in Prison Depths und Ossuary nur öffnen, wenn danach genug Gegner folgen.",
            "Ohne Rise of the Giant: Slumbering Sanctuary → Clock Tower/Forgotten Sepulcher → Clock Room."
        ],
        "sources": [W + "Biomes", "https://gamersdecide.com/articles/dead-cells-best-routes", "https://www.trueachievements.com/game/Dead-Cells/walkthrough/12"]
    },
]
