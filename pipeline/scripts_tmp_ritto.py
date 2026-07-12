import re, json
from scripts_tmp_ritto_data import ROWS

CATMAP = {
    '彫': ('有形文化財','彫刻'),
    '工': ('有形文化財','工芸品'),
    '建': ('有形文化財','建造物'),
    '名': ('記念物(史跡・名勝・天然記念物)','名勝'),
    '史': ('記念物(史跡・名勝・天然記念物)','史跡'),
    '絵': ('有形文化財','絵画'),
    '考': ('有形文化財','考古資料'),
    '書': ('有形文化財','書跡'),
    '歴': ('有形文化財','歴史資料'),
    '無民': ('民俗文化財','無形民俗文化財'),
}
WAREKI = {'明治':1868,'大正':1912,'昭和':1926,'平成':1989,'令和':2019}
def to_iso(s):
    if not s: return None
    m = re.search(r'(明治|大正|昭和|平成|令和)(\d+|元)年(\d+)月(\d+)日', s)
    if not m: return None
    era, y, mo, d = m.groups()
    y = 1 if y=='元' else int(y)
    year = WAREKI[era] + y - 1
    return f"{year:04d}-{int(mo):02d}-{int(d):02d}"

url = "https://www.city.ritto.lg.jp/material/files/group/55/shiteibunkazai251127.pdf"
out = []
for (no, date_s, kind, name, loc, owner, era) in ROWS:
    cat, subcat = CATMAP[kind]
    date_iso = to_iso(date_s)
    location = " ".join(x for x in [loc, owner] if x) or None
    desc = f"指定番号第{no}号"
    if era:
        desc += f"、時代:{era}"
    out.append({
        "pref": "滋賀県",
        "municipality": "栗東市",
        "name": name,
        "category": cat,
        "subcategory": subcat,
        "designation": "市指定",
        "designated_date": date_iso,
        "location": location,
        "description": desc,
        "source_url": url,
        "source_format": "pdf",
        "fetched_at": "2026-07-12T00:00:00Z"
    })

print(len(out))
with open('/Users/user/bunkazai/pipeline/out/滋賀県/ritto.jsonl', 'w', encoding='utf-8') as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
nulls = sum(1 for o in out if o['designated_date'] is None)
print('nulls', nulls)
