import json, sys
sys.path.insert(0, '/Users/miyazakihitohata/bunkazai/pipeline')
from scratch_shimane_wareki import wareki_to_iso

def wshort2(s):
    import re
    era_map = {'M':'明治','T':'大正','S':'昭和','H':'平成','R':'令和'}
    ERA_START = {'明治':1868,'大正':1912,'昭和':1926,'平成':1989,'令和':2019}
    m = re.match(r'(明治|大正|昭和|平成|令和|昭|平|令)\s*(\d+)\.\s*(\d+)\.\s*(\d+)', s)
    if not m:
        return None
    era_c, y, mo, d = m.groups()
    era_map2 = {'昭':'昭和','平':'平成','令':'令和','明治':'明治','大正':'大正','昭和':'昭和','平成':'平成','令和':'令和'}
    era = era_map2[era_c]
    year = ERA_START[era] + int(y) - 1
    return f'{year:04d}-{int(mo):02d}-{int(d):02d}'

SRC = 'https://www.town.ayagawa.lg.jp/docs/2011070700194/file_contents/tiikibousaisiryou.pdf'
FETCHED = '2026-07-12T22:20:00Z'

CAT = {
 '彫刻': ('有形文化財','彫刻'),
 '書跡': ('有形文化財','書跡'),
 '考古資料': ('有形文化財','考古資料'),
 '無形民俗文化財': ('民俗文化財','無形民俗文化財'),
}

# (subcat, name, qty, loc, owner, date_raw)
rows = [
 ('彫刻','木造牛頭天王像','1躯','綾川町滝宮1314','滝宮天満宮','昭51.9.14'),
 ('彫刻','木造孔子像','1躯','綾川町滝宮1314','滝宮天満宮','昭51.9.14'),
 ('書跡','天満宮記','1巻','綾川町滝宮1314','滝宮天満宮','昭51.9.14'),
 ('書跡','滝宮念仏踊制札','2枚','綾川町滝宮1314','滝宮天満宮','昭51.9.14'),
 ('考古資料','龍頭院跡出土古瓦','6枚','綾川町滝宮1314','滝宮天満宮','昭51.9.14'),
 ('無形民俗文化財','主基斎田お田植え祭',None,'綾川町山田上甲1484-7','主基斎田保存会','平12.6.18'),
]

results = []
for subcat, name, qty, loc, owner, date_raw in rows:
    cat, sc = CAT[subcat]
    iso = wshort2(date_raw)
    desc_parts = []
    if qty:
        desc_parts.append(f'員数{qty}')
    desc_parts.append(f'所有者（管理団体）:{owner}')
    results.append({
        "pref": "香川県", "municipality": "綾川町", "name": name,
        "category": cat, "subcategory": sc, "designation": "町指定",
        "designated_date": iso, "location": loc, "description": '、'.join(desc_parts),
        "source_url": SRC, "source_format": "pdf", "fetched_at": FETCHED,
    })

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/香川県/ayagawa.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
print('null dates:', [r['name'] for r in results if r['designated_date'] is None])
