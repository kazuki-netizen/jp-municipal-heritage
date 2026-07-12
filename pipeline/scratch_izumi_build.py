import json, re, os
from bs4 import BeautifulSoup

CACHE = 'cache/鹿児島県/izumi'
manifest = json.load(open(f'{CACHE}/manifest.json'))

SUB_TO_CAT = {
    '史跡': ('記念物', '史跡'),
    '名勝': ('記念物', '名勝'),
    '天然記念物': ('記念物', '天然記念物'),
    '有形文化財（書画）': ('有形文化財', '書画'),
    '有形文化財（工芸品）': ('有形文化財', '工芸品'),
    '有形文化財（古文書）': ('有形文化財', '古文書'),
    '有形文化財（考古資料）': ('有形文化財', '考古資料'),
    '有形文化財（歴史資料）': ('有形文化財', '歴史資料'),
    '有形文化財（建造物）': ('有形文化財', '建造物'),
    '有形文化財（彫刻）': ('有形文化財', '彫刻'),
    '有形文化財': ('有形文化財', None),
    '無形文化財': ('無形文化財', None),
    '有形民俗文化財': ('民俗文化財', '有形民俗文化財'),
    '無形民俗文化財': ('民俗文化財', '無形民俗文化財'),
}

HEADER_RE = re.compile(r'^市指定文化財(?:（(.*)）)?$')
ITEM_RE = re.compile(r'^(\d{1,2}(?:-\d)?)(?!\d)[ 　](.+)')

def classify(label):
    if not label:
        return None, None
    if label in SUB_TO_CAT:
        return SUB_TO_CAT[label]
    m = re.match(r'^(有形文化財|無形文化財|有形民俗文化財|無形民俗文化財)（(.+)）$', label)
    if m:
        outer, inner = m.groups()
        cat = {'有形文化財': '有形文化財', '無形文化財': '無形文化財',
               '有形民俗文化財': '民俗文化財', '無形民俗文化財': '民俗文化財'}[outer]
        sub = inner if outer in ('有形文化財', '無形文化財') else outer
        return cat, sub
    for key, val in SUB_TO_CAT.items():
        if key == label:
            return val
    for key, val in SUB_TO_CAT.items():
        if key in label:
            return val
    return None, label

records = []
seen = set()

for h, entry in manifest.items():
    if entry.get('http_status') != 200 or entry.get('format') != 'html':
        continue
    if entry['url'].endswith('page_40015.html'):
        continue  # index page: bare list, no per-item data
    path = f"{CACHE}/{entry['filename']}"
    if not os.path.exists(path):
        continue
    soup = BeautifulSoup(open(path, errors='ignore').read(), 'html.parser')
    txt = soup.get_text('\n', strip=True)
    m = re.search(r'更新日：\d{4}年\d{1,2}月\d{1,2}日\n', txt)
    if not m:
        continue
    body = txt[m.end():]
    endm = re.search(r'お問い合わせ先', body)
    body = body[:endm.start()] if endm else body
    lines = [l for l in body.split('\n') if l.strip()]

    cat = sub = None
    cur = None  # current record dict
    for l in lines:
        hm = HEADER_RE.match(l)
        if hm:
            label = hm.group(1)
            if label:
                cat, sub = classify(label)
            else:
                # bare "市指定文化財" header (no parenthetical) seen on the
                # 出水麓武家屋敷 sub-item page (17-1..17-4): these are part of
                # the 記念物/史跡 designated group (item 7).
                cat, sub = '記念物', '史跡'
            continue
        im = ITEM_RE.match(l)
        if im:
            if cur:
                records.append(cur)
            no, name = im.groups()
            key = (entry['url'], no)
            if key in seen:
                cur = None
                continue
            seen.add(key)
            cur = {
                'pref': '鹿児島県', 'municipality': '出水市', 'name': name.strip(),
                'category': cat, 'subcategory': sub, 'designation': '市指定',
                'designated_date': None, 'location': None,
                '_desc': [], 'no': no,
                'source_url': entry['url'], 'source_format': 'html',
                'fetched_at': entry.get('fetched_at'),
            }
            continue
        if cur is not None:
            cur['_desc'].append(l)
    if cur:
        records.append(cur)

