# Gemeinsamer Recherche-Brief: Dead Cells Fan-Guide

Ziel: Eine statische, deutschsprachige Fan-Website (GitHub Pages) über Dead Cells, die Spielern hilft:
beste Builds, Routen, Waffen und Synergien, Freischaltungen (Entwürfe/Blueprints), Mutationen, Boss-Cell-Stufen (0–5 BC) usw.
Spielstand: finale Version 3.5 „The End is Near“ inklusive aller DLCs (Rise of the Giant, The Bad Seed, Fatal Falls,
The Queen and the Sea, Return to Castlevania) und kostenloser Updates (z. B. „Everyone is Here“ — zählt als Basisspiel).

Projektwurzel: `F:/fun/deadcells-expädde/`
- Fertige Daten: `data/*.json` (UTF-8, ohne BOM, schön formatiert mit indent=1 oder 2, `ensure_ascii=False`).
- Bilder: `assets/<bereich>/<id>.png`.
- Eigene Skripte: `tools/*.py`. Rohdaten/Caches: `research/cache/<bereich>/…` (darf groß sein).
- Den Ordner `_alt-openai/` und `prisoners-guide/` NICHT verändern (nur lesen erlaubt; dort gibt es Vorarbeiten, z. B.
  `_alt-openai/research-gear.json`, `_alt-openai/research-builds.json`, `_alt-openai/research-routes.json`).

## Quellen & Zugriff
- Primär: Dead Cells Wiki auf wiki.gg. Die MediaWiki-API funktioniert:
  `https://deadcells.wiki.gg/api.php?action=parse&page=<Titel>&prop=wikitext|text&format=json`
  `…?action=query&list=categorymembers&cmtitle=Category:<X>&cmlimit=500&format=json`
  `…?action=query&titles=File:<Name>.png&prop=imageinfo&iiprop=url&format=json` (Bild-URLs)
  Benutze `requests` mit User-Agent `Mozilla/5.0 (DeadCellsFanGuide research)`, höchstens ~2 Anfragen/Sekunde,
  bei HTTP 429 `Retry-After` respektieren. Antworten in `research/cache/` cachen, damit erneute Läufe nichts neu laden.
- Ergänzend: offizielle Patchnotes (dead-cells.com), Reddit r/deadcells, Steam-Guides, YouTube-Beschreibungen,
  Fandom-Wiki (deadcells.fandom.com, teils veraltet – wiki.gg hat Vorrang). Nutze WebSearch/WebFetch dafür.
- Python mit Dateien aus dem Netz: Skripte in `tools/`, mit `python -I` ausführen.

## Konventionen
- Spiel-Eigennamen (Items, Mutationen, Gegner, Biome, Bosse) IMMER exakt im englischen Wiki-Schreibweise in `name`.
  Optional `nameDe` (deutscher Spielname), nur wenn verlässlich belegt, sonst `null`.
- Alle Erklärtexte auf Deutsch, eigene knappe Formulierungen (keine Wiki-Texte kopieren). Zahlen/Mechaniken korrekt.
- Biome und Bosse werden über ihre exakten englischen Namen referenziert (z. B. "Prisoners' Quarters",
  "Promenade of the Condemned", "Black Bridge", "Throne Room"). ID = slug: Kleinbuchstaben, Nicht-Alphanumerisches → "-",
  Apostrophe entfernen (z. B. "prisoners-quarters", "high-peak-castle", "the-concierge" → Bosse ohne "The": "concierge").
- Farben/Scaling: "brutality" | "tactics" | "survival" | "colorless".
- DLC-Feld: null (Basisspiel/kostenlose Updates) oder exakt einer von
  "Rise of the Giant", "The Bad Seed", "Fatal Falls", "The Queen and the Sea", "Return to Castlevania".
- Ehrlichkeit vor Vollständigkeit: Unsicheres als `null` lassen oder in einem `notes`-Feld kennzeichnen. Nichts erfinden.
- Am Ende: kurzer Bericht (max. ~15 Zeilen): was erzeugt wurde, Anzahl Einträge, bekannte Lücken/Unsicherheiten.
