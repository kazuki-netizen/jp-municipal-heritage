#!/usr/bin/env python3
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "gyokuto.jsonl")
SRC_URL = "https://www.town.gyokuto.kumamoto.jp/kiji00388/3_88_shinsei1_7g032l7m.pdf"

ERA = {"明治": 1867, "大正": 1911, "昭和": 1925, "平成": 1988, "令和": 2018}


def wareki_to_iso(s):
    if not s or s == "―":
        return None
    s = s.replace("年年", "年")
    m = re.match(r"^(明治|大正|昭和|平成|令和)(\d+)年(\d+)月(\d+)日$", s)
    if not m:
        return None
    era, y, mo, d = m.groups()
    year = ERA[era] + int(y)
    date = f"{year:04d}-{int(mo):02d}-{int(d):02d}"
    if date > "2026-07-10":
        return None
    return date


# (num, name, category, subcat, date, location, area, owner, note)
ROWS = [
    (12, "山北八幡宮仁王像", "有形文化財", "建造物", "昭和49年10月24日", "白木1828", "19㎡", "山北八幡宮", "寛政4(1792)年に寄進された仁王像"),
    (13, "原倉清田氏五輪塔附板碑群", "有形文化財", "建造物", "昭和60年10月1日", "原倉1271", "927㎡", "本村下組共有地", "豊後国代官・清田宗甫の供養塔"),
    (14, "西安寺瓦", "有形文化財", "工芸品", None, None, None, None, "西安寺跡に使われていた瓦"),
    (15, "稲佐廃寺瓦", "有形文化財", "工芸品", "昭和51年8月21日", "稲佐608-6", None, None, "稲佐廃寺跡に使われていた瓦"),
    (16, "窪田家古文書", "有形文化財", "書跡", "昭和51年8月21日", "木葉字横町", None, "個人", "2通"),
    (17, "伊形霊雨の墓", "記念物(史跡・名勝・天然記念物)", "史跡", "昭和45年6月1日", "木葉字段1283", "509㎡", "個人", "江戸時代中期の詩人、伊形霊雨一族の墓"),
    (18, "大谷石器製造所跡", "記念物(史跡・名勝・天然記念物)", "史跡", "昭和45年6月1日", "原倉字大谷2455、2456", "190,660㎡", "個人", "縄文時代の石器製作所"),
    (19, "むくろじ製鉄所跡", "記念物(史跡・名勝・天然記念物)", "史跡", "昭和45年6月1日", "原倉字荒強当2403", "6,312㎡", "個人", "平安時代末の製鉄遺跡"),
    (20, "有栖川の宮御督戦の地", "記念物(史跡・名勝・天然記念物)", "史跡", "昭和47年4月1日", "木葉826", "1,173㎡", "町", "明治10年西南戦争で政府軍征討総督有栖川宮が督戦された地"),
    (21, "梛群", "記念物(史跡・名勝・天然記念物)", "天然記念物", "平成9年12月1日", "稲佐399（熊野座神社内）", None, "稲佐熊野座神社", "まき科常緑高木"),
    (22, "楠", "記念物(史跡・名勝・天然記念物)", "天然記念物", "平成9年12月1日", "木葉1164（木葉宇都宮神社内）", None, "木葉宇都宮神社", "くすのき科常緑高木"),
    (23, "一位樫", "記念物(史跡・名勝・天然記念物)", "天然記念物", "平成9年12月1日", "原倉", None, "個人", "穀斗カシ属の常緑高木"),
    (24, "西安寺神楽保存会", "民俗文化財", "無形民俗文化財", "平成30年4月10日", "西安寺", None, None, "白山宮に奉納される神楽"),
]


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "gyokuto", "manifest.json"), encoding="utf-8"))
    entry = [v for v in m.values() if v["url"] == SRC_URL][0]
    fetched_at = entry["fetched_at"]

    out_rows = []
    for num, name, category, subcat, date, loc, area, owner, note in ROWS:
        desc_parts = [f"整理番号{num}"]
        if area:
            desc_parts.append(f"面積{area}")
        if owner:
            desc_parts.append(f"所有者:{owner}")
        if note:
            desc_parts.append(note)
        out_rows.append({
            "pref": "熊本県", "municipality": "玉東町", "name": name,
            "category": category, "subcategory": subcat, "designation": "町指定",
            "designated_date": wareki_to_iso(date), "location": loc,
            "description": "、".join(desc_parts),
            "source_url": SRC_URL, "source_format": "pdf", "fetched_at": fetched_at,
        })

    assert len(out_rows) == 13, len(out_rows)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