# The city's own detail pages contain a genuine numbering glitch: both
# "紅葉城跡" and "木牟礼城跡" are labelled "21", which shifts every
# subsequent item's on-page number down by one versus the authoritative
# master list (page_40015.html, the official 出水市の指定文化財 index).
# Re-derive the correct number by matching on name against that master
# list instead of trusting the (buggy) per-item page number.
MASTER_NO = {
    '野間関跡及び古井戸':'1','薩州島津家の墓':'2','山田昌巖の墓':'3','五万石溝底水道':'4',
    '城山':'5','上場遺跡':'6','出水市麓武家屋敷':'7','山伏石像':'8','宇土殿墓':'9',
    '五輪塔・層塔':'10','五輪塔':'11','逆修碑':'12','山田昌巖灰塚':'13','軍役高帳':'14',
    '三十六歌仙':'15','児請絵巻':'16',
    '税所邸':'17-1','旧竹添邸':'17-2','伊藤邸':'17-3','伊牟田邸':'17-4',
    '出水の大楠':'18','ヒノタニシダ':'19','日置流腰矢指矢':'20','紅葉城跡':'21',
    '木牟礼城跡':'22','磨崖仏':'23','五輪宝塔':'24','六地蔵塔':'25','砂原の庚申碑':'26',
    '麓の田ノ神像':'27','仁礼家':'28','浦の田の神像':'29','八久保頭首工水神碑':'30',
    '榎園鎮守社':'31','馬頭観音像':'32','山神橋':'33','海の王子':'34',
    '西水流木造毘沙門天立像':'35','餅井奴':'36','感応寺五廟社':'37','俊寛僧都碑':'38',
    '感応寺仁王像':'39','大日集落の仁王像':'40','別府の田之神':'41','田多園の田之神':'42',
    '中郡の田之神':'43','大日の田之神':'44','青木の田之神':'45','下特手の田之神':'46',
    '屋地の田之神':'47','久木野の田之神':'48','餅井の田之神':'49','天神の田之神':'50',
    '菅原神社の庚申碑':'51','旧小松神社の庚申碑':'52','下特手の道標':'53','八幡の庚申碑':'54',
    '大日の庚申碑':'55','天神の石敢当':'56',
    '武家屋敷門（吉満邸）':'57-1','武家屋敷門（浜田邸）':'57-2','武家屋敷門（吉冨邸）':'57-4',
    '武家屋敷門（石澤邸）':'57-5',
    '川平の巨石群':'58',
    '七田家のソテツ':'59-1','橋元家のソテツ':'59-2','感応寺のソテツ':'59-3',
    '亀井山城':'60',
}

def master_no(name):
    if '層塔' in name:
        return '10'
    if name.startswith('五輪塔') and '層塔' not in name:
        return '11'
    for key, no in MASTER_NO.items():
        if key in name:
            return no
    return None

# 武家屋敷門（吉満邸） appears twice on the source page (57-1 and 57-3 share
# the same owner name); disambiguate the second occurrence explicitly.
seen_yoshimitsu = 0
for r in records:
    if '武家屋敷門（吉満邸）' in r['name']:
        seen_yoshimitsu += 1
        if seen_yoshimitsu == 2:
            r['_master_no_override'] = '57-3'

for r in records:
    no = r.pop('no')
    desc = '；'.join(r.pop('_desc'))
    official_no = r.pop('_master_no_override', None) or master_no(r['name']) or no
    r['description'] = (f'指定番号{official_no}号' if official_no else '') + ('；' + desc if desc else '')
    r['_sortno'] = official_no

def sortkey(r):
    parts = r['_sortno'].split('-')
    return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)

# item 15 (三十六歌仙・絵扁額35枚) is listed in the official index
# (page_40015.html) but has no dedicated detail sub-page among the fetched
# URLs; record it from the index listing alone (name only, null-over-guess
# for fields the index does not state).
records.append({
    'pref': '鹿児島県', 'municipality': '出水市', 'name': '三十六歌仙（絵扁額35枚）',
    'category': '有形文化財', 'subcategory': '絵画', 'designation': '市指定',
    'designated_date': None, 'location': None,
    'description': '指定番号15号',
    'source_url': 'https://www.city.kagoshima-izumi.lg.jp/page/page_40015.html',
    'source_format': 'html', 'fetched_at': '2026-07-12T10:59:05Z',
    '_sortno': '15',
})

records.sort(key=sortkey)
print(len(records))
for r in records:
    print(r['_sortno'], r['name'], r['category'], r['subcategory'])
for r in records:
    del r['_sortno']

with open('out/鹿児島県/izumi.jsonl', 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
