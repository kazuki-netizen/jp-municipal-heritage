import json, re, sys
sys.path.insert(0, '.')
from scratch_oita_wareki import wareki_to_iso

raw = open('/tmp/saiki_shi.txt', encoding='utf-8').read()
# strip standalone/merged "市   指定" watermark prefix
raw = re.sub(r'市\s*指\s*定\s*', '', raw)
lines = raw.split('\n')

SRC = 'https://www.city.saiki.oita.jp/kiji0033505/3_3505_52505_up_m3jbbunk.pdf'
FETCHED = '2026-07-12T09:53:37Z'

era_letter_map = {'S': '昭', 'H': '平', 'R': '令', 'M': '明', 'T': '大'}


def conv_date(raw_d):
    if not raw_d:
        return None
    if raw_d[0] in era_letter_map:
        raw_d = era_letter_map[raw_d[0]] + raw_d[1:]
    return wareki_to_iso(raw_d)


CAT_MAP = {
    '有形文化財': ('有形文化財', '有形文化財'),
    '有形民俗文化財': ('民俗文化財', '有形民俗文化財'),
    '無形民俗文化財': ('民俗文化財', '無形民俗文化財'),
    '史跡': ('記念物(史跡・名勝・天然記念物)', '史跡'),
    '名勝': ('記念物(史跡・名勝・天然記念物)', '名勝'),
    '天然記念物': ('記念物(史跡・名勝・天然記念物)', '天然記念物'),
    '無形文化財': ('無形文化財', '無形文化財'),
}

ROW_RE = re.compile(r'^\s*(\d+)\s+(.*)$')
DATE_RE = re.compile(r'[SHRMT]\d+\.\d{1,2}(?:\.\d{1,2})?$')
DITTO_RE = re.compile(r'^[〃\s]+$')
TOP_PREFIX_RE = re.compile(
    r'^(有\s*形\s*文\s*化\s*財|有\s*形\s*民\s*俗\s*文\s*化\s*財|無\s*形\s*民\s*俗\s*文\s*化\s*財|'
    r'無\s*形\s*文\s*化\s*財|史\s*跡|名\s*勝|天\s*然\s*記\s*念\s*物)\s*'
)

results = []
cur_top = None
unmatched = []

for line in lines:
    m = ROW_RE.match(line)
    if not m:
        continue
    no, rest = m.groups()
    rest = rest.strip()
    if not rest:
        continue

    tm = TOP_PREFIX_RE.match(rest)
    if tm:
        top = re.sub(r'\s+', '', tm.group(1))
        cur_top = top
        rest = rest[tm.end():].strip()
    elif DITTO_RE.match(rest.split(None, 1)[0]) if rest.split(None, 1) else False:
        top = cur_top
        rest = rest.split(None, 1)[1].strip() if len(rest.split(None, 1)) > 1 else ''
    else:
        # maybe starts with ditto mark possibly followed directly by rest without much space
        first_tok = rest.split(None, 1)[0]
        if '〃' in first_tok:
            top = cur_top
            rest = rest[len(first_tok):].strip()
        else:
            unmatched.append((no, line))
            continue

    if top not in CAT_MAP:
        unmatched.append((no, line))
        continue
    cat, subcat = CAT_MAP[top]

    cols = re.split(r'\s{2,}', rest)
    cols = [c.strip() for c in cols if c.strip()]
    remainder = cols
    if not remainder:
        unmatched.append((no, line))
        continue
    # last element(s): look for date at the end
    date_raw = None
    if DATE_RE.match(remainder[-1].replace(' ', '')):
        date_raw = remainder[-1].replace(' ', '')
        remainder = remainder[:-1]
    name = remainder[0] if remainder else ''
    loc = ' '.join(remainder[1:]) if len(remainder) > 1 else None

    date = conv_date(date_raw)
    results.append({
        "pref": "大分県", "municipality": "佐伯市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": date, "location": loc, "description": f'指定番号{no}号',
        "source_url": SRC, "source_format": "pdf", "fetched_at": FETCHED,
    })

print('parsed:', len(results), 'unmatched:', len(unmatched))
for u in unmatched[:30]:
    print('UNMATCHED', u)

with open('out/大分県/saiki.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

from collections import Counter
print(Counter((r['category'], r['subcategory']) for r in results))
print('nulls date:', sum(1 for r in results if r['designated_date'] is None))
