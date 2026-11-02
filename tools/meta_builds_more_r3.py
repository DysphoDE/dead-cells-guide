"""Zusätzliche Builds (Runde 3) – Kürzel `r3`: Community-belegte Builds für Items, die bisher in keinem Build vorkamen.
Jeder Build stützt sich auf mindestens eine Spielerquelle (YouTube-Titel/-Beschreibung, Steam-Diskussion), die genau
den Kern (Waffe + Skill bzw. Waffe + Waffe) nennt. Was die Quelle NICHT nennt (meist Mutationen oder ein zweiter Skill),
ist redaktionell aus den Wiki-Seiten ergänzt und in `weaknesses` als solches gekennzeichnet.
Item-/Mutationsnamen exakt nach deadcells.wiki.gg, Mechanik geprüft gegen die Wiki-Seiten (Stand 3.5, abgerufen 2026-10-30)."""

W = "https://deadcells.wiki.gg/wiki/"

# Evidenz je Quelle (nicht veröffentlicht):
SRC = {
    # VeeDotMe 2019-08-12 (1.4): „This vid's build: Collector's Syringe | Boomerang + Hokuto's Bow + Great Owl of War“, 5BC
    "r3-yt-vee-syringe14": "https://youtu.be/OuIJpxlM1pE",
    # VeeDotMe 2024-09-06: „SPIN TO WIN (Newly Buffed)“ – Update 35 Collector's Syringe Showcase, 5BC
    "r3-yt-vee-syringe35": "https://youtu.be/uijTUAbl9LE",
    # Relaxing Games 2023-05-28: Collector's Syringe als „best power skill“, 5BC-Bosse ohne Treffer
    "r3-yt-rg-syringe": "https://youtu.be/_sXXWFNFISw",
    # JoDirac 2025-07-25: „Hemorrhage with GRENADIER ~ 5BC“ – Hemorrhage + Sadist's Stiletto (gleiche Krit-Bedingung),
    # Powerful + Oil Grenade, Gift-Affix auf der Granate; Tags flawless/hitless
    "r3-yt-jodirac-hemo": "https://youtu.be/gKilgwMcM1M",
    # Kevin Fetters 2020-07-31: „Is Hemorrhage Legit?“ – Hemo + Blood Sword, rät zu Wolf Trap, Schild, Powerful Grenade
    "r3-yt-kf-hemo": "https://youtu.be/Ww9LHvWrqAo",
    # sekani 2022-02-20: „Shrapnel Boi Axe Ripper vs HOTK“ – „Build: Boy's Axe, Shrapnel Axes, Phaser, Wave of Denial“ (Credit VeeDotMe)
    "r3-yt-sekani-axes": "https://youtu.be/IL2vgXP29CQ",
    # ALIVE CELLS (Z) 2024-12-24: 5BC Hitless „with Shrapnel Axe's & Boy's Axe“
    "r3-yt-alive-axes": "https://youtu.be/vEd6hJ2dbjo",
    # VeeDotMe 2020-04-27 (1.8): „This video build: Flashing Fans | Ice Bow | Smoke Bomb | Wolf Trap“, 5BC
    "r3-yt-vee-fans": "https://youtu.be/Hk9AS69qdkc",
    # gameplay.tips 2020-02-23: Flashing Fans „should make The Giant pretty trivial“
    "r3-gameplay-tips": "https://gameplay.tips/guides/6703-dead-cells.html",
    # VeeDotMe 2020-11-27: „Tactics Build … uses Frost Blast and Barrel Launcher to kill monsters with maximum safety“
    "r3-yt-vee-barrel": "https://youtu.be/Gsm6JOx6mCY",
    # Alembic Overflow 2020-08-30: „Barrel Launcher/Tesla Coil Run“ 5BC; Wand-Abpraller für Krits
    "r3-yt-ao-barrel": "https://youtu.be/6JlrttuJ5DY",
    # Klyze Jr 2020-12-07 (2.1 alpha): „tentacle with frostblast dope combo“ + Melee-Mutation (+ Acrobatipack, heute so nicht mehr)
    "r3-yt-klyze-tentacle": "https://youtu.be/g8ZV2juP91c",
    # Alembic Overflow 2020-05-23: Tentacle-5BC-Run; „building around melee is advised“, Turrets für Status-Synergien
    "r3-yt-ao-tentacle": "https://youtu.be/-Et36K0HJxo",
    # VeeDotMe 2020-08-10 (1.9): Viewer Build #12 „Hayabusa Gauntlet, Spartan Sandals OR Hayabusa Boots, Grappling Hook, Ice Armor“ 5BC
    "r3-yt-vee-hayabusa": "https://youtu.be/XEa21zFafTI",
    # Disappointed Giant 2026-02-15: „Hayabusa Gauntlets AND Boots for the Win … 5BC Longplay“
    "r3-yt-dg-hayabusa": "https://youtu.be/Sp_gVnl1Yww",
    # Kevin Fetters 2020-08-19: „10 Brutality Builds To Beat 5BC“ – Kapitel „Blood Sword + Throwing Knife“,
    # „Oil Sword + Firebrands“, „Torch + Hokuto“
    "r3-yt-kf-10brut": "https://youtu.be/1iBOZTuI1P4",
    # Steam „Help with build“ 2020-07-06, kermat_: „Sadist's stiletto with Throwing knife, knife dance, cleaver and/or Open wounds mutation (red build)“
    "r3-steam-helpbuild": "https://steamcommunity.com/app/588650/discussions/5/2570942392189945602/",
    # VeeDotMe 2020-06-08: Viewer Build #2 „Fire Blast, Fire Brand, Fire Grenade, Flame Thrower“, Brutality, 5BC
    "r3-yt-vee-fire": "https://youtu.be/5KIJQycNCh4",
    # Kevin Fetters 2023-08-05: „5 Brutality Builds To Beat 5BC (2023)“ – Kapitel Firebrands
    "r3-yt-kf-5brut": "https://youtu.be/Gd83lQSRcVI",
    # VeeDotMe 2021-01-22: „Viewers Say TORCH is OP“ – Brutality-Viewer-Build, 5BC
    "r3-yt-vee-torch": "https://youtu.be/haINuN4k60A",
    # JoDirac 2025-06-07: „Pollo Power is truly unique ~ 5BC“ – aktiviert u. a. Front Line Shield, Initiative, Scheme, Ripper,
    # Open Wounds, Melee, IotMoA, Combo; „with chicks triggers Hand Hook's critical damage“
    "r3-yt-jodirac-pollo": "https://youtu.be/8CqoVPzF-lk",
    # Modesto 2022-11-17 (v32): „Brutality Win w/ Serenade (5BC)“ – Wish-Mutation auf Serenade lohnt sich
    "r3-yt-modesto-serenade": "https://youtu.be/B7_U6RAp1H8",
    # XeroIQ 2021-10-24: „ONLY SERENADE“ – „Mutation: Open wound, no mercy, Instinct master of arms“
    "r3-yt-xeroiq-serenade": "https://youtu.be/CAEZlWRE8g0",
    # VeeDotMe 2023-03-21: „100% Fool-proof Cursed Sword Build“ – Cursed Sword, Ice Armor, Diverse Deck (Foresight Card), 5BC
    "r3-yt-vee-cursed-deck": "https://youtu.be/eF5xxvGnBF4",
    # VeeDotMe 2020-07-13 (1.9): Viewer Build #7 „Spartan Sandals and Javelin“, 5BC
    "r3-yt-vee-sandals-jav": "https://youtu.be/-DJg0fhKsLs",
    # VeeDotMe 2019-03-24 (1.2): „This vid's build: Shrapnel Axe | Alchemic Carbine | Stun Grenade | Cluster Grenade“, 2BC-Sieg
    "r3-yt-vee-shrapnel12": "https://youtu.be/ec1rsIAG0uI",
    # Wiki-Seiten (Mechanik-Prüfung)
    "r3-wiki-syringe": W + "Collector's_Syringe",
    "r3-wiki-hemorrhage": W + "Hemorrhage",
    "r3-wiki-shrapnel": W + "Shrapnel_Axes",
    "r3-wiki-flashingfans": W + "Flashing_Fans",
    "r3-wiki-barrel": W + "Barrel_Launcher",
    "r3-wiki-tentacle": W + "Tentacle",
    "r3-wiki-acrobatipack": W + "Acrobatipack",
    "r3-wiki-hayabusaboots": W + "Hayabusa_Boots",
    "r3-wiki-cleaver": W + "Cleaver_(Skill)",
    "r3-wiki-firebrands": W + "Firebrands",
    "r3-wiki-torch": W + "Torch",
    "r3-wiki-pollo": W + "Pollo_Power",
    "r3-wiki-handhook": W + "Hand_Hook",
    "r3-wiki-serenade": W + "Serenade",
    "r3-wiki-diversedeck": W + "Diverse_Deck",
    "r3-wiki-warjavelin": W + "War_Javelin",
    "r3-wiki-cluster": W + "Cluster_Grenade",
}


