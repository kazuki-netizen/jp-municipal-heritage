#!/usr/bin/env python3
import json, os
from bs4 import BeautifulSoup
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "kumamoto.jsonl")
SRC_URL = "https://www.city.kumamoto.jp/kiji00361908/index.html"
FETCHED_AT = "2026-07-12T00:00:00Z"  # placeholder, overwritten below from manifest

CAT_MAP = {
    "有形文化財": "有形文化財",
    "無形文化財": "無形文化財",
    "民俗文化財": "民俗文化財",
    "記念物": "記念物(史跡・名勝・天然記念物)",
}

def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "kumamoto", "manifest.json"), encoding="utf-8"))
    entry = list(m.values())[0]
    fetched_at = entry["fetched_at"]
    html_path = os.path.join(HERE, "cache", "熊本県", "kumamoto", entry["filename"])
    html = open(html_path, encoding="utf-8-sig").read()
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    rows = table.find_all("tr")[1:]
    out_rows = []
    for r in rows:
        cells = [c.get_text(strip=True) for c in r.find_all(["th", "td"])]
        if len(cells) != 3:
            continue
        top, sub, name = cells
        if not name:
            continue
        category = CAT_MAP.get(top)
        if category is None:
            continue
        row = {
            "pref": "熊本県",
            "municipality": "熊本市",
            "name": name,
            "category": category,
            "subcategory": sub or None,
            "designation": "市指定",
            "designated_date": None,
            "location": None,
            "description": None,
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
