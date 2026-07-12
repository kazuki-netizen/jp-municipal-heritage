import json, re

def wareki_to_iso(s):
    s = s.strip()
    m = re.match(r'^([SHR])(\d+)\.(\d+)\.(\d+)$', s)
    if not m:
        return None
    era, y, mo, d = m.groups()
    y=int(y); mo=int(mo); d=int(d)
    base = {"S":1925, "H":1988, "R":2018}[era]
    return f"{base+y:04d}-{mo:02d}-{d:02d}"

SRC = "https://www.town.yoshida.shizuoka.jp/secure/11098/4_dai4jikokudoriyoukeikakusankousiryou_an.pdf"
FETCHED = "2026-07-12T03:51:48Z"
PREF = "静岡県"
MUNI = "吉田町"

# (category, subcategory, name, date)
rows = [
("記念物","史跡","家康御陣場跡","S39.4.1"),
("記念物","史跡","大熊備前守屋敷跡","S39.4.1"),
("有形文化財","工芸品","萬年の茶がま","S39.4.1"),
("記念物","史跡","小山城跡","S39.4.1"),
("記念物","史跡","能満寺原古墳","S39.4.1"),
("有形文化財","工芸品","和泉太夫使用の人形（その墓と関係文書）","S39.4.1"),
("記念物","史跡","条里制遺跡","S39.4.1"),
("記念物","天然記念物","萬年のサツキ","S39.4.1"),
("記念物","史跡","鈴木養邦師の石橋","S39.4.1"),
("記念物","史跡","長源寺の経塚","S48.4.1"),
("民俗文化財","無形民俗文化財","地蔵院の百万遍","S53.2.9"),
("有形文化財","古文書","野中家所蔵の古文書","S56.2.10"),
("有形文化財","工芸品","三番神社所蔵の人形の首","S56.2.10"),
("有形文化財","古文書","武田氏の朱印状","S56.2.10"),
("有形文化財","古文書","能満寺の古文書","S57.5.3"),
("有形文化財","彫刻","本寿寺の木彫り龍","S63.6.1"),
("民俗文化財","無形民俗文化財","寺島川除地蔵の灯篭あげ","H3.12.1"),
("有形文化財","書跡","能満寺の山号額・寺号額","H5.8.1"),
("有形文化財","絵画","川本月下「梅花の図」","H8.5.31"),
("有形文化財","工芸品","林泉寺の十王像","H14.12.2"),
("有形文化財","建造物","川尻の道標","H19.5.29"),
("民俗文化財","有形民俗文化財","片岡神社（通称住吉神社）船絵馬群","R2.3.25"),
]

out_path = "/Users/user/bunkazai/pipeline/out/静岡県/yoshida.jsonl"
with open(out_path, "w", encoding="utf-8") as f:
    for cat, subcat, name, date in rows:
        iso = wareki_to_iso(date)
        rec = {
            "pref": PREF,
            "municipality": MUNI,
            "name": name,
            "category": cat,
            "subcategory": subcat,
            "designation": "町指定",
            "designated_date": iso,
            "location": None,
            "description": None,
            "source_url": SRC,
            "source_format": "pdf",
            "fetched_at": FETCHED,
        }
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"wrote {len(rows)} rows to {out_path}")
