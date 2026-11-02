---
version: 1
slug: "index-html"
primary_target: "index.html"
related_targets: ["css/style.css","js/main.js"]
---

# Surface brief: Prisoner's Guide (whole app shell + all views)

Scope: the entire static guide (`index.html`, `css/style.css`, `js/main.js`, `js/views/*`). Visitor mode: **Read** (with Operate tools inside: workshop, route planner, unlock tracker).
Audience/job: the author and friends, German-speaking Dead Cells players, at the desk between runs or in long browsing sessions; they want to find the next build/route and understand why it works.
Constraints: no build step, no dependencies, self-hosted fonts, game sprites from the wiki stay the imagery, fan disclaimer stays, all content/features preserved.
Unresolved: dark-room variant of the page (not requested); bigger combo database is a separate content task.

## Direction contract

THESIS: The guide is a printed strategy guide (Piggyback lineage) laid open on a dark desk: chapters, running heads, a fore-edge thumb index, numbered callouts and dense tables. It refuses the game-database default of dark panels, card grids and neon accents.

OWN-WORLD: White coated page (#fff) lying on near-black "desk" (#18181a); ink #121212. Three chapter colours own their chapters: ochre #e9a21a (Run vorbereiten), teal #0f8b8d (Nachschlagen), cell blue #1677c9 (Fortschritt). Scaling colours red/purple/green stay data chips only. Heavy Barlow Condensed (800/900, uppercase) for titles and table heads; Inter for the reading column. 3px black rules under section heads; tables with black header rows and tabular figures. State is a mark, not a hue: owned = check stamp, locked = struck/punched, missing = dashed outline.

STORY: The reader opens a chapter, knows where they stand from the running head and thumb tab, reads a calm column, and finds the answer in a table or a numbered loadout callout; then turns the page (next/prev) or jumps chapters.

FIRST VIEWPORT: Black top strip (logo, search, BC selector, EN/DE, profile). Left: contents rail on the dark desk, numbered 1.1, 1.2 … grouped by chapter, each chapter's number in its colour. Centre: the white page with a running head (chapter number + name, section), a chapter-coloured thumb tab on the page's right fore-edge (three tabs stacked, current one extends), big uppercase title, lede at 60–70ch, then content: tables, loadout plates with numbered callouts.

FORM: The Solution Book, my own grounded candidate #1 (IMPECCABLE'S PICK), chosen by the user over the assigned #4. seed:5edaa1efaf3a0c2f. Kept from declined challengers: tables at real data density (datamatics); state as mark not hue (cutting bench); scaling colour confined to chips/edges, reading column achromatic (cloud).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
