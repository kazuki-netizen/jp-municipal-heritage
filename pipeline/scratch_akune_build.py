import json, re, sys
sys.path.insert(0, '.')
from scratch_kagoshima_wareki import wareki
from bs4 import BeautifulSoup

manifest = json.load(open('cache/鹿児島県/akune/manifest.json'))
fn = list(manifest.values())[0]['filename']
url = list(manifest.values())[0]['url']
soup = BeautifulSoup(open(f'cache/鹿児島県/akune/{fn}', errors='ignore').read(), 'html.parser')
txt = soup.get_text('\n', strip=True)
start = txt.index('1．八郷のヘゴ')
end = txt.index('この記事に関するお問い合わせ先')
body = txt[start:end]

# split entries on "N．name" pattern
entries = re.split(r'\n(?=\d{1,2}．)', '\n' + body)
entries = [e for e in entries if e.strip()]

SUB_TO_CAT = {
    '天然記念物': ('記念物', '天然記念物'),
    '史跡': ('記念物', '史跡'),
    '有形民俗文化財': ('民俗文化財', '有形民俗文化財'),
    '有形文化財': ('有形文化財', None),  # subcategory refined below
}

records = []
for e in entries:
    lines = [l.strip() for l in e.split('\n') if l.strip()]
    m0 = re.match(r'(\d{1,2})．(.+)', lines[0])
    no, name = m0.groups()
    # find 種別
    si = lines.index('種別')
    kind = lines[si+1]  # e.g. 市指定天然記念物
    di = lines.index('指定年月日')
    date_line = lines[di+1]
    dm = re.match(r'(明治|大正|昭和|平成|令和)(\d+|元)年(\d+)月(\d+)日', date_line)
    date = wareki(*dm.groups()) if dm else None
    desc = '；'.join(lines[di+2:])
    kind_clean = kind.replace('市指定', '')
    if kind_clean == '天然記念物':
        cat, sub = '記念物', '天然記念物'
    elif kind_clean == '史跡':
        cat, sub = '記念物', '史跡'
    elif kind_clean == '有形民俗文化財':
        cat, sub = '民俗文化財', '有形民俗文化財'
    elif kind_clean == '有形文化財':
        cat, sub = '有形文化財', None
    else:
        cat, sub = None, kind_clean
    records.append({
        'pref': '鹿児島県', 'municipality': '阿久根市', 'name': name,
        'category': cat, 'subcategory': sub, 'designation': '市指定',
        'designated_date': date, 'location': None,
        'description': f'指定番号{no}号' + ('；' + desc if desc else ''),
        'source_url': url, 'source_format': 'html',
        'fetched_at': '2026-07-12T12:05:00Z',
    })

SUB_FIX = {
    '河南文書': '古文書', '沼田文書': '古文書', '南方神社の石鳥居': '建造物',
    '南方神社宝物': '工芸品', '脇本古墳群出土遺物': '考古資料',
    '小木原三楽の墓': '建造物', '木造阿弥陀如来坐像': '彫刻',
}
for r in records:
    if r['name'] in SUB_FIX:
        r['subcategory'] = SUB_FIX[r['name']]

with open('out/鹿児島県/akune.jsonl', 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(records))
for r in records:
    print(r['name'], r['category'], r['subcategory'], r['designated_date'])
