# Brief: Mehr Builds (Runde 2)

Feedback des Nutzers: „Es sind zu wenige Builds – auch mit den Mutationen.“ Ziel: deutlich mehr Builds, und **jeder Build
mit vollständigem Loadout inklusive drei Mutationen, jeweils begründet**.

Allgemeine Regeln aus `research/BRIEF.md` gelten (Deutsch, exakte englische Wiki-Namen, nichts erfinden).

## Wo und wie
- Vorhandene Builds: `tools/meta_builds.py` (NICHT editieren). Generator: `tools/build_meta.py`.
- Du schreibst **eine eigene Datei** `tools/meta_builds_more_<dein-kürzel>.py` mit:
  ```python
  SRC = {"kuerzel": "https://…"}          # neue Quellen-Kürzel (bestehende aus meta_builds.SRC dürfen genutzt werden)
  BUILDS = [ {…}, … ]                       # neue Builds, gleiches Schema wie in meta_builds.py
  PATCHES = {"build-id": {"core": {...}, "mutationWhy": {...}, ...}}   # Ergänzungen für bestehende Builds deiner Farbe
  ```
  Schreibe die Datei erst unter einem anderen Namen (z. B. `_draft_<kürzel>.py`) und benenne sie erst um, wenn
  `python -I tools/build_meta.py --check` für deine Builds keine Fehler mehr meldet (andere Agenten arbeiten parallel;
  Fehler in fremden Builds ignorierst du). **Niemals ohne `--check` ausführen** – das finale Schreiben macht der Koordinator.
- `--check` prüft alle Namen gegen den Wiki-Cache, DLC-Ableitung, Quellen-Kürzel und Vollständigkeit.

## Schema je Build (alle Felder Pflicht, außer markiert)
`id` (slug, eindeutig), `name` (deutsch, griffig, nicht doppelt), `tagline` (1 Satz), `color`
(brutality|tactics|survival|colorless|hybrid), `secondaryColor` (oder None), `archetype`, `difficulty` (1–3),
`bcMin`, `bcMax`, `phase` (early|mid|late|any), `tier` (S|A|B), `dlc` (Liste; muss exakt den DLCs der Kern-Waffen/-Skills
entsprechen – `--check` sagt dir, was erwartet wird),
`core`: `weapons` = **genau 2** (oder genau 1 Zweihänder wie Repeater Crossbow, Heavy Crossbow, Ice Crossbow, Explosive
Crossbow, Scythe Claw, Whip Sword, Hard Light Sword, Ferryman's Lantern), `skills` = **genau 2**, `mutations` = **genau 3**,
`alternatives` (weapons/skills/mutations, je 1–4),
`mutationWhy` = `{Mutation: "Deutsch, 1 Satz, warum genau diese Mutation in diesem Build"}` für **alle 3** Kern-Mutationen,
`bossMutations` (optional, 1–3 Mutationen, die man vor Bossen beim Respec tauscht) + `bossMutationsWhy` (1 Satz),
`statFocus`, `affixes` (2–4), `whyItWorks` (2–4 Sätze Mechanik), `howToPlay` (3–5 Schritte), `strengths`, `weaknesses`,
`sources` (Kürzel; mindestens 1, ehrlich – eine reine Mechanik-Herleitung aus Wiki-Seiten ist ok, dann Wiki-URL als Quelle).

## Qualitätsziele
- Mechanisch stimmig (Krit-Bedingungen, Farb-Skalierung, Cooldown-Synergien). Bei Unsicherheit Wiki-Seite prüfen
  (Cache: `research/cache/`, API siehe BRIEF.md). Patchstand 3.5 beachten (Nerfs!).
- Vielfalt: verschiedene Hauptwaffen, Einsteiger-Builds mit früh verfügbaren Items (0–1 BC), Endgame-Builds (4–5 BC),
  Boss-Killer vs. Biom-Clear, DLC-Items. Möglichst viele verschiedene Mutationen sinnvoll einsetzen (auch weniger
  bekannte wie Initiative, Porcupack, Parting Gift, Ripper, Ranger's Gear, Crow's Foot, Tactical Retreat, Adrenaline,
  Spite, Recovery, Extended Healing, Velocity, Get Rich Quick, Gold Plating, Masochist, Ygdar Orus Li Ox, Damned Vigor …),
  aber nur wo es wirklich passt.
- Keine Duplikate bestehender Builds (Liste in `data/builds.json`); Varianten nur mit klar anderem Kern.
- Community-Quellen: Steam-Foren/-Guides, YouTube-Titel/Beschreibungen, Wiki; Reddit ist meist nicht abrufbar.

## Abschluss
Kurzer Bericht (≤ 12 Zeilen): Anzahl neuer Builds, gepatchte Builds, welche Mutationen neu abgedeckt sind, Unsicherheiten.
