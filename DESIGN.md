---
name: Prisoner's Guide
description: An unofficial Dead Cells strategy guide, set as a printed solution book lying open on a dark desk.
colors:
  desk: "#18181a"
  desk-raised: "#222225"
  desk-line: "#36363a"
  desk-text: "#ebe9e4"
  desk-muted: "#a6a6a1"
  strip: "#0e0e0f"
  paper: "#ffffff"
  ink: "#121212"
  ink-secondary: "#34363a"
  muted: "#5c5f65"
  dim: "#6c6f75"
  rule-hair: "#e1e0db"
  rule-soft: "#c4c3bd"
  plate: "#f4f3ef"
  plate-2: "#ecebe6"
  plate-3: "#e0dfd9"
  table-zebra: "#faf9f6"
  chapter-ochre: "#e9a21a"
  chapter-ochre-ink: "#855600"
  chapter-ochre-tint: "#fcf1d9"
  chapter-teal: "#0f8b8d"
  chapter-teal-ink: "#0a6668"
  chapter-teal-tint: "#e0f1f1"
  chapter-blue: "#1677c9"
  chapter-blue-ink: "#11599a"
  chapter-blue-tint: "#e2edf8"
  scaling-brutality: "#cf3428"
  scaling-tactics: "#7445cf"
  scaling-survival: "#24803e"
  scaling-colorless: "#8c877d"
  tier-s: "#121212"
  tier-a: "#4a4a4c"
  tier-b: "#6e6e70"
  tier-c: "#cfcfca"
  tier-d: "#ffffff"
typography:
  display:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "clamp(40px, 5.2vw, 76px)"
    fontWeight: 800
    lineHeight: 0.92
    letterSpacing: "-0.005em"
  display-opener:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "clamp(48px, 6.4vw, 96px)"
    fontWeight: 800
    lineHeight: 0.88
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "32px"
    fontWeight: 800
    lineHeight: 1.02
  title:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "24px"
    fontWeight: 800
    lineHeight: 1.02
  body:
    fontFamily: "Inter, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
    fontFeature: "'cv11', 'ss01'"
  lede:
    fontFamily: "Inter, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "14px"
    fontWeight: 700
    letterSpacing: "0.1em"
  table-head:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "15px"
    fontWeight: 700
    letterSpacing: "0.08em"
rounded:
  print: "2px"
  stamp: "50%"
spacing:
  hair: "4px"
  tight: "10px"
  base: "16px"
  column: "24px"
  row: "28px"
  block: "36px"
  section: "56px"
  gutter: "clamp(20px, 4vw, 56px)"
components:
  button:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.print}"
    padding: "0 18px"
    height: "42px"
  button-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.print}"
    padding: "0 18px"
    height: "42px"
  chip:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-secondary}"
    rounded: "{rounded.print}"
    padding: "0 12px"
    height: "34px"
  chip-pressed:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  tag:
    backgroundColor: "{colors.plate-2}"
    textColor: "{colors.ink}"
    padding: "2px 7px"
  tag-boss-cells:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    padding: "2px 7px"
  tier-s:
    backgroundColor: "{colors.tier-s}"
    textColor: "{colors.paper}"
    size: "28px"
  tier-d:
    backgroundColor: "{colors.tier-d}"
    textColor: "{colors.ink}"
    size: "28px"
  input:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.print}"
    padding: "0 12px"
    height: "42px"
  table-head:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.table-head}"
    padding: "7px 12px"
  sprite-plate:
    backgroundColor: "{colors.plate}"
    size: "44px"
---

# Design System: Prisoner's Guide

## Overview

**Creative North Star: "The Solution Book"**

The guide is a printed strategy guide laid open on a dark desk. A single white sheet sits on a near-black desk under a black top strip. The contents rail sits on the desk to the left, and coloured thumb tabs stand out from the sheet's right fore-edge. On the sheet, everything is set like print: a running head with the chapter number and section, heavy condensed uppercase titles, a calm Inter reading column, black-headed tables with tabular figures, and loadout plates with numbered callouts. The page is dense where data is dense and quiet everywhere else.

Structure comes from rules, not from boxes. Every section opens under a 3px ink rule, and entries are separated by hairlines. No section sits inside a tinted or bordered container. Colour does three jobs and nothing else: it marks the chapter you are in, marks an item's scaling colour as a small square, and fills the sprite plates the game art sits on. State is printed as a mark. A check stamp, a dashed outline, hatching with a strike, or a heavy bottom rule each say something a hue never has to.

The build rejects the game-database default of dark panels, card grids and neon accents. Game sprites are the only imagery, always on pale plates with pixelated rendering.

