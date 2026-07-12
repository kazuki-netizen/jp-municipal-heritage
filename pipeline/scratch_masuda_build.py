import json, sys
from bs4 import BeautifulSoup
sys.path.insert(0, '/Users/miyazakihitohata/bunkazai/pipeline')
from scratch_shimane_wareki import wareki_to_iso

CAT_MAP = {
 '有建': ('有形文化財','建造物'), '絵画': ('有形文化財','絵画'), '彫刻': ('有形文化財','彫刻'),
 '工芸': ('有形文化財','工芸品'), '有古': ('有形文化財','古文書'), '有考': ('有形文化財','考古資料'),
 '有歴': ('有形文化財','歴史資料'), '有民': ('民俗文化財','有形民俗文化財'), '無民': ('民俗文化財','無形民俗文化財'),
 '史跡': ('記念物(史跡・名勝・天然記念物)','史跡'), '史名': ('記念物(史跡・名勝・天然記念物)','史跡及び名勝'),
 '天然': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

with open('/Users/miyazakihitohata/bunkazai/pipeline/cache/島根県/masuda/c541f3276a5477b5.html', encoding='utf-8', errors='replace') as f:
    html = f.read()
soup = BeautifulSoup(html, 'lxml')
t = soup.find_all('table')[0]
rows = t.find_all('tr')

SRC = 'https://www.city.masuda.lg.jp/kanko_bunka_sports/rekishi_bunkazai/bunkazai/2/5212.html'
FETCHED = '2026-07-12T06:55:30Z'
results = []
for r in rows[1:]:
    cells = [c.get_text(strip=True) for c in r.find_all(['td','th'])]
    if len(cells) < 6:
        continue
    catword, date, name, qty, loc, note = cells
    cat, subcat = CAT_MAP.get(catword, (None, catword))
    iso = wareki_to_iso(date)
    desc_parts = [f'員数{qty}']
    if note:
        desc_parts.append(note)
    desc = '、'.join(desc_parts)
    results.append({
        "pref": "島根県", "municipality": "益田市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": iso, "location": loc or None, "description": desc,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/島根県/masuda.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
print('null cat', sum(1 for r in results if r['category'] is None))
