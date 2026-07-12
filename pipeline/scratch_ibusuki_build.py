import json, re, sys
sys.path.insert(0, '.')
from scratch_kagoshima_wareki import wareki
from bs4 import BeautifulSoup

manifest = json.load(open('cache/鹿児島県/ibusuki/manifest.json'))
fn = list(manifest.values())[0]['filename']
url = list(manifest.values())[0]['url']
fetched = list(manifest.values())[0]['fetched_at']
soup = BeautifulSoup(open(f'cache/鹿児島県/ibusuki/{fn}', errors='ignore').read(), 'html.parser')
tables = soup.find_all('table')
DISTRICTS = ['指宿地区', '山川地区', '開聞地区']

SUB_TO_CAT = {
    '史跡': ('記念物', '史跡'),
    '天然記念物': ('記念物', '天然記念物'),
    '名勝': ('記念物', '名勝'),
    '有形文化財': ('有形文化財', None),
    '無形文化財': ('無形文化財', None),
    '有形民俗文化財': ('民俗文化財', '有形民俗文化財'),
    '無形民俗文化財': ('民俗文化財', '無形民俗文化財'),
}

def parse_date(s):
    m = re.match(r'(明治|大正|昭和|平成|令和)(\d+|元)年(\d+)月(\d+)日', s)
    if not m:
        return None
    return wareki(*m.groups())

records = []
for district, table in zip(DISTRICTS, tables):
    trs = table.find_all('tr')
    header = [x.get_text(strip=True) for x in trs[0].find_all(['th', 'td'])]
    for tr in trs[1:]:
        cells = [x.get_text(' ', strip=True) for x in tr.find_all(['th', 'td'])]
        if len(cells) < 5:
            continue
        kind, name, loc, date_s, kubun = cells[:5]
        if '市指定' not in kubun:
            continue
        cat, sub = SUB_TO_CAT.get(kind, (None, kind))
        records.append({
            'pref': '鹿児島県', 'municipality': '指宿市', 'name': name,
            'category': cat, 'subcategory': sub, 'designation': '市指定',
            'designated_date': parse_date(date_s), 'location': loc or None,
            'description': f'地区: {district}',
            'source_url': url, 'source_format': 'html', 'fetched_at': fetched,
        })

with open('out/鹿児島県/ibusuki.jsonl', 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(records))
for r in records:
    print(r['name'], r['category'], r['subcategory'], r['designated_date'])
