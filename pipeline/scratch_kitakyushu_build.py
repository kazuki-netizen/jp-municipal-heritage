import json, re
from bs4 import BeautifulSoup

files = {
 '建造物':('menu02_0044.html','有形文化財'),
 '絵画':('menu02_0034.html','有形文化財'),
 '彫刻':('menu02_0035.html','有形文化財'),
 '工芸品':('menu02_0036.html','有形文化財'),
 '古文書':('menu02_0037.html','有形文化財'),
 '考古資料':('menu02_0038.html','有形文化財'),
 '有形民俗文化財':('menu02_0039.html','民俗文化財'),
 '無形民俗文化財':('menu02_0040.html','民俗文化財'),
 '史跡':('menu02_0041.html','記念物(史跡・名勝・天然記念物)'),
 '天然記念物':('menu02_0042.html','記念物(史跡・名勝・天然記念物)'),
}
rows = []
for subcat, (fn, cat) in files.items():
    with open(f'cache/福岡県/kitakyushu/{fn}', encoding='utf-8', errors='replace') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    for a in soup.find_all('a'):
        t = a.get_text(strip=True)
        if t.startswith('【市指定】'):
            name = t.replace('【市指定】', '').strip()
            rows.append({
                "pref": "福岡県", "municipality": "北九州市", "name": name,
                "category": cat, "subcategory": subcat, "designation": "市指定",
                "designated_date": None, "location": None,
                "description": None,
                "source_url": "https://www.city.kitakyushu.lg.jp/kanko/" + fn,
                "source_format": "html", "fetched_at": "2026-07-12T20:57:00Z"
            })

with open('out/福岡県/kitakyushu.jsonl', 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(rows))
