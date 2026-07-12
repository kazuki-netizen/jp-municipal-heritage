import json, re, sys
sys.path.insert(0, '.')
from scratch_oita_wareki import wareki_to_iso
from bs4 import BeautifulSoup

soup = BeautifulSoup(open('cache/大分県/hiji/6ba76439bcb4066a.html', encoding='utf-8', errors='replace'), 'lxml')
for tag in soup(['script', 'style']):
    tag.decompose()
main = soup.find('div', id='main') or soup
els = main.find_all(['h3', 'h4', 'table'])

SRC = 'https://www.town.hiji.lg.jp/gyoseijoho/shisetsuannai/shiryokan_kinenkan/bunkazai-lists.html'
manifest = json.load(open('cache/大分県/hiji/manifest.json'))
FETCHED = list(manifest.values())[0]['fetched_at']

CAT_MAP = {
    '有形文化財（建造物）': ('有形文化財', '建造物'),
    '有形文化財（絵画）': ('有形文化財', '絵画'),
    '有形文化財（彫刻）': ('有形文化財', '彫刻'),
    '有形文化財（工芸）': ('有形文化財', '工芸品'),
    '重要文化財ー有形文化財（建造物）': ('有形文化財', '建造物'),
    '民俗文化財（有形民俗文化財）': ('民俗文化財', '有形民俗文化財'),
    '民俗文化財（無形民俗文化財）': ('民俗文化財', '無形民俗文化財'),
    '記念物（史跡）': ('記念物(史跡・名勝・天然記念物)', '史跡'),
    '記念物（名勝）': ('記念物(史跡・名勝・天然記念物)', '名勝'),
    '記念物（天然記念物）': ('記念物(史跡・名勝・天然記念物)', '天然記念物'),
    '天然記念物': ('記念物(史跡・名勝・天然記念物)', '天然記念物'),
    '名勝': ('記念物(史跡・名勝・天然記念物)', '名勝'),
}

cur_h3 = None
results = []
i = 0
while i < len(els):
    el = els[i]
    if el.name == 'h3':
        cur_h3 = el.get_text(strip=True)
        i += 1
        continue
    if el.name == 'table':
        # find the h4 label that follows (may be immediately next, or none if end of section)
        label = None
        if i + 1 < len(els) and els[i+1].name == 'h4':
            label = els[i+1].get_text(strip=True)
        if cur_h3 == '日出町指定文化財' and label in CAT_MAP:
            cat, subcat = CAT_MAP[label]
            rows = el.find_all('tr')
            header = [th.get_text(strip=True) for th in rows[0].find_all(['td', 'th'])]
            for tr in rows[1:]:
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if len(cells) < 2:
                    continue
                name, date_raw = cells[0], cells[1]
                date = wareki_to_iso(date_raw)
                results.append({
                    "pref": "大分県", "municipality": "日出町", "name": name,
                    "category": cat, "subcategory": subcat, "designation": "町指定",
                    "designated_date": date, "location": None, "description": None,
                    "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
                })
        i += 1
        continue
    i += 1  # h4, skip (already consumed by lookahead)

with open('out/大分県/hiji.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print('total:', len(results))
from collections import Counter
print(Counter((r['category'], r['subcategory']) for r in results))
print('nulls date:', sum(1 for r in results if r['designated_date'] is None))
