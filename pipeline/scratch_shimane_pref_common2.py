import re, json, sys
from bs4 import BeautifulSoup
sys.path.insert(0, '/Users/user/bunkazai/pipeline')
from scratch_shimane_wareki import ERA_START

FULLWIDTH = str.maketrans('０１２３４５６７８９', '0123456789')

def wareki_code(s):
    s = s.strip().translate(FULLWIDTH)
    m = re.match(r'(H|S|R|M|T)0*(\d+)\.(\d+)\.(\d+)', s)
    if not m:
        return None
    era_c, y, mo, d = m.groups()
    era_map = {'M': '明治', 'T': '大正', 'S': '昭和', 'H': '平成', 'R': '令和'}
    era = era_map[era_c]
    y = int(y)
    mo = int(mo)
    d = int(d)
    year = ERA_START[era] + y - 1
    return f'{year:04d}-{mo:02d}-{d:02d}'

CAT_MAP = {
    '建': ('有形文化財', '建造物'), '絵': ('有形文化財', '絵画'), '彫': ('有形文化財', '彫刻'),
    '工': ('有形文化財', '工芸品'), '書': ('有形文化財', '書跡'), '典': ('有形文化財', '典籍'),
    '古': ('有形文化財', '古文書'), '考': ('有形文化財', '考古資料'), '歴': ('有形文化財', '歴史資料'),
    '工技': ('無形文化財', '工芸技術'), '芸': ('無形文化財', '芸能'),
    '有民': ('民俗文化財', '有形民俗文化財'), '無民': ('民俗文化財', '無形民俗文化財'),
    '史': ('記念物(史跡・名勝・天然記念物)', '史跡'), '名': ('記念物(史跡・名勝・天然記念物)', '名勝'),
    '天': ('記念物(史跡・名勝・天然記念物)', '天然記念物'),
}

HEADER_CELLS = ['番号', '種別', '指定年月日', '名称', '員数', '所在地', '所有者・保持者', '備考']


def extract(html_path, municipality, designation, src_url, fetched_at):
    with open(html_path, encoding='utf-8', errors='replace') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')
    for tag in soup(['script', 'style']):
        tag.decompose()
    results = []
    for table in soup.find_all('table'):
        rows = table.find_all('tr', recursive=False) or table.find_all('tr')
        for tr in rows:
            cells = [c.get_text(strip=True) for c in tr.find_all(['td', 'th'], recursive=False)]
            if not cells or len(cells) != 8:
                continue
            if cells[0] == '番号' or cells == HEADER_CELLS:
                continue
            num, code, date, name, count, loc, owner, note = cells
            if not re.match(r'^[0-9０-９]+$', num):
                continue
            cat, subcat = CAT_MAP.get(code, (None, code))
            iso = wareki_code(date)
            desc_parts = [f'指定番号{num.translate(FULLWIDTH)}号']
            if count:
                desc_parts.append(f'員数{count}')
            if owner:
                desc_parts.append(f'所有者・保持者{owner}')
            if note:
                desc_parts.append(note)
            desc = '、'.join(desc_parts)
            results.append({
                "pref": "島根県", "municipality": municipality, "name": name,
                "category": cat, "subcategory": subcat, "designation": designation,
                "designated_date": iso, "location": loc or None, "description": desc,
                "source_url": src_url, "source_format": "html", "fetched_at": fetched_at,
            })
    return results


def write_jsonl(results, out_path):
    with open(out_path, 'w') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    return len(results)
