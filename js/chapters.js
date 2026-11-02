// Gliederung des Guides: Kapitel → Abschnitte. Treibt Inhaltsverzeichnis, Kolumnentitel, Daumenregister und Blättern.
export const CHAPTERS = [
  {
    n: 1, title: 'Run vorbereiten', sections: [
      ['', 'Übersicht', 'Dein Spielstand und was du als Nächstes spielen kannst.'],
      ['builds', 'Builds', 'Kuratierte Builds, sortiert nach deiner BC und deinen Freischaltungen.'],
      ['workshop', 'Was passt zusammen?', 'Loadout zusammenstellen und Synergien prüfen.'],
      ['routes', 'Routenplaner', 'Empfohlene Routen mit Schriftrollen, Zeittüren und Entwürfen.'],
    ],
  },
  {
    n: 2, title: 'Nachschlagen', sections: [
      ['arsenal', 'Waffen & Skills', 'Jede Waffe, jeder Skill mit Krit-Bedingung und Fundort.'],
      ['mutations', 'Mutationen', 'Alle Mutationen plus bewährte 3er-Kombis.'],
      ['tiers', 'Tierlisten', 'Waffen, Skills, Schilde und Mutationen nach Stärke.'],
      ['world', 'Biome & Bosse', 'Ausgänge, Schriftrollen und Boss-Taktiken.'],
      ['bc', 'Boss Cells', 'Was sich auf jeder BC-Stufe ändert.'],
      ['knowledge', 'Wissen & Mechaniken', 'Collector-Upgrades, Affixe, Statuseffekte, Glossar.'],
    ],
  },
  {
    n: 3, title: 'Fortschritt', sections: [
      ['unlocks', 'Freischaltungen', 'Dein Tracker samt Entwurf-Atlas.'],
      ['outfits', 'Outfits', 'Alle Outfits und wo es sie gibt.'],
    ],
  },
];

// Detailseiten gehören zum Abschnitt ihrer Liste
export const PARENT = { build: 'builds', item: 'arsenal', mutation: 'mutations', biome: 'world', boss: 'world', about: 'knowledge' };

/** Flache Liste aller Abschnitte mit Kapitel und Nummer („1.2“). */
export const SECTIONS = CHAPTERS.flatMap((c) => c.sections.map(([path, label, blurb], i) => ({ path, label, blurb, ch: c, no: `${c.n}.${i + 1}` })));

export const sectionFor = (path) => SECTIONS.find((s) => s.path === (PARENT[path] ?? path)) ?? null;
