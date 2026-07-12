#!/usr/bin/env python3
import json, os, re
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "aso.jsonl")
SRC_URL = "https://www.city.aso.kumamoto.jp/education/cultural-property/list_of_cultural_property/"

ERA = {"M": 1867, "T": 1911, "S": 1925, "H": 1988, "R": 2018}


def wareki_to_iso(s):
    s = s.replace("Ｓ", "S").replace("Ｈ", "H").replace("Ｒ", "R").replace("Ｔ", "T").replace("Ｍ", "M")
    m = re.match(r"^([MTSHR])(\d+)\.(\d+)\.(\d+)$", s)
    if not m:
        return None
    era, y, mo, d = m.groups()
    year = ERA[era] + int(y)
    date = f"{year:04d}-{int(mo):02d}-{int(d):02d}"
    if date > "2026-07-10":
        return None
    return date


def cat_for(sub):
    m = re.match(r"^(有形文化財|民俗文化財|記念物)（(.+)）$", sub)
    if not m:
        return None, sub
    top, inner = m.groups()
    if top == "有形文化財":
        return "有形文化財", inner
    if top == "民俗文化財":
        return "民俗文化財", ("有形民俗文化財" if inner == "有形" else "無形民俗文化財")
    if top == "記念物":
        return "記念物(史跡・名勝・天然記念物)", inner
    return None, sub


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "aso", "manifest.json"), encoding="utf-8"))
    entry = [v for v in m.values() if v["url"] == SRC_URL][0]
    fetched_at = entry["fetched_at"]
    html = open(os.path.join(HERE, "cache", "熊本県", "aso", entry["filename"]), encoding="utf-8").read()
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find_all("table")[12]
    rows = table.find_all("tr")[1:]
    out_rows = []
    for r in rows:
        cells = [c.get_text(strip=True) for c in r.find_all(["th", "td"])]
        if len(cells) == 7:
            num, sub, name, loc, date, count, note = cells
        elif len(cells) == 6:
            num, sub, name, loc, date, note = cells
            count = None
        else:
            continue
        if not name:
            continue
        category, subcat = cat_for(sub)
        if category is None:
            continue
        desc_parts = [f"番号{num}"]
        if count:
            desc_parts.append(f"員数{count}")
        if note:
            desc_parts.append(note)
        out_rows.append({
            "pref": "熊本県", "municipality": "阿蘇市", "name": name,
            "category": category, "subcategory": subcat, "designation": "市指定",
            "designated_date": wareki_to_iso(date), "location": loc or None,
            "description": "、".join(desc_parts),
            "source_url": SRC_URL, "source_format": "html", "fetched_at": fetched_at,
        })
    assert len(out_rows) == 97, len(out_rows)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
