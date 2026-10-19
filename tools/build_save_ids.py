"""Baut data/save-ids.json: interne Spiel-IDs (aus data.cdb) -> Einträge des Guides.

Wird für den Savegame-Import gebraucht. Quelle: research/cache/lang/data.cdb und main.en.mo
(aus der lokalen res.pak, siehe tools/pak_extract.py). Nur lesend.
Nutzung: python -I tools/build_save_ids.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from mo_read import read_mo  # noqa: E402

LANG = ROOT / 'research' / 'cache' / 'lang'

# Interne IDs, deren Spielname nicht dem Wiki-Namen entspricht
ALIASES = {
    'SnakeSwordWeapon': 'gear:whip-sword',
    'MarkBow': 'gear:hokutos-bow',
    'FlyingSword': 'gear:serenade',
    'DiverseDeckJuggernaut': 'gear:diverse-deck',
    'P_DemonicForce': 'mutation:demonic-strength',
    'PrisonerBobby': 'outfit:trailer-bobby-outfit',
    'Bobby': 'outfit:bobby-outfit',
    'PokebombUnlock': 'collector:specialistsshowroom',
    'RichterROB': 'outfit:richter-outfit',
}


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower().replace("'", '').replace('’', ''))


def main():
    cdb = json.loads((LANG / 'data.cdb').read_text(encoding='utf-8'))
    en = read_mo(LANG / 'main.en.mo')
    items = next(s for s in cdb['sheets'] if s['name'] == 'item')['lines']

    entries = {}
    for kind, file, key in [('gear', 'gear', 'items'), ('mutation', 'mutations', 'mutations'), ('outfit', 'outfits', 'outfits')]:
        for e in json.loads((ROOT / 'data' / f'{file}.json').read_text(encoding='utf-8'))[key]:
            entries.setdefault(norm(e['name']), []).append(f'{kind}:{e["id"]}')

    world = json.loads((ROOT / 'data' / 'world.json').read_text(encoding='utf-8'))
    for r in world.get('runes', []):
        entries.setdefault(norm(r['name']), []).append(f'rune:{r["id"]}')
    mech = json.loads((ROOT / 'data' / 'mechanics.json').read_text(encoding='utf-8'))
    for c in mech.get('collector', []):
        entries.setdefault(norm(c['name']), []).append(f'collector:{norm(c["name"])}')

    mapping, unmatched, bossCells = {}, [], {}
    for line in items:
        iid, fr = line.get('id'), line.get('name')
        if not iid or not fr or (iid.startswith('Richter') and iid not in ALIASES):
            continue
        if iid in ALIASES:
            mapping[iid] = ALIASES[iid]
            continue
        m = re.fullmatch(r'BossRune(\d)', iid)
        if m:
            bossCells[iid] = int(m.group(1))
            continue
        name = en.get(fr, fr)
        if iid.startswith('ASP_'):
            mapping[iid] = f'aspect:{name}'
            continue
        keys = entries.get(norm(name), [])
        if keys:
            mapping[iid] = keys[0] if len(keys) == 1 else keys
        else:
            unmatched.append((iid, name))

    out = {'meta': {'source': 'data.cdb (item-Sheet) + main.en.mo der Spielversion 3.5', 'count': len(mapping)},
           'bossCells': bossCells, 'ids': dict(sorted(mapping.items()))}
    (ROOT / 'data' / 'save-ids.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    (LANG / 'save_ids_unmatched.json').write_text(json.dumps(unmatched, ensure_ascii=False, indent=1), encoding='utf-8')
    kinds = {}
    for v in mapping.values():
        for k in (v if isinstance(v, list) else [v]):
            kinds[k.split(':')[0]] = kinds.get(k.split(':')[0], 0) + 1
    print('zugeordnet:', len(mapping), kinds, '| ohne Treffer:', len(unmatched))


if __name__ == '__main__':
    main()
