import json, re, subprocess, sys
sys.path.insert(0, '.')
from scratch_oita_wareki import wareki_to_iso

out = subprocess.run(['python3', '_h2t.py', 'cache/大分県/kusu/6963155a6791cbf1.html'],
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

t = tables[2]  # 町指定 table (no16-44)
SRC = 'https://www.town.kusu.oita.jp/soshiki/shakaikyoikuka/2/5/bunkazai/936.html'
manifest = json.load(open('cache/大分県/kusu/manifest.json'))
FETCHED = list(manifest.values())[0]['fetched_at']

CAT_MAP = {
    '有形文化財': ('有形文化財', '有形文化財'),
    '無形民俗文化財': ('民俗文化財', '無形民俗文化財'),
    '史跡': ('記念物(史跡・名勝・天然記念物)', '史跡'),
    '天然記念物': ('記念物(史跡・名勝・天然記念物)', '天然記念物'),
}

results = []
header = [c.strip() for c in t[0].split('|')]
for line in t[1:]:
    cells = [c.strip() for c in line.split('|')]
    if len(cells) < len(header):
        continue
    d = dict(zip(header, cells))
    shurui = d.get('種類', '')
    cat, subcat = CAT_MAP.get(shurui, (None, shurui))
    date = wareki_to_iso(d.get('指定年月日', ''))
    desc_parts = [f"指定番号{d.get('No.')}号"]
    setsumei = d.get('説明', '')
    if setsumei and setsumei != d.get('名称'):
        desc_parts.append(setsumei)
    results.append({
        "pref": "大分県", "municipality": "玖珠町", "name": d.get('名称', ''),
        "category": cat, "subcategory": subcat, "designation": "町指定",
        "designated_date": date, "location": None, "description": '、'.join(desc_parts),
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('out/大分県/kusu.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print('total:', len(results))
from collections import Counter
print(Counter((r['category'], r['subcategory']) for r in results))
print('nulls date:', sum(1 for r in results if r['designated_date'] is None))
