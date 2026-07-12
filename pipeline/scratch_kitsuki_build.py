import json, re, subprocess, sys
sys.path.insert(0, '.')
from scratch_oita_wareki import wareki_to_iso

out = subprocess.run(['python3', '_h2t.py', 'cache/大分県/kitsuki/63d648b520e9de4b.html'],
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

SRC = 'https://www.city.kitsuki.lg.jp/soshiki/7/bunka/bunkazai/bunkazai/1822.html'
manifest = json.load(open('cache/大分県/kitsuki/manifest.json'))
FETCHED = list(manifest.values())[0]['fetched_at']

CAT_MAP = {
    '市有文': '有形文化財',
    '市指有民': ('民俗文化財', '有形民俗文化財'),
    '市指無民': ('民俗文化財', '無形民俗文化財'),
    '市史跡': ('記念物(史跡・名勝・天然記念物)', '史跡'),
    '市名勝': ('記念物(史跡・名勝・天然記念物)', '名勝'),
    '市天然': ('記念物(史跡・名勝・天然記念物)', '天然記念物'),
}

t = tables[2]  # 市指定 table
header = [c.strip() for c in t[0].split('|')]
results = []
for line in t[1:]:
    cells = [c.strip() for c in line.split('|')]
    if len(cells) < len(header):
        continue
    d = dict(zip(header, cells))
    kubun = d.get('区分', '')
    if kubun not in CAT_MAP:
        continue
    mapping = CAT_MAP[kubun]
    if kubun == '市有文':
        subcat = d.get('細区分') or '有形文化財'
        cat = '有形文化財'
    else:
        cat, subcat = mapping
    name = d.get('名称及び物件', '')
    date = wareki_to_iso(d.get('指定年月日', ''))
    loc = d.get('所在地') or None
    owner = d.get('所有者及び管理団体', '')
    naiyou = d.get('内容及び参考', '')
    desc_parts = [f'指定番号{d.get("番号")}号']
    if naiyou:
        desc_parts.append(naiyou)
    if owner:
        desc_parts.append(f'所有者・管理団体: {owner}')
    desc = '、'.join(desc_parts)
    results.append({
        "pref": "大分県", "municipality": "杵築市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": date, "location": loc, "description": desc,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('out/大分県/kitsuki.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print('total:', len(results))
from collections import Counter
print(Counter((r['category'], r['subcategory']) for r in results))
print('nulls cat:', sum(1 for r in results if r['category'] is None))
print('nulls date:', sum(1 for r in results if r['designated_date'] is None))
