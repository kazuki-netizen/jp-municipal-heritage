import json, re, sys
sys.path.insert(0, '.')
from scratch_kagoshima_wareki import wareki

NENGO_CHAR = {'M': '明治', 'T': '大正', 'S': '昭和', 'H': '平成', 'R': '令和'}
DATE_RE = re.compile(r'([MTSHR])(\d+|元)\.(\d+)\.(\d+)')

def parse_date(s):
    m = DATE_RE.search(s)
    if not m:
        return None
    c, y, mo, d = m.groups()
    return wareki(NENGO_CHAR[c], y, mo, d)

QTY_RE = re.compile(r'(\d+)\s*(件|基|対|面|幅|振|式|体|口|枚|箇所|ヶ所|冊|巻|棟|区|点|柱)')

lines = open('/tmp/minamikyushu.txt', encoding='utf-8').read().split('\n')
start = next(i for i, l in enumerate(lines) if '市指定文化財' in l)
body = lines[start + 1:]

HEADER_SKIP = re.compile(r'種\s*別|区\s*分|名\s*称|員数|所在地|指定年月日|備\s*考')
NO_RE = re.compile(r'^(\d{1,3})\s+(有形|無形|記念物|民俗)\s+(\S+(?:\(.+?\))?)\s+(.*)')

SUB_MAP = {
    ('有形', '建造物'): ('有形文化財', '建造物'),
    ('無形', None): ('無形文化財', None),
    ('民俗', '有形'): ('民俗文化財', '有形民俗文化財'),
    ('民俗', '無形'): ('民俗文化財', '無形民俗文化財'),
    ('記念物', '史跡'): ('記念物', '史跡'),
    ('記念物', '名勝'): ('記念物', '名勝'),
    ('記念物', '天然記念物'): ('記念物', '天然記念物'),
}

def classify(top, sub_raw):
    if top == '有形':
        m = re.match(r'建造物・美工\((.+)\)', sub_raw)
        if m:
            return '有形文化財', m.group(1)
        if sub_raw == '建造物':
            return '有形文化財', '建造物'
        m = re.match(r'美工\((.+)\)', sub_raw)
        if m:
            return '有形文化財', m.group(1)
        return '有形文化財', sub_raw
    if top == '無形':
        return '無形文化財', sub_raw if sub_raw not in ('None',) else None
    if top == '民俗':
        if '有形' in sub_raw:
            return '民俗文化財', '有形民俗文化財'
        if '無形' in sub_raw:
            return '民俗文化財', '無形民俗文化財'
        return '民俗文化財', sub_raw
    if top == '記念物':
        return '記念物', sub_raw
    return None, sub_raw

# assemble entries: an entry starts at a NO_RE-matching line and continues
# until the next NO_RE-matching line (or a header/footer line to skip).
entries = []
cur = None
for raw in body:
    l = raw.rstrip()
    if not l.strip():
        continue
    if HEADER_SKIP.search(l) and NO_RE.match(l) is None:
        continue
    if '南九州市の指定文化財一覧表' in l or '令和' in l and '現在' in l:
        continue
    m = NO_RE.match(l.strip())
    if m:
        if cur:
            entries.append(cur)
        no, top, sub_raw, rest = m.groups()
        cur = {'no': no, 'top': top, 'sub_raw': sub_raw, 'lines': [rest]}
    else:
        if cur:
            cur['lines'].append(l.strip())
if cur:
    entries.append(cur)

records = []
for e in entries:
    full = ' '.join(e['lines'])
    date = parse_date(full)
    date_span = None
    dm = DATE_RE.search(full)
    if dm:
        date_span = dm.span()
    before_date = full[:date_span[0]].strip() if date_span else full
    qm = QTY_RE.search(before_date)
    if qm:
        name = before_date[:qm.start()].strip()
        location = before_date[qm.end():].strip()
    else:
        name = before_date.strip()
        location = None
    cat, sub = classify(e['top'], e['sub_raw'])
    records.append({
        'pref': '鹿児島県', 'municipality': '南九州市', 'name': name,
        'category': cat, 'subcategory': sub, 'designation': '市指定',
        'designated_date': date, 'location': location or None,
        'description': f"指定番号{e['no']}号" + (f'；員数: {qm.group(0)}' if qm else ''),
        'source_url': 'https://www.city.minamikyushu.lg.jp/material/files/group/20/shiteibunkaitiran.pdf',
        'source_format': 'pdf', 'fetched_at': '2026-07-12T11:00:00Z',
    })

# Fix known parser edge case: rows whose 区分 wraps across three physical
# lines as "建造物・美工\n(歴史資料)" or "美工(歴史資\n料)" (name = 中央行のみ).
# For those rows the middle line has no 区分 token, so classify() mistakenly
# read the item's NAME as the subcategory and left name blank.
FIX_HISTORY_NO = {'5', '6', '7', '8', '47', '48', '49', '50', '51', '52',
                   '53', '54', '55', '56', '57', '58', '59', '60'}
for r in records:
    nm = re.match(r'指定番号(\d+)号', r['description'])
    no = nm.group(1) if nm else ''
    if no in FIX_HISTORY_NO and not r['name']:
        r['name'] = r['subcategory']
        r['subcategory'] = '歴史資料'
    if no == '111':
        r['name'] = '飯倉神社お田植祭りに伴う芸能　宮棒踊り'

print(len(records))
for r in records[:20]:
    print(r['no'] if 'no' in r else '', r['name'], '|', r['category'], r['subcategory'], '|', r['designated_date'], '|', r['location'])
with open('out/鹿児島県/minamikyushu.jsonl', 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
