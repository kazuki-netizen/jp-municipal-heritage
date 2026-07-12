#!/usr/bin/env python3
import json, os, re
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "kikuchi.jsonl")
SRC_URL = "https://www.city.kikuchi.lg.jp/article/view/1244/466.html"

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
    if sub == "無形民俗":
        return "民俗文化財", "無形民俗文化財"
    if sub in ("史跡", "名勝", "天然記念物"):
        return "記念物(史跡・名勝・天然記念物)", sub
    return "有形文化財", sub


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "kikuchi", "manifest.json"), encoding="utf-8"))
    entry = [v for v in m.values() if v["url"] == SRC_URL][0]
    fetched_at = entry["fetched_at"]
    html = open(os.path.join(HERE, "cache", "熊本県", "kikuchi", entry["filename"]), encoding="utf-8").read()
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    table = tables[3]
    rows = table.find_all("tr")[1:]
    out_rows = []
    for r in rows:
        cells = [c.get_text(strip=True) for c in r.find_all(["th", "td"])]
        if len(cells) != 6:
            continue
        num, sub, name, loc, date, note = cells
        name = re.sub(r"\(PDF[^)]*\)", "", name).strip()
        if not name:
            continue
        category, subcat = cat_for(sub)
        desc_parts = [f"番号{num}"]
        if note and note != "-":
            desc_parts.append(note)
        row = {
            "pref": "熊本県",
            "municipality": "菊池市",
            "name": name,
            "category": category,
            "subcategory": subcat,
            "designation": "市指定",
            "designated_date": wareki_to_iso(date),
            "location": loc or None,
            "description": "、".join(desc_parts),
            "source_url": SRC_URL,
            "source_format": "html",
            "fetched_at": fetched_at,
        }
        out_rows.append(row)
    assert len(out_rows) == 119, len(out_rows)
    with open(OUT, "w", encoding="utf-8") as f:
        for row in out_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
