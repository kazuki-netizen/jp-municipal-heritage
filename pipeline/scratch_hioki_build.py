import json, re, os
from bs4 import BeautifulSoup

CACHE = 'cache/鹿児島県/hioki'
manifest = json.load(open(f'{CACHE}/manifest.json'))

DISTRICT_BY_PATH = {
    'higashiichiki': '東市来', 'ijuin': '伊集院', 'hiyoshi': '日吉', 'fukiage': '吹上',
}

SUB_TO_CAT = {
    '天然記念物': ('記念物', '天然記念物'), '史跡': ('記念物', '史跡'), '名勝': ('記念物', '名勝'),
    '有形民俗文化財': ('民俗文化財', '有形民俗文化財'), '無形民俗文化財': ('民俗文化財', '無形民俗文化財'),
    '有形文化財': ('有形文化財', None), '無形文化財': ('無形文化財', None),
    '建造物': ('有形文化財', '建造物'), '彫刻': ('有形文化財', '彫刻'), '絵画': ('有形文化財', '絵画'),
    '工芸品': ('有形文化財', '工芸品'), '書跡': ('有形文化財', '書跡'), '古文書': ('有形文化財', '古文書'),
    '考古資料': ('有形文化財', '考古資料'), '歴史資料': ('有形文化財', '歴史資料'),
    '民俗芸能': ('民俗文化財', '民俗芸能'), '風俗慣習': ('民俗文化財', '風俗慣習'),
    '民俗資料': ('民俗文化財', '民俗資料'),
}

def classify(kubun):
    # kubun like "市指定有形文化財" / "市指定史跡" / "市指定彫刻" / "国指定天然記念物" / "未指定"
    if not kubun.startswith('市指定'):
        return None, None, None
    label = kubun[len('市指定'):]
    for key, val in sorted(SUB_TO_CAT.items(), key=lambda kv: -len(kv[0])):
        if key == label:
            return ('市指定',) + val
    for key, val in sorted(SUB_TO_CAT.items(), key=lambda kv: -len(kv[0])):
        if key in label:
            return ('市指定',) + val
    return ('市指定', None, label or None)

records = []
for h, entry in manifest.items():
    if entry.get('http_status') != 200 or entry.get('format') != 'html':
        continue
    url = entry['url']
    m = re.search(r'/(higashiichiki|ijuin|hiyoshi|fukiage)/', url)
    if not m:
        continue
    district = DISTRICT_BY_PATH[m.group(1)]
    path = f"{CACHE}/{entry['filename']}"
    if not os.path.exists(path):
        continue
    soup = BeautifulSoup(open(path, errors='ignore').read(), 'html.parser')
    txt = soup.get_text('\n', strip=True)
    m2 = re.search(r'ここから本文です。\n(.+?)\n名称\n(.+?)\n区分\n(.+?)\n概要\n(.+?)\nお問い合わせ', txt, re.S)
    if not m2:
        continue
    title, name, kubun, gaiyo = m2.groups()
    desig = classify(kubun.strip())
    if desig[0] is None:
        continue
    _, cat, sub = desig
    records.append({
        'pref': '鹿児島県', 'municipality': '日置市', 'name': name.strip(),
        'category': cat, 'subcategory': sub, 'designation': '市指定',
        'designated_date': None, 'location': None,
        'description': f'地区: {district}；' + gaiyo.strip().replace('\n', '；'),
        'source_url': url, 'source_format': 'html',
        'fetched_at': entry.get('fetched_at'),
    })

with open('out/鹿児島県/hioki.jsonl', 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(records))
for r in records:
    print(r['name'], r['category'], r['subcategory'])
