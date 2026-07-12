import json, xlrd, datetime

CAT_MAP = {
    '有形文化財': '有形文化財', '無形文化財': '無形文化財',
    '民俗文化財': '民俗文化財', '記念物': '記念物',
    '伝統的建造物群': '伝統的建造物群', '文化的景観': '文化的景観',
}

book = xlrd.open_workbook('cache/鹿児島県/satsumasendai/7673189367f2f017.xls')
sh = book.sheet_by_index(0)

def excel_date(v):
    if not v or not isinstance(v, float):
        return None
    try:
        d = xlrd.xldate.xldate_as_datetime(v, book.datemode)
        return f'{d:%Y-%m-%d}'
    except Exception:
        return None

records = []
for r in range(3, sh.nrows):
    kubun = sh.cell_value(r, 3)  # col D: 国/県/市
    if kubun != '市':
        continue
    kind2 = sh.cell_value(r, 4)  # 行為: 指定 etc
    cat1 = sh.cell_value(r, 6)   # 種別１
    cat2 = sh.cell_value(r, 7)   # 種別２
    cat3 = sh.cell_value(r, 8)   # 種別３
    name = sh.cell_value(r, 9)
    if not name:
        continue
    region = sh.cell_value(r, 10)
    district = sh.cell_value(r, 11)
    loc = sh.cell_value(r, 12)
    owner = sh.cell_value(r, 13)
    date = excel_date(sh.cell_value(r, 16))
    no = sh.cell_value(r, 1)
    note = sh.cell_value(r, 23) if sh.ncols > 23 else ''
    cat = CAT_MAP.get(cat1, cat1 or None)
    sub = cat3 or cat2 or None
    loc_full = ' '.join(x for x in [region, district, str(loc).replace('\n', ' ')] if x) or None
    desc_parts = []
    if no:
        desc_parts.append(f'指定番号{int(no)}号' if isinstance(no, float) else f'指定番号{no}号')
    if owner:
        desc_parts.append(f'所有者又は管理者: {str(owner).replace(chr(10)," ")}')
    if note:
        desc_parts.append(str(note))
    records.append({
        'pref': '鹿児島県', 'municipality': '薩摩川内市', 'name': str(name).replace('　', ' ').strip(),
        'category': cat, 'subcategory': sub, 'designation': '市指定',
        'designated_date': date, 'location': loc_full,
        'description': '；'.join(desc_parts) or None,
        'source_url': 'https://www.city.satsumasendai.lg.jp/material/files/group/48/satsumasendai_bunkazai.xls',
        'source_format': 'xls', 'fetched_at': '2026-07-12T13:30:00Z',
    })

with open('out/鹿児島県/satsumasendai.jsonl', 'w', encoding='utf-8') as f:
    for rec in records:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')
print(len(records))
