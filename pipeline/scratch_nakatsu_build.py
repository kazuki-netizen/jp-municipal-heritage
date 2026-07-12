import json, re, sys
sys.path.insert(0, '.')
from scratch_oita_wareki import wareki_to_iso

raw = open('/tmp/nakatsu_shi.txt', encoding='utf-8').read()
lines = raw.split('\n')

row_start_re = re.compile(r'^\s*(\d+)\s+(.*)$')
DATE_RE = re.compile(r'[SHR明大昭平令][\dａ-ｚ]*\d+\.\d{1,2}\.\d{1,2}')

starts = []
for i, l in enumerate(lines):
    m = row_start_re.match(l)
    if m and re.search(r'(有形文化財|無形文化財|民俗文化財|記念物)', l[:30]):
        starts.append(i)

blocks = []
for idx, s in enumerate(starts):
    e = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
    blocks.append(lines[s:e])

SRC = 'https://www.city-nakatsu.jp/doc/2024101700025/file_contents/shiteibunkazai.pdf'
FETCHED = '2026-07-12T09:53:32Z'

TOP_VOCAB = ['有形文化財', '無形文化財', '民俗文化財', '記念物']
SUB_VOCAB = ['建造物', '絵画', '彫刻', '工芸品', '書跡', '古文書', '考古資料', '歴史資料',
             '有形民俗', '無形民俗', '史跡', '名勝', '天然記念物']

CAT_MAP = {
    ('有形文化財', None): ('有形文化財', '有形文化財'),
    ('無形文化財', None): ('無形文化財', '無形文化財'),
    ('民俗文化財', '有形民俗'): ('民俗文化財', '有形民俗文化財'),
    ('民俗文化財', '無形民俗'): ('民俗文化財', '無形民俗文化財'),
    ('記念物', '史跡'): ('記念物(史跡・名勝・天然記念物)', '史跡'),
    ('記念物', '名勝'): ('記念物(史跡・名勝・天然記念物)', '名勝'),
    ('記念物', '天然記念物'): ('記念物(史跡・名勝・天然記念物)', '天然記念物'),
}
for s in ['建造物', '絵画', '彫刻', '工芸品', '書跡', '古文書', '考古資料', '歴史資料']:
    CAT_MAP[('有形文化財', s)] = ('有形文化財', s)

results = []
unmatched = []

for block in blocks:
    nospace = re.sub(r'\s+', '', ''.join(block))
    nm = re.match(r'^(\d+)(.*)$', nospace)
    no, rest = nm.groups()

    dm = DATE_RE.search(rest)
    if not dm:
        unmatched.append(('nodate', block))
        continue
    header = rest[:dm.start()]
    date_raw = dm.group(0)

    top = next((t for t in TOP_VOCAB if header.startswith(t)), None)
    sub = None
    if top:
        remainder = header[len(top):]
        sub = next((s for s in SUB_VOCAB if remainder.startswith(s)), None)
    if top is None:
        unmatched.append(('notop', block))
        continue

    # now get name/owner/desc from the date-line column split (spaced version)
    date_line_idx = None
    for i, l in enumerate(block):
        if DATE_RE.search(l):
            date_line_idx = i
            break
    date_line = block[date_line_idx]
    cols = re.split(r'\s{2,}', date_line.strip())
    # last col of cols contains the date somewhere; find its index
    date_col_i = next((i for i, c in enumerate(cols) if DATE_RE.search(c)), None)
    tail_cols = cols[date_col_i + 1:] if date_col_i is not None else []
    name = tail_cols[0] if len(tail_cols) > 0 else ''
    owner = tail_cols[1] if len(tail_cols) > 1 else ''
    desc_parts = tail_cols[2:] if len(tail_cols) > 2 else []

    for l in block[date_line_idx + 1:]:
        s = l.strip()
        if s:
            desc_parts.append(s)
    # prepend any desc text that appeared on lines BEFORE the date_line but after the number-line (wrap-around desc from prior row is already handled since block starts at this row's number line)
    for l in block[:date_line_idx]:
        s = l.strip()
        if s and not any(s.startswith(t) for t in TOP_VOCAB) and s not in SUB_VOCAB:
            # could be stray wrapped 種別② fragment or genuine desc; keep short vocab-like fragments out
            if len(s) <= 3 and any(ch in s for ch in '財列形無有俗'):
                continue
            desc_parts.append(s)

    desc = ''.join(desc_parts) if desc_parts else None

    mapping = CAT_MAP.get((top, sub)) or CAT_MAP.get((top, None))
    if mapping is None:
        unmatched.append(('nomap', block))
        continue
    cat, subcat = mapping
    era_letter_map = {'S': '昭', 'H': '平', 'R': '令', 'M': '明', 'T': '大'}
    date_conv = date_raw
    if date_raw and date_raw[0] in era_letter_map:
        date_conv = era_letter_map[date_raw[0]] + date_raw[1:]
    date = wareki_to_iso(date_conv)

    full_desc = desc
    if owner:
        full_desc = f'所有者: {owner}' + (f'、{desc}' if desc else '')

    results.append({
        "pref": "大分県", "municipality": "中津市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": date, "location": None, "description": full_desc,
        "source_url": SRC, "source_format": "pdf", "fetched_at": FETCHED,
    })

