import json, sys
sys.path.insert(0, '/Users/user/bunkazai/pipeline')
from scratch_shimane_wareki import wareki_to_iso

CAT_MAP = {
 '記・史': ('記念物(史跡・名勝・天然記念物)', '史跡'),
 '無・民': ('民俗文化財', '無形民俗文化財'),
 '有・書': ('有形文化財', '書跡'),
 '有・工': ('有形文化財', '工芸品'),
 '有・建': ('有形文化財', '建造物'),
 '有・古': ('有形文化財', '古文書'),
 '有・彫': ('有形文化財', '彫刻'),
 '記・天': ('記念物(史跡・名勝・天然記念物)', '天然記念物'),
}

with open('/Users/user/bunkazai/pipeline/scratch_ama_table.json', encoding='utf-8') as f:
    data = json.load(f)

SRC = 'https://www.town.ama.shimane.jp/kurashi-tetsuduki/bunka-sports/bunka/1tbofvyngk'
FETCHED = '2026-07-12T08:43:14Z'

results = []
for row in data:
    if len(row) < 7:
        continue
    name, loc, owner, date, code, num, note = row
    name = name.lstrip('★').strip()
    cat, subcat = CAT_MAP.get(code, (None, code))
    iso = wareki_to_iso(date)
    desc_parts = [f'指定番号{num}']
    if note:
        desc_parts.append(f'員数{note}')
    if owner:
        desc_parts.append(f'所有者{owner}')
    desc = '、'.join(desc_parts)
    results.append({
        "pref": "島根県", "municipality": "海士町", "name": name,
        "category": cat, "subcategory": subcat, "designation": "町指定",
        "designated_date": iso, "location": loc or None, "description": desc,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('/Users/user/bunkazai/pipeline/out/島根県/ama.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
print('null cat', sum(1 for r in results if r['category'] is None))
