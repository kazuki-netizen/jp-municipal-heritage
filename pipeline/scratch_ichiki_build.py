import json

records = []

def add(name, cat, sub, note=None):
    records.append({
        'pref': '鹿児島県', 'municipality': 'いちき串木野市', 'name': name,
        'category': cat, 'subcategory': sub, 'designation': '市指定',
        'designated_date': None, 'location': None,
        'description': note,
        'source_url': None, 'source_format': 'html',
        'fetched_at': '2026-07-12T13:40:00Z',
    })

MINZOKU_URL = 'https://www.city.ichikikushikino.lg.jp/bunka1/siteiminnzoku.html'
SHISEKI_URL = 'https://www.city.ichikikushikino.lg.jp/bunka1/shisekimeisyourisuto.html'

# 市指定民俗文化財：無形文化財
for name in ['野元虎とり', '羽島南方神社太鼓踊', '川上踊', '虫追踊', '祇園祭']:
    records.append({
        'pref': '鹿児島県', 'municipality': 'いちき串木野市', 'name': name,
        'category': '民俗文化財', 'subcategory': '無形民俗文化財', 'designation': '市指定',
        'designated_date': None, 'location': None, 'description': None,
        'source_url': MINZOKU_URL, 'source_format': 'html',
        'fetched_at': '2026-07-12T13:40:00Z',
    })
# 市指定民俗文化財：有形文化財（本ページの区分名。実質は有形民俗文化財）
for name in ['一石並立型田の神', '神像型田の神']:
    records.append({
        'pref': '鹿児島県', 'municipality': 'いちき串木野市', 'name': name,
        'category': '民俗文化財', 'subcategory': '有形民俗文化財', 'designation': '市指定',
        'designated_date': None, 'location': None, 'description': None,
        'source_url': MINZOKU_URL, 'source_format': 'html',
        'fetched_at': '2026-07-12T13:40:00Z',
    })
# 市指定：史跡
for name in ['驪龍巌（りりょうがん）', 'さつま焼発祥の地', '留学生渡欧の地', '大中公の廟（だいちゅうこうのびょう）',
             '串木野氏の墓', '北口屋橋・椿平橋', '来迎寺跡墓塔群', '金鍾寺跡（きんしょうじあと）', '船着場跡',
             '鍋ヶ城跡と惟宗廣言の墓（なべがじょうあととこれむねひろのりのはか）', '町門の跡', '川口番所跡',
             'お仮屋跡', '孝子德右衛門の墓（こうしとくうえもんのはか）', 'お仮屋通用門', '川上城跡', '岩屋観音',
             '中原の治水溝', '川上中組墓塔群', '旧入来邸武家屋敷と古木']:
    records.append({
        'pref': '鹿児島県', 'municipality': 'いちき串木野市', 'name': name,
        'category': '記念物', 'subcategory': '史跡', 'designation': '市指定',
        'designated_date': None, 'location': None, 'description': None,
        'source_url': SHISEKI_URL, 'source_format': 'html',
        'fetched_at': '2026-07-12T13:40:00Z',
    })
# 市指定：天然記念物
for name in ['うっがんどんの森', '十里塚の榎（じゅうりづかのえのき）', '蘇鉄（そてつ）']:
    records.append({
        'pref': '鹿児島県', 'municipality': 'いちき串木野市', 'name': name,
        'category': '記念物', 'subcategory': '天然記念物', 'designation': '市指定',
        'designated_date': None, 'location': None, 'description': None,
        'source_url': SHISEKI_URL, 'source_format': 'html',
        'fetched_at': '2026-07-12T13:40:00Z',
    })

with open('out/鹿児島県/ichikikushikino.jsonl', 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(records))
