from bs4 import BeautifulSoup
import json

CATMAP = {
    '建造物': ('有形文化財','建造物'),
    '絵画': ('有形文化財','絵画'),
    '彫刻': ('有形文化財','彫刻'),
    '工芸品': ('有形文化財','工芸品'),
    '書跡': ('有形文化財','書跡'),
    '考古資料': ('有形文化財','考古資料'),
    '名勝': ('記念物(史跡・名勝・天然記念物)','名勝'),
    '天然記念物': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
    '有形民俗文化財': ('民俗文化財','有形民俗文化財'),
    '歴史資料': ('有形文化財','歴史資料'),
}
ORDER = ['建造物','絵画','彫刻','工芸品','書跡','考古資料','名勝','天然記念物','有形民俗文化財','歴史資料']

soup = BeautifulSoup(open('/Users/user/bunkazai/pipeline/cache/滋賀県/omihachiman/page.html', encoding='utf-8', errors='ignore'), 'lxml')
tables = soup.find_all('table')
url = "https://www.city.omihachiman.lg.jp/soshiki/kanko/4_1/1519.html"
out = []
for idx, tbl_i in enumerate(range(14, 24)):
    kind = ORDER[idx]
    cat, subcat = CATMAP[kind]
    t = tables[tbl_i]
    rows = t.find_all('tr')[1:]
    for r in rows:
        cells = r.find_all(['td','th'])
        texts = [c.get_text(' ', strip=True) for c in cells]
        if len(texts) < 3:
            continue
        name, loc, era = texts[0], texts[1], texts[2]
        desc = f"時代:{era}" if era else None
        out.append({
            "pref": "滋賀県",
            "municipality": "近江八幡市",
            "name": name,
            "category": cat,
            "subcategory": kind,
            "designation": "市指定",
            "designated_date": None,
            "location": loc if loc else None,
            "description": desc,
            "source_url": url,
            "source_format": "html",
            "fetched_at": "2026-07-12T00:00:00Z"
        })

print(len(out))
with open('/Users/user/bunkazai/pipeline/out/滋賀県/omihachiman.jsonl', 'w', encoding='utf-8') as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
