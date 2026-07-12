import json

def wareki(s):
    era_map = {"昭和":1925,"平成":1988,"令和":2018}
    for era,base in era_map.items():
        if s.startswith(era):
            rest = s[len(era):]
            rest = rest.replace("年","-").replace("月","-").replace("日","")
            year_str, month, day = rest.split("-")
            year = 1 if year_str=="元" else int(year_str)
            return f"{base+year:04d}-{int(month):02d}-{int(day):02d}"
    return None

items = [
("歴史資料","青柳宿下ノ町茶屋の宿札","平成29年1月16日","古賀市青柳"),
("考古資料","花見遺跡古墳群出土品一括","平成29年1月16日","古賀市"),
("歴史資料","藤井甚太郎資料","平成26年4月23日","古賀市"),
("考古資料","色姫の墓","平成2年4月27日","古賀市青柳石瓦"),
("考古資料","十三仏板碑十三体","平成2年4月27日","古賀市小山田"),
("考古資料","大日如来座像","平成2年4月27日","古賀市青柳寺浦"),
("考古資料","天降神社神殿の彫刻","平成3年3月19日","古賀市"),
("考古資料","阿弥陀如来座像","平成10年2月3日","古賀市"),
("考古資料","青柳宿西構口跡","平成15年3月31日","古賀市青柳"),
("考古資料","鹿部山経塚出土品","平成14年12月10日","古賀市歴史資料館展示"),
("考古資料","鹿部山皇石神社境内出土銅戈","平成19年2月22日","古賀市立歴史資料館展示"),
("歴史資料","『筵内村「掟」』櫃蓋裏記載小箪笥","平成22年1月20日","古賀市立歴史資料館蔵"),
("考古資料","私年号「亀光元年」銘墓石","平成30年8月22日","古賀市"),
]

out = []
for subcat, name, date_raw, loc in items:
    out.append({
        "pref": "福岡県", "municipality": "古賀市", "name": name,
        "category": "有形文化財", "subcategory": subcat, "designation": "市指定",
        "designated_date": wareki(date_raw), "location": loc,
        "description": None,
        "source_url": "https://www.city.koga.fukuoka.jp/guide/culture/003.php",
        "source_format": "html", "fetched_at": "2026-07-12T16:54:00Z"
    })

out.append({
    "pref": "福岡県", "municipality": "古賀市", "name": "谷山の盆綱",
    "category": "民俗文化財", "subcategory": "無形民俗文化財", "designation": "市指定",
    "designated_date": wareki("平成31年3月25日"), "location": "古賀市谷山",
    "description": "保持団体：谷山区",
    "source_url": "https://www.city.koga.fukuoka.jp/guide/culture/003.php",
    "source_format": "html", "fetched_at": "2026-07-12T16:54:00Z"
})

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/福岡県/koga.jsonl', 'w', encoding='utf-8') as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(out))
