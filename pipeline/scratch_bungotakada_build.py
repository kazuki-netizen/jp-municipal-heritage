import json, re, sys
sys.path.insert(0, '.')
from scratch_oita_wareki import wareki_to_iso

lines = [l for l in open('/tmp/btd_shi_raw.txt', encoding='utf-8') if re.match(r'^\s*\d+\s+市\s+\d+\s', l)]

SRC = 'https://www.city.bungotakada.oita.jp/uploaded/attachment/4286.pdf'
FETCHED = '2026-07-12T09:53:32Z'

AREA_RE = re.compile(r'(高田|真玉|香々地)')
DATE_RE = re.compile(r'(\d{4})[（(]([^)）]+)[)）][.．]?(\d{2})[.．](\d{2})')

SHUBETSU_PATTERNS = [
    (r'美\s*術\s*工\s*芸\s*品\s*[\[［]\s*彫\s*刻\s*[\]］]', ('有形文化財', '彫刻')),
    (r'美\s*術\s*工\s*芸\s*品\s*[\[［]\s*絵\s*画\s*[\]］]', ('有形文化財', '絵画')),
    (r'美\s*術\s*工\s*芸\s*品\s*[\[［]\s*工\s*芸\s*品\s*[\]］]', ('有形文化財', '工芸品')),
    (r'美\s*術\s*工\s*芸\s*品\s*[\[［]\s*書\s*跡\s*[\]］]', ('有形文化財', '書跡')),
    (r'美\s*術\s*工\s*芸\s*品\s*[\[［]\s*歴\s*史\s*資\s*料\s*[\]］]', ('有形文化財', '歴史資料')),
    (r'美\s*術\s*工\s*芸\s*品\s*[\[［]\s*考\s*古\s*資\s*料\s*[\]］]', ('有形文化財', '考古資料')),
    (r'美\s*術\s*工\s*芸\s*品\s*[\[［]\s*書\s*跡\s*[･・]\s*典\s*籍\s*[\]］]', ('有形文化財', '書跡・典籍')),
    (r'美\s*術\s*工\s*芸\s*品\s*[\[［]\s*古\s*文\s*書\s*[\]］]', ('有形文化財', '古文書')),
    (r'建\s*造\s*物', ('有形文化財', '建造物')),
    (r'天\s*然\s*記\s*念\s*物', ('記念物(史跡・名勝・天然記念物)', '天然記念物')),
    (r'名\s*勝', ('記念物(史跡・名勝・天然記念物)', '名勝')),
    (r'史\s*跡', ('記念物(史跡・名勝・天然記念物)', '史跡')),
    (r'有\s*形\s*民\s*俗', ('民俗文化財', '有形民俗文化財')),
    (r'無\s*形\s*民\s*俗', ('民俗文化財', '無形民俗文化財')),
    (r'無\s*形', ('無形文化財', '無形文化財')),
]

results = []
unmatched = []
for line in lines:
    line = line.rstrip('\n')
    m = re.match(r'^\s*(\d+)\s+市\s+(\d+)\s+(.*)$', line)
    serial, ban, rest = m.groups()

    dm = DATE_RE.search(rest)
    if not dm:
        unmatched.append(line)
        continue
    date_start, date_end = dm.span()
    before_date = rest[:date_start]
    after_date = rest[date_end:].strip()
    date = wareki_to_iso(f"{dm.group(2).strip()[0]}{dm.group(2).strip()[1:]}.{int(dm.group(3))}.{int(dm.group(4))}") \
        if False else None
    # build western date directly
    year = int(dm.group(1))
    date = f"{year:04d}-{int(dm.group(3)):02d}-{int(dm.group(4)):02d}"

    # find 種別
    cat = subcat = None
    for pat, mapping in SHUBETSU_PATTERNS:
        mm = list(re.finditer(pat, before_date))
        if mm:
            last = mm[-1]
            cat, subcat = mapping
            shubetsu_start = last.start()
            break
    if cat is None:
        unmatched.append(line)
        continue

    head = before_date[:shubetsu_start]
    # split head into 名称 + area/location using area token (skip a match at position 0,
    # which would mean the 名称 itself starts with an area-like substring, e.g. "真玉八幡社")
    am = AREA_RE.search(head, 1)
    if am:
        name = head[:am.start()].strip()
        loc = head[am.start():].strip()
    else:
        name = head.strip()
        loc = None
    name = re.sub(r'\s+', '', name)
    loc = re.sub(r'\s+', ' ', loc).strip() if loc else None

    desc = f'指定番号{ban}号'
    if after_date:
        desc += f'、{after_date}'

    results.append({
        "pref": "大分県", "municipality": "豊後高田市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": date, "location": loc, "description": desc,
        "source_url": SRC, "source_format": "pdf", "fetched_at": FETCHED,
    })

print('parsed:', len(results), 'unmatched:', len(unmatched))
for u in unmatched:
    print('UNMATCHED:', u)

with open('out/大分県/bungotakada.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

from collections import Counter
print(Counter((r['category'], r['subcategory']) for r in results))
