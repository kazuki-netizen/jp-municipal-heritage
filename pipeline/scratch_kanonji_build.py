import json, re, subprocess, sys
sys.path.insert(0, '/Users/miyazakihitohata/bunkazai/pipeline')
from scratch_shimane_wareki import wareki_to_iso

SRC = 'https://www.city.kanonji.kagawa.jp/soshiki/30/559.html'
FETCHED = '2026-07-12T19:20:00Z'

CAT = {
 '建造物': ('有形文化財','建造物'),
 '絵画': ('有形文化財','絵画'),
 '彫刻': ('有形文化財','彫刻'),
 '工芸品': ('有形文化財','工芸品'),
 '書跡': ('有形文化財','書跡'),
 '古文書': ('有形文化財','古文書'),
 '考古資料': ('有形文化財','考古資料'),
 '有形民俗文化財': ('民俗文化財','有形民俗文化財'),
 '無形民俗文化財': ('民俗文化財','無形民俗文化財'),
 '史跡': ('記念物(史跡・名勝・天然記念物)','史跡'),
 '天然記念物': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

out = subprocess.run(['python3','_h2t.py','cache/香川県/kanonji/5dade5b13f7d8bcb.html'],
                      cwd='/Users/miyazakihitohata/bunkazai/pipeline', capture_output=True, text=True).stdout
lines = out.split('\n')
idx = [i for i,l in enumerate(lines) if l=='=== TABLE ===']
end = [i for i,l in enumerate(lines) if l=='=== /TABLE ===']
t3 = lines[idx[2]+1:end[2]][1:]  # skip header row

WAREKI_RE = re.compile(r'(明治|大正|昭和|平成|令和)\d+年\d+月\d+日')

results = []
cur_kubun = None
for row_str in t3:
    parts = [p.strip() for p in row_str.split('|')]
    first = parts[0]
    m = WAREKI_RE.match(first)
    # determine if first col is a 種別(kubun) label or already a 名称 (continuation row)
    dates_in_last = WAREKI_RE.findall(parts[-1])
    if len(parts) == 5:
        kubun_raw = parts[0]
        # strip parenthetical qualifiers like （建造物）-> just category word after 有形文化財
        mm = re.search(r'[（(]([^）)]+)[）)]', kubun_raw)
        if mm:
            cur_kubun = mm.group(1)
        else:
            cur_kubun = kubun_raw
        name, loc, owner, date_raw = parts[1], parts[2], parts[3], parts[4]
    else:
        name, loc, owner, date_raw = parts[0], parts[1], parts[2], parts[3]
    cat, subcat = CAT.get(cur_kubun, (None, cur_kubun))
    dts = [m.group(0) for m in WAREKI_RE.finditer(date_raw)]
    primary = dts[0] if dts else date_raw
    iso = wareki_to_iso(primary)
    desc = None
    if len(dts) > 1:
        desc = f'追加指定等: {date_raw}'
    results.append({
        "pref": "香川県", "municipality": "観音寺市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": iso, "location": loc or None,
        "description": desc,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/香川県/kanonji.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
print([r['name'] for r in results if r['category'] is None])
print([r['name'] for r in results if r['designated_date'] is None])
