import json, re, subprocess

SRC = 'https://www.town.tadotsu.kagawa.jp/kanko_bunka_event/rekishi_bunka/1312.html'
FETCHED = '2026-07-12T22:40:00Z'

CAT = {
 '絵画': ('有形文化財','絵画'),
 '書跡': ('有形文化財','書跡'),
 '考古資料': ('有形文化財','考古資料'),
 '建造物': ('有形文化財','建造物'),
 '歴史資料': ('有形文化財','歴史資料'),
 '彫刻': ('有形文化財','彫刻'),
 '工芸品': ('有形文化財','工芸品'),
 '古文書': ('有形文化財','古文書'),
 '史跡': ('記念物(史跡・名勝・天然記念物)','史跡'),
 '天然記念物': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
 '有形民俗文化財': ('民俗文化財','有形民俗文化財'),
 '無形民俗文化財': ('民俗文化財','無形民俗文化財'),
}

out = subprocess.run(['python3','_h2t.py','cache/香川県/tadotsu/11d12ee27d0f6656.html'],
                      cwd='/Users/miyazakihitohata/bunkazai/pipeline', capture_output=True, text=True).stdout
lines = out.split('\n')
idx = [i for i,l in enumerate(lines) if l=='=== TABLE ===']
end = [i for i,l in enumerate(lines) if l=='=== /TABLE ===']
t3 = lines[idx[2]+1:end[2]][1:]  # skip header row, table index 2 = 町指定 (0-based)

results = []
last_qty_only = None
for row_str in t3:
    parts = [p.strip() for p in row_str.split('|')]
    if len(parts) == 5:
        num, shubetsu, name, qty, loc = parts
    elif len(parts) == 2:
        # continuation row: qty | loc (multi-location item)
        qty, loc = parts
    else:
        continue
    m = re.match(r'種別（(.+)）|(.+)（(.+)）', shubetsu) if len(parts)==5 else None
    if len(parts) == 5:
        mm = re.search(r'（([^）]+)）', shubetsu)
        subcat = mm.group(1) if mm else shubetsu
        cat, sc = CAT.get(subcat, (None, subcat))
        results.append({
            "pref": "香川県", "municipality": "多度津町", "name": name,
            "category": cat, "subcategory": sc, "designation": "町指定",
            "designated_date": None, "location": loc,
            "description": f'指定番号{num}、員数{qty}' if qty and qty != '不明' else f'指定番号{num}',
            "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
        })
    else:
        # append additional location to last item's description/location
        if results:
            results[-1]["location"] = (results[-1]["location"] or '') + '／' + loc

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/香川県/tadotsu.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
print('null cat:', [r['name'] for r in results if r['category'] is None])
