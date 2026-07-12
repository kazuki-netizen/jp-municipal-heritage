import json, subprocess, sys
sys.path.insert(0, '/Users/user/bunkazai/pipeline')
from scratch_shimane_wareki import wareki_to_iso

SRC = 'https://www.higashikagawa.jp/soshikikarasagasu/shogaigakushuka/gyomuannai/8/1/1085.html'
FETCHED = '2026-07-12T21:20:00Z'

CAT = {
 '絵画': ('有形文化財','絵画'),
 '彫刻': ('有形文化財','彫刻'),
 '工芸品': ('有形文化財','工芸品'),
 '書跡': ('有形文化財','書跡'),
 '古文書': ('有形文化財','古文書'),
 '考古資料': ('有形文化財','考古資料'),
 '歴史資料': ('有形文化財','歴史資料'),
 '建造物': ('有形文化財','建造物'),
 '有形民俗文化財': ('民俗文化財','有形民俗文化財'),
 '無形民俗文化財': ('民俗文化財','無形民俗文化財'),
 '史跡': ('記念物(史跡・名勝・天然記念物)','史跡'),
 '天然記念物': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

out = subprocess.run(['python3','_h2t.py','cache/香川県/higashikagawa/705d8a75ddf8815b.html'],
                      cwd='/Users/user/bunkazai/pipeline', capture_output=True, text=True).stdout
lines = out.split('\n')
idx = [i for i,l in enumerate(lines) if l=='=== TABLE ===']
end = [i for i,l in enumerate(lines) if l=='=== /TABLE ===']
t1 = lines[idx[0]+1:end[0]][1:]  # skip header

results = []
for row_str in t1:
    parts = [p.strip() for p in row_str.split('|')]
    if len(parts) != 4:
        continue
    daishu, shoshu, name, date_raw = parts
    cat, subcat = CAT.get(shoshu, (None, shoshu))
    iso = wareki_to_iso(date_raw)
    results.append({
        "pref": "香川県", "municipality": "東かがわ市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": iso, "location": None, "description": None,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('/Users/user/bunkazai/pipeline/out/香川県/higashikagawa.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
print('null cat:', [r['name'] for r in results if r['category'] is None])
print('null date:', [r['name'] for r in results if r['designated_date'] is None])
