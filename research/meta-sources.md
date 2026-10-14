# Quellen der Meta-Ebene (builds.json, meta.json)

Recherche: 2026-10-14. Spielstand: 3.5 „The End is Near“ (35.8 live seit 2024-08; 35.9 vom 2026-06-15 nur Stabilitäts-Fixes).
Erzeugt mit `tools/build_meta.py` aus `tools/meta_*.py`. Alle Eigennamen sind gegen den Wiki-Cache (`research/cache/gear`, `research/cache/mutations`) geprüft.

## Wichtig: Grenzen
- **Reddit war technisch nicht erreichbar.** Gesperrt waren reddit.com, old.reddit, die JSON-API, pullpush, Redlib-Mirrors und archive.org. Ein einziger Reddit-Beitrag (Synergien-Thread, 2022) floss nur über ein Suchmaschinen-Snippet ein.
- Gewichtung: Steam-Foren, Steam-Guides und Videotitel als Community-Quellen. Tier-Listen-Seiten zählen schwach:
  - PocketGamer ranked laut eigener Aussage nach Grundschaden.
  - BeatCop und gamedatacentral erfinden Items und wurden verworfen.
- Die fundiertesten Experten-Rankings stecken in YouTube-Videos (VeeDotMe, Disappointed Giant, Pseychie_DC). Davon waren nur Titel und Beschreibungen lesbar, keine Platzierungen.
- Viele Community-Beiträge stammen aus 2022–2023. Deshalb wurden alle Bewertungen mit den Patch-Historien 3.0–3.5 abgeglichen (Nerfs/Buffs stehen im jeweiligen `why`).

## Primär: Mechanik und Patches
| Quelle | Datum |
|---|---|
| Dead Cells Wiki (wiki.gg): Item- und Mutationsseiten mit History-Abschnitten, dazu Biomes, Curse, Stats, Boss_Stem_Cells, Time_doors, Affixes, Aspects. Cache: `research/cache/meta/`, `research/cache/world/txt/` | abgerufen 2026-10-14 |
| https://deadcells.wiki.gg/wiki/Version_3.0 bis Version_3.5 | 2022-08 bis 2024-08 |
| Offizielle Patchnotes https://deadcells.com/patchnotes/30 bis /35 (inkl. Hotfix-Logs) | 2022-08 bis 2024-08 |

Wichtigste Balance-Punkte für die Meta:
- **3.4:**
  - Support: Grundbonus von +10 % auf +35 %.
  - Combo: neu aufgebaut, stapelt jetzt pro Treffer.
  - Berserker: neu aufgebaut (bis 90 % Schadensreduktion, Stun-Immunität).
  - Necromancy: neu aufgebaut, ohne Obergrenze.
  - Heart of Ice, Soldier's Resistance, Predator, Gold Plating und Midas' Blood: generft.
  - Disengagement: wirkt nur noch einmal pro Biom.
  - Slow: neu aufgebaut, 5 Stapel frieren ein.
- **3.0:**
  - Generft: Rapier, Hokuto's Bow, Repeater Crossbow (Krit), Point Blank, Smoke Bomb und Grappling Hook (Skalierung).
  - Hunter's Grenade gibt keine Stats mehr.
  - Gebufft: Wrecking Ball, Maw of the Deep, Hard Light Sword.
- **3.2:** Hattori's Katana generft.
- **3.3:** Starfury gebufft, Baseball Bat generft (Exploit entfernt).
- **3.5:**
  - Neu: Fluch-Inhalte (Misericorde, Anathema, Indulgence, Cursed Flask, Demonic Strength, Damned Vigor) und Cursed Biomes.
  - Neue Legendary-Affixe, z. B. Tesla Coil und Lightning Rods „Double Use“, Leghugger „Mitosis“.

