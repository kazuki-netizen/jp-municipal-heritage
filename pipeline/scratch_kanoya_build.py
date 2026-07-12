import json, re, sys
sys.path.insert(0, '.')
from scratch_kagoshima_wareki import wareki

NENGO_RE = r'(明治|大正|昭和|平成|令和)'
DATE_END_RE = re.compile(r'^（' + NENGO_RE + r'(\d+|元)年(\d+)月(\d+)日指定[）)]?$|^（' + NENGO_RE + r'(\d+|元)年(\d+)月(\d+)日指定\)$')

def parse_date(line):
    m = re.match(r'^[（(]' + NENGO_RE + r'(\d+|元)年(\d+)月(\d+)日指定[）)]$', line)
    if not m:
        return None
    nengo, y, mo, da = m.groups()
    return wareki(nengo, y, mo, da)

def is_date_line(line):
    return parse_date(line) is not None

lines = [l.strip() for l in open('/tmp/kanoya.txt', encoding='utf-8')]
# restrict to 市指定文化財一覧 section (line 139 onward, 0-indexed 138) until footer 'お問い合わせ'
start = next(i for i,l in enumerate(lines) if l == '市指定文化財一覧')
end = next(i for i,l in enumerate(lines) if l == 'お問い合わせ')
body = lines[start+1:end]

SECTION_MAP = {
    '有形文化財': ('有形文化財', None),
    '民俗文化財（有形民俗文化財）': ('民俗文化財', None),
    '民俗文化財（無形民俗文化財）': ('民俗文化財', None),
    '記念物（史跡）': ('記念物', None),
    '記念物（天然記念物）': ('記念物', None),
}
SUB_HEADERS = {'考古資料','建造物','彫刻','有形民俗文化財','無形民俗文化財','史跡','天然記念物'}
NOISE = {'写真','名称','所在地','説明','（外部サイトへリンク）','(外部サイトへリンク)'}

cat = None
sub = None
buf = []
records = []

def flush(buf, cat, sub):
    if not buf:
        return
    date = None
    if is_date_line(buf[-1]):
        date = parse_date(buf[-1])
        content = buf[:-1]
    else:
        content = buf[:]
    if not content:
        return
    name = content[0]
    location = content[1] if len(content) > 1 else None
    desc = '；'.join(content[2:]) if len(content) > 2 else None
    records.append({
        'pref': '鹿児島県', 'municipality': '鹿屋市', 'name': name,
        'category': cat, 'subcategory': sub, 'designation': '市指定',
        'designated_date': date, 'location': location,
        'description': desc,
        'source_url': 'https://www.city.kanoya.lg.jp/bunkazaic/bunka/bunka/bunkazai/shitebunkazai.html',
        'source_format': 'html', 'fetched_at': None,
    })

i = 0
extra_notes = []
while i < len(body):
    l = body[i]
    if l in SECTION_MAP:
        cat, forced_sub = SECTION_MAP[l]
        if l == '記念物（天然記念物）':
            sub = '天然記念物'
        i += 1
        continue
    if l in SUB_HEADERS:
        sub = l
        i += 1
        continue
    if l in NOISE:
        i += 1
        continue
    if l == '鹿屋市の無形民俗文化財の紹介':
        i += 1
        continue
    # collect until date line (inclusive), but watch for trailing note lines
    if buf and is_date_line(buf[-1]):
        # buf already complete from prior iteration edge-case; shouldn't happen
        pass
    buf.append(l)
    if is_date_line(l):
        flush(buf, cat, sub)
        buf = []
    i += 1
if buf:
    flush(buf, cat, sub)

# manual patches for entries whose name wrapped onto two lines
for r in records:
    if r['name'] == '上野寺田の' and r['location'] == '庚申塔':
        r['name'] = '上野寺田の庚申塔'
        r['location'] = '上野町'
        r['description'] = None
    elif r['name'] == '長谷観音' and r['location'] == '長谷城跡中世石塔群':
        r['name'] = '長谷観音・長谷城跡中世石塔群'
        r['location'] = '祓川町（大園観音堂）'
    elif r['name'] == '海軍航空隊串良基地跡の地下壕' and r['location'] == '電信司令室':
        r['location'] = '串良町有里4963-7'
    elif r['name'] == '令和元年6月13日一部指定解除（モミ）' and r['location'] == '北原墓地の銀杏':
        # the preceding entry's trailing note ("令和元年...モミ") leaked in as a
        # fake name; this record is really 北原墓地の銀杏.
        note = r['name']
        r['name'] = '北原墓地の銀杏'
        r['location'] = '串良町細山田平瀬'
        if r['description'] and r['description'].startswith('串良町細山田平瀬；'):
            r['description'] = r['description'][len('串良町細山田平瀬；'):]
        for r2 in records:
            if r2['name'] == '諏訪両神社の古木':
                r2['description'] = (r2['description'] + '；' if r2['description'] else '') + note

fetched = '2026-07-12T10:59:00Z'
for r in records:
    r['fetched_at'] = fetched

with open('out/鹿児島県/kanoya.jsonl', 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('written', len(records))
