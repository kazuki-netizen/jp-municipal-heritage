import openpyxl, json, re

SUBCAT_MAP = {
    '彫刻': ('有形文化財','彫刻'),
    '絵画': ('有形文化財','絵画'),
    '建造物': ('有形文化財','建造物'),
    '書跡等': ('有形文化財','書跡・典籍・古文書'),
    '史跡': ('記念物(史跡・名勝・天然記念物)','史跡'),
    '有民': ('民俗文化財','有形民俗文化財'),
    '工芸品': ('有形文化財','工芸品'),
    '考古資料': ('有形文化財','考古資料'),
    '歴史資料': ('有形文化財','歴史資料'),
    '無民': ('民俗文化財','無形民俗文化財'),
    '天然': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
    '名勝': ('記念物(史跡・名勝・天然記念物)','名勝'),
}

wb = openpyxl.load_workbook('/Users/user/bunkazai/pipeline/cache/滋賀県/otsu/data.xlsx', data_only=True)
ws = wb.active
url = "https://www.city.otsu.lg.jp/soshiki/010/2406/od/41153.html"
out = []
for row in ws.iter_rows(min_row=2, values_only=True):
    bunrui = row[8]
    if not bunrui or '市指定' not in bunrui:
        continue
    name = row[4]
    kind = row[9]
    fine = row[34] if len(row) > 34 else None
    cat, subcat = SUBCAT_MAP.get(fine, (None, fine or kind or bunrui.replace('市指定','')))
    addr = row[11]
    count_num = row[17]
    count_unit = row[18]
    owner = row[20]
    desig_date = row[21]
    date_iso = desig_date.strftime('%Y-%m-%d') if hasattr(desig_date, 'strftime') else None
    desc_parts = []
    if count_num:
        desc_parts.append(f"員数{count_num}{count_unit or ''}")
    if owner:
        desc_parts.append(f"所有者:{owner}")
    desc = "、".join(desc_parts) if desc_parts else None
    out.append({
        "pref": "滋賀県",
        "municipality": "大津市",
        "name": name,
        "category": cat,
        "subcategory": fine or kind,
        "designation": "市指定",
        "designated_date": date_iso,
        "location": addr,
        "description": desc,
        "source_url": "https://www.city.otsu.lg.jp/material/files/group/67/20250601_cultural_property.xlsx",
        "source_format": "opendata",
        "fetched_at": "2026-07-12T00:00:00Z"
    })

print(len(out))
with open('/Users/user/bunkazai/pipeline/out/滋賀県/otsu.jsonl', 'w', encoding='utf-8') as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
