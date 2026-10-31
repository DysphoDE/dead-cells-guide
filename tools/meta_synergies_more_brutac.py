# Kombi-Datenbank Runde 3, Bereich "brutac": Synergie-Paare fuer Items mit Farben (ohne colorless) == ["brutality", "tactics"].
# Jeder Eintrag nennt mindestens eine Community-Quelle, die genau dieses Paar nennt (Steam-Forum, Spieler-Guide, Videotitel).
# Steam-Daten: Datum laut Beitrag; #c-Anker zeigen auf den Kommentar. Gamersdecide/gameplay.tips sind Spieler-Guides mit Begruendung
# (schwach gewichtet). YouTube: nur Titel aus Suchtreffern, Seiten selbst waren gesperrt.

_ST = "https://steamcommunity.com/app/588650/discussions/"
_GD = "https://gamersdecide.com/articles/"
_GT = "https://gameplay.tips/guides/6703-dead-cells.html"

SYNERGIES = [
    # ---------- Flashing Fans ----------
    {"items": ["Flashing Fans", "Infantry Bow"], "kind": "weapon+weapon",
     "why": "Beide Waffen belohnen das Spiel auf kurze Distanz: Der Infantry Bow kritet gegen nahe Ziele, die Fächer werfen gegnerische Geschosse zurück und schalten danach 8 s lang Krits frei. So deckt das Paar Nahkämpfer und Fernkämpfer ab.",
     "sources": ["https://www.youtube.com/watch?v=AU164KJ9Kuw", _ST + "0/3196993316880981361/#c3196993316881323653"],
     "evidence": "YouTube-Titel '1BC Flashing Fans + Infantry Bow - Dead Cells #4' (nur Titel/Snippet); Steam 'Lighthouse is tough' 2022-01: Build mit Infantry Bow, dazu 'shovel/flashing fans/iron staff to reflect projectiles'."},

    # ---------- Hard Light Sword ----------
    {"items": ["Hard Light Sword", "Grappling Hook"], "kind": "weapon+skill",
     "why": "Die Hard Light Gun markiert Gegner, das Schwert kritet gegen markierte Ziele. Der Grappling Hook zieht das markierte Ziel heran, sodass der Krit-Schlag sofort sitzt, und der nächste Treffer bekommt zusätzlich +40 % und betäubt.",
     "sources": ["https://note.com/seirensen0815/n/n6a3db61b6f99"],
     "evidence": "Spieler-Guide MagiAs (note.com, 2025-03-15, japanisch): Brutalitäts-Build Hard Light Sword/Gun + Grappling Hook, 'vor dem Angriff mit dem Hook heranziehen', für Tempo nach dem Markieren. Post-3.5."},
    {"items": ["Hard Light Sword", "Giantkiller"], "kind": "weapon+weapon",
     "why": "Das Hard Light Sword belegt beide Waffenplätze; der Giantkiller liegt im Rucksack und wird für Bosse und Elites gewechselt, gegen die er dauerhaft kritet. Das Schwert-Paar räumt die normalen Gegner.",
     "sources": ["https://www.youtube.com/watch?v=TkFYOs4dHHo"],
     "evidence": "YouTube-Titel '[4BC] Dead Cells - Hard Light Sword & Giantkiller playthrough' (nur Titel/Snippet, Datum unbekannt). Schwache Quelle, nur Videotitel."},

    # ---------- Spartan Sandals ----------
    {"items": ["Spartan Sandals", "Grappling Hook"], "kind": "weapon+skill",
     "why": "Der Grappling Hook zieht einen Gegner heran und betäubt ihn kurz; danach tritt man ihn mit den Sandalen dreimal gegen die nächste Wand, wo jeder Aufprall Zusatzschaden macht.",
     "sources": [_ST + "0/3196993316881133865/#c3196993316892579301"],
     "evidence": "Steam 'What's your favorite build?' Tetrafish_21 2022-01: Spartan Sandal + Grapple + Teleport, 'Grapple, Kick 3x, then Teleport, Kick 3x. Repeat.'"},
    {"items": ["Spartan Sandals", "Scheme"], "kind": "weapon+mutation",
     "why": "Scheme gibt dem ersten Nahkampftreffer nach einem Skill +200 Schaden; mit Grappling Hook oder Teleport vorneweg wird der erste Tritt der Sandalen zum schweren Eröffnungstreffer.",
     "sources": [_ST + "0/3196993316881133865/#c3196993316892579301"],
     "evidence": "Steam 'What's your favorite build?' Tetrafish_21 2022-01: Mutationen Open Wounds, Scheme; 'With Scheme, you can Grapple, then Teleport, then attack for big damage!'"},
    {"items": ["Valmont's Whip", "Spartan Sandals"], "kind": "weapon+weapon",
     "why": "Valmont's Whip kritet nur mit der Peitschenspitze auf Maximalreichweite. Die Sandalen treten Gegner genau auf diese Distanz weg, danach folgt der Krit-Hieb mit der Peitsche.",
     "sources": [_GD + "dead-cells-best-melee-weapons-2"],
     "evidence": "Gamersdecide 'Best Melee Weapons' (Update 2024-01-02): Valmont's Whip 'works well with roots and freezes', genannte Partner Ice Bow, Spartan Sandals, The Boy's Axe."},

    # ---------- Valmont's Whip ----------
    {"items": ["Valmont's Whip", "Ice Bow"], "kind": "weapon+weapon",
     "why": "Eingefrorene Gegner bleiben stehen, sodass man in Ruhe die Maximaldistanz für den Spitzen-Krit der Peitsche einnehmen kann. Gegen Bosse mit großer Trefferfläche wird der Krit noch leichter.",
     "sources": [_GD + "dead-cells-best-melee-weapons-2"],
     "evidence": "Gamersdecide 'Best Melee Weapons' (Update 2024-01-02): Valmont's Whip 'works well with roots and freezes', Partner u. a. Ice Bow."},

    # ---------- Starfury ----------
    {"items": ["Starfury", "Networking"], "kind": "weapon+mutation",
     "why": "Die fallenden Sterne der Starfury zählen als Fernkampftreffer und markieren damit für Networking. Markierte Gegner teilen sich den Schaden, und die Sterne treffen bevorzugt weitere Ziele in der Nähe.",
     "sources": [_GD + "dead-cells-best-builds"],
     "evidence": "Gamersdecide 'Top 10 Best Builds' (Update 2024-01-05), Platz 1 'The Fury of the Stars': Starfury + Networking + Point Blank, Networking 'links together enemies hit by ranged attacks'. Nach dem Starfury-Buff 3.3."},
    {"items": ["Starfury", "Point Blank"], "kind": "weapon+mutation",
     "why": "Die Sterne der Starfury gelten als Fernkampf und erhalten den Nahdistanz-Bonus von Point Blank (+30 %), weil man mit dem Schwert ohnehin direkt am Gegner steht.",
     "sources": [_GD + "dead-cells-best-builds"],
     "evidence": "Gamersdecide 'Top 10 Best Builds' (Update 2024-01-05), 'The Fury of the Stars': Point Blank 'boosts close-range projectiles'."},
    {"items": ["Starfury", "Alchemic Carbine"], "kind": "weapon+weapon",
     "why": "Taktik-Spaß-Build: Die Alchemic Carbine vergiftet Gruppen aus der Distanz, die Sterne der Starfury treffen zusätzlich Ziele außer Reichweite. Laut Quelle ab 3 BC zu schwach im Nahkampf.",
     "sources": [_ST + "0/3759977302534965606/"],
     "evidence": "Steam 'Builds that are hideously fun but not very efficient' gbors 2023-01: Alchemic Carbine + Starfury + Acrobatipack, 'Ridiculously fun', ab BC3 unpraktisch. Vor dem Starfury-Buff 3.3 (der die Waffe stärkt)."},

    # ---------- Smoke Bomb ----------
    {"items": ["Assassin's Dagger", "Smoke Bomb"], "kind": "weapon+skill",
     "why": "Die Smoke Bomb macht 8 s unsichtbar, Gegner verlieren dich aus den Augen. Man läuft hinter das Ziel, wo der Assassin's Dagger kritet, und der erste Treffer aus der Unsichtbarkeit bekommt zusätzlich +50 %.",
     "sources": [_ST + "5/3362524231623492342/#c3387294407394634922"],
     "evidence": "Steam 'Tips for 4BC?' d.locc$ta 2022-10: 5-BC-Brutalitäts-Build Assassin dagger, Frost blast, Phaser, Smoke bomb ('escape crowds')."},
    {"items": ["Smoke Bomb", "Predator"], "kind": "skill+mutation",
     "why": "Beide machen unsichtbar: Predator nach jedem Nahkampf-Kill, die Smoke Bomb auf Knopfdruck. Predator überbrückt so die Abklingzeit der Bombe. Seit 3.4 ist Predator kürzer (1 s, max. 2,8 s).",
     "sources": [_GT],
     "evidence": "gameplay.tips 'Comprehensive Build Guide' 2020-02: Smoke Bomb + Predator, 'you don't need to wait for your Smoke to get off cooldown to turn invisible'. Vor dem Predator-Nerf 3.4, Grundprinzip gilt weiter."},

    # ---------- Phaser ----------
    {"items": ["Phaser", "Smoke Bomb"], "kind": "skill+skill",
     "why": "Phaser teleportiert hinter den Gegner, die Smoke Bomb lässt dich danach unsichtbar aus der Gruppe verschwinden. Zusammen ergibt das den Assassinen-Stil aus Rückenangriff und Rückzug.",
     "sources": [_ST + "5/3362524231623492342/#c3387294407394634922"],
     "evidence": "Steam 'Tips for 4BC?' d.locc$ta 2022-10: Phaser und Smoke bomb im selben 5-BC-Build, 'blinking around like a proper assassin'."},
    {"items": ["Phaser", "Killer Instinct"], "kind": "skill+mutation",
     "why": "Killer Instinct verkürzt bei jedem Nahkampf-Kill die Skill-Abklingzeiten um 0,4 s. Der Phaser mit seiner kurzen Abklingzeit ist dadurch fast dauernd bereit.",
     "sources": [_ST + "5/3362524231623492342/#c3387294407394634922"],
     "evidence": "Steam 'Tips for 4BC?' d.locc$ta 2022-10: 'Killer instinct (to spam the sh*t out of phaser)'."},

    # ---------- Infantry Bow ----------
    {"items": ["Infantry Bow", "Point Blank"], "kind": "weapon+mutation",
     "why": "Der Infantry Bow kritet auf kurze Distanz, Point Blank gibt Fernkampfangriffen auf kurze Distanz +30 %. Beide Boni greifen in genau derselben Situation.",
     "sources": [_ST + "5/3362524231623492342/#c3362524231624687718", _GD + "dead-cells-best-ranged-weapons", _ST + "0/3879344844058693551/#c3881596897262248831"],
     "evidence": "Steam 'Tips for 4BC?' gbors 2022-10: 'with the Infantry Bow, Point Blank is potent with any primary stat'; Gamersdecide Ranged (Update 2024-01-05): Point Blank 'boosting the Infantry Bow's already powerful crit damage'; Steam 2023-09 Build mit beiden."},
    {"items": ["Infantry Bow", "Quick Bow"], "kind": "weapon+weapon",
     "why": "Zwei Bögen für Taktik: Der Quick Bow spickt Ziele aus der Distanz und kritet ab drei steckenden Pfeilen, der Infantry Bow übernimmt, sobald Gegner herankommen.",
     "sources": [_ST + "0/1698293255121137579/#c1698293255121307393"],
     "evidence": "Steam 'Best Item Synergy - What Works With What? Combos!' Gatebase 2018-03: 'I love the Infantry Bow and Quick Bow combo for a tactics build'. Alt, beide Bögen seitdem mechanisch unverändert."},

    # ---------- Throwing Knife ----------
    {"items": ["Sadist's Stiletto", "Throwing Knife"], "kind": "weapon+weapon",
     "why": "Das zielsuchende Throwing Knife lässt Gegner aus der Distanz bluten, das Sadist's Stiletto kritet gegen blutende Ziele. Der Bleed-Klassiker.",
     "sources": [_GD + "dead-cells-best-builds-1"],
     "evidence": "Gamersdecide 'Best Builds' (Update 2024-01-02), Platz 5 'Bleed': Sadist's Stiletto + Throwing Knife."},
    {"items": ["Throwing Knife", "Knife Dance"], "kind": "weapon+skill",
     "why": "Beide verteilen Blutung: Knife Dance schlagartig rundum, das Throwing Knife gezielt nach. Zusammen bauen sie schnell hohe Blutungsstapel auf.",
     "sources": [_ST + "0/3879344844058693551/#c3881596897259257749"],
     "evidence": "Steam 'Favorite weapon combo?' PhantomRise 2023-09: 'full DoT build with dual Throwing Knives or Firebrand + Throwing Knife with Knife Dance and Fire Nade'."},
    {"items": ["Firebrands", "Throwing Knife"], "kind": "weapon+weapon",
     "why": "Doppelter Fernkampf-DoT: Firebrands setzt Gegner und Boden in Brand, das Throwing Knife legt Blutung. Beide wirken weiter, während man ausweicht.",
     "sources": [_ST + "0/3879344844058693551/#c3881596897259257749"],
     "evidence": "Steam 'Favorite weapon combo?' PhantomRise 2023-09: 'Firebrand + Throwing Knife with Knife Dance and Fire Nade' als 'OP destruction of a full DoT build'."},
    {"items": ["Throwing Knife", "Ripper"], "kind": "weapon+mutation",
     "why": "Wurfmesser bleiben im Gegner stecken; Ripper reißt sie beim nächsten Nahkampftreffer (oder Sturzangriff) heraus, verursacht je 118 Schaden und gibt die Munition zurück.",
     "sources": [_GT],
     "evidence": "gameplay.tips 'Comprehensive Build Guide' 2020-02: Throwing Knives 'function well with the Ripper mutation'. Ripper wurde in 2.4 verstärkt."},

    # ---------- Flamethrower Turret ----------
    {"items": ["Flamethrower Turret", "Oil Grenade"], "kind": "skill+skill",
     "why": "Die Oil Grenade überzieht Gegner und Boden mit Öl, das Flamethrower Turret entzündet alles in Reichweite. Brennendes Öl macht ein Vielfaches des normalen Feuerschadens.",
     "sources": [_GD + "dead-cells-best-skills-1", _GD + "dead-cells-best-builds"],
     "evidence": "Gamersdecide 'Best Skills' (Update 2024-01-02): 'best paired with the weapon Oil Blade or the skill Oil Grenade'; 'Best Builds' (2024-01-05) Feuer-Build mit beiden."},

    # ---------- Sinew Slicer ----------
    {"items": ["Hokuto's Bow", "Sinew Slicer"], "kind": "weapon+skill",
     "why": "Zwei Sinew Slicer halten Gegner im Dauerfeuer, Hokuto's Bow markiert das Hauptziel für Zusatzschaden. Man selbst bleibt auf Abstand.",
     "sources": [_ST + "0/1698293255121137579/#c3111404628292223709"],
     "evidence": "Steam 'Best Item Synergy - What Works With What? Combos!' 2021-06: 'it is ez, 2 sinew slicers and hokuto's bow'."},
    {"items": ["Sinew Slicer", "Double Crossb-o-matic"], "kind": "skill+skill",
     "why": "Doppel-Geschütz für Taktik: Der Sinew Slicer lässt bluten, die Double Crossb-o-matic schießt mit einem Bonus gegen Blutende (Affix) hinterher.",
     "sources": [_ST + "0/1679189548074467170/#c1679189548074591614"],
     "evidence": "Steam 2019-04 SilkySmooth: 'double cross-bow-matic works wonders with the sinew slicer'. Alt; Bonus gegen Blutende hängt vom Affix ab."},

    # ---------- Corrupted Power ----------
    {"items": ["Corrupted Power", "Recovery"], "kind": "skill+mutation",
     "why": "Unter Corrupted Power nimmst du 30 % mehr Schaden, machst aber 50 % mehr. Recovery verdreifacht das Zeitfenster, in dem du verlorene HP durch eigene Treffer zurückholst; mit dem Schadensbonus geht das schnell.",
     "sources": [_GD + "dead-cells-best-skills-1"],
     "evidence": "Gamersdecide 'Best Skills' (Update 2024-01-02): Corrupted Power 'combine it with the mutation Recovery, so the time available to recover your health after a hit is multiplied by 3'."},

    # ---------- Snake Fangs / Lacerating Aura / Knife Dance ----------
    {"items": ["Snake Fangs", "Lacerating Aura"], "kind": "weapon+skill",
     "why": "Snake Fangs teleportiert dich zum nächsten Gegner, also mitten in die Gruppe. Dort trifft die Lacerating Aura alles direkt um dich herum.",
     "sources": [_ST + "0/3196993316881133865/#c3196993316891375279"],
     "evidence": "Steam 'What's your favorite build?' DrunkHobo 2022-01: Snake Fangs + Open Wounds + Melee + Master of Arms, 'I use it with knife dance and lacerating', erster 5-BC-Sieg."},
    {"items": ["Snake Fangs", "Knife Dance"], "kind": "weapon+skill",
     "why": "Nach dem Teleport von Snake Fangs steht man im Pulk; Knife Dance lässt dort sofort alles bluten.",
     "sources": [_ST + "0/3196993316881133865/#c3196993316891375279"],
     "evidence": "Steam 'What's your favorite build?' DrunkHobo 2022-01 (siehe oben), Knife Dance im selben 5-BC-Build."},
    # ---------- Nachtrag: Steam-Guides ----------
    {"items": ["Snake Fangs", "The Boy's Axe"], "kind": "weapon+weapon",
     "why": "Die Boy's Axe bleibt im Ziel stecken und verwurzelt es, Snake Fangs teleportiert von Ziel zu Ziel und stapelt Gift bis zur Krit-Schwelle. Beim Zurückrufen trifft die Axt noch einmal hart.",
     "sources": ["https://steamcommunity.com/sharedfiles/filedetails/?id=2631135482"],
     "evidence": "Steam-Guide 'Тактический билд ГРЫЗЬ 1-5BC, v. 25+FF' (impulse 101, 2021-10-18, russisch): Kern 'Топорик и Клыки' (Boy's Axe + Snake Fangs), schnelles Springen von Ziel zu Ziel mit Gift."},
    {"items": ["Firebrands", "Oil Grenade"], "kind": "weapon+skill",
     "why": "Die Oil Grenade überzieht Gegner und Boden mit Öl, Firebrands entzündet es. Brennendes Öl verursacht ein Vielfaches des normalen Feuerschadens.",
     "sources": ["https://steamcommunity.com/sharedfiles/filedetails/?id=1537535975"],
     "evidence": "Steam-Guide 'Pyromancer Build Guide' 2018-10: Fire Brands 'can be well accompanied with the Oil Grenade'; 'Oil Grenade can be used along with the Fire Brands ... for a fast barbeque'. Alt, Öl-Mechanik unverändert."},
    {"items": ["Fire Blast", "Flamethrower Turret"], "kind": "weapon+skill",
     "why": "Das Flamethrower Turret brennt wie ein zweiter, beidseitiger Fire Blast weiter, während du selbst zielst. Die Krits beider Feuerwaffen hängen aber weiter an Öl.",
     "sources": ["https://steamcommunity.com/sharedfiles/filedetails/?id=1537535975"],
     "evidence": "Steam-Guide 'Pyromancer Build Guide' 2018-10: Flamethrower Turret 'can be a promising partner with Fire Blast or Pyrotechnics', 'basically another dual-casting Fire Blast'. Alt."},
    {"items": ["Pyrotechnics", "Flamethrower Turret"], "kind": "weapon+skill",
     "why": "Pyrotechnics beschießt aus großer Distanz, das Flamethrower Turret hält nahe Gegner in Brand. So deckt das Paar Fern- und Nahbereich ab. Für Krits braucht Pyrotechnics zusätzlich Öl.",
     "sources": ["https://steamcommunity.com/sharedfiles/filedetails/?id=1537535975"],
     "evidence": "Steam-Guide 'Pyromancer Build Guide' 2018-10: Flamethrower Turret 'promising partner with Fire Blast or Pyrotechnics'. Alt."},
    {"items": ["Assassin's Dagger", "Throwing Knife"], "kind": "weapon+weapon",
     "why": "Der Assassin's Dagger kritet bei Rückentreffern, kann aber keine Flieger erreichen. Das zielsuchende Throwing Knife holt sie herunter und legt nebenbei Blutung.",
     "sources": ["https://steamcommunity.com/sharedfiles/filedetails/?id=3310947780"],
     "evidence": "Steam-Guide 'Білди для початківців' 2024-08-17 (ukrainisch), Brutalitäts-Build 1: Kinzhal vbyvtsi (Assassin's Dagger) + Metalnyi nizh (Throwing Knife) 'für Kontrolle fliegender Gegner und Blutung'. Post-3.5."},
    {"items": ["Sinew Slicer", "Support"], "kind": "skill+mutation",
     "why": "Support gibt +35 % Schaden, solange du nahe an einem aufgestellten Geschütz oder einer Falle stehst. Der Sinew Slicer arbeitet nur in deiner Nähe und hält diesen Bonus so automatisch aktiv.",
     "sources": ["https://steamcommunity.com/sharedfiles/filedetails/?id=3310947780"],
     "evidence": "Steam-Guide 'Білди для початківців' 2024-08-17, Taktik-Build 2: Wolf Trap + Sinew Slicer, Mutationen Support (Pidtrymka), Tranquility, Vengeance. Post-3.4 (Support-Buff)."},
]