**Key Characteristics:**
- White sheet (paper) on a near-black desk; all reading happens on paper.
- 3px ink rules open sections and entries; hairlines separate rows.
- Barlow Condensed 800 uppercase for titles, labels and table heads; Inter for prose.
- Three chapter colours, each confined to its own chapter.
- State as mark, not hue; tiers on a monochrome ink ramp.
- Scaling colours only as square chips and the 3px sprite-plate bar.
- Near-square print corners (2px); circles only for numbered callouts and stamps.

## Colors

The sheet is achromatic ink on white. Colour is rationed: three chapter hues own their chapters, and three scaling hues appear only as small marks.

### Primary
- **Chapter Ochre** (chapter-ochre, with chapter-ochre-ink for text on white and chapter-ochre-tint for highlights): Chapter 1, Run vorbereiten. Appears as the thumb tab, the chapter number block in the contents rail and running head, the active-section number, the hover rule on entries, the active tab underline, primary-button hover, list bullets and the search/dialog top bar while that chapter is open.
- **Chapter Teal** (chapter-teal / -ink / -tint): Chapter 2, Nachschlagen. Same roles, same places, active only inside chapter 2. Text on the teal block is white.
- **Chapter Blue** (chapter-blue / -ink / -tint): Chapter 3, Fortschritt. Same roles inside chapter 3, with white text on the block.

The active chapter is resolved once on the body (`data-ch`) into `--ch`, `--ch-ink`, `--ch-tint` and `--ch-on`. Components consume only those four variables and never name a chapter directly. The contents rail, thumb tabs and contents index are the exception, since they show all three chapters at once.

### Secondary
- **Scaling Red** (scaling-brutality), **Scaling Violet** (scaling-tactics), **Scaling Green** (scaling-survival), **Scaling Stone** (scaling-colorless): the game's Brutality / Tactics / Survival / colourless scaling. A multi-colour item uses a three-band gradient of the same values.

### Neutral
- **Desk** (desk) and **Desk Raised** (desk-raised): the table the book lies on, and the search field sunk into it.
- **Strip** (strip): the black top bar.
- **Desk Line / Desk Text / Desk Muted**: dividers, text and secondary text on the desk.
- **Paper** (paper): the sheet, dialogs and inputs.
- **Ink** (ink): all text on paper, every structural rule, table header rows, pressed states, Boss Cells marks and cell figures.
- **Ink Secondary** (ink-secondary): the reading column and ledes. **Muted** (muted) and **Dim** (dim): metadata, labels, placeholders.
- **Hair Rule** (rule-hair) and **Soft Rule** (rule-soft): row separators, input and chip strokes.
- **Plate / Plate 2 / Plate 3**: the pale grounds that sprites, tags, meters and the route graph paper sit on. They are material, not containers.
- **Table Zebra** (table-zebra): even table rows.

### Named Rules
**The Chapter Ownership Rule.** Ochre, teal and blue belong only to their chapters, through `--ch*`. Boss Cells, cells and progress data are ink. No chapter hue is ever used as a generic accent, warning colour or status colour.

**The Chip-and-Bar Rule.** Brutality, Tactics and Survival colours appear only as a 10px square chip (in tags and filter chips) and as the 3px bar along the bottom of a sprite plate. They never colour text, rules, backgrounds or headings.

**The Ink Ramp Rule.** Tier badges use a monochrome ink ramp: S solid ink, A and B mid-greys with white type, C pale grey, D paper. All five carry a 1.5px ink keyline. Tiers never borrow a hue.

## Typography

**Display Font:** Barlow Condensed 600/700/800, self-hosted (fallback Arial Narrow)
**Body Font:** Inter, self-hosted (fallback system-ui)

**Character:** Barlow Condensed is the guide's printed voice. It is set heavy, uppercase and tight for titles, and heavy uppercase with wide tracking for labels, table heads and buttons. Inter carries the reading column. The two never swap roles.

### Hierarchy
- **Display** (800, clamp(40px, 5.2vw, 76px), 0.92, uppercase): page and detail titles. The overview opener scales up to clamp(48px, 6.4vw, 96px) at 0.88.
- **Headline** (800, 32px, uppercase; 27px on phones): section heads, set on the 3px rule.
- **Title** (800, 21 to 27px, uppercase): entry, panel and plate titles (entries 27px, panels 24px, list items 21px).
- **Body** (Inter 400, 16px, 1.6): prose. Ledes are 17px, at most 66ch, in ink-secondary. Lists and notes run at 14.5 to 15px.
- **Label** (Barlow 700, 13 to 15px, 0.06 to 0.12em tracking, uppercase): running head, field labels, key/value terms, tags, counts, buttons. Numbers inside labels use tabular figures.
- **Table head** (Barlow 700, 15px, 0.08em, uppercase): white on ink.

