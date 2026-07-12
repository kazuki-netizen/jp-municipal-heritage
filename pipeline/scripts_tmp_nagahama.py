import re, json
from scripts_tmp_nagahama_data import ROWS

CATMAP = {
    '建造物': ('有形文化財','建造物'),
    '絵画': ('有形文化財','絵画'),
    '彫刻': ('有形文化財','彫刻'),
    '工芸品': ('有形文化財','工芸品'),
    '書跡': ('有形文化財','書跡・典籍・古文書'),
    '考古資料': ('有形文化財','考古資料'),
    '歴史資料': ('有形文化財','歴史資料'),
    '有形民俗': ('民俗文化財','有形民俗文化財'),
    '無形民俗': ('民俗文化財','無形民俗文化財'),
    '史跡': ('記念物(史跡・名勝・天然記念物)','史跡'),
    '名勝': ('記念物(史跡・名勝・天然記念物)','名勝'),
    '天然記念物': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

WAREKI = {'明治':1868,'大正':1912,'昭和':1926,'平成':1989,'令和':2019}
def to_iso(s):
    if not s:
        return None
    m = re.search(r'(明治|大正|昭和|平成|令和)(\d+|元)年(\d+)月(\d+)日', s)
    if not m:
        return None
    era, y, mo, d = m.groups()
    y = 1 if y=='元' else int(y)
    year = WAREKI[era] + y - 1
    return f"{year:04d}-{int(mo):02d}-{int(d):02d}"

url = "https://www.city.nagahama.lg.jp/cmsfiles/contents/0000014/14176/ichiran.pdf"
out = []
for (no, kind, name, count, era, date_wareki, owner, loc) in ROWS:
    cat, subcat = CATMAP[kind]
    date_iso = to_iso(date_wareki)
    desc_parts = [f"指定番号{no}"]
    if count:
        desc_parts.append(f"員数{count}")
    if era:
        desc_parts.append(f"時代:{era}")
    out.append({
        "pref": "滋賀県",
        "municipality": "長浜市",
        "name": name,
        "category": cat,
        "subcategory": kind,
        "designation": "市指定",
        "designated_date": date_iso,
        "location": f"{owner} {loc}".strip() if owner or loc else None,
        "description": "、".join(desc_parts),
        "source_url": url,
        "source_format": "pdf",
        "fetched_at": "2026-07-12T00:00:00Z"
    })

print(len(out))
with open('/Users/miyazakihitohata/bunkazai/pipeline/out/滋賀県/nagahama.jsonl', 'w', encoding='utf-8') as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")

nulls = sum(1 for o in out if o['designated_date'] is None)
print('null dates', nulls)
