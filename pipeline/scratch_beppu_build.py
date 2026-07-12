import json, re, subprocess, sys
sys.path.insert(0, '.')
from scratch_oita_wareki import wareki_to_iso

out = subprocess.run(['python3', '_h2t.py', 'cache/大分県/beppu/8248d0124a46dc55.html'],
                      capture_output=True, text=True).stdout
lines = out.split('\n')

tables = []
i = 0
while i < len(lines):
    if lines[i] == '=== TABLE ===':
        j = lines.index('=== /TABLE ===', i)
        tables.append(lines[i+1:j])
        i = j+1
    else:
        i += 1

CAT_MAP = {
    '絵画': ('有形文化財', '絵画'), '工芸品': ('有形文化財', '工芸品'), '考古': ('有形文化財', '考古資料'),
    '建造物': ('有形文化財', '建造物'), '古文書': ('有形文化財', '古文書'), '彫刻': ('有形文化財', '彫刻'),
    '書跡': ('有形文化財', '書跡'), '歴史資料': ('有形文化財', '歴史資料'), '典籍': ('有形文化財', '典籍'),
}

SRC = 'https://www.city.beppu.oita.jp/gakusyuu/bunkazai/bunkazai_shiteibunkazai.html'
manifest = json.load(open('cache/大分県/beppu/manifest.json'))
FETCHED = list(manifest.values())[0]['fetched_at']


def parse_table(rows):
    header = rows[0]
    body = rows[1:]
    ncols = len(header.split('|'))
    prev = [''] * ncols
    out = []
    for line in body:
        cells = [c.strip() for c in line.split('|')]
        while len(cells) < ncols:
            cells.insert(0, '')  # rowspan eats leading columns
        resolved = []
        for idx, c in enumerate(cells):
            if c in ('', '〃', '"', '""'):
                resolved.append(prev[idx])
            else:
                resolved.append(c)
        prev = resolved
        out.append(resolved)
    return out


results = []

rows0 = parse_table(tables[0])
for r in rows0:
    shitei, name, shubetsu, loc, owner, date = r
    if shitei != '市':
        continue
    cat, subcat = CAT_MAP.get(shubetsu, (None, shubetsu))
    iso = wareki_to_iso(date)
    desc = f'所有（管理）者: {owner}' if owner else None
    results.append({
        "pref": "大分県", "municipality": "別府市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": iso, "location": loc or None, "description": desc,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

rows2 = parse_table(tables[2])
for r in rows2:
    shitei, name, shubetsu, loc, owner, date = r
    if shitei != '市':
        continue
    iso = wareki_to_iso(date)
    desc = f'種別: {shubetsu}' if shubetsu and shubetsu != 'ー' else None
    if owner and owner != '－':
        desc = (desc + f'、所有（管理）者: {owner}') if desc else f'所有（管理）者: {owner}'
    results.append({
        "pref": "大分県", "municipality": "別府市", "name": name,
        "category": "民俗文化財", "subcategory": "無形民俗文化財", "designation": "市指定",
        "designated_date": iso, "location": loc or None, "description": desc,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

rows3 = parse_table(tables[3])
for r in rows3:
    shitei, name, shubetsu, loc, owner, date = r
    if shitei != '市':
        continue
    iso = wareki_to_iso(date)
    results.append({
        "pref": "大分県", "municipality": "別府市", "name": name,
        "category": "民俗文化財", "subcategory": "有形民俗文化財", "designation": "市指定",
        "designated_date": iso, "location": loc or None, "description": None,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

rows4 = parse_table(tables[4])
for r in rows4:
    shitei, name, shubetsu, loc, owner, date = r
    if shitei != '市':
        continue
    iso = wareki_to_iso(date)
    desc = f'所有（管理）者: {owner}' if owner else None
    results.append({
        "pref": "大分県", "municipality": "別府市", "name": name,
        "category": "記念物(史跡・名勝・天然記念物)", "subcategory": "史跡", "designation": "市指定",
        "designated_date": iso, "location": loc or None, "description": desc,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

rows5 = parse_table(tables[5])
for r in rows5:
    shitei, name, shubetsu, loc, owner, date = r
    if shitei != '市':
        continue
    iso = wareki_to_iso(date)
    results.append({
        "pref": "大分県", "municipality": "別府市", "name": name,
        "category": "記念物(史跡・名勝・天然記念物)", "subcategory": "名勝", "designation": "市指定",
        "designated_date": iso, "location": loc or None, "description": None,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

rows6 = parse_table(tables[6])
for r in rows6:
    shitei, name, shubetsu, loc, owner, date = r
    if shitei != '市':
        continue
    iso = wareki_to_iso(date)
    desc = f'所有（管理）者: {owner}' if owner else None
    results.append({
        "pref": "大分県", "municipality": "別府市", "name": name,
        "category": "記念物(史跡・名勝・天然記念物)", "subcategory": "天然記念物", "designation": "市指定",
        "designated_date": iso, "location": loc or None, "description": desc,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('out/大分県/beppu.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print('total:', len(results))
from collections import Counter
print(Counter((r['category'], r['subcategory']) for r in results))
print('nulls cat:', sum(1 for r in results if r['category'] is None))
