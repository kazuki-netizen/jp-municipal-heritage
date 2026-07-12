#!/usr/bin/env python3
import json, os
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "uki.jsonl")
SRC_URL = "https://www.city.uki.kumamoto.jp/kankobunka/bunka/bunkazai/shitei/ichiran_bunkazai/2269276"

CAT_MAP = {
    "有形文化財": ("有形文化財", "有形文化財"),
    "無形文化財": ("無形文化財", "無形文化財"),
    "無形民俗文化財": ("民俗文化財", "無形民俗文化財"),
    "史跡": ("記念物(史跡・名勝・天然記念物)", "史跡"),
    "名勝": ("記念物(史跡・名勝・天然記念物)", "名勝"),
    "天然記念物": ("記念物(史跡・名勝・天然記念物)", "天然記念物"),
}


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "uki", "manifest.json"), encoding="utf-8"))
    entry = [v for v in m.values() if v["url"] == SRC_URL][0]
    fetched_at = entry["fetched_at"]
    html = open(os.path.join(HERE, "cache", "熊本県", "uki", entry["filename"]), encoding="utf-8").read()
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find_all("table")[0]
    rows = table.find_all("tr")[1:]
    out_rows = []
    for r in rows:
        cells = [c.get_text(strip=True) for c in r.find_all(["th", "td"])]
        if len(cells) != 4 or cells[1] != "市":
            continue
        num, desig, sub, name = cells
        if sub not in CAT_MAP or not name:
            continue
        category, subcat = CAT_MAP[sub]
        out_rows.append({
            "pref": "熊本県", "municipality": "宇城市", "name": name,
            "category": category, "subcategory": subcat, "designation": "市指定",
            "designated_date": None, "location": None,
            "description": f"番号{num}",
            "source_url": SRC_URL, "source_format": "html", "fetched_at": fetched_at,
        })
    assert len(out_rows) == 92, len(out_rows)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
