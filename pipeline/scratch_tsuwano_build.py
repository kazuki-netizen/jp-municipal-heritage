import json, re, sys
sys.path.insert(0, '/Users/miyazakihitohata/bunkazai/pipeline')
from scratch_shimane_wareki import ERA_START

def wareki_hm(s):
    s = s.strip()
    m = re.match(r'(M|T|S|H|R)(\d+)\.(\d+)\.(\d+)', s)
    if not m:
        return None
    era_c, y, mo, d = m.groups()
    era_map = {'M':'明治','T':'大正','S':'昭和','H':'平成','R':'令和'}
    era = era_map[era_c]
    y = int(y); mo = int(mo); d = int(d)
    year = ERA_START[era] + y - 1
    return f'{year:04d}-{mo:02d}-{d:02d}'

CAT_MAP = {
 '建造物': ('有形文化財','建造物'),
 '歴史資料': ('有形文化財','歴史資料'),
 '無形民俗文化財': ('民俗文化財','無形民俗文化財'),
 '史跡': ('記念物(史跡・名勝・天然記念物)','史跡'),
 '天然記念物': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

SRC = 'https://www.town.tsuwano.lg.jp/www/contents/1682570698880/simple/dai1syou.pdf'
FETCHED = '2026-07-12T06:55:50Z'

# (subcat, name, date)
rows = [
('建造物','竹原家住宅','H18.5.1'),
('歴史資料','鷲原八幡宮社殿奉納掲額','S52.12.17'),
('無形民俗文化財','鷲原八幡宮の流鏑馬神事','H8.4.1'),
('無形民俗文化財','日原奴道中','H30.2.22'),
('無形民俗文化財','青原奴道中','H30.2.22'),
('無形民俗文化財','子鷺踊り','R2.11.30'),
('史跡','木薗遺跡','S54.9.15'),
('史跡','岡熊臣旧宅','H8.12.10'),
('史跡','下瀬山城跡','S41.8.1'),
('史跡','宗梧監守禅師の墓','S41.8.1'),
('史跡','（伝）下瀬加賀守の墓','S41.8.1'),
('史跡','社地脇古墳','S50.9.5'),
('史跡','天正十三年在銘宝篋印塔','S50.9.5'),
('史跡','龍谷たたら跡','S50.9.5'),
('史跡','枕瀬代官所跡','S50.9.5'),
('史跡','青原代官所跡','S50.9.5'),
('史跡','弥栄神社','R2.11.30'),
('天然記念物','愛宕神社の大銀杏','S48.10.23'),
('天然記念物','愛宕神社の無患子','S48.10.23'),
('天然記念物','弥栄神社の大欅','S48.10.23'),
('天然記念物','鷲原八幡宮の大杉','S48.10.23'),
('天然記念物','若宮神社跡たぶの木','S56.4.28'),
('天然記念物','三渡八幡宮社叢','S50.9.5'),
('天然記念物','青原八幡宮社叢','S50.9.5'),
('天然記念物','左鐙八幡宮社叢','S50.9.5'),
('天然記念物','徳次のフクジュソウ群生地','R4.2.4'),
('天然記念物','徳次のカキノキ','R4.2.4'),
]

results = []
for subcat, name, date in rows:
    cat, _ = CAT_MAP[subcat]
    iso = wareki_hm(date)
    results.append({
        "pref": "島根県", "municipality": "津和野町", "name": name,
        "category": cat, "subcategory": subcat, "designation": "町指定",
        "designated_date": iso, "location": None, "description": None,
        "source_url": SRC, "source_format": "pdf", "fetched_at": FETCHED,
    })

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/島根県/tsuwano.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
