#!/usr/bin/env python3
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "nankan.jsonl")
SRC_URL = "https://www.town.nankan.lg.jp/files/3_1861_5053_up_RH6QX501.pdf"

ERA = {"明治": 1867, "大正": 1911, "昭和": 1925, "平成": 1988, "令和": 2018}


def wareki_to_iso(s):
    m = re.match(r"^(明治|大正|昭和|平成|令和)(\d+)年(\d+)月(\d+)日$", s)
    if not m:
        return None
    era, y, mo, d = m.groups()
    year = ERA[era] + int(y)
    date = f"{year:04d}-{int(mo):02d}-{int(d):02d}"
    if date > "2026-07-10":
        return None
    return date


def cat_for(sub):
    if sub == "建造物":
        return "有形文化財", "建造物"
    if sub.startswith("美術工芸品"):
        inner = re.sub(r"^美術工芸品（(.+)）$", r"\1", sub)
        return "有形文化財", f"美術工芸品（{inner}）"
    if sub == "天然記念物":
        return "記念物(史跡・名勝・天然記念物)", "天然記念物"
    if sub == "史跡":
        return "記念物(史跡・名勝・天然記念物)", "史跡"
    if sub == "無形民俗文化財":
        return "民俗文化財", "無形民俗文化財"
    return None, sub


# (num, 種別, 名称, 所在地, 指定年月日)
ROWS = [
    (1, "天然記念物", "東坂上神社の樟", "豊永", "平成5年11月22日"),
    (2, "美術工芸品（彫刻）", "木造菩薩形立像", "関東", "平成5年11月22日"),
    (3, "美術工芸品（工芸品）", "佛照寺の梵鐘", "肥猪", "平成5年11月22日"),
    (4, "建造物", "麻扱場橋", "関町", "平成11年3月5日"),
    (5, "美術工芸品（彫刻）", "笛鹿観音堂の木造十一面観音坐像", "関東", "平成11年3月5日"),
    (6, "建造物", "大迫六地藏", "豊永", "平成11年3月5日"),
    (7, "建造物", "坂下阿蘇神社三重塔（助継塔）", "下坂下", "平成11年3月5日"),
    (8, "美術工芸品（彫刻）", "坂下阿蘇神社石造狛犬", "下坂下", "平成11年3月5日"),
    (9, "美術工芸品（彫刻）", "水かけ毘沙門堂の毘沙門天立像", "下坂下", "平成11年3月5日"),
    (10, "美術工芸品（彫刻）", "瀬上家の金銅菩薩形立像", "宮尾", "平成11年3月5日"),
    (11, "天然記念物", "宮尾のケヤキ", "宮尾", "平成12年3月15日"),
    (12, "天然記念物", "小原宮のイチイガシ", "小原", "平成12年3月15日"),
    (13, "天然記念物", "石井家のヒガンザクラ", "関外目", "平成12年3月15日"),
    (14, "天然記念物", "南関第三小学校のハゼ", "相谷", "平成12年3月15日"),
    (15, "天然記念物", "乙丸馬頭観音のクロガネモチ", "細永", "平成12年3月15日"),
    (16, "天然記念物", "肥猪のシダレザクラ", "肥猪", "平成12年3月15日"),
    (17, "史跡", "小代焼野田窯跡", "関町", "平成14年8月23日"),
    (18, "美術工芸品（工芸品）", "顕如書状", "長山", "平成14年8月23日"),
    (19, "美術工芸品（彫刻）", "竹林寺跡の木造天部形立像", "下坂下", "平成15年10月21日"),
    (20, "美術工芸品（書跡）", "北原白秋直筆「南関尋常高等小学校々歌歌詞」", "関町", "平成18年8月28日"),
    (21, "美術工芸品（書跡）", "山田耕筰直筆「南関尋常高等小学校々歌楽譜」", "関町", "平成18年8月28日"),
    (22, "建造物", "安原六地藏", "豊永", "平成20年7月10日"),
    (23, "美術工芸品（彫刻）", "今村神宮石造狛犬", "今", "平成21年6月10日"),
    (24, "建造物", "追分の道しるべ", "細永", "平成22年7月12日"),
    (25, "史跡", "山添磨崖仏岩薬師 附 板碑八基", "細永", "平成23年6月10日"),
    (26, "建造物", "久野次郎左衛門の墓", "関町", "平成24年7月11日"),
    (27, "無形民俗文化財", "古代楽", "小原", "平成25年9月9日"),
    (28, "建造物", "徳太六地蔵", "長山", "平成26年7月8日"),
    (29, "建造物", "大場六地蔵", "下坂下", "平成28年4月18日"),
]


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "nankan", "manifest.json"), encoding="utf-8"))
    entry = [v for v in m.values() if v["url"] == SRC_URL][0]
    fetched_at = entry["fetched_at"]

    out_rows = []
    for num, sub, name, loc, date in ROWS:
        category, subcat = cat_for(sub)
        out_rows.append({
            "pref": "熊本県", "municipality": "南関町", "name": name,
            "category": category, "subcategory": subcat, "designation": "町指定",
            "designated_date": wareki_to_iso(date), "location": loc,
            "description": f"件数{num}",
            "source_url": SRC_URL, "source_format": "pdf", "fetched_at": fetched_at,
        })

    assert len(out_rows) == 29, len(out_rows)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
