#!/usr/bin/env python3
import json, os, re
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "misato.jsonl")
SRC_URL = "https://www.town.kumamoto-misato.lg.jp/soshiki/shakaikyoiku/1/9/1/bunkazai00/index.html"

ERA = {"明治": 1867, "大正": 1911, "昭和": 1925, "平成": 1988, "令和": 2018}


def wareki_to_iso(s):
    if not s:
        return None
    m = re.match(r"^(明治|大正|昭和|平成|令和)(\d+)年(?:(\d+)月(?:(\d+)日)?)?$", s)
    if not m:
        return None
    era, y, mo, d = m.groups()
    year = ERA[era] + int(y)
    if mo is None or d is None:
        return None  # imprecise -> null-over-guess
    date = f"{year:04d}-{int(mo):02d}-{int(d):02d}"
    if date > "2026-07-10":
        return None
    return date


def cat_for(sub1, sub2):
    if sub1 == "有形文化財":
        return "有形文化財", sub2 or None
    if sub1 == "無形民俗文化財":
        return "民俗文化財", "無形民俗文化財"
    if sub1 == "天然記念物":
        return "記念物(史跡・名勝・天然記念物)", "天然記念物"
    return None, sub1


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "misato", "manifest.json"), encoding="utf-8"))
    entry = list(m.values())[0]
    fetched_at = entry["fetched_at"]
    html = open(os.path.join(HERE, "cache", "熊本県", "misato", entry["filename"]), encoding="utf-8").read()
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    rows2 = tables[2].find_all("tr")[1:]
    rows3 = tables[3].find_all("tr")

    records = []
    for r in rows2:
        records.append([c.get_text(strip=True) for c in r.find_all(["th", "td"])])
    for r in rows3:
        records.append([c.get_text(strip=True) for c in r.find_all(["th", "td"])])

    merged = []
    i = 0
    while i < len(records):
        cur = records[i]
        if len(cur) == 1 and i + 1 < len(records) and records[i + 1][0] == "":
            nxt = records[i + 1]
            merged.append([cur[0]] + nxt[1:])
            i += 2
        else:
            merged.append(cur)
            i += 1

    out_rows = []
    for cells in merged:
        if len(cells) != 5:
            continue
        name, sub1, sub2, era_txt, date = cells
        if not name:
            continue
        category, subcat = cat_for(sub1, sub2)
        if category is None:
            continue
        desc = f"時代:{era_txt}" if era_txt else None
        out_rows.append({
            "pref": "熊本県", "municipality": "美里町", "name": name,
            "category": category, "subcategory": subcat, "designation": "町指定",
            "designated_date": wareki_to_iso(date), "location": None,
            "description": desc,
            "source_url": SRC_URL, "source_format": "html", "fetched_at": fetched_at,
        })

    with open(OUT, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
