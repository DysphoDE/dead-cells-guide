# Brief: Kombinations-Datenbank (Runde 3)

Wunsch des Nutzers: „eine viel größere Datenbank bewährter Kombinationen“. Diese Runde deckt drei Inhalte ab:
Synergie-Paare, Mutations-Trios und Builds für Items, die noch in keinem Build vorkommen.

**Harte Regel: nur Community-belegt.** Jeder neue Eintrag braucht mindestens eine URL zu einer Spielerquelle, die
**genau diese Kombination** nennt (beide Items/alle drei Mutationen). Eine reine Mechanik-Herleitung aus Wiki-Texten
zählt in dieser Runde nicht, so plausibel sie ist. Lieber weniger Einträge als erfundene.

Allgemeine Regeln aus `research/BRIEF.md` gelten weiter: Erklärtexte auf Deutsch in eigenen Worten, Eigennamen exakt
in englischer Wiki-Schreibweise, nichts erfinden, Patchstand 3.5 beachten.

## Was als Quelle zählt
- **Ja:**
  - Steam-Diskussionen und Steam-Guides (steamcommunity.com)
  - Reddit-Threads: direkt gesperrt, aber per Websuche auffindbar. Nur, wenn Titel oder Snippet die Kombination sichtbar nennt; dann im `evidence`-Feld „Snippet“ vermerken.
  - YouTube-Videos, deren Titel oder Beschreibung die Kombination nennt
  - Foren (GameFAQs u. Ä.)
  - Spieler-Guides auf Gaming-Seiten, wenn sie die Kombination konkret begründen
- **Nein:**
  - Wiki allein (deadcells.wiki.gg, fandom)
  - Seiten, die Items erfinden: BeatCop, gamedatacentral
  - Reine Tier-Listen ohne Kombinationsaussage
  - KI-generierte Listen
- **Alte Quellen:** Stammt eine Quelle von vor 3.4 (August 2023) und wurde ein beteiligtes Item seitdem generft oder umgebaut (siehe `research/meta-sources.md`), dann prüf die Kombination gegen die Wiki-History.
  - Gilt sie weiter, schreib die Einschränkung ins `why`.
  - Gilt sie nicht mehr, lass den Eintrag weg.

## Werkzeuge
- **Websuche und Seitenabruf:** WebSearch / WebFetch. Die Wiki-API ist erreichbar, z. B. `https://deadcells.wiki.gg/api.php?action=parse&page=<Titel>&prop=wikitext&format=json` (höchstens etwa 2 Anfragen pro Sekunde).
- **Python mit Netzdaten:** nur mit `python -I`.
- **Kanonische Namen:** `data/gear.json` (`items[].name`, `colors`, `type`) und `data/mutations.json` (`mutations[].name`). Vorhandene Kombis: `data/meta.json` (`synergies`, `mutationSets`), Builds: `data/builds.json`.

## Dateien und Prüfung
- **Nur deine eigene Datei bearbeiten.** Andere Agenten arbeiten parallel. Sonst nichts anfassen, auch nicht `data/*.json`.
- **Erst als Entwurf schreiben:** `tools/_draft_<kürzel>.py` (Entwürfe werden nicht geladen).
- **Prüfen:** Kopier den Entwurf nach `tools/meta_synergies_more_<kürzel>.py` (Builds: `tools/meta_builds_more_<kürzel>.py`) und führ `python -I tools/build_meta.py --check` aus.
  - Melden fremde Dateien Fehler, ignorier sie.
  - Behebe nur deine eigenen.
  - Meldet die Prüfung ein Duplikat mit einem anderen Agenten, streich deinen Eintrag.
- **Niemals ohne `--check` ausführen.** Das endgültige Schreiben übernimmt der Koordinator.
- **Fertig:** Deine Datei liegt unter dem endgültigen Namen, und `--check` meldet für sie keine Fehler mehr.

### Schema: Synergie-Paare (`tools/meta_synergies_more_<kürzel>.py`)
```python
SYNERGIES = [
    {"items": ["Name A", "Name B"],          # genau 2, exakte Wiki-Namen
     "kind": "weapon+skill",                 # weapon+weapon | weapon+skill | skill+skill | weapon+mutation | skill+mutation | mutation+mutation
     "why": "1–2 Sätze Deutsch: welcher Mechanismus die beiden verbindet (z. B. A erzeugt X, B kritet gegen X).",
     "sources": ["https://…"],               # mindestens 1 Community-URL, die diese Kombi nennt
     "evidence": "kurz: wo/wie die Quelle es sagt (Zitat-Paraphrase, Datum, ggf. 'Snippet')"},  # wird nicht veröffentlicht
]
```
Die Reihenfolge der Items folgt `kind` (Waffe zuerst, dann Skill, dann Mutation). Schilde zählen als `weapon`.

### Schema: Mutations-Trios (im selben Modul möglich)
```python
MUTATION_SETS = [
    {"name": "Deutscher, griffiger Name", "color": "brutality",   # brutality|tactics|survival|colorless|hybrid
     "mutations": ["A", "B", "C"], "forWhat": "Für welche Waffen/Spielweise",
     "why": "1–2 Sätze Mechanik", "sources": ["https://…"], "evidence": "…"},
]
```

### Builds
Schema und Regeln wie in `research/BRIEF-builds.md`, Datei `tools/meta_builds_more_<kürzel>.py`. Zusätzlich muss
jeder Build mindestens ein Quellen-Kürzel haben, das auf eine Community-URL zeigt (eine Wiki-URL allein reicht nicht).

## Ziel und Bericht
- **Abdeckung:** jedes Item in deinem Bereich bekommt möglichst 2–3 belegte Partner. Bevorzugt stärkere, häufig genannte Kombis.
- **Mutationen:** Paare mit Mutationen (weapon+mutation) zählen voll.
- **Bericht am Ende** (höchstens etwa 15 Zeilen):
  - Anzahl der Einträge
  - welche Quellen am meisten trugen
  - welche Items ohne belegten Partner geblieben sind
  - Unsicherheiten
