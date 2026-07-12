import json, re, sys
sys.path.insert(0, '/Users/user/bunkazai/pipeline')
from scratch_shimane_wareki import wareki_to_iso

with open('/Users/user/bunkazai/pipeline/scratch_izumo_table7.json', encoding='utf-8') as f:
    data = json.load(f)

CAT_MAP = {
 '建造物':('有形文化財','建造物'), '絵画':('有形文化財','絵画'), '彫刻':('有形文化財','彫刻'),
 '工芸品':('有形文化財','工芸品'), '書跡':('有形文化財','書跡'), '典籍':('有形文化財','典籍'),
 '古文書':('有形文化財','古文書'), '考古資料':('有形文化財','考古資料'), '歴史資料':('有形文化財','歴史資料'),
 '無形民俗':('民俗文化財','無形民俗文化財'), '有形民俗':('民俗文化財','有形民俗文化財'),
 '有形民俗文化財':('民俗文化財','有形民俗文化財'), '無形民俗文化財':('民俗文化財','無形民俗文化財'),
 '史跡':('記念物(史跡・名勝・天然記念物)','史跡'), '名勝':('記念物(史跡・名勝・天然記念物)','名勝'),
 '天然記念物':('記念物(史跡・名勝・天然記念物)','天然記念物'),
 '工芸技術':('無形文化財','工芸技術'), '芸能':('無形文化財','芸能'),
}

SRC = 'https://www.city.izumo.shimane.jp/www/contents/1142485283146/index.html'
FETCHED = '2026-07-12T06:55:30Z'
results = []
for row in data:
    if len(row) < 6:
        continue
    catword, name, qty, date, loc, owner = row[0], row[1], row[2], row[3], row[4], row[5]
    cat, subcat = CAT_MAP.get(catword, (None, catword))
    iso = wareki_to_iso(date)
    desc = f'員数{qty}、指定年月日{date}、所有者・保持者{owner}' if owner else f'員数{qty}、指定年月日{date}'
    results.append({
        "pref": "島根県", "municipality": "出雲市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": iso, "location": loc or None, "description": desc,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('/Users/user/bunkazai/pipeline/out/島根県/izumo.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
nulls = [r for r in results if r['category'] is None]
print('null cat count', len(nulls), nulls[:5])
