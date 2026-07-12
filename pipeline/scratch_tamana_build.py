#!/usr/bin/env python3
import json, os, re
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "tamana.jsonl")
SRC_URL = "https://www.city.tamana.lg.jp/q/aview/564/22145.html"


def cat_for(sub):
    if sub.startswith("重要有形文化財"):
        inner = re.sub(r"^重要有形文化財\(?(.*)\)?$", r"\1", sub).strip("()")
        return "有形文化財", inner or None
    if sub == "重要有形民俗文化財":
        return "民俗文化財", "有形民俗文化財"
    if sub == "重要無形民俗文化財":
        return "民俗文化財", "無形民俗文化財"
    if sub in ("史跡", "名勝", "天然記念物"):
        return "記念物(史跡・名勝・天然記念物)", sub
    return None, sub


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "tamana", "manifest.json"), encoding="utf-8"))
    entry = [v for v in m.values() if v["url"] == SRC_URL][0]
    fetched_at = entry["fetched_at"]
    html = open(os.path.join(HERE, "cache", "熊本県", "tamana", entry["filename"]), encoding="euc-jp").read()
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    table = tables[4]
    rows = table.find_all("tr")[1:]
    out_rows = []
    for r in rows:
        cells = [c.get_text(strip=True) for c in r.find_all(["th", "td"])]
        if len(cells) != 6:
            continue
        num, sub, name, count, loc, owner = cells
        if num.startswith("(") or not name:
            continue
        category, subcat = cat_for(sub)
        if category is None:
            continue
        desc_parts = [f"指定番号{num}号"]
        if count:
            desc_parts.append(f"員数{count}")
        if owner:
            desc_parts.append(f"所有者:{owner}")
        row = {
            "pref": "熊本県",
            "municipality": "玉名市",
            "name": name,
            "category": category,
            "subcategory": subcat,
            "designation": "市指定",
            "designated_date": None,
            "location": loc or None,
            "description": "、".join(desc_parts),
            "source_url": SRC_URL,
            "source_format": "html",
            "fetched_at": fetched_at,
        }
        out_rows.append(row)
    with open(OUT, "w", encoding="utf-8") as f:
        for row in out_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