### Named Rules
**The Tag-Below Rule.** Nothing small sits above a heading. Tags, tier badges, BC marks and DLC marks go on a row below the title and lede. A label may stand alone as a heading over a list (field label, slot label), but it is never a kicker over a larger title.

**The Tabular Rule.** Every figure that can line up in a column, row or ledger uses tabular numerals.

## Layout

The shell is fixed. A black top strip is 60px tall. The contents rail is 252px wide and sits on the desk. The sheet sits in the remaining width with 28px of desk above it, and a 46px fore-edge column on its right holds the sticky thumb tabs. Content inside the sheet is capped at 1280px and uses a fluid gutter (spacing.gutter). The running head and page-turn row hang inside the same gutter under and over a 1px ink rule.

Sections are spaced 56px apart. Grids use 28px row and 24px column gaps for entries, and 16px for tighter grids. Detail pages split 1.6 : 1 (main column and fact column) with a 48px gap. The overview splits 1.15 : 1. The ledger and stat strips run four across, separated by soft vertical hairlines rather than boxes.

Responsive steps:
- At 1180px, four-column strips drop to two, and the workshop and overview split stack.
- At 980px, the rail becomes an off-canvas drawer over a scrim, the thumb tabs and the sheet shadow disappear, and the sheet runs full-bleed.
- At 720px, the top strip wraps with search on its own line, the gutter tightens to 16px, every grid becomes one column, and key/value lists stack.

## Elevation & Depth

Elevation is physical: depth exists only between the desk and what lies on it. The sheet casts one long soft shadow onto the desk. Floating layers (dialogs, the search results, the toast and the mobile drawer) share a single overlay shadow. On the paper itself everything is flat. Hierarchy comes from rule weight (3px ink for sections, 1px ink for heads and table ends, hairlines for rows), never from lift.

### Shadow Vocabulary
- **Sheet on desk** (`box-shadow: 0 30px 60px -30px rgba(0,0,0,.8), 0 1px 0 rgba(255,255,255,.04)`): the page only.
- **Overlay** (`box-shadow: 0 18px 40px -16px rgba(0,0,0,.55), 0 2px 6px rgba(0,0,0,.18)`): dialogs, search results, toast, mobile drawer.
- **Node lift** (`box-shadow: 0 4px 10px -4px rgba(0,0,0,.35)`): hover on route-map nodes only.

Inset keylines (`inset 0 0 0 1px` or `1.5px` ink) are used as print strokes on tags, tiers and path steps. They are borders, not elevation.

### Named Rules
**The Open Page Rule.** There are no tinted panels and no nested boxes. A section is open paper under a 3px ink rule. Entries are an ink top rule plus content. Sub-columns inside a section are divided by vertical hairlines, never boxed. Pale plate fills are reserved for sprites, tags, meters, table zebra and the route map's graph paper.

## Shapes

