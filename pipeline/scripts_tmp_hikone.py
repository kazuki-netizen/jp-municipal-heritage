import re, json
from bs4 import BeautifulSoup

CATMAP = {
    '建造物': ('有形文化財','建造物'),
    '絵画': ('有形文化財','絵画'),
    '彫刻': ('有形文化財','彫刻'),
    '工芸品': ('有形文化財','工芸品'),
    '書跡': ('有形文化財','書跡'),
    '古文書': ('有形文化財','古文書'),
    '考古資料': ('有形文化財','考古資料'),
    '無形民俗': ('民俗文化財','無形民俗文化財'),
    '有形民俗': ('民俗文化財','有形民俗文化財'),
    '史跡': ('記念物(史跡・名勝・天然記念物)','史跡'),
    '名勝': ('記念物(史跡・名勝・天然記念物)','名勝'),
    '天然記念物': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

WAREKI = {'明治':1868,'大正':1912,'昭和':1926,'平成':1989,'令和':2019}
def to_iso(s):
    m = re.search(r'(明治|大正|昭和|平成|令和)(\d+|元)年(\d+)月(\d+)日', s)
    if not m:
        return None
    era, y, mo, d = m.groups()
    y = 1 if y=='元' else int(y)
    year = WAREKI[era] + y - 1
    return f"{year:04d}-{int(mo):02d}-{int(d):02d}"

soup = BeautifulSoup(open('page.html', encoding='utf-8', errors='ignore'), 'lxml')
t = soup.find_all('table')[2]
rows = t.find_all('tr')[1:]
out = []
url = "https://www.city.hikone.lg.jp/kakuka/kanko_bunka/8/2_2/4655.html"
for r in rows:
    cells = r.find_all(['td','th'])
    texts = [c.get_text(' ', strip=True) for c in cells]
    kind, num, name_date, era, loc_owner, count, _ = texts[:7]
    cat, subcat = CATMAP.get(kind, (None, kind))
    date_iso = to_iso(name_date)
    # name is text before the date pattern
    name = re.split(r'(明治|大正|昭和|平成|令和)\d+年', name_date)[0].strip()
    name = re.sub(r'\s+', ' ', name)
    loc = loc_owner
    desc_parts = [f"指定番号{num}", f"員数{count}"]
    if era:
        desc_parts.append(f"時代:{era}")
    desc = "、".join(desc_parts)
    out.append({
        "pref": "滋賀県",
        "municipality": "彦根市",
        "name": name,
        "category": cat,
        "subcategory": kind,
        "designation": "市指定",
        "designated_date": date_iso,
        "location": loc if loc else None,
        "description": desc,
        "source_url": url,
        "source_format": "html",
        "fetched_at": "2026-07-12T00:00:00Z"
    })

print(len(out))
with open('/Users/user/bunkazai/pipeline/out/滋賀県/hikone.jsonl', 'w', encoding='utf-8') as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