print('parsed:', len(results), 'unmatched:', len(unmatched))
for kind, u in unmatched:
    print('UNMATCHED', kind, u)

# Manually transcribed rows for the 20 that failed automatic column-split due to
# vertically-stacked 種別② text wrapping (verified against raw pdftotext -layout output).
MANUAL = [
    ('高瀬の辻の道標', '個人', 'S60.6.20', '有形民俗', '勅使街道と日田街道が交わる要衝に建てられた道標。'),
    ('織部燈籠', '個人', 'S60.6.20', '有形民俗', '別称キリシタン燈籠。安土桃山から江戸初期の大名、古田織部の考案。'),
    ('納涼塚', '個人', 'S60.6.20', '有形民俗', '文化13年(1816)の建立。筆跡は、本田丹後守忠永。'),
    ('中津祇園の鉦', '個人', 'H27.4.24', '有形民俗', '両方の鉦とも伏鉦で、祇園の時に囃子鉦として使用されていた。'),
    ('白髭神社の神楽面', '白髭神社宮司', 'R5.6.30', '有形民俗', '木造・鍛金造の面。豊前神楽で用いられる面一式が揃う。'),
    ('かます餅祭り', '貴船神社', 'S60.6.20', '無形民俗', '白鳥の大群が芋の苗をくわえて飛来し、苗が餅となって飢える人々を救ったと伝わる祭礼。'),
    ('さいすくい祭り', '貴船神社', 'S60.6.20', '無形民俗', '宮下の小川に入り、すくいあげた小魚を神前に供え、豊穣の感謝と安泰を祈念する神事。'),
    ('小祝番所踊り', '番所踊り保存会', 'H21.5.28', '無形民俗', '島原の乱（1637年）に中津藩が出陣し多数の死傷者を出したため、その供養踊りとして始まった。'),
    ('大野八幡神社やんさ祭', '大野八幡神社やんさ祭保存会', 'S50.1.10', '無形民俗', '応永元年（1394）より始まった野中氏にまつわる勇壮な裸祭り。'),
    ('豊前国耶馬渓神楽', '本耶馬渓町神楽保存会', 'S50.1.25', '無形民俗', '東谷村の頃、屋成多三吉という宮大工によって東谷と屋形に伝えられる。'),
    ('岩戸神楽', '戸原神楽保存会・深耶馬神楽保存会', 'S50.1.10', '無形民俗', '豊前岩戸神楽と称し、現在では戸原神楽社と深耶馬神楽社と2つの神楽社がその継承に努めている耶馬溪地方に伝わる神楽。'),
    ('白地楽', '白地楽保存会', 'S54.2.17', '無形民俗', '約280年前から伝わる楽。子ども4名、大人4名で水神（カッパ）を鎮める所作。'),
    ('樋山路楽・二瀬楽', '樋山路共有', 'H29.5.8', '無形民俗', '樋山路共有が保持するカッパ祭り。伊勢山大神社と二瀬天満宮でそれぞれ実施される。'),
    ('白髭神社の大名行列', '白髭神社大名行列保存会', 'R5.6.30', '無形民俗', '隔年の秋の祭礼時に奉納される。疫病流行の折には中津藩主・奥平家による社参等を受けることも多く、この供奉の様子が大名行列の原型とする説もある。'),
    ('天満宮の照葉樹林', '個人', 'S56.4.14', '天然記念物', '犬丸天満宮の自然林。'),
    ('長久寺のコジイ林（アラカシ林）', '個人', 'S60.6.20', '天然記念物', '田丸城跡の濠内側の土塁上に自生。'),
    ('サザンカ', '個人', 'S52.4.1', '天然記念物', '推定樹齢400年'),
    ('キンモクセイ', '個人', 'S52.4.1', '天然記念物', '推定樹齢400年'),
    ('光円寺のしだれ桜', '竜求山光円寺', 'S53.12.1', '天然記念物', '樹齢350年以上といわれ、樹の太さ約3m、高さ10mの枝垂桜。'),
    ('ベッコウトンボ', '個人', 'R6.7.26', '天然記念物', '野依新池に生息する年1世代のトンボ。絶滅危惧種ⅠA類'),
]

era_letter_map = {'S': '昭', 'H': '平', 'R': '令', 'M': '明', 'T': '大'}
for name, owner, date_raw, sub, desc in MANUAL:
    cat, subcat = CAT_MAP[('民俗文化財', sub)] if sub in ('有形民俗', '無形民俗') else CAT_MAP[('記念物', sub)]
    date_conv = era_letter_map[date_raw[0]] + date_raw[1:]
    date = wareki_to_iso(date_conv)
    full_desc = f'所有者: {owner}、{desc}' if owner else desc
    results.append({
        "pref": "大分県", "municipality": "中津市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": date, "location": None, "description": full_desc,
        "source_url": SRC, "source_format": "pdf", "fetched_at": FETCHED,
    })

with open('out/大分県/nakatsu.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

from collections import Counter
print(Counter((r['category'], r['subcategory']) for r in results))
print('nulls date:', sum(1 for r in results if r['designated_date'] is None))
print('empty name:', sum(1 for r in results if not r['name']))
