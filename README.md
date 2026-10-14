# Prisoner's Guide – Dead Cells

Inoffizieller, deutschsprachiger Begleiter für **Dead Cells** (Stand 3.5 „The End is Near“, inkl. aller DLCs):

- **Builds** – kuratiert aus Community-Konsens, sortiert nach deiner Boss-Cell-Stufe und deinen Freischaltungen
- **Was passt zusammen?** – Synergie-Werkstatt: Loadout zusammenstellen, Farben/Krit-Bedingungen/bekannte Kombos prüfen, Vorschläge für freie Plätze
- **Routenplaner** – interaktive Biom-Karte mit empfohlenen Routen, Schriftrollen, Zeittüren, Runen und Entwürfen auf dem Weg
- **Waffen & Skills, Mutationen, Tierlisten** – mit Krit-Bedingung, Werten, Entwurf-Fundort und Partnern
- **Biome, Bosse, Runen, Boss Cells** – Ausgänge, Tipps, Boss-Taktiken, was sich auf jeder BC-Stufe ändert
- **Freischaltungen** – persönlicher Tracker inkl. „Entwurf-Atlas“ (was fehlt mir in welchem Biom?), Outfits, Export/Import
- **Wissen** – Collector-Upgrades, Affixe, Statuseffekte, Glossar, Tipps

Alles läuft statisch im Browser (keine Abhängigkeiten, kein Build-Schritt). Fortschritt wird nur lokal im `localStorage` gespeichert.

## Lokal starten

```bash
python -m http.server 8000
```

Dann <http://localhost:8000> öffnen. (Direkt per `file://` geht es nicht, weil die Daten per `fetch` geladen werden.)

## Struktur

| Pfad | Inhalt |
| --- | --- |
| `index.html`, `css/`, `js/` | App (ES-Module, Hash-Router, eine Datei pro Ansicht in `js/views/`) |
| `data/*.json` | Datenbasis: `gear`, `mutations`, `outfits`, `world`, `builds`, `meta`, `mechanics`, `names-de` |
| `assets/` | Icons und Bilder (aus dem Dead Cells Wiki), Schriften (selbst gehostet) |
| `tools/` | Python-Skripte, mit denen die Daten aus der Wiki-API gebaut wurden, plus `validate.py` |

`python tools/validate.py` prüft die Daten auf Konsistenz (läuft auch vor jedem Deployment).

## Deployment

GitHub Pages über die Action in `.github/workflows/pages.yml` (Repo-Einstellungen → Pages → Source: „GitHub Actions“).

## Quellen & Rechtliches

Spieldaten aus dem [Dead Cells Wiki](https://deadcells.wiki.gg) (CC BY-SA) und den offiziellen Patchnotes; Builds, Tierlisten und Routen sind redaktionelle Einschätzungen aus mehreren Community-Quellen (siehe `data/builds.json` / `data/meta.json`).
Fan-Projekt ohne Verbindung zu Motion Twin, Evil Empire oder Playdigious. „Dead Cells“, Grafiken und Namen gehören ihren Rechteinhabern.
