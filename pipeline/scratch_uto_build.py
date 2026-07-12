#!/usr/bin/env python3
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "uto.jsonl")
SRC_URL = "https://www.city.uto.lg.jp/d?q=68bb5d3bd168605dcbfc1513b72e5d87.csv"

CAT_MAP = {
    "宇土市指定記念物": ("記念物(史跡・名勝・天然記念物)", "記念物"),
    "宇土市指定史跡": ("記念物(史跡・名勝・天然記念物)", "史跡"),
    "宇土市指定天然記念物": ("記念物(史跡・名勝・天然記念物)", "天然記念物"),
    "宇土市指定文化財": ("記念物(史跡・名勝・天然記念物)", None),
    "宇土市指定無形文化財": ("無形文化財", "無形文化財"),
    "宇土市指定無形民俗文化剤": ("民俗文化財", "無形民俗文化財"),
    "宇土市指定無形民俗文化財": ("民俗文化財", "無形民俗文化財"),
    "宇土市指定名勝": ("記念物(史跡・名勝・天然記念物)", "名勝"),
    "宇土市指定有形文化財": ("有形文化財", "有形文化財"),
}


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "uto", "manifest.json"), encoding="utf-8"))
    entry = [v for v in m.values() if v["url"] == SRC_URL][0]
    fetched_at = entry["fetched_at"]
    path = os.path.join(HERE, "cache", "熊本県", "uto", entry["filename"])
    with open(path, encoding="cp932") as f:
        rows = list(csv.reader(f))[1:]

    out_rows = []
    for r in rows:
        if len(r) < 12:
            continue
        kubun, no, pref_name, muni, name, kana, loc, lat, lon, tel, url, note = r[1:13]
        if kubun not in CAT_MAP:
            continue  # skip non-city designations (国/県)
        category, subcat = CAT_MAP[kubun]
        row = {
            "pref": "熊本県",
            "municipality": "宇土市",
            "name": name,
            "category": category,
            "subcategory": subcat,
            "designation": "市指定",
            "designated_date": None,
            "location": loc or None,
            "description": f"開放データNo.{no}" + (f"、{note}" if note else ""),
            "source_url": SRC_URL,
            "source_format": "csv",
            "fetched_at": fetched_at,
        }
        out_rows.append(row)

    assert len(out_rows) == 85, len(out_rows)
    with open(OUT, "w", encoding="utf-8") as f:
        for row in out_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
