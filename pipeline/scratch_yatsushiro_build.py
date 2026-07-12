#!/usr/bin/env python3
import json, os
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "yatsushiro.jsonl")
SRC_URL = "https://www.city.yatsushiro.lg.jp/kiji003474/index.html"

def cat_for(sub):
    if sub.startswith("有形文化財"):
        return "有形文化財", sub[len("有形文化財"):].strip("（）()") or None
    if sub in ("有形民俗文化財", "無形民俗文化財"):
        return "民俗文化財", sub
    if sub in ("史跡", "名勝", "天然記念物"):
        return "記念物(史跡・名勝・天然記念物)", sub
    return None, sub

def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "yatsushiro", "manifest.json"), encoding="utf-8"))
    entry = [v for v in m.values() if v["url"] == SRC_URL][0]
    fetched_at = entry["fetched_at"]
    html = open(os.path.join(HERE, "cache", "熊本県", "yatsushiro", entry["filename"]), encoding="utf-8-sig").read()
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find_all("table")[0]
    rows = table.find_all("tr")[1:]
    out_rows = []
    for r in rows:
        cells = [c.get_text(strip=True) for c in r.find_all(["th", "td"])]
        if len(cells) != 4 or cells[0] != "市指定":
            continue
        _, sub, name, loc = cells
        if not name:
            continue
        category, subcat = cat_for(sub)
        if category is None:
            continue
        row = {
            "pref": "熊本県",
            "municipality": "八代市",
            "name": name,
            "category": category,
            "subcategory": subcat,
            "designation": "市指定",
            "designated_date": None,
            "location": loc or None,
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
