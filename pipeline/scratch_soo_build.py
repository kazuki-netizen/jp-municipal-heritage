import json, re, os
from bs4 import BeautifulSoup

CACHE = 'cache/鹿児島県/soo'
manifest = json.load(open(f'{CACHE}/manifest.json'))
master_items = json.load(open('/tmp/soo_items.json'))  # (no, href, name)
name_by_url_tail = {href: name for _, href, name in master_items}
no_by_url_tail = {href: no for no, href, _ in master_items}

SUB_MAP = {
    '史跡': ('記念物', '史跡'), '名勝': ('記念物', '名勝'), '天然記念物': ('記念物', '天然記念物'),
    '有(建)': ('有形文化財', '建造物'), '有(彫)': ('有形文化財', '彫刻'), '有(絵)': ('有形文化財', '絵画'),
    '有(工)': ('有形文化財', '工芸品'), '有(書)': ('有形文化財', '書跡'), '有(古文書)': ('有形文化財', '古文書'),
    '有(考)': ('有形文化財', '考古資料'), '有(歴史資料)': ('有形文化財', '歴史資料'),
    '有形民俗': ('民俗文化財', '有形民俗文化財'), '無形民俗': ('民俗文化財', '無形民俗文化財'),
}

def classify(s):
    s = s.strip()
    if s in SUB_MAP:
        return SUB_MAP[s]
    return None, s or None

records = []
for h, entry in manifest.items():
    if entry.get('http_status') != 200 or entry.get('format') != 'html':
        continue
    if 'siseki/index.html' in entry['url']:
        continue
    path = f"{CACHE}/{entry['filename']}"
    if not os.path.exists(path):
        continue
    url_tail = entry['url'].rsplit('/', 1)[-1]
    known_name = name_by_url_tail.get(url_tail)
    known_no = no_by_url_tail.get(url_tail)
    soup = BeautifulSoup(open(path, errors='ignore').read(), 'html.parser')
    txt = soup.get_text('\n', strip=True)
    m = re.search(r'>\s*(\S+)\n(?:ツイート\n)?指定区分：(.+?)\n種別：(.+?)\n指定日：(.+?)\n所在地：(.+?)\n(.+?)\n(?:Map|お問い合わせ)', txt, re.S)
    if not m:
        # try without trailing 'ツイート' assumption, more lenient
        m = re.search(r'指定区分：(.+?)\n種別：(.+?)\n指定日：(.+?)\n所在地：(.+?)\n(.+)', txt, re.S)
        if not m:
            print('NO MATCH', entry['url'])
            continue
        kubun, kind, date_s, loc, rest = m.groups()
        title_m = re.search(r'>\s*([^\n>]+)\nツイート', txt)
        name = title_m.group(1) if title_m else None
    else:
        name, kubun, kind, date_s, loc, rest = m.groups()
    if '市指定' not in kubun:
        continue
    cat, sub = classify(kind)
    desc = rest.split('\n')[0].strip() if 'rest' in dir() else None
    final_name = known_name or (name.strip() if name else None)
    desc_parts = []
    if known_no:
        desc_parts.append(f'指定番号{known_no}号')
    desc_parts.append(f'指定日(原表記): {date_s.strip()}')
    if desc:
        desc_parts.append(desc)
    records.append({
        'pref': '鹿児島県', 'municipality': '曽於市', 'name': final_name,
        'category': cat, 'subcategory': sub, 'designation': '市指定',
        'designated_date': None, 'location': loc.strip(),
        'description': '；'.join(desc_parts),
        'source_url': entry['url'], 'source_format': 'html',
        'fetched_at': entry.get('fetched_at'),
    })

with open('out/鹿児島県/soo.jsonl', 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(records))
for r in records[:10]:
    print(r['name'], r['category'], r['subcategory'], r['description'][:40])
