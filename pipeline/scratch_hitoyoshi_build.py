#!/usr/bin/env python3
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "hitoyoshi.jsonl")
SRC_URL = "https://www.city.hitoyoshi.lg.jp/resource.php?e=c611ca775a995dcf93e2a949d9aa1a2e51dac0db45e34b54c98c7f8f857ba0c2415fc80b48bf19084dcf8ec3c216aca9"
FETCHED_AT = "2026-07-12T00:00:00Z"

SUBCAT = {"建": "建造物", "絵": "絵画", "彫": "彫刻", "工": "工芸品",
          "書": "書跡", "古": "古文書", "歴": "歴史資料"}

def wareki_to_iso(s):
    if not s:
        return None
    m = re.match(r"^([MTSHR])(\d+)\.(\d+)\.(\d+)$", s)
    if not m:
        return None
    era, y, mo, d = m.groups()
    base = {"M": 1867, "T": 1911, "S": 1925, "H": 1988, "R": 2018}[era]
    year = base + int(y)
    date = f"{year:04d}-{int(mo):02d}-{int(d):02d}"
    if date > "2026-07-10":
        return None
    return date

# (number, subcat_letter or None, name, date, location)
YUKEI = [
    (1, "建", "石造三重塔", "S35.9.27", "願成寺町"),
    (2, "建", "石造五重塔", "S50.9.15", "土手町"),
    (3, "建", "阿弥陀三尊石塔婆", "S50.9.15", "七地町"),
    (4, "建", "眼鏡橋", "S50.9.15", "下原田町"),
    (5, "建", "堀合門", "S54.5.29", "土手町"),
    (6, "建", "方（角）柱塔婆", "S62.3.31", "七地町"),
    (7, "建", "キリシタン灯籠", "S62.3.31", None),
    (8, "建", "長福寺阿弥陀堂", "H6.4.28", "下原田町"),
    (9, "建", "城本の笠塔婆", "H19.3.12", "城本町"),
    (10, "建", "青井大神宮 内宮・外宮", "H25.5.28", "上青井町"),
    (11, "建", "矢黒神社本殿、覆屋及び拝殿・神供所", "H25.5.28", "矢黒町"),
    (12, "建", "遥拝阿蘇神社本殿、覆屋及び拝殿・神供所", "H25.5.28", "上林町"),
    (13, "建", "村山観音堂", "H25.5.28", "城本町"),
    (14, "絵", "紙本雪中山水の図 細井平洲作", "S35.10.13", None),
    (15, "絵", "絹本山水の図 細井平洲作", "S35.10.13", None),
    (16, "絵", "絹本青緑山水の図 細井平洲作", "S35.10.13", None),
    (17, "絵", "板絵御正体", "S62.3.31", "上青井町"),
    (18, "絵", "相良家歴代当主肖像画", "H3.12.26", None),
    (19, "絵", "人吉城油絵", "H3.12.26", None),
    (20, "彫", "銅造千手観音立像", "S62.3.31", "城本町"),
    (21, "彫", "木造千手観音立像", "S62.3.31", "城本町"),
    (22, "彫", "木造阿弥陀如来立像", "S62.3.31", "鬼木町"),
    (23, "彫", "木造阿弥陀如来立像", "S62.3.31", "鶴田町"),
    (24, "彫", "木造聖観音坐像", "S62.3.31", "赤池水無町"),
    (25, "彫", "木造神像二体", "S62.3.31", "中神町"),
    (26, "彫", "木造伝観音菩薩坐像", "H3.12.26", "古仏頂町"),
    (27, "彫", "木造神像四体", "H3.12.26", "下原田町"),
    (28, "彫", "木造随身倚像一対", "H3.12.26", "下原田町"),
    (29, "彫", "木造伝四天王像", "H25.5.28", "城本町"),
    (30, "工", "扁額", "S33.3.10", "北泉田町"),
    (31, "工", "槍", "S35.10.13", None),
    (32, "工", "槍", "S35.10.13", None),
    (33, "工", "槍", "S35.10.13", None),
    (34, "工", "刀", "S35.10.13", None),
    (35, "工", "刀", "S35.10.13", None),
    (36, "工", "兜", "S35.10.13", None),
    (37, "工", "兜", "S35.10.13", None),
    (38, "工", "太刀拵", "S35.10.13", None),
    (39, "工", "脇差拵", "S35.10.13", None),
    (40, "工", "鐔", "S35.10.13", None),
    (41, "工", "鐔", "S35.10.13", None),
    (42, "工", "鐔", "S35.10.13", None),
    (43, "工", "短刀", "S62.3.31", None),
    (44, "工", "懸仏", "S62.3.31", "上青井町"),
    (45, "工", "相良家甲冑（櫃共）", "H3.12.26", None),
    (46, "工", "銅製懸仏（五面）", "H3.12.26", "下原田町"),
    (47, "工", "牛塚毘沙門堂鰐口", "H17.3.31", None),
    (48, "工", "西門釈迦堂鰐口", "H17.3.31", None),
    (49, "工", "観音寺観音堂鰐口", "H17.3.31", "願成寺町"),
    (50, "書", "書跡（佐藤一斎作）", "S35.10.13", None),
    (51, "書", "書跡（佐藤一斎作）", "S35.10.13", None),
    (52, "書", "書跡（佐藤一斎作）", "S35.10.13", None),
    (53, "書", "書跡（細井平洲作）", "S35.10.13", None),
    (54, "古", "相良家文書（写）", "S62.3.31", None),
    (55, "古", "探源記", "S62.3.31", None),
    (56, "古", "歴代私鑑", "S62.3.31", None),
    (57, "古", "南藤蔓綿録", "S62.3.31", None),
    (58, "古", "歴代嗣誠独集覧", "S62.3.31", None),
    (59, "古", "歴代参考下書", "S62.3.31", None),
    (60, "古", "佐無田家文書", "H6.4.28", "七日町"),
    (61, "古", "相良三十三観音御詠歌", "H19.3.12", "浪床町"),
    (62, "歴", "繊月石", "H3.12.26", None),
    (63, "歴", "乗物（担棒共）", "H3.12.26", None),
    (64, "歴", "時の太鼓（桴共）", "H3.12.26", None),
]

