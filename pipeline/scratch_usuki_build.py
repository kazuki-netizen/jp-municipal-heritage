import json, re, subprocess, sys
sys.path.insert(0, '.')
from scratch_oita_wareki import wareki_to_iso

out = subprocess.run(['python3', '_h2t.py', 'cache/大分県/usuki/18cbd8aa5878a044.html'],
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

SRC = 'https://www.city.usuki.oita.jp/docs/2014021200040/'
manifest = json.load(open('cache/大分県/usuki/manifest.json'))
FETCHED = None
for v in manifest.values():
    if v['url'] == SRC:
        FETCHED = v['fetched_at']

CAT_MAP = {
    '有形民俗文化財': ('民俗文化財', '有形民俗文化財'),
    '無形民俗文化財': ('民俗文化財', '無形民俗文化財'),
    '史跡': ('記念物(史跡・名勝・天然記念物)', '史跡'),
    '名勝': ('記念物(史跡・名勝・天然記念物)', '名勝'),
    '天然記念物': ('記念物(史跡・名勝・天然記念物)', '天然記念物'),
}


def parse_table(rows):
    header = [c.strip() for c in rows[0].split('|')]
    ncols = len(header)
    prev = [''] * ncols
    out = []
    for line in rows[1:]:
        cells = [c.strip() for c in line.split('|')]
        while len(cells) < ncols:
            cells.insert(0, '')
        resolved = []
        for idx, c in enumerate(cells):
            if c in ('', '〃'):
                resolved.append(prev[idx])
            else:
                resolved.append(c)
        prev = resolved
        out.append((header, resolved))
    return out


def parse_date(s):
    # strip parenthetical re-designation date e.g. 昭和48年12月10日(平成17年1月1日)
    s = re.sub(r'[（(].*?[）)]', '', s).strip()
    return wareki_to_iso(s)


results = []
for t in tables:
    rows = parse_table(t)
    for header, cells in rows:
        d = dict(zip(header, cells))
        shubetsu = d.get('種別', '')
        cat, subcat = CAT_MAP.get(shubetsu, (None, shubetsu))
        name = re.sub(r'\(.*?\)', '', d.get('名称', d.get('名　　称', ''))).strip()
        date = parse_date(d.get('指定年月日', ''))
        loc = d.get('所在地') or None
        desc_parts = []
        if d.get('員数'):
            desc_parts.append(f"員数{d['員数']}")
        if d.get('時代'):
            desc_parts.append(f"時代:{d['時代']}")
        if d.get('面積(m2)'):
            desc_parts.append(f"面積{d['面積(m2)']}m2")
        if d.get('年代（樹齢）'):
            desc_parts.append(f"年代（樹齢）:{d['年代（樹齢）']}")
        if d.get('保持者及び保持団体の所在地'):
            loc = d['保持者及び保持団体の所在地']
        desc = '、'.join(desc_parts) if desc_parts else None
        results.append({
            "pref": "大分県", "municipality": "臼杵市", "name": name,
            "category": cat, "subcategory": subcat, "designation": "市指定",
            "designated_date": date, "location": loc, "description": desc,
            "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
        })

with open('out/大分県/usuki.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print('total:', len(results))
from collections import Counter
print(Counter((r['category'], r['subcategory']) for r in results))
print('nulls cat:', sum(1 for r in results if r['category'] is None))
print('nulls date:', sum(1 for r in results if r['designated_date'] is None))
