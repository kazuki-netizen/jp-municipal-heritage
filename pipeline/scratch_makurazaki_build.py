import json, re, sys
sys.path.insert(0, '.')
from scratch_kagoshima_wareki import wareki
from bs4 import BeautifulSoup

NENGO = {'明治':'明治','大正':'大正','昭和':'昭和','平成':'平成','令和':'令和'}

def parse_wareki_date(s):
    m = re.search(r'(明治|大正|昭和|平成|令和)(\d+|元)年(\d+)月(\d+)日', s)
    if not m:
        return None
    n, y, mo, d = m.groups()
    return wareki(n, y, mo, d)

manifest = json.load(open('cache/鹿児島県/makurazaki/manifest.json'))
url_to_file = {v['url']: v['filename'] for v in manifest.values()}

ITEMS = [
    # (page url no, name(url filename id used to look up), category, subcategory)
    ('5648', '万句賀親乾', '有形文化財', '書跡・典籍', 22),
    ('5649', '播磨椙原', '有形文化財', '書跡・典籍', None),
    ('5650', '捨小舟', '有形文化財', '書跡・典籍', None),
    ('5659', '松之尾貝製腕輪', '有形文化財', '考古資料', None),
    ('5658', '枕崎風景画', '有形文化財', '絵画', None),
    ('5657', '大山祗神社の太鼓・面', '民俗文化財', '有形民俗文化財', None),
    ('5656', '城山の梵鐘', '有形文化財', '工芸品', None),
    ('22291', '道野樟脳製造所遺構', '記念物', '史跡', None),
    ('5662', '硫黄山岩崎寺跡', '記念物', '史跡', None),
    ('5655', '下園モモカンドン', '民俗文化財', '有形民俗文化財', None),
    ('5654', '桜之城跡', '記念物', '史跡', None),
    ('5653', '茅野の田の神', '民俗文化財', '有形民俗文化財', None),
    ('5652', '小園の田の神', '民俗文化財', '有形民俗文化財', None),
    ('5651', '喜入氏累代の墓', '記念物', '史跡', None),
    ('432', '宗前岳の牧神', '民俗文化財', '有形民俗文化財', None),
    ('431', '松之尾遺跡', '記念物', '史跡', None),
    ('430', '田布川の田の神', '民俗文化財', '有形民俗文化財', None),
]

# No. from the official list (5646.html) 1-17
NO_MAP = {
    '万句賀親乾':1,'播磨椙原':2,'捨小舟':3,'喜入氏累代の墓':4,'小園の田の神':5,
    '茅野の田の神':6,'田布川の田の神':7,'松之尾遺跡':8,'桜之城跡':9,'下園モモカンドン':10,
    '城山の梵鐘':11,'大山祗神社の太鼓・面':12,'枕崎風景画':13,'松之尾貝製腕輪':14,
    '宗前岳の牧神':15,'硫黄山岩崎寺跡':16,'道野樟脳製造所遺構':17,
}
LOC_MAP = {
    '万句賀親乾':'枕崎市山手町','播磨椙原':'枕崎市山手町','捨小舟':'枕崎市山手町',
    '喜入氏累代の墓':'枕崎市桜山本町','小園の田の神':'枕崎市桜山本町','茅野の田の神':'枕崎市茅野町',
    '田布川の田の神':'枕崎市田布川町','松之尾遺跡':'枕崎市汐見町','桜之城跡':'枕崎市桜山町',
    '下園モモカンドン':'枕崎市妙見町','城山の梵鐘':'枕崎市桜山町','大山祗神社の太鼓・面':'枕崎市金山町',
    '枕崎風景画':'枕崎市山手町','松之尾貝製腕輪':'枕崎市山手町','宗前岳の牧神':'枕崎市春日町',
    '硫黄山岩崎寺跡':'枕崎市立神本町','道野樟脳製造所遺構':'枕崎市桜山上町',
}

records = []
for page_id, name, cat, sub, _ in ITEMS:
    url = f'https://www.city.makurazaki.lg.jp/site/history/{page_id}.html'
    fn = url_to_file[url]
    soup = BeautifulSoup(open(f'cache/鹿児島県/makurazaki/{fn}', errors='ignore').read(), 'html.parser')
    txt = soup.get_text('\n', strip=True)
    idx = txt.rfind('掲載日')
    body = txt[idx:]
    m = re.search(r'指定日\n(.+?)\n', body)
    date = parse_wareki_date(m.group(1)) if m else None
    # description: between the second occurrence of the name and "指定日"
    parts = body.split('指定日')
    desc_block = parts[0]
    lines = [l for l in desc_block.split('\n') if l.strip()]
    # drop leading '掲載日：...' and the repeated title line
    desc_lines = lines[2:] if len(lines) > 2 else lines
    desc = ''.join(desc_lines).strip() or None
    records.append({
        'pref': '鹿児島県', 'municipality': '枕崎市', 'name': name,
        'category': cat, 'subcategory': sub, 'designation': '市指定',
        'designated_date': date, 'location': LOC_MAP[name],
        'description': (f'指定番号{NO_MAP[name]}号' + ('；' + desc if desc else '')),
        'source_url': url, 'source_format': 'html',
        'fetched_at': '2026-07-12T12:00:00Z',
    })

records.sort(key=lambda r: NO_MAP[r['name']])
with open('out/鹿児島県/makurazaki.jsonl', 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(records))
for r in records:
    print(r['name'], r['category'], r['subcategory'], r['designated_date'])