MINZOKU = [
    (65, "三十三観音巡り", "H11.4.27", "市内12ケ所"),
    (66, "井ノ口の虎踊り", "S62.3.31", "井ノ口町"),
]

SHISEKI = [
    (67, "東林寺岩壁画", "S33.3.10", "浪床町"),
    (68, "御薬園及び下屋敷", "S33.3.10", "七地町"),
    (69, "矢瀬ヶ津留", "S33.3.10", "東間上町"),
    (70, "赤池城跡", "S33.3.10", "赤池原町"),
    (71, "相良家下屋敷", "S33.3.10", "相良町"),
    (72, "荒毛遺跡", "H6.4.28", "下原田町"),
    (73, "古仏頂観音堂境内地", "H11.4.27", "古仏頂町"),
    (74, "笹原番所跡", "H16.11.15", "大畑麓町"),
    (75, "了清院跡及び了清院墓地", "H21.3.2", "富ヶ尾町"),
]

MEISHO = [
    (76, "稲荷山", "S33.3.10", "西間下町"),
]

TENNEN = [
    (77, "青井神社の楠", "S33.3.10", "上青井町"),
    (78, "人吉城跡のイチイガシ", "S33.3.10", "麓町"),
    (79, "石水寺の海棠", "S50.9.15", "下原田町"),
    (80, "人吉東小学校の大クス", "H21.3.2", "七日町"),
]


def row(name, category, subcategory, date, loc, num):
    return {
        "pref": "熊本県",
        "municipality": "人吉市",
        "name": name,
        "category": category,
        "subcategory": subcategory,
        "designation": "市指定",
        "designated_date": wareki_to_iso(date),
        "location": loc,
        "description": f"指定番号{num}号",
        "source_url": SRC_URL,
        "source_format": "pdf",
        "fetched_at": FETCHED_AT,
    }


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "hitoyoshi", "manifest.json"), encoding="utf-8"))
    entry = [v for v in m.values() if v["url"] == SRC_URL][0]
    fetched_at = entry["fetched_at"]
    global FETCHED_AT
    FETCHED_AT = fetched_at

    out_rows = []
    for num, letter, name, date, loc in YUKEI:
        out_rows.append(row(name, "有形文化財", SUBCAT[letter], date, loc, num))
    for num, name, date, loc in MINZOKU:
        out_rows.append(row(name, "民俗文化財", "無形民俗文化財", date, loc, num))
    for num, name, date, loc in SHISEKI:
        out_rows.append(row(name, "記念物(史跡・名勝・天然記念物)", "史跡", date, loc, num))
    for num, name, date, loc in MEISHO:
        out_rows.append(row(name, "記念物(史跡・名勝・天然記念物)", "名勝", date, loc, num))
    for num, name, date, loc in TENNEN:
        out_rows.append(row(name, "記念物(史跡・名勝・天然記念物)", "天然記念物", date, loc, num))

    with open(OUT, "w", encoding="utf-8") as f:
        for r in out_rows:
            r["fetched_at"] = fetched_at
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
