import json

SRC = 'https://www.town.yoshika.lg.jp/about/art/bunkazai.html'
FETCHED = '2026-07-12T06:55:51Z'

items = [
("石積古墳","記念物(史跡・名勝・天然記念物)","史跡",None,
 "大きなふた石や石室を構成していた石がたくさんあり、土器片などが出土している"),
("愛宕神社社叢","記念物(史跡・名勝・天然記念物)","天然記念物",None,
 "旧柿木村指定文化財（現吉賀町）。ケンポ梨・大トチ・大カツラなどの大樹が林立し、樹齢千年といわれる大杉がある"),
("亀田の水穴","記念物(史跡・名勝・天然記念物)","史跡",None,
 "水田に必要な水を引くためくり貫かれた灌漑用の用水トンネル。長さ約95メートル、高低差約10メートル。1645年貫通"),
("しだれ桜","記念物(史跡・名勝・天然記念物)","天然記念物",None,
 "みろく公園にある樹齢300年以上のしだれ桜"),
]

results = []
for name, cat, subcat, date, note in items:
    results.append({
        "pref": "島根県", "municipality": "吉賀町", "name": name,
        "category": cat, "subcategory": subcat, "designation": "町指定",
        "designated_date": date, "location": None, "description": note,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/島根県/yoshika.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
