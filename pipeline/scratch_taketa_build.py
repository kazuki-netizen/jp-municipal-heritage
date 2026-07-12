import json, csv, sys
sys.path.insert(0, '.')

SRC_CSV = 'https://data.bodik.jp/dataset/80c26418-9fba-4121-bc25-4b5d233dd074/resource/cb045c6d-0759-475f-954a-0834244e6c80/download'
FETCHED = '2026-07-12T09:53:00Z'

with open('/tmp/taketa.csv', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

MUKEI_MINZOKU = {
    '姫だるま製造技術', '庚申講', '禰疑野神楽', '禰疑野神社病除祭', '城原神楽',
    '荻神社神楽', '荻神社獅子舞', '橘木神社神楽', '橘木神社獅子舞', '田代八幡神楽',
    '田代八幡神社獅子舞', '恵良原天満社獅子舞', '八坂神社獅子舞', '久住夏越祭りの曳山行事',
    '二又天祖神社岩戸神楽',
}

YUKEI_SUBCAT = {
    '建造物': '建造物',
    '美術工芸品(彫刻)': '彫刻',
    '美術工芸品(工芸品)': '工芸品',
    '美術工芸品(古文書)': '古文書',
    '美術工芸品(絵画)': '絵画',
    '美術工芸品(考古資料)': '考古資料',
    '美術工芸品(歴史資料)': '歴史資料',
}

results = []
for r in rows:
    bunrui = r['文化財分類']
    if not bunrui.startswith('市指定'):
        continue
    name = r['名称'].replace('\n', '　')
    date = r['文化財指定日'] or None
    loc = r['所在地_連結表記'] or None
    if r['所在地_町字']:
        loc = (loc or '') + r['所在地_町字']
    owner = r['所有者等'] or None
    desc = f'所有者等: {owner}' if owner else None

    if bunrui == '市指定有形文化財':
        cat = '有形文化財'
        subcat = YUKEI_SUBCAT.get(r['種類'], '有形文化財')
    elif bunrui == '市指定史跡':
        cat, subcat = '記念物(史跡・名勝・天然記念物)', '史跡'
    elif bunrui == '市指定天然記念物':
        cat, subcat = '記念物(史跡・名勝・天然記念物)', '天然記念物'
    elif bunrui == '市指定名勝':
        cat, subcat = '記念物(史跡・名勝・天然記念物)', '名勝'
    elif bunrui == '市指定民俗文化財':
        if name in MUKEI_MINZOKU:
            cat, subcat = '民俗文化財', '無形民俗文化財'
        else:
            cat, subcat = '民俗文化財', '有形民俗文化財'
    else:
        continue

    results.append({
        "pref": "大分県", "municipality": "竹田市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": date, "location": loc, "description": desc,
        "source_url": SRC_CSV, "source_format": "csv", "fetched_at": FETCHED,
    })

with open('out/大分県/taketa.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print('total:', len(results))
from collections import Counter
print(Counter((r['category'], r['subcategory']) for r in results))
print('nulls date:', sum(1 for r in results if r['designated_date'] is None))
