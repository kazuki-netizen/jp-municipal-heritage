#!/usr/bin/env python3
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "arao.jsonl")
SRC_URL = "https://www.city.arao.lg.jp/fs/2/5/3/2/2/2/_/_________________8_3_6____.pdf"

ERA = {"明治": 1867, "大正": 1911, "昭和": 1925, "平成": 1988, "令和": 2018}


def wareki_to_iso(s):
    if not s:
        return None
    m = re.match(r"^(明治|大正|昭和|平成|令和)(\d+|元)年(\d+)月(\d+)日$", s)
    if not m:
        return None
    era, y, mo, d = m.groups()
    y = 1 if y == "元" else int(y)
    year = ERA[era] + y
    date = f"{year:04d}-{int(mo):02d}-{int(d):02d}"
    if date > "2026-07-10":
        return None
    return date


# (num, subcat, name, location, date, count, note)
ROWS = [
    (1, "建造物", "聖人塚板碑", "荒尾市上井手字上人原734", "昭和51年3月16日", "2基", None),
    (2, "建造物", "阿蘇惟富供養碑", "荒尾市平山字薬師上前282", "昭和51年3月16日", "1基", None),
    (3, "建造物", "御成門", "荒尾市府本字町369", "昭和53年6月1日", "1棟", None),
    (4, "建造物", "三ノ宮四方仏", "荒尾市下井手字持田丸107", "昭和53年6月1日", "1基", "下井手神社（三ノ宮）境内"),
    (5, "建造物", "住吉明神石厨子", "荒尾市宮内出目字住吉 住吉山頂", "昭和53年6月1日", "1基", None),
    (6, "建造物", "専行寺板碑", "荒尾市大島町3丁目8-22", "昭和53年6月1日", "1基", "平成29年6月26日名称変更（旧名・専行寺笠塔婆）"),
    (7, "建造物", "一部六地蔵石塔", "荒尾市一部字中磯153", "昭和57年10月5日", "1基", None),
    (8, "建造物", "阿弥陀ヶ池阿弥陀如来板碑", "荒尾市平山字野中2637", "昭和57年10月5日", "1基", None),
    (9, "建造物", "光徳寺板碑", "荒尾市平山字小路778", "昭和57年10月5日", "2基", "平成29年6月26日名称変更（旧名・藤原加賀守忠弘銘卒塔婆）"),
    (10, "建造物", "賀庭寺近世石造物群", "荒尾市樺字堂辺田565", "昭和53年6月1日", "11基", "賀庭寺境内"),
    (11, "建造物", "妙見の山ノ神", "荒尾市原万田字星ケ谷96-1", "令和元年12月25日", "1基", "万田公園内"),
    (12, "建造物", "宗善寺跡古塔群", "荒尾市府本字乱塔1024-2、1024-3", "令和元年12月25日", "11基", None),
    (13, "工芸資料", "大別当A窯出土の陶硯", "荒尾市緑ケ丘1丁目1-1", "昭和40年6月1日", "1面", "荒尾市立図書館に展示"),
    (14, "考古資料", "四山古墳出土品", "荒尾市大島字笹原818", "昭和57年10月5日", "83点", "四山神社"),
    (15, "考古資料", "立願寺出土の鬼瓦", "個人蔵", "昭和57年10月5日", "1個", None),
    (16, "民俗資料", "境崎貝塚の岩偶", "熊本市中央区古京町3-2", "昭和40年6月1日", "1点", "熊本市立熊本博物館"),
    (17, "書跡", "氷室家文書", "個人蔵", "昭和40年6月1日", "7通", None),
    (18, "彫刻", "大蔵廃寺毘沙門天立像", "荒尾市平山字旗ヶ坂1332", "昭和53年6月1日", "1体", None),
    (19, "彫刻", "賀庭寺薬師仏群", "荒尾市樺字堂辺田565", "昭和53年6月1日", "20体", "賀庭寺境内。1体は県立美術館に寄託。"),
]

MINZOKU = [
    (20, "野原八幡宮神事節頭行事", "荒尾市野原字山中1528", "昭和51年3月16日", None, "野原八幡宮"),
    (21, "上荒尾熊野座神社神楽", "荒尾市荒尾967", "平成14年5月2日", None, "上荒尾熊野座神社"),
]

SHISEKI = [
    (22, "四山古墳", "荒尾市大島字笹原山909", "昭和40年6月1日", "1基", "四山神社境内"),
    (23, "三ノ宮古墳", "荒尾市下井手字持田丸", "昭和40年6月1日", "1基", "下井手神社（三ノ宮）境内"),
    (24, "田次郎丸居館址及び古塔群", "荒尾市原万田原区字浦田785他", "昭和40年6月1日", "15基", "東光寺他"),
    (25, "野原古墳群", "荒尾市野原字山中1528", "昭和40年6月1日", "１基", "野原八幡宮境内"),
    (26, "月田蒙斎の墓", "荒尾市荒尾字合路1956", "昭和57年10月5日", "1基", None),
]


def build_desc(num, count, note):
    parts = [f"指定番号{num}号"]
    if count:
        parts.append(f"員数{count}")
    if note:
        parts.append(note)
    return "、".join(parts)


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "arao", "manifest.json"), encoding="utf-8"))
    entry = [v for v in m.values() if v["url"] == SRC_URL][0]
    fetched_at = entry["fetched_at"]

    out_rows = []
    for num, sub, name, loc, date, count, note in ROWS:
        out_rows.append({
            "pref": "熊本県", "municipality": "荒尾市", "name": name,
            "category": "有形文化財", "subcategory": sub, "designation": "市指定",
            "designated_date": wareki_to_iso(date), "location": loc,
            "description": build_desc(num, count, note),
            "source_url": SRC_URL, "source_format": "pdf", "fetched_at": fetched_at,
        })
    for num, name, loc, date, count, note in MINZOKU:
        out_rows.append({
            "pref": "熊本県", "municipality": "荒尾市", "name": name,
            "category": "民俗文化財", "subcategory": "無形民俗文化財", "designation": "市指定",
            "designated_date": wareki_to_iso(date), "location": loc,
            "description": build_desc(num, count, note),
            "source_url": SRC_URL, "source_format": "pdf", "fetched_at": fetched_at,
        })
    for num, name, loc, date, count, note in SHISEKI:
        out_rows.append({
            "pref": "熊本県", "municipality": "荒尾市", "name": name,
            "category": "記念物(史跡・名勝・天然記念物)", "subcategory": "史跡", "designation": "市指定",
            "designated_date": wareki_to_iso(date), "location": loc,
            "description": build_desc(num, count, note),
            "source_url": SRC_URL, "source_format": "pdf", "fetched_at": fetched_at,
        })

    with open(OUT, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
