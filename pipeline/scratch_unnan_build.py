import json, re, subprocess, sys
sys.path.insert(0, '/Users/miyazakihitohata/bunkazai/pipeline')
from scratch_shimane_wareki import ERA_START

def wareki_code(s):
    s = s.strip()
    m = re.match(r'(H|S|R|M|T)0*(\d+)\.(\d+)\.(\d+)', s)
    if not m:
        return None
    era_c, y, mo, d = m.groups()
    era_map = {'M':'明治','T':'大正','S':'昭和','H':'平成','R':'令和'}
    era = era_map[era_c]
    y = int(y); mo = int(mo); d = int(d)
    year = ERA_START[era] + y - 1
    return f'{year:04d}-{mo:02d}-{d:02d}'

CAT_MAP = {
 '建': ('有形文化財','建造物'), '絵': ('有形文化財','絵画'), '彫': ('有形文化財','彫刻'),
 '工': ('有形文化財','工芸品'), '古': ('有形文化財','古文書'), '考': ('有形文化財','考古資料'),
 '歴': ('有形文化財','歴史資料'),
 '有民': ('民俗文化財','有形民俗文化財'), '無民': ('民俗文化財','無形民俗文化財'),
 '史': ('記念物(史跡・名勝・天然記念物)','史跡'), '天': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

out = subprocess.run(['python3', '_h2t.py', 'cache/島根県/unnan/pref_unnan.html'],
                      cwd='/Users/miyazakihitohata/bunkazai/pipeline', capture_output=True, text=True).stdout
lines = out.split('\n')

SRC = 'https://www.pref.shimane.lg.jp/life/bunka/bunkazai/shimane/sityouson/unnan.html'
FETCHED = '2026-07-12T08:43:05Z'
results = []
i = 0
while i < len(lines):
    if lines[i] == '=== TABLE ===':
        j = i + 1
        while lines[j] != '=== /TABLE ===':
            if lines[j] != '番号 | 種別 | 指定年月日 | 名称 | 員数 | 所在地 | 所有者・保持者 | 備考':
                parts = [p.strip() for p in lines[j].split('|')]
                if len(parts) == 8:
                    num, code, date, name, count, loc, owner, note = parts
                    cat, subcat = CAT_MAP.get(code, (None, code))
                    iso = wareki_code(date)
                    desc_parts = [f'指定番号{num}号']
                    if count:
                        desc_parts.append(f'員数{count}')
                    if owner:
                        desc_parts.append(f'所有者・保持者{owner}')
                    if note:
                        desc_parts.append(note)
                    desc = '、'.join(desc_parts)
                    results.append({
                        "pref": "島根県", "municipality": "雲南市", "name": name,
                        "category": cat, "subcategory": subcat, "designation": "市指定",
                        "designated_date": iso, "location": loc or None, "description": desc,
                        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
                    })
            j += 1
        i = j
    i += 1

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/島根県/unnan.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
print('null cat', sum(1 for r in results if r['category'] is None))
