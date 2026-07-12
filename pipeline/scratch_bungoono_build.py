import json, re, sys
sys.path.insert(0, '.')
from bs4 import BeautifulSoup

soup = BeautifulSoup(open('cache/大分県/bungo-ono/1f121129d370dd8d.html', encoding='utf-8', errors='replace'), 'lxml')
for tag in soup(['script', 'style']):
    tag.decompose()
text = soup.get_text('\n')
lines = [l.strip() for l in text.split('\n')]
lines = [l for l in lines if l]

start = lines.index('市指定文化財')
end = lines.index('お問い合わせ', start)
body = lines[start+2:end]  # skip '市指定文化財' and '(計388件)'

SRC = 'https://www.bungo-ohno.jp/docs/2015022000035/'
manifest = json.load(open('cache/大分県/bungo-ono/manifest.json'))
FETCHED = list(manifest.values())[0]['fetched_at']

TOP_MAP = {
    '有形文化財': ('有形文化財', '有形文化財'),
    '有形民俗文化財': ('民俗文化財', '有形民俗文化財'),
    '無形民俗文化財': ('民俗文化財', '無形民俗文化財'),
    '史跡': ('記念物(史跡・名勝・天然記念物)', '史跡'),
    '名勝': ('記念物(史跡・名勝・天然記念物)', '名勝'),
    '天然記念物': ('記念物(史跡・名勝・天然記念物)', '天然記念物'),
}

cur_top = None
cur_sub = None
results = []
item_re = re.compile(r'([^【】]+)【([^】]*)】')

for line in body:
    if line in TOP_MAP:
        cur_top = line
        cur_sub = None
        continue
    if re.match(r'^\d+件$', line):
        continue
    if line.startswith('《') and line.endswith('》'):
        cur_sub = line.strip('《》')
        continue
    if cur_top is None:
        continue
    for m in item_re.finditer(line):
        name = m.group(1).strip()
        loc = m.group(2).strip()
        if not name:
            continue
        cat, subcat = TOP_MAP[cur_top]
        desc = f'区分: {cur_sub}' if cur_sub else None
        results.append({
            "pref": "大分県", "municipality": "豊後大野市", "name": name,
            "category": cat, "subcategory": subcat, "designation": "市指定",
            "designated_date": None, "location": loc or None, "description": desc,
            "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
        })

with open('out/大分県/bungo-ono.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print('total:', len(results))
from collections import Counter
print(Counter((r['category'], r['subcategory']) for r in results))