def B(**kw):
    return kw


PATCHES = {}

BUILDS = [
    # ---------- Collector's Syringe ----------
    B(id="spritzen-wirbel", name="Spritzen-Wirbel", tagline="Die Collector's Syringe dreht sich durch ganze Räume, Hokuto's Bow und der Boomerang übernehmen die Pausen dazwischen.",
      color="tactics", secondaryColor="survival", archetype="Flächenschaden, Biom-Clear, Endgame-Skill", difficulty=2, bcMin=0, bcMax=5, phase="late", tier="A", dlc=["Rise of the Giant"],
      core={"weapons": ["Boomerang", "Hokuto's Bow"], "skills": ["Collector's Syringe", "Great Owl of War"], "mutations": ["Combo", "Melee", "Necromancy"]},
      alternatives={"weapons": ["Throwing Knife", "Ice Bow", "Rampart"], "skills": ["Wolf Trap", "Heavy Turret"], "mutations": ["Initiative", "Recovery", "Hunter's Instinct"]},
      statFocus="Taktik für Bögen, Boomerang und Eule; die Spritze skaliert mit Brutalität/Überleben – Überleben als Zweitfarbe macht sie stärker und gibt Puffer.",
      affixes=["Global Shield on Use (Legendary der Spritze)", "Movespeed on kill (fest auf der Spritze)", "+1 Ammo (Boomerang)"],
      whyItWorks="Die Collector's Syringe kreist um dich, trifft zehnmal pro Sekunde und wird bei jedem erneuten Aktivieren stärker (bis 240 Basis-DPS, ab der zweiten Stufe gegen ein paar Zellen). Laufen und Springen sind erlaubt, jede andere Aktion beendet sie. Deshalb trägt der Build Fernwaffen für die Abklingzeit: Hokuto's Bow markiert Ziele für zusätzliche +52 DPS, der Boomerang kehrt von selbst zurück. Die Great Owl of War feuert nebenher.",
      howToPlay=["Eule rufen, dann die Spritze zünden und in die Gegnergruppe laufen – nur laufen und springen, sonst endet der Wirbel.", "Die Spritze mehrfach nachaktivieren, solange genug Zellen da sind.", "In der Abklingzeit (20 s) mit Hokuto's Bow markieren und den Boomerang durch die Gruppe werfen.", "Gegen den Collector selbst einen anderen Skill mitnehmen – er nimmt dir vor dem Kampf alle Zellen."],
      strengths=["Räumt Biome extrem schnell", "Spritze gibt Tempo und Sprunghöhe zum Ausweichen", "Mehrfach in 5-BC-Runs gezeigt (VeeDotMe 2019 und erneut 2024 in 3.5)"],
      weaknesses=["Blueprint erst nach dem ersten Sieg über den Collector auf 5 BC", "Keine Spritze im Collector-Kampf (Zellen weg)", "Mutationen redaktionell ergänzt; Eule verschwindet bei jedem Treffer"],
      mutationWhy={
          "Combo": "Die Spritze gilt als Nahkampfangriff und trifft zehnmal pro Sekunde – seit 3.4 stapelt Combo pro Treffer, der Bonus baut sich also in Sekunden auf.",
          "Melee": "Jeder Spritzentreffer verlangsamt; Gegner kommen nicht aus dem Wirbel heraus, solange du dranbleibst.",
          "Necromancy": "Der Wirbel tötet ganze Gruppen auf einmal – jeder Kill heilt ein Stück.",
      },
      bossMutations=["Recovery"],
      bossMutationsWhy="Im Bosskampf gibt es kaum Kills für Necromancy; Recovery verdreifacht das Fenster, um Treffer mit den dauernden Spritzentreffern zurückzuholen.",
      sources=["r3-yt-vee-syringe14", "r3-yt-vee-syringe35", "r3-yt-rg-syringe", "r3-wiki-syringe"]),

    # ---------- Hemorrhage ----------
    B(id="aderlass-granaten", name="Aderlass mit Granaten", tagline="Hemorrhage und Sadist's Stiletto kritten unter derselben Bedingung – blutend oder vergiftet; die Granaten sorgen für den Rest.",
      color="brutality", secondaryColor="tactics", archetype="Blutung/Gift, Boss-Killer", difficulty=2, bcMin=2, bcMax=5, phase="mid", tier="A", dlc=["Rise of the Giant"],
      core={"weapons": ["Hemorrhage", "Sadist's Stiletto"], "skills": ["Powerful Grenade", "Oil Grenade"], "mutations": ["Open Wounds", "Instinct of the Master of Arms", "Killer Instinct"]},
      alternatives={"weapons": ["Blood Sword", "Throwing Knife", "Rampart"], "skills": ["Wolf Trap", "Corrosive Cloud", "Knife Dance"], "mutations": ["Ripper", "Combo", "Necromancy"]},
      statFocus="Brutalität voll, Taktik als Zweitfarbe – beide Waffen skalieren Brutalität/Taktik.",
      affixes=["+80 % gegen Vergiftete auf einer Granate (liefert Gift = Krit-Bedingung)", "+60 % gegen Blutende", "Bleed Propagation (Legendary der Hemorrhage)"],
      whyItWorks="Hemorrhage verursacht selbst Blutung und kritet gegen blutende oder vergiftete Ziele – nach dem ersten Schuss ist also jeder weitere ein Krit. Sadist's Stiletto hat genau dieselbe Krit-Bedingung und erbt die Blutung. JoDirac suchte zusätzlich eine Granate mit Gift-Affix, damit auch der erste Treffer kritet; Powerful und Oil Grenade zusammen sieht er bei rund 300 Schaden.",
      howToPlay=["Bosse und Elites mit einem Hemorrhage-Schuss anbluten, dann mit dem Stiletto im Dauerkrit nachsetzen.", "Granaten mit Gift- oder Blutungs-Affix bevorzugen – sie öffnen den Krit schon vor dem ersten Schuss.", "Hemorrhage hat wenig Munition: Schüsse gezielt auf Einzelziele setzen, Gruppen mit dem Stiletto und der Powerful Grenade erledigen.", "Oil Grenade vorlegen, wenn ein Feuer-Affix im Spiel ist."],
      strengths=["Dauerkrit mit beiden Waffen", "Hemorrhage bricht Elites und unterbricht Bosse durch hohen Breach", "2025 in einem 5-BC-Run ohne Treffer gezeigt (JoDirac)"],
      weaknesses=["Wenig Munition, langsamer Schuss – schwach gegen große Gruppen", "Ohne passenden Affix fehlt der Krit für den ersten Treffer", "Mutationen redaktionell ergänzt"],
      mutationWhy={
          "Open Wounds": "Jeder Stiletto-Stich legt eine Blutung nach – so bleibt die Krit-Bedingung beider Waffen auch dann bestehen, wenn die Hemorrhage-Blutung ausläuft.",
          "Instinct of the Master of Arms": "Beide Waffen kritten fast immer; jeder Krit verkürzt die Granaten-Abklingzeiten.",
          "Killer Instinct": "Stiletto-Kills im Nahkampf senken die Abklingzeiten zusätzlich – die Granaten sind fast in jedem Raum bereit.",
      },
      bossMutations=["Ripper"],
      bossMutationsWhy="Gegen Bosse fehlen Kills für Killer Instinct; Ripper holt mit jedem Stiletto-Stich die im Boss steckenden Hemorrhage-Geschosse zurück (je 118 Basisschaden) und löst so das Munitionsproblem.",
      sources=["r3-yt-jodirac-hemo", "r3-yt-kf-hemo", "r3-wiki-hemorrhage"]),

    # ---------- Shrapnel Axes + The Boy's Axe ----------
    B(id="splitter-ripper", name="Splitter-Ripper", tagline="The Boy's Axe wurzelt fest, die Shrapnel Axes spicken das Ziel mit Splittern – Ripper reißt alles auf einmal heraus.",
      color="tactics", secondaryColor="brutality", archetype="Ripper, Nah-/Fernkampf-Hybrid", difficulty=2, bcMin=1, bcMax=5, phase="mid", tier="B", dlc=["Rise of the Giant"],
      core={"weapons": ["Shrapnel Axes", "The Boy's Axe"], "skills": ["Phaser", "Wave of Denial"], "mutations": ["Ripper", "Scheme", "Heart of Ice"]},
      alternatives={"weapons": ["Throwing Knife", "Quick Bow"], "skills": ["Wolf Trap", "Root Grenade"], "mutations": ["Combo", "Tactical Retreat", "Ammo"]},
      statFocus="Taktik voll (Ripper, Boy's Axe, Wave of Denial), Brutalität für die Äxte und Phaser.",
      affixes=["Root Damage (Boy's Axe)", "Fire Bullet (Legendary der Shrapnel Axes)", "Extra Ammo Few (Legendary der Boy's Axe)"],
      whyItWorks="Die Shrapnel Axes verschießen Splitter, wenn kein Gegner in Nahkampfreichweite steht; die Splitter bleiben wie Pfeile im Ziel stecken, und der direkte Axthieb zählt als Nahkampf. Genau das braucht Ripper: Jeder Nahkampftreffer reißt bis zu sechs steckende Geschosse heraus (je 118 Basisschaden) – auch die Boy's Axe. Die Boy's Axe wurzelt das Ziel fest und verursacht beim Zurückrufen 80 Schaden; Phaser bringt dich hinter das gespickte Ziel, Wave of Denial schafft Platz und belohnt Wandtreffer mit +90.",
      howToPlay=["Ziel mit der Boy's Axe festwurzeln, aus Abstand mit den Äxten Splitter hineinjagen.", "Mit Phaser heranspringen und den Nahkampfhieb setzen – Ripper zieht die Splitter, Scheme legt +200 drauf.", "Boy's Axe zurückrufen (80 Schaden) und neu werfen.", "Wave of Denial, wenn du umzingelt bist, möglichst Richtung Wand."],
      strengths=["Starker Burst gegen Einzelziele", "Munition kommt über Ripper sofort zurück", "Von mehreren Spielern als 5-BC-Build gezeigt (u. a. hitless)"],
      weaknesses=["Nahkampftreffer erzeugen keine Splitter – der Rhythmus aus Abstand und Nähe will geübt sein", "Boy's Axe seit 3.0 schwächer (Grundschaden gesenkt)", "Scheme und Heart of Ice redaktionell ergänzt"],
      mutationWhy={
          "Ripper": "Das Herz des Builds: Jeder Nahkampftreffer zieht sechs steckende Splitter oder die Axt aus dem Ziel – Burst und Munition zugleich.",
          "Scheme": "Nach Phaser oder Wave of Denial trifft der nächste Nahkampfhieb mit +200 – genau der Hieb, der Ripper auslöst.",
          "Heart of Ice": "Die Boy's Axe wurzelt fest; Treffer auf verwurzelte Ziele aus der Nähe verkürzen Phaser und Wave of Denial.",
      },
      sources=["r3-yt-sekani-axes", "r3-yt-alive-axes", "r3-wiki-shrapnel"]),

    # ---------- Flashing Fans ----------
    B(id="faecher-spiegel", name="Fächer-Spiegel", tagline="Flashing Fans schlagen Geschosse zurück und kritten danach 8 Sekunden lang – Ice Bow und Wolf Trap halten den Rest auf.",
      color="brutality", secondaryColor="tactics", archetype="Reflexion, Krit-Nahkampf, Kontrolle", difficulty=3, bcMin=1, bcMax=5, phase="mid", tier="B", dlc=["The Bad Seed"],
      core={"weapons": ["Flashing Fans", "Ice Bow"], "skills": ["Smoke Bomb", "Wolf Trap"], "mutations": ["Instinct of the Master of Arms", "Heart of Ice", "Combo"]},
      alternatives={"weapons": ["Spartan Sandals", "Frost Blast", "Parry Shield"], "skills": ["Ice Grenade", "Phaser"], "mutations": ["Parting Gift", "Tactical Retreat", "Necromancy"]},
      statFocus="Brutalität für die Fächer, Taktik für Ice Bow und Wolf Trap.",
      affixes=["Bleed on Hit (Legendary der Flashing Fans)", "+175 % gegen Gefrorene", "Strong Ice (Legendary des Ice Bow)"],
      whyItWorks="Die Flashing Fans werfen gegnerische Geschosse zurück und kritten danach 8 Sekunden lang. Eigene Bomben lassen sich ebenfalls zurückschlagen, lösen den Krit aber nicht aus. Der Ice Bow friert kurz ein, Wolf Trap verwurzelt; Smoke Bomb macht dich 8 s unsichtbar, und der erste Angriff aus der Unsichtbarkeit trifft mit +50 %. Gegen geschossreiche Bosse wie The Giant ist die Krit-Phase fast dauerhaft aktiv.",
      howToPlay=["Schützen und Bomber bewusst anvisieren und ihre Geschosse mit den Fächern zurückschlagen – danach 8 s Dauerkrit.", "Nahkämpfer mit Ice Bow einfrieren oder in die Wolf Trap locken.", "Smoke Bomb zum Ausweichen und für den +50-%-Eröffnungsschlag.", "Gegen Bosse mit Geschossen möglichst jedes Projektil zurückschlagen."],
      strengths=["Sehr hoher Krit-Schaden gegen Fernkämpfer und Bosse mit Geschossen", "Gute Kontrolle durch Frost und Falle", "Laut gameplay.tips macht der Build The Giant 'trivial'"],
      weaknesses=["Gegen reine Nahkampf-Gegner fehlt der Krit-Auslöser", "Timing-intensiv", "Quelle von 2020 (1.8); Mutationen redaktionell ergänzt"],
      mutationWhy={
          "Instinct of the Master of Arms": "In der 8-s-Krit-Phase ist jeder Fächerhieb ein Krit – das hält Smoke Bomb und Wolf Trap fast ständig bereit.",
          "Heart of Ice": "Gefrorene (Ice Bow) und verwurzelte (Wolf Trap) Gegner aus der Nähe zu treffen, verkürzt die Skill-Abklingzeiten.",
          "Combo": "Die Fächer treffen schnell hintereinander; seit 3.4 stapelt Combo pro Treffer.",
      },
      sources=["r3-yt-vee-fans", "r3-gameplay-tips", "r3-wiki-flashingfans"]),

    # ---------- Barrel Launcher ----------
    B(id="fass-artillerie", name="Fass-Artillerie", tagline="Barrel Launcher kritet nach einem Wandabpraller; Frost Blast friert die Gegner ein, damit sie die Fässer nicht zurückschlagen.",
      color="tactics", secondaryColor=None, archetype="Explosionen, Fernkampf, Kontrolle", difficulty=2, bcMin=1, bcMax=5, phase="mid", tier="B", dlc=[],
      core={"weapons": ["Barrel Launcher", "Frost Blast"], "skills": ["Tesla Coil", "Wings of the Crow"], "mutations": ["Masochist", "Support", "Frostbite"]},
      alternatives={"weapons": ["Ice Bow", "Rampart"], "skills": ["Wave of Denial", "Ice Grenade", "Heavy Turret"], "mutations": ["Tranquility", "Networking", "Hunter's Instinct"]},
      statFocus="Taktik voll – Barrel Launcher, Tesla Coil, Wings of the Crow und Support skalieren damit; Frost Blast (Taktik/Überleben) ebenso.",
      affixes=["Triple Bullets (Legendary seit 3.5)", "+175 % gegen Gefrorene", "Reduces unfreezing (Strong Ice, Frost Blast)"],
      whyItWorks="Das Fass explodiert kritisch, wenn es vorher an einer Wand abprallt oder zwischen dir und einem Gegner hin- und hergeschlagen wurde. Gegner können Fässer aber auf dich zurückschlagen – laut Wiki verhindern Einfrieren oder Betäuben das. Frost Blast friert deshalb alles vor dir ein, bevor die Fässer fliegen (VeeDotMe: 'maximum safety'). Tesla Coil schießt nebenher, Wings of the Crow lässt dich schweben und erleichtert laut Wiki die Wand-Krits in Bosskämpfen.",
      howToPlay=["Gruppen mit Frost Blast einfrieren, dann Fässer gegen die Wand hinter ihnen schießen.", "Tesla Coil an engen Stellen stellen und daneben kämpfen (Support).", "Gegen Bosse mit Wings of the Crow schweben und Fässer über Wände abprallen lassen.", "Zurückgeschlagene Fässer mit einem Sofortangriff erneut zurückschlagen – dann kritten sie."],
      strengths=["Hoher Flächenschaden mit Krit über Wandabpraller", "Frost schützt vor dem eigenen Fass", "Zwei Spieler-Videos von 2020 mit 5-BC-Sieg"],
      weaknesses=["Zurückgeschlagene Fässer treffen dich selbst", "Die farblose Version aus der Derelict Distillery kann nicht in den Rucksack", "Wings of the Crow und die Mutationen redaktionell ergänzt (Wiki-Synergien)"],
      mutationWhy={
          "Masochist": "Zurückgeschlagene Fässer zählen als Falle – mit Masochist sinkt ihr Schaden von höchstens 30 % auf höchstens 10 % deiner Max-HP.",
          "Support": "Nahe der Tesla Coil verursachst du +35 % Schaden – auch mit den Fässern.",
          "Frostbite": "Von Frost Blast eingefrorene Gegner zählen als volle Verlangsamungs-Stapel und erleiden dauerhaft Zusatzschaden.",
      },
      sources=["r3-yt-vee-barrel", "r3-yt-ao-barrel", "r3-wiki-barrel"]),

    # ---------- Tentacle ----------
    B(id="tentakel-frost", name="Tentakel-Frost", tagline="Tentacle zieht dich heran und kritet mit dem Nachschlag – Frost Blast hält das Ziel dafür fest.",
      color="brutality", secondaryColor="tactics", archetype="Mobilität, Krit-Nahkampf, Frost", difficulty=2, bcMin=0, bcMax=4, phase="mid", tier="B", dlc=[],
      core={"weapons": ["Tentacle", "Frost Blast"], "skills": ["Wolf Trap", "Double Crossb-o-matic"], "mutations": ["Melee", "Frostbite", "Heart of Ice"]},
      alternatives={"weapons": ["Ice Bow", "Symmetrical Lance"], "skills": ["Ice Grenade", "Heavy Turret"], "mutations": ["Networking", "Combo", "Necromancy"]},
      statFocus="Brutalität für den Krit-Hieb (Tentacle Brutalität/Taktik), Taktik als Zweitfarbe für Frost Blast und die Fallen.",
      affixes=["+175 % gegen Gefrorene", "Poison on Hit (Legendary)", "Heavy Crit"],
      whyItWorks="Der erste Tentacle-Treffer ist ein Fernangriff, der dich zum Ziel zieht und Schilde ignoriert; greifst du während des Heranziehens erneut an, folgt ein Nahkampf-Krit. Klyze Jr zeigte 2020 die Kombination mit Frost Blast und der Melee-Mutation, Alembic Overflow riet, um den Nahkampf herum zu bauen und Turrets für Status-Effekte mitzunehmen. Frost Blast friert das Ziel ein; ein gefrorenes Ziel ist ein sicherer Landeplatz für den Krit-Hieb.",
      howToPlay=["Gruppe mit Frost Blast einfrieren.", "Mit dem Tentacle heranziehen und im Flug erneut angreifen – der Krit-Hieb trifft alles auf dem Weg.", "Zu nah dran? Dann tritt das Tentacle nur weg – vorher etwas Abstand nehmen.", "Wolf Trap und Turret für Bosse ablegen und dazwischen pendeln."],
      strengths=["Schnelle Annäherung, ignoriert Schilde", "Gefrorene und verwurzelte Ziele machen den Hieb sicher", "Gut gegen Fernkämpfer"],
      weaknesses=["Der Acrobatipack-Trick aus dem Video funktioniert seit dem Umbau der Mutation nicht mehr – nur Waffen, die selbst Fernkampfwaffen sind, lösen sie aus", "Tentacle gilt bei mehreren Spielern als nur mittelstark (Alembic Overflow: B-Tier)", "Skills teils redaktionell ergänzt"],
      mutationWhy={
          "Melee": "Der Krit-Hieb zählt als Nahkampf und legt zwei Verlangsamungs-Stapel – das Ziel bleibt in Reichweite (aus dem Quellvideo).",
          "Frostbite": "Jeder Verlangsamungs-Stapel aus Melee verursacht Schaden, gefrorene Ziele zählen als volle Stapel.",
          "Heart of Ice": "Hiebe auf gefrorene oder verwurzelte Ziele aus der Nähe verkürzen Wolf Trap und Turret.",
      },
      sources=["r3-yt-klyze-tentacle", "r3-yt-ao-tentacle", "r3-wiki-tentacle", "r3-wiki-acrobatipack"]),

    # ---------- Hayabusa Boots ----------
    B(id="ninja-tritte", name="Ninja-Tritte", tagline="Hayabusa Boots treten Gruppen weg, die Hayabusa Gauntlets kritten unter 40 % HP – das volle Ryu-Hayabusa-Set.",
      color="brutality", secondaryColor=None, archetype="Krit-Nahkampf, Knockback", difficulty=2, bcMin=0, bcMax=5, phase="any", tier="B", dlc=["Rise of the Giant"],
      core={"weapons": ["Hayabusa Boots", "Hayabusa Gauntlets"], "skills": ["Grappling Hook", "Ice Armor"], "mutations": ["Kill Rhythm", "Combo", "Necromancy"]},
      alternatives={"weapons": ["Spartan Sandals", "Front Line Shield"], "skills": ["Phaser", "Powerful Grenade"], "mutations": ["No Mercy", "Initiative", "Berserker"]},
      statFocus="Brutalität voll – beide Waffen und Grappling Hook skalieren damit.",
      affixes=["Super Bump (Legendary der Boots)", "Omae Wa Mou (Legendary der Gauntlets)", "Heavy Crit"],
      whyItWorks="Der letzte Tritt der Hayabusa Boots trifft alles um dich herum (200 Basisschaden seit 2.4), stößt zurück und verursacht an Wänden Zusatzschaden; er schlägt auch Granaten zurück. Die Hayabusa Gauntlets kritten, sobald ein Gegner unter 40 % HP fällt – die Tritte bringen ganze Gruppen dorthin. Grappling Hook zieht Weggetretene zurück (+40 % und 1 s Betäubung), Ice Armor schluckt einen Treffer.",
      howToPlay=["Gruppen mit den Boots antreten, bis die Gegner unter 40 % sind.", "Auf die Gauntlets wechseln und mit Krits beenden – der Wechsel löst Kill Rhythm aus.", "Weggetretene oder fliehende Gegner mit dem Grappling Hook zurückholen.", "Ice Armor vor Elites und Bossen aktivieren."],
      strengths=["Alle Teile früh verfügbar", "Starker Flächenschaden durch den letzten Tritt", "Mehrfach als 5-BC-Run gezeigt (VeeDotMe 2020, Disappointed Giant 2026)"],
      weaknesses=["Knockback kann Gegner aus der eigenen Reichweite treiben", "Gauntlets-Krit erst unter 40 % HP – schwach in der Eröffnung", "Mutationen redaktionell ergänzt"],
      mutationWhy={
          "Kill Rhythm": "Der Build lebt vom Wechsel zwischen Boots (anschlagen) und Gauntlets (beenden) – jeder Wechsel gibt Angriffstempo.",
          "Combo": "Beide Waffen treffen schnell; seit 3.4 stapelt Combo pro Treffer und verfällt erst nach 2,5 s ohne Treffer.",
          "Necromancy": "Die Tritte töten ganze Gruppen – jeder Kill heilt etwas.",
      },
      bossMutations=["No Mercy"],
      bossMutationsWhy="Bosse kommen langsam unter 40 %; No Mercy statt Necromancy richtet Mobs unter 15 % sofort hin und wirkt auf Bosse mit halbem Schwellenwert.",
      sources=["r3-yt-vee-hayabusa", "r3-yt-dg-hayabusa", "r3-wiki-hayabusaboots"]),

    # ---------- Blood Sword + Cleaver ----------
    B(id="saegeblatt-blutung", name="Sägeblatt-Blutung", tagline="Blood Sword, Throwing Knife, Cleaver und Knife Dance stapeln Blutung, bis die fünfte Ladung als Blutstoß platzt.",
      color="brutality", secondaryColor=None, archetype="Blutung, Einsteiger, Fallen", difficulty=1, bcMin=0, bcMax=3, phase="early", tier="B", dlc=[],
      core={"weapons": ["Blood Sword", "Throwing Knife"], "skills": ["Cleaver", "Knife Dance"], "mutations": ["Open Wounds", "Melee", "Killer Instinct"]},
      alternatives={"weapons": ["Sadist's Stiletto", "Hemorrhage", "Bloodthirsty Shield"], "skills": ["Lacerating Aura", "Sinew Slicer"], "mutations": ["Combo", "Necromancy", "Vengeance"]},
      statFocus="Brutalität voll – Blood Sword und Cleaver skalieren nur damit, Throwing Knife und Knife Dance mit Brutalität/Taktik.",
      affixes=["Double Stack (Legendary: zwei Blutungsstapel statt einem)", "+60 % gegen Blutende", "+80 % gegen Vergiftete (gilt laut Wiki auch für die Blutung des Blood Sword)"],
      whyItWorks="Das Blood Sword legt bei jedem Treffer eine lange Blutung an (12 s), Throwing Knife, Knife Dance und der Cleaver bringen weitere Stapel; bei fünf Stapeln entlädt sich die Blutung in einem Blutstoß. Der Cleaver blutet jeden Gegner an, der über die Sägeblätter läuft, und kann bis zu 50 Stapel verteilen. Kevin Fetters zeigt Blood Sword + Throwing Knife als 5-BC-Build, ein Steam-Spieler empfiehlt Throwing Knife, Knife Dance, Cleaver und Open Wounds als roten Build.",
      howToPlay=["Cleaver an der Stelle ablegen, an der du kämpfen willst – nicht zu weit weggehen, sonst stoppt er.", "Mit dem Blood Sword auf dem Sägebett zuschlagen, Fliehende mit dem Throwing Knife anbluten.", "Knife Dance in Gruppen zünden – meist reicht das für den fünften Stapel.", "Gegen Bosse Cleaver unter ihren Laufweg legen."],
      strengths=["Fast nur frühe, günstige Items", "Blutung wirkt auch gegen Bosse", "Einfache Spielweise, viel Schaden ohne Krit-Bedingung"],
      weaknesses=["Schaden kommt verzögert – schwach gegen schnelle Burst-Situationen", "Ab 4 BC zu wenig Schaden", "Kombination aus zwei Quellen zusammengesetzt; Mutationen teils redaktionell"],
      mutationWhy={
          "Open Wounds": "Jeder Nahkampftreffer legt einen zusätzlichen Blutungsstapel – mit dem Blood Sword zwei pro Hieb, der Blutstoß kommt viel schneller (aus der Steam-Empfehlung).",
          "Melee": "Verlangsamte Gegner kommen nicht vom Cleaver-Sägebett herunter und sammeln dort weiter Stapel.",
          "Killer Instinct": "Nahkampf-Kills verkürzen Cleaver und Knife Dance, damit das Sägebett im nächsten Raum wieder liegt.",
      },
      sources=["r3-yt-kf-10brut", "r3-steam-helpbuild", "r3-wiki-cleaver"]),

    # ---------- Firebrands ----------
    B(id="flaechenbrand", name="Flächenbrand", tagline="Fire Blast, Firebrands, Fire Grenade und Flamethrower Turret – alles brennt, auch der Boden.",
      color="brutality", secondaryColor="tactics", archetype="Feuer, Schaden über Zeit", difficulty=1, bcMin=0, bcMax=4, phase="early", tier="B", dlc=[],
      core={"weapons": ["Fire Blast", "Firebrands"], "skills": ["Fire Grenade", "Flamethrower Turret"], "mutations": ["Support", "Point Blank", "Necromancy"]},
      alternatives={"weapons": ["Oiled Sword", "Torch", "Hokuto's Bow"], "skills": ["Oil Grenade", "Heavy Turret"], "mutations": ["Combo", "Tranquility", "Hunter's Instinct"]},
      statFocus="Brutalität voll (so verlangt es der Viewer-Build), Taktik als Zweitfarbe – Fire Blast, Firebrands und der Turret skalieren mit beiden.",
      affixes=["Double Stack (Legendary der Firebrands)", "+40 % gegen Brennende", "+100 % gegen Ziele in brennendem Öl"],
      whyItWorks="Firebrands setzen Gegner und Boden in Brand, Fire Blast verbrennt alles vor dir, Fire Grenade und Flamethrower Turret legen nach – so stehen Gegner praktisch nie ohne Feuer da und Affixe gegen Brennende greifen dauernd. Fire Blast kritet, wenn Öl vorhanden ist; der Original-Build hat keine Öl-Quelle, deshalb steht Oil Grenade als erste Alternative bereit.",
      howToPlay=["Turret an engen Stellen aufstellen und daneben kämpfen.", "Firebrands vorwerfen, dann mit Fire Blast durch die brennende Gruppe.", "Fire Grenade für Gruppen hinter Ecken oder auf anderen Ebenen.", "Wer Öl findet (Oil Grenade, Öl-Affixe), tauscht – dann kritet Fire Blast und Feuer wird zu blauem Feuer."],
      strengths=["Alle Teile früh und günstig", "Viel passiver Schaden, sicheres Spiel aus Abstand", "Firebrands in zwei Brutalitäts-Guides von Kevin Fetters als 5-BC-tauglich genannt"],
      weaknesses=["Ohne Öl kein Fire-Blast-Krit", "Feuer auf dem Boden profitiert nicht von Point Blank und Status-Affixen", "Mutationen redaktionell ergänzt"],
      mutationWhy={
          "Support": "Nahe am Flamethrower Turret machst du +35 % Schaden – auch der Brand des Turrets profitiert.",
          "Point Blank": "Fire Blast wirkt aus kurzer Distanz; Point Blank verstärkt laut Wiki auch die direkt verursachten Brandstapel der Firebrands.",
          "Necromancy": "Feuer tötet ganze Gruppen nebenbei – jeder Kill heilt ein Stück.",
      },
      sources=["r3-yt-vee-fire", "r3-yt-kf-5brut", "r3-yt-kf-10brut", "r3-wiki-firebrands"]),

    # ---------- Torch ----------
    B(id="fackelzug", name="Fackelzug", tagline="Die Torch setzt bei jedem Hieb Feuerpfützen, Hokuto's Bow verstärkt jeden Brandtick auf markierten Zielen.",
      color="brutality", secondaryColor="tactics", archetype="Feuer-Nahkampf, Schaden über Zeit", difficulty=1, bcMin=0, bcMax=4, phase="early", tier="B", dlc=[],
      core={"weapons": ["Torch", "Hokuto's Bow"], "skills": ["Oil Grenade", "Wolf Trap"], "mutations": ["Combo", "Killer Instinct", "Necromancy"]},
      alternatives={"weapons": ["Firebrands", "Rampart"], "skills": ["Fire Grenade", "Flamethrower Turret", "Powerful Grenade"], "mutations": ["Melee", "Open Wounds", "Vengeance"]},
      statFocus="Brutalität voll für die Torch, Taktik als Zweitfarbe für Hokuto's Bow und Wolf Trap.",
      affixes=["Double Stack (Legendary der Torch)", "+100 % gegen Ziele in brennendem Öl", "+40 % gegen Brennende"],
      whyItWorks="Jeder Torch-Hieb setzt das Ziel in Brand und hinterlässt Feuerpfützen, die mit dem Kombo-Fortschritt größer und länger werden. Hokuto's Bow markiert Gegner für +52 DPS, solange irgendein Schadenseffekt auf ihnen liegt – Brand reicht. Die Oil Grenade macht aus dem Feuer blaues Feuer, Wolf Trap hält Gegner in den Pfützen. Kevin Fetters zeigt Torch + Hokuto als 5-BC-Brutalitäts-Build, VeeDotMe spielte 2021 einen Torch-Viewer-Build auf 5 BC.",
      howToPlay=["Bosse und Elites zuerst mit Hokuto's Bow markieren.", "Oil Grenade legen, dann mit der Torch hineinschlagen – Öl plus Feuer gibt blaues Feuer.", "Die volle Torch-Kombo durchziehen, der letzte Hieb legt die größte Pfütze.", "Wolf Trap, um Gegner in den Flammen zu halten."],
      strengths=["Startnahe Items, sehr günstig freizuschalten", "Breite Angriffe, viel Schaden über Zeit", "Hokuto-Markierung wird durch den Dauerbrand voll genutzt"],
      weaknesses=["Wenig Burst – auf hohen BC zu langsam (so auch ein Steam-Spieler über die Torch)", "Hokuto-Markierungsschaden lässt sich nicht durch Mutationen verstärken", "Skills und Mutationen redaktionell ergänzt"],
      mutationWhy={
          "Combo": "Laut Wiki verstärkt Combo die direkt von der Torch angelegten Brandstapel – jeder Hieb erhöht also auch den Feuerschaden.",
          "Killer Instinct": "Nahkampf-Kills mit der Torch verkürzen Oil Grenade und Wolf Trap.",
          "Necromancy": "Brand tötet viele Gegner nebenbei; jeder Kill heilt ein wenig.",
      },
      sources=["r3-yt-kf-10brut", "r3-yt-vee-torch", "r3-wiki-torch"]),

    # ---------- Pollo Power ----------
    B(id="huehnerhaken", name="Hühnerhaken", tagline="Pollo Power legt Eier, die kritten und Mutationen auslösen – als Legendary schlüpfen Küken, an denen der Hand Hook kritet.",
      color="brutality", secondaryColor="tactics", archetype="Skill-Burst, Wurf-Krit, Spaß-Build", difficulty=2, bcMin=1, bcMax=5, phase="mid", tier="B", dlc=["The Queen and the Sea"],
      core={"weapons": ["Hand Hook", "Front Line Shield"], "skills": ["Pollo Power", "Swarm"], "mutations": ["Combo", "Open Wounds", "Instinct of the Master of Arms"]},
      alternatives={"weapons": ["Impaler", "Bladed Tonfas"], "skills": ["Grappling Hook", "Taunt"], "mutations": ["Scheme", "Initiative", "Ripper"]},
      statFocus="Brutalität für Hand Hook, Schild und Mutationen; Taktik als Zweitfarbe für Pollo Power und Swarm.",
      affixes=["Miracle of Life (Legendary der Pollo Power: Küken schlüpfen)", "Bleed on Hit (Legendary des Hand Hook)", "+60 % gegen Blutende"],
      whyItWorks="Pollo Power verwandelt dich kurz in ein Huhn, das explosive Eier legt; ab dem zweiten Ei pro Gegner ist jeder Treffer ein Krit und 15 % stärker als der vorige. Die Eier zählen als Nahkampf und lösen laut JoDirac u. a. Combo, Open Wounds, Instinct of the Master of Arms und Front Line Shield aus – die Krits verkürzen so sogar die eigene Abklingzeit. Der Hand Hook schleudert Gegner hinter dich und kritet, wenn sie an eine Wand oder in verbündete Biter prallen; Küken aus der Legendary-Pollo-Power und die Biter aus Swarm zählen dafür.",
      howToPlay=["Swarm rufen, dann Gegner mit dem Hand Hook in die Biter oder gegen die Wand werfen.", "Pollo Power mitten in Gruppen oder unter Bossen zünden – du bleibst angreifbar, also nicht in volle Angriffe hinein.", "Nach einer Parade mit dem Front Line Shield 6 s lang +50 % Nahkampfschaden nutzen.", "Mit Wish (falls vorhanden) die Pollo Power legendär machen."],
      strengths=["Pollo Power ist einer der stärksten Burst-Skills gegen Bosse", "Viele Mutationen werden von den Eiern ausgelöst", "Laut JoDirac auf 5 BC gespielt"],
      weaknesses=["Küken-Krit nur mit legendärer Pollo Power", "Während der Verwandlung keine Rolle, keine Waffen", "Hand Hook + Swarm und die Mutationswahl sind aus der Quellenliste und dem Wiki abgeleitet; Pollo Power stürzt laut Steam-Bugreport gegen Thorny ab"],
      mutationWhy={
          "Combo": "Die Eier gelten als Nahkampftreffer und kommen in schneller Folge – Combo stapelt mit jedem Ei.",
          "Open Wounds": "Jedes Ei legt Blutung an; mit dem Bleed-Affix des Hand Hook wird daraus schnell ein Blutstoß.",
          "Instinct of the Master of Arms": "Fast jedes Ei ist ein Krit – das verkürzt die Abklingzeit der Pollo Power selbst und die von Swarm.",
      },
      sources=["r3-yt-jodirac-pollo", "r3-wiki-pollo", "r3-wiki-handhook"]),

    # ---------- Serenade ----------
    B(id="serenade-duett", name="Serenade-Duett", tagline="Fliegendes Schwert markiert, Schwert in der Hand kritet – und umgekehrt; mit Wish bleibt die Serenade ewig aktiv.",
      color="brutality", secondaryColor=None, archetype="Begleiter, Krit-Nahkampf", difficulty=2, bcMin=1, bcMax=5, phase="mid", tier="B", dlc=["Fatal Falls"],
      core={"weapons": ["Sadist's Stiletto", "Rampart"], "skills": ["Serenade", "Phaser"], "mutations": ["Wish", "Open Wounds", "Instinct of the Master of Arms"]},
      alternatives={"weapons": ["Balanced Blade", "Front Line Shield"], "skills": ["Powerful Grenade", "Ice Armor"], "mutations": ["No Mercy", "Combo", "Necromancy"]},
      statFocus="Brutalität voll – Serenade skaliert nur damit, der Stiletto mit Brutalität/Taktik.",
      affixes=["Durability Up (Legendary der Serenade: bleibt dauerhaft aktiv)", "+60 % gegen Blutende", "Movespeed nach Krit"],
      whyItWorks="Die Serenade wird als fliegendes Schwert beschworen und markiert getroffene Gegner; ein zweites Aktivieren holt sie als Handwaffe in den Waffenslot ihrer Seite. Treffer gegen Ziele mit der jeweils anderen Markierung kritten – du wechselst also zwischen Begleiter und Handwaffe. Ohne Krit verschwindet sie nach 30 s; die Legendary-Version bleibt dauerhaft. Modesto nennt Serenade als eines der Items, für das sich Wish lohnt; XeroIQ spielte sie mit Open Wounds, No Mercy und Instinct of the Master of Arms.",
      howToPlay=["Wish früh nehmen und erst beim Aufheben der Serenade auslösen lassen.", "Serenade beschwören, markieren lassen, dann in die Hand holen und die markierten Gegner kritten – danach wieder fliegen lassen.", "Phaser hinter Gegner für den Eröffnungshieb, Rampart-Paraden als Sicherheit.", "Keine anderen Begleiter-Skills mitnehmen – die Serenade zerstört sie."],
      strengths=["Dauerhafter Begleiter-Schaden plus Krit-Handwaffe", "Mehrfach auf 5 BC gezeigt", "Open Wounds erfüllt nebenbei die Krit-Bedingung des Stiletto"],
      weaknesses=["Blueprint im Geheimbereich der Fractured Shrines", "Wish sperrt danach den Mutations-Slot für den Rest des Runs", "Waffen und Phaser redaktionell ergänzt; die Quellen nennen nur Serenade und die Mutationen"],
      mutationWhy={
          "Wish": "Macht das nächste aufgehobene Item legendär – bei der Serenade heißt das 'Durability Up': sie verschwindet nie (Modesto).",
          "Open Wounds": "Nahkampftreffer der Serenade in der Hand und des Stiletto bluten; der Stiletto kritet dann gegen jedes angeschlagene Ziel (aus XeroIQs Mutationsliste).",
          "Instinct of the Master of Arms": "Der Wechsel-Krit der Serenade kommt ständig und verkürzt dabei Phaser (aus XeroIQs Mutationsliste).",
      },
      bossMutations=["No Mercy"],
      bossMutationsWhy="Nach dem Auslösen ist Wish gesperrt; vor Bossen tauscht man daher Open Wounds gegen No Mercy, das XeroIQ ebenfalls spielte – Adds unter 15 % fallen sofort.",
      sources=["r3-yt-modesto-serenade", "r3-yt-xeroiq-serenade", "r3-wiki-serenade"]),

    # ---------- Diverse Deck ----------
    B(id="vorsehungs-fluch", name="Vorsehungs-Fluch", tagline="Cursed Sword stirbt beim ersten Treffer – die Foresight-Karte des Diverse Deck fängt genau diesen Treffer ab.",
      color="brutality", secondaryColor="survival", archetype="Glaskanone, High-Skill", difficulty=3, bcMin=1, bcMax=5, phase="mid", tier="B", dlc=["Rise of the Giant"],
      core={"weapons": ["Cursed Sword", "Rampart"], "skills": ["Ice Armor", "Diverse Deck"], "mutations": ["Killer Instinct", "Initiative", "Blind Faith"]},
      alternatives={"weapons": ["Front Line Shield", "Parry Shield"], "skills": ["Cocoon", "Phaser"], "mutations": ["Scheme", "Combo", "Ygdar Orus Li Ox"]},
      statFocus="Brutalität für das Cursed Sword, Überleben als Zweitfarbe für Ice Armor und Rampart (mehr HP helfen hier kaum – Schutz kommt aus Negieren).",
      affixes=["Upgraded Foresight (Legendary des Diverse Deck: Passiv nach 5 statt 8 Kills)", "True Evil (Legendary des Cursed Sword)", "+Damage"],
      whyItWorks="Das Cursed Sword macht enormen Schaden, aber jeder Treffer tötet dich. Die Foresight-Karte des Diverse Deck verhindert passiv den ersten Schaden und lädt sich nach 8 Kills neu; abgeworfen macht sie dich 2 s immun. Ice Armor schluckt einen weiteren Treffer, Rampart-Paraden blocken komplett und erzeugen 2 s Kraftfeld. VeeDotMe nannte genau diese drei Teile (Cursed Sword, Ice Armor, Diverse Deck mit Foresight) seinen '100 % zuverlässigen' Cursed-Sword-Build.",
      howToPlay=["Diverse Deck bis zur Foresight-Karte durchschalten und dort lassen – die Kills zählen nur, solange Foresight auf der Hand ist.", "Ice Armor vor jedem Raum aktiv haben; Foresight und Rüstung sind zwei Leben pro Kampf.", "Gegen gefährliche Angriffe Foresight abwerfen: 2 s Immunität.", "Rampart nur zum Parieren nutzen, nicht zum Halten."],
      strengths=["Sehr hoher Grundschaden", "Zwei verlässliche Treffer-Puffer", "Paraden senken über Blind Faith die Abklingzeiten"],
      weaknesses=["Jeder Fehler nach verbrauchtem Puffer ist der Tod", "Foresight lädt nur über Kills – gegen Bosse ohne Adds bleibt nach dem ersten Treffer nur Ice Armor", "VeeDotMe spielte im Custom Mode; Rampart und die Mutationen redaktionell ergänzt"],
      mutationWhy={
          "Killer Instinct": "Jeder Nahkampf-Kill senkt die Abklingzeiten von Ice Armor und Diverse Deck – der Schutz ist schneller wieder da.",
          "Initiative": "Der erste Hieb gegen jeden Gegner trifft mit +100 – mit dem Cursed Sword fallen die meisten Mobs damit sofort.",
          "Blind Faith": "Jede Rampart-Parade verkürzt Ice Armor um mehrere Sekunden.",
      },
      sources=["r3-yt-vee-cursed-deck", "r3-wiki-diversedeck"]),

    # ---------- War Javelin ----------
    B(id="sparta-speer", name="Sparta-Speer", tagline="Spartan Sandals treten Gegner gegen die Wand, der War Javelin spießt sie dort für +90 Schaden auf.",
      color="tactics", secondaryColor="brutality", archetype="Wandschaden, Knockback, Mobilität", difficulty=2, bcMin=0, bcMax=5, phase="any", tier="B", dlc=["Rise of the Giant"],
      core={"weapons": ["Spartan Sandals", "War Javelin"], "skills": ["Grappling Hook", "Wolf Trap"], "mutations": ["Ammo", "Networking", "Tactical Retreat"]},
      alternatives={"weapons": ["Hayabusa Boots", "Impaler"], "skills": ["Wave of Denial", "Phaser"], "mutations": ["Initiative", "Kill Rhythm", "Necromancy"]},
      statFocus="Taktik voll (War Javelin, Wolf Trap, Networking), Brutalität als Zweitfarbe für Sandals und Grappling Hook.",
      affixes=["Super Bump (Legendary der Sandals)", "Fire Bullet (Legendary des Javelin)", "+Damage near walls"],
      whyItWorks="Die Spartan Sandals stoßen Gegner weg und verursachen +90, wenn sie gegen eine Wand prallen. Der War Javelin durchbohrt alle Gegner auf seinem Weg, verursacht ebenfalls +90 nahe einer Wand und teleportiert dich beim erneuten Drücken zum Speer. So drückst du Gruppen an die Wand und spießt sie dort auf; Grappling Hook zieht Weggetretene zurück. VeeDotMe spielte Spartan Sandals + Javelin 2020 als Viewer-Build auf 5 BC.",
      howToPlay=["Gegner mit den Sandals gegen die nächste Wand treten.", "Javelin durch die ganze Reihe an der Wand werfen – erneut drücken, um hinterherzuteleportieren.", "Weggetretene mit Grappling Hook zurückholen, Wolf Trap für Bosse.", "Mit Ammo (seit 3.4 wirksam) zwei Speere werfen, bevor du teleportierst."],
      strengths=["Doppelter Wandbonus", "Javelin-Teleport als Ausweich- und Angriffswerkzeug", "Sandals früh verfügbar"],
      weaknesses=["Offene Räume ohne Wände halbieren den Schaden", "Javelin muss eingesammelt werden (oder kommt nach 10 s zurück)", "Skills und Mutationen redaktionell ergänzt; Quelle von 2020 (1.9)"],
      mutationWhy={
          "Ammo": "Seit 3.4 verdoppelt Ammo auch die Javelins – zwei Würfe vor dem Teleport.",
          "Networking": "Der Javelin durchbohrt die ganze Reihe und markiert alle; markierte Ziele teilen sich den Schaden, den eines davon erleidet.",
          "Tactical Retreat": "Last-Second-Rollen verlangsamen die Gegner um dich – Zeit, sie zur Wand zu treten.",
      },
      sources=["r3-yt-vee-sandals-jav", "r3-wiki-warjavelin"]),

    # ---------- Cluster Grenade ----------
    B(id="splitter-streubombe", name="Splitter und Streubombe", tagline="Shrapnel Axes in Brutalität, Alchemic Carbine vergiftet, Stun Grenade hält fest, Cluster Grenade zerlegt die Gruppe.",
      color="brutality", secondaryColor="tactics", archetype="Flächenschaden, Hybrid", difficulty=1, bcMin=0, bcMax=3, phase="early", tier="B", dlc=[],
      core={"weapons": ["Shrapnel Axes", "Alchemic Carbine"], "skills": ["Stun Grenade", "Cluster Grenade"], "mutations": ["Combo", "Killer Instinct", "Heart of Ice"]},
      alternatives={"weapons": ["The Boy's Axe", "Hokuto's Bow"], "skills": ["Powerful Grenade", "Oil Grenade"], "mutations": ["Ripper", "Necromancy", "Melee"]},
      statFocus="Brutalität für die Äxte und Cluster Grenade (Brutalität/Überleben), Taktik als Zweitfarbe für Carbine und Splitter.",
      affixes=["Echo (Legendary der Cluster Grenade: explodiert ein zweites Mal)", "+80 % gegen Vergiftete", "Fire Bullet (Legendary der Shrapnel Axes)"],
      whyItWorks="Die Cluster Grenade zerfällt in sechs Bomben zu je 50 Schaden und trifft in kleinen Räumen fast alles mehrfach. Stun Grenade betäubt 4,5 s – Zeit für Cluster Grenade und eine volle Axt-Kombo. Die Alchemic Carbine vergiftet aus Abstand, sodass Affixe gegen Vergiftete auf Äxten und Granaten ständig greifen. VeeDotMe gewann mit genau diesem Loadout 2019 auf 2 BC.",
      howToPlay=["Gruppen mit der Stun Grenade betäuben, Cluster Grenade direkt hinterher.", "Mit den Äxten im Nahkampf nachsetzen, auf Abstand fliegen Splitter.", "Carbine auf gefährliche Ziele halten, damit sie vergiftet bleiben.", "Kleine Räume bevorzugen – dort trifft die Cluster Grenade am besten."],
      strengths=["Früh verfügbare Teile", "Sehr hoher Flächenschaden pro Granate", "Betäubung schafft sichere Angriffsfenster"],
      weaknesses=["Quelle von 2019 (1.2) – seither: Cluster Grenade löst keine Abklingzeit-Mutationen mehr aus, Shrapnel Axes leicht gebufft", "Ab 4 BC fehlt Krit-Schaden", "Mutationen redaktionell ergänzt"],
      mutationWhy={
          "Combo": "Die Äxte treffen schnell; jeder Treffer stapelt Combo.",
          "Killer Instinct": "Nahkampf-Kills mit den Äxten verkürzen beide Granaten.",
          "Heart of Ice": "Treffer auf betäubte Gegner aus der Nähe verkürzen die Abklingzeiten – nach jeder Stun Grenade kommt die nächste schneller.",
      },
      sources=["r3-yt-vee-shrapnel12", "r3-wiki-cluster"]),
]
