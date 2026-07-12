import json, re, subprocess, sys
sys.path.insert(0, '/Users/miyazakihitohata/bunkazai/pipeline')
from scratch_shimane_wareki import ERA_START

def wareki_short_to_iso(s):
    # formats like 昭44.11. 3 / 平 7. 3.28 / 令5.７.27 / 平31．3.19 / 令 2. 3.19
    s = s.strip()
    s = s.translate(str.maketrans('０１２３４５６７８９．', '0123456789.'))
    m = re.match(r'(明|大|昭|平|令)\s*(\d+)\.\s*(\d+)\.\s*(\d+)', s)
    if not m:
        return None
    era_c, y, mo, d = m.groups()
    era_map = {'明':'明治','大':'大正','昭':'昭和','平':'平成','令':'令和'}
    era = era_map[era_c]
    y = int(y); mo = int(mo); d = int(d)
    year = ERA_START[era] + y - 1
    return f'{year:04d}-{mo:02d}-{d:02d}'

CAT_MAP = {
 '絵画':('有形文化財','絵画'), '彫刻':('有形文化財','彫刻'), '工芸品':('有形文化財','工芸品'),
 '書跡':('有形文化財','書跡'), '典籍':('有形文化財','典籍'), '古文書':('有形文化財','古文書'),
 '考古資料':('有形文化財','考古資料'), '歴史資料':('有形文化財','歴史資料'),
 '無形文化財':('無形文化財','無形文化財'),
 '有形民俗文化財':('民俗文化財','有形民俗文化財'), '無形民俗文化財':('民俗文化財','無形民俗文化財'),
 '史跡':('記念物(史跡・名勝・天然記念物)','史跡'), '天然記念物':('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

out = subprocess.run(['python3', '_h2t.py', 'cache/島根県/hamada/2b75043440be14f3.html'],
                      cwd='/Users/miyazakihitohata/bunkazai/pipeline', capture_output=True, text=True).stdout
lines = out.split('\n')
start = lines.index('=== TABLE ===') + 1
end = lines.index('=== /TABLE ===')
rows = lines[start+1:end]  # skip header row

SRC = 'https://www.city.hamada.shimane.jp/www/contents/1001000003242/index.html'
FETCHED = '2026-07-12T06:55:29Z'
results = []
for line in rows:
    parts = [p.strip() for p in line.split('|')]
    if len(parts) < 5:
        continue
    num_cat, date, name, loc, note = parts[0], parts[1], parts[2], parts[3], parts[4]
    m = re.match(r'(\d+)\.(.+)', num_cat)
    if not m:
        continue
    num, catword = m.groups()
    cat, subcat = CAT_MAP.get(catword, (None, catword))
    iso = wareki_short_to_iso(date)
    desc_parts = [f'指定番号{num}号']
    if note:
        desc_parts.append(note)
    desc = '、'.join(desc_parts)
    results.append({
        "pref": "島根県", "municipality": "浜田市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": iso, "location": loc or None, "description": desc,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/島根県/hamada.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
nulls = [r for r in results if r['category'] is None]
print('null cats:', nulls)