## Community (Steam)
| Quelle | Datum | Inhalt |
|---|---|---|
| https://steamcommunity.com/app/588650/discussions/0/3196993316881133865 („What's your favorite build?“) | 2022-01 | Builds (War Spear + Giantkiller, Snake Fangs, Repeater, Bleed, Katana) und Mutationen |
| https://steamcommunity.com/app/588650/discussions/5/3844431603849506591 („How to abuse and beat 5BC, Survival Build“) | 2023-06/07 | 5-BC-Survival, Baseball Bat + The Boy's Axe, Malaise-Taktik |
| https://steamcommunity.com/app/588650/discussions/0/3196992771953380337 („Tips for 5bc?“) | 2022-01 | Routen und Boss-Tipps, Lantern |
| https://steamcommunity.com/app/588650/discussions/0/4408466785409709597 („Just beat the game on 5BC“) | 2022-03 | War Spear + Frost Blast, alle Rollen in Überleben |
| https://steamcommunity.com/app/588650/discussions/0/1749024925637860623 („Your Top 3 Best Weapons?“) | 2020 | Waffenmeinungen (Rapier, Giantkiller, Alchemic Carbine) |
| https://steamcommunity.com/app/588650/discussions/0/2333276539600959406 | älter | Electric Whip + Wings of the Crow |
| https://steamcommunity.com/sharedfiles/filedetails/?id=3323424572 („A guide to cheesing 5 Boss Cells (V35)“) | 2024-09-02 | Fluch-Build mit Damned, Cursed Flask, Demonic Strength; 5-BC-Max-Rollen-Route |
| https://steamcommunity.com/sharedfiles/filedetails/?id=1741877710 („Strategy for 5 Boss Cell Difficulty“) | 2019 | historisch, nur ergänzend |
| https://steamcommunity.com/sharedfiles/filedetails/?id=3310947780 (ukrainischer Einsteiger-Guide) | 2024-08-17 | Einsteiger-Builds 0–1 BC |
| https://www.reddit.com/r/deadcells/comments/wbi413/wiki_synergies_page/ | 2022-07 | nur Such-Snippet: „Repeater + Hokuto + Barbed Tips + Acrobatipack + Networking“ als klassischer Taktik-Build |

## Video (nur Titel und Beschreibungen)
| Quelle | Datum |
|---|---|
| VeeDotMe: Mutations Tier List (The Final Update) – https://youtu.be/6okDiuQAiUw | 2024-06-10 |
| VeeDotMe: Ranking ALL Items (Final Update) – https://youtu.be/lc11NC1FPcY | 2024-12-21 |
| VeeDotMe: Electric Whip + Kill Rhythm 5BC – https://youtu.be/wIgEjRuyTQM | 2022-06 |
| VeeDotMe: 3 Survival Builds – https://youtu.be/WoZTgpXYpSA | 2026-04-17 |
| Disappointed Giant: 9 Early Game Beginner Builds – https://youtu.be/0Sb97vWE16E | 2024-12 |
| Disappointed Giant: How to Farm Cells on ANY BC – https://youtu.be/iHY19it-L2s | 2023-10 |
| Daniel SaN: Throwing Knife/Boomerang Tactics – https://youtu.be/Gu8g_pQFC_M | 2026-08 |

## Tier-Listen-Seiten (schwach gewichtet)
| Quelle | Datum |
|---|---|
| Choost Games, Weapon Tier List „Final Update“ (5-BC-Fokus) – https://choostgames.com/blog/dead-cells-weapon-tier-list/ | 2026-04-30 |
| PocketGamer, Weapon Tier List v3.5.9 (nach Grundschaden) – https://www.pocketgamer.com/dead-cells/weapon-tier-list | 2026-10-08 |
| ScreenRant, 10 Best Weapons – https://screenrant.com/dead-cells-best-weapons/ | 2024-01-05 |
| Gamersdecide: Builds, Melee, Ranged, Skills, Mutations, Routes – https://gamersdecide.com/articles/dead-cells-best-builds (und Unterseiten) | 2021–2024 |
| AllClash, Melee Tier List – https://www.allclash.com/the-best-weapons-tier-list-in-dead-cells/ | 2022-08-06 |
| TheGamer / GameRant (Mutationen, Castlevania-Waffen) | 2021–2023 |
| TrueAchievements, 5-BC-Walkthrough (Routen) – https://www.trueachievements.com/game/Dead-Cells/walkthrough/12 | o. D. |
| GameTruth, Best Weapons and Builds – https://www.gametruth.com/guides/dead-cells-best-weapons-and-builds-guide-meta-weapons-ranked/ | 2025/2026 |

## Konsens (in 3 oder mehr unabhängigen Quellen hoch eingestuft)
- **Waffen:**
  - Nahkampf: Meat Skewer, Rapier, Ferryman's Lantern, Death's Scythe, Giantkiller, War Spear.
  - Fernkampf: Ice Bow und Ice Crossbow.
- **Schilde:** Spiked Shield, Knockback Shield.
- **Skills:** Ice Armor, Phaser, Wolf Trap, Barnacle.
- **Mutationen:** Gastronomy, Necromancy, Open Wounds, Instinct of the Master of Arms, Disengagement, Soldier's Resistance, Emergency Triage, Vengeance.
- **Builds:**
  - Assassin's Dagger + Phaser
  - Frost-Kontrolle
  - Turrets mit Support
  - Baseball-Bat-Kontrolle
  - Survival-Tank mit War Spear und Giantkiller
  - Bleed mit Open Wounds
