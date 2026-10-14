"""Prüft die Datendateien auf Konsistenz (läuft auch in der GitHub-Action).

Fehler (Exit-Code 1): kaputtes JSON, doppelte IDs, fehlende Pflichtfelder, fehlende Icons.
Warnungen: Namen in Builds/Meta/Routen, die keinem Eintrag zugeordnet werden können.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
errors, warnings = [], []


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower().replace("'", '').replace('’', ''))


def load(name):
    p = DATA / f'{name}.json'
    if not p.exists():
        warnings.append(f'{name}.json fehlt')
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        errors.append(f'{name}.json: ungültiges JSON ({e})')
        return {}


gear = load('gear').get('items', [])
muts = load('mutations').get('mutations', [])
outfits = load('outfits').get('outfits', [])
world = load('world')
builds = load('builds').get('builds', [])
meta = load('meta')

for label, items, icon_key in [('gear', gear, 'icon'), ('mutations', muts, 'icon'), ('outfits', outfits, 'image')]:
    ids = [i.get('id') for i in items]
    dup = {x for x in ids if ids.count(x) > 1}
    if dup:
        errors.append(f'{label}: doppelte IDs {sorted(dup)}')
    for i in items:
        if not i.get('id') or not i.get('name'):
            errors.append(f'{label}: Eintrag ohne id/name: {i}')
        icon = i.get(icon_key)
        if icon and not (ROOT / icon).exists():
            errors.append(f'{label}/{i.get("id")}: Bild fehlt ({icon})')

names = {norm(i['name']) for i in gear + muts if i.get('name')}
biomes = world.get('biomes', [])
biome_keys = {b['id'] for b in biomes} | {norm(b['name']) for b in biomes}
bosses = {norm(b['name']) for b in world.get('bosses', [])} | {norm(b['name'].replace('The ', '')) for b in world.get('bosses', [])}

for b in biomes:
    for ex in b.get('exits', []):
        if ex.get('to') not in biome_keys and norm(ex.get('to')) not in biome_keys:
            errors.append(f'world: {b["id"]} → unbekanntes Ziel {ex.get("to")}')

for b in builds:
    for part in ('core', 'alternatives'):
        for slot, lst in (b.get(part) or {}).items():
            for n in lst or []:
                if norm(n) not in names:
                    warnings.append(f'builds/{b.get("id")}: {part}.{slot} "{n}" unbekannt')

for cat, lst in (meta.get('tiers') or {}).items():
    for t in lst:
        if norm(t.get('name')) not in names:
            warnings.append(f'meta.tiers.{cat}: "{t.get("name")}" unbekannt')
for s in meta.get('synergies', []):
    for n in s.get('items', []):
        if norm(n) not in names:
            warnings.append(f'meta.synergies: "{n}" unbekannt')
for s in meta.get('mutationSets', []):
    for n in s.get('mutations', []):
        if norm(n) not in names:
            warnings.append(f'meta.mutationSets: "{n}" unbekannt')
for r in meta.get('routes', []):
    for n in r.get('path', []):
        if norm(n) not in biome_keys and n not in biome_keys:
            warnings.append(f'meta.routes/{r.get("id")}: Biom "{n}" unbekannt')

for w in warnings:
    print('WARNUNG:', w)
for e in errors:
    print('FEHLER: ', e)
print(f'{len(gear)} Ausrüstung · {len(muts)} Mutationen · {len(outfits)} Outfits · {len(biomes)} Biome · {len(builds)} Builds')
print(f'{len(errors)} Fehler, {len(warnings)} Warnungen')
sys.exit(1 if errors else 0)
