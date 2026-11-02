# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Static HTML/CSS/vanilla ES modules, no build step, no dependencies. Hash router, one file per view in `js/views/`. Data in `data/*.json` built by Python scripts in `tools/`. Deployed via GitHub Pages. Fonts are self-hosted in `assets/fonts/`.

## Purpose

Prisoner's Guide is an unofficial, German-language companion for Dead Cells (final version 3.5 "The End is Near", all DLCs). It answers "what should I play next, and how do I get there?" by combining curated builds, a synergy workshop, a route planner, and reference pages with the player's own progress (Boss Cell level, unlocks, runes, imported savegame).

What sets it apart from the wiki: everything is filtered against *your* state. Builds sort by what you can play right now; routes lock exits your BC/runes/DLCs don't allow; the blueprint atlas shows what is still missing per biome.

## Users

Primarily the author and their friends: German-speaking Dead Cells players across the whole range from first run to 5 BC. Public hosting on GitHub Pages is incidental, not a growth goal.

Usage scenes (confirmed):
- **Between runs at the desk.** Game paused or just died; wide screen beside the game, planning the next build or route.
- **Long browsing sessions.** Reading tier lists, mechanics, and builds for their own sake, away from the game.

Phone use mid-session is not a primary scene (must still work responsively).

## Capabilities

- Builds (97, curated from community consensus) filtered by BC and unlocks; build detail pages with full loadout and three mutations
- "Was passt zusammen?": synergy workshop for loadouts (colors, crit conditions, known combos, suggestions)
- Route planner: interactive biome map, recommended routes, scrolls, timed doors, runes, blueprints on the way
- Reference: weapons & skills (184), mutations (56), tier lists, biomes (37) & bosses (13), Boss Cells, knowledge & mechanics
- Progress: unlock tracker, blueprint atlas, outfits (150), savegame import (`user_0.dat`, PC/Steam), JSON export/import; stored only in localStorage
- Game names switchable EN (wiki spelling) / DE (German game names)

## Content & voice

All explanatory copy in German, own concise wording, informal "du". Game proper nouns keep exact English wiki spelling, with optional German names. Honesty over completeness: uncertain data stays null or is flagged.

## Assets & constraints

- Game sprites (items, mutations, outfits, biomes, bosses) and logo come from the Dead Cells Wiki; graphics and names belong to Motion Twin / Evil Empire. Fan-project disclaimer must stay visible.
- Data licensing: wiki data CC BY-SA, attribution on the About page.
- No external runtime dependencies; everything must run from static files.

## Accessibility

Keyboard navigation (skip link, Ctrl+K search, focus states), reduced-motion respected, German `lang`. Target WCAG AA contrast.

## Open goals

- **Much bigger database of proven combinations** (requested 2026-10-30): currently 65 synergies, 18 mutation sets, 97 builds in `data/meta.json` / `data/builds.json`. Expansion is research/data work, separate from visual redesign; new entries must stay sourced, never invented.