The guide is near-square print. The 2px corner is used on buttons, chips, inputs and keys, and most marks (tags, tiers, plates, tabs, chips' colour squares) are fully square. The only circles are stamps: numbered callouts on loadout plates and step lists, the owned-check stamp, the tip mark and insight marks. Dashed strokes mean "missing / empty slot / drop zone". Hatching (−45°, 6px paper / 1px plate) means "locked".

## Components

### Buttons
- **Character:** printed, uppercase, ink-stroked.
- **Shape:** 2px corners, 42px tall (34px small), 2px ink border (1.5px small).
- **Default:** paper with ink label; hover inverts to ink with a white label; active nudges down 1px.
- **Primary:** ink fill; hover takes the chapter colour (`--ch` fill, `--ch-on` text).
- **Ghost:** no border, underlined, with a chapter-ink hover.
- **Link button:** uppercase Barlow in chapter ink.
- **Disabled:** 40% opacity.
- **Focus (everywhere):** 2px ink outline with a 2px offset.

### Chips
- **Style:** paper, 1px soft-rule stroke, 2px corners, 34px tall, Inter 14px/500.
- **Pressed:** solid ink with white text. Unavailable chips are struck through in dim.
- **Scaling chips** carry a 10px square in their scaling colour; the label stays ink.

### Tags and Marks
- **Tag:** Barlow 700 13.5px uppercase on plate-2, square corners.
- **Scaling tag:** transparent, led by the 10px colour square.
- **Boss Cells tag:** solid ink, white text.
- **DLC and found tags:** 1px ink keyline on transparent.
- **Ok tag:** a drawn check.
- **Locked tag:** muted and struck through.
- **Tier badge:** 28px square on the ink ramp with an ink keyline.
- **Difficulty:** three 6×13px ink-outlined bars, filled to the level.

### Entries (cards)
- **Corner Style:** none; there is no container.
- **Structure:** 3px ink top rule, 14px above the content, transparent background.
- **Hover:** the rule takes the chapter colour and the title underlines (2px, 4px offset).
- **Foot:** a hairline plus uppercase Barlow metadata.
- **Item rows** use a soft 1px top rule that turns ink on hover.

### Inputs / Fields
- **Style:** paper, 1.5px soft-rule stroke, 2px corners, 42px tall. The select uses a drawn ink chevron.
- **Hover:** the stroke goes to muted.
- **Focus:** an ink stroke plus a 3px halo of the chapter colour at 40%.
- **Switch:** a square ink-keyline track with a square ink thumb. When on, the track turns ink and the thumb takes the chapter colour.
- **Checkbox accent:** ink.

### Navigation
- **Top strip:** black, with desk-coloured controls. Segmented selectors (Boss Cells 0 to 5, EN/DE) invert to desk-text on ink when pressed.
- **Contents rail:** each chapter has a heading with a chapter-coloured number block. Section links show a 1.1-style number. On the active link the number block fills with its chapter colour and the label turns white at weight 600.
- **Thumb tabs:** 34×150px vertical tabs that are dimmed on the desk. The current tab extends to 46px at full chapter colour.
- **Running head:** a chapter number block plus the chapter name on the left and the section on the right, over a 1px ink rule.
- **Page turn:** previous/next titles over a 1px ink rule.
- **Tabs:** uppercase Barlow. The selected tab gets a 4px chapter-colour underline.

### Tables
An ink header row with white uppercase Barlow, 7px by 12px cells, a hairline between rows, zebra on even rows, a first column in ink at weight 600, and a closing 1px ink rule. Ratings are an ink fill (top), an ink keyline (good) or muted text (low).

### Sprite Plate (signature)
Game art sits on a square plate-coloured ground with a 1px hairline keyline, rendered pixelated. Sizes are 34, 44, 80 and 120px. A 3px bar along the bottom edge carries the item's scaling colour (or the three-band gradient for multi-colour items). Owned items get a 16px black circular stamp with a white check at the top-right corner.

### State Marks (signature)
- **Owned:** black check stamp (on plates) or a solid ink tick/toggle.
- **Missing:** dashed outline; the sprite drops to 45 to 55% opacity.
- **Locked:** hatched ground and struck-through label at 50% opacity, with dashed route edges.
- **Boss:** heavy bottom rule (4px on route nodes and path steps).
- **In path:** chapter fill. **Current:** 3px ink outline. **Next:** dashed chapter-ink border on chapter tint.

### Numbered Callouts
Loadout plates and step lists number their entries with 26 to 28px ink circles carrying white Barlow 800 figures. On plates the circle overlaps the sprite's top-left corner.

### Icons
Every pictogram comes from the IC SVG set: a 24-unit viewBox, 2px round-capped stroke in currentColor, sized at 1.05em. The three shell icons in the top strip (menu, search, profile) are drawn to the same standard. New icons are added to IC, never typed as glyphs or emoji.

## Do's and Don'ts

### Do:
- **Do** open every section and entry with a 3px ink rule over open paper, and separate rows with 1px hairlines.
- **Do** set titles, labels, table heads and buttons in Barlow Condensed uppercase, and prose in Inter at 16px/1.6 with ledes capped at 66ch.
- **Do** route chapter colour through `--ch`, `--ch-ink`, `--ch-tint` and `--ch-on` so it follows the open chapter.
- **Do** show state as a mark: black check stamp for owned, dashed outline for missing, hatching plus strike for locked, heavy bottom rule for boss.
- **Do** put tags, tier badges, BC and DLC marks on a row below the title.
- **Do** keep sprites on plate-coloured squares, pixelated, with the 3px scaling bar.
- **Do** use tabular figures for every number in a column, ledger or selector.

### Don't:
- **Don't** wrap sections or entries in tinted panels or bordered boxes, and don't nest boxes inside sections.
- **Don't** place a small label, kicker or tag above a heading.
- **Don't** use ochre, teal or blue outside their own chapter, including for warnings, Boss Cells or cell figures; those are ink.
- **Don't** colour tier badges; keep the S-to-D ink ramp.
- **Don't** use Brutality, Tactics or Survival colours for text, rules, headings or fills beyond the square chip and the 3px plate bar.
- **Don't** use emoji, Unicode pictographs or text glyphs as icons; draw them into the IC set.
- **Don't** add glows, neon accents or dark panels on the paper; shadows belong only to the sheet and floating overlays.
- **Don't** round corners beyond 2px, except the circular callout and stamp marks.
