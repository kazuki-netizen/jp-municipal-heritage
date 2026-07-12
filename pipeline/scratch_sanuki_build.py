import json, subprocess

SRC = 'https://www.city.sanuki.kagawa.jp/education/culture/culturalasset'
FETCHED = '2026-07-12T19:40:00Z'
NOTE_ARCHIVE = 'Wayback Machine snapshot 2025-12-10 (原サイトTLS証明書期限切れ・503のため)'

CAT = {
 '建造物': ('有形文化財','建造物'),
 '絵画': ('有形文化財','絵画'),
 '彫刻': ('有形文化財','彫刻'),
 '工芸品': ('有形文化財','工芸品'),
 '古文書': ('有形文化財','古文書'),
 '考古資料': ('有形文化財','考古資料'),
 '歴史資料': ('有形文化財','歴史資料'),
 '無形民俗': ('民俗文化財','無形民俗文化財'),
 '史跡': ('記念物(史跡・名勝・天然記念物)','史跡'),
 '名勝': ('記念物(史跡・名勝・天然記念物)','名勝'),
 '天然記念物': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

out = subprocess.run(['python3','_h2t.py',
    '/private/tmp/claude-501/-Users-miyazakihitohata/3df58887-c317-49b8-ac70-21b70159396b/scratchpad/sanuki_wayback.html'],
    cwd='/Users/miyazakihitohata/bunkazai/pipeline', capture_output=True, text=True).stdout
lines = out.split('\n')
idx = [i for i,l in enumerate(lines) if l=='=== TABLE ===']
end = [i for i,l in enumerate(lines) if l=='=== /TABLE ===']
t3 = lines[idx[2]+1:end[2]][1:]  # skip header row

results = []
cur = None
for row_str in t3:
    parts = [p.strip() for p in row_str.split('|')]
    if len(parts) == 4:
        kubun, cur, name, loc = parts
    elif len(parts) == 3:
        cur, name, loc = parts
    else:
        name, loc = parts
    cat, subcat = CAT.get(cur, (None, cur))
    results.append({
        "pref": "香川県", "municipality": "さぬき市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": None, "location": loc or None,
        "description": NOTE_ARCHIVE,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/香川県/sanuki.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
print([r['name'] for r in results if r['category'] is None])
