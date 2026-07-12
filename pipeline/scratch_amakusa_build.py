#!/usr/bin/env python3
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "amakusa.jsonl")

FILES = [
    ("f52ac5eb99464ae3", "有形文化財", "建造物", "https://www.city.amakusa.kumamoto.jp/list00791.html"),
    ("5c5aafc26bea149f", "有形文化財", "歴史資料", "https://www.city.amakusa.kumamoto.jp/list00793.html"),
    ("e6a7ab55e59966ee", "有形文化財", "書跡・古文書", "https://www.city.amakusa.kumamoto.jp/list00795.html"),
    ("f9bb00c4d59d037c", "有形文化財", "工芸品", "https://www.city.amakusa.kumamoto.jp/list00797.html"),
    ("0471edb218d2e2d5", "有形文化財", "考古資料", "https://www.city.amakusa.kumamoto.jp/list00799.html"),
    ("a3b76fb1b1814821", "有形文化財", "彫刻", "https://www.city.amakusa.kumamoto.jp/list00801.html"),
    ("1952ed2999419dcd", "民俗文化財", "無形民俗文化財", "https://www.city.amakusa.kumamoto.jp/list00803.html"),
    ("fa4dfaa864f558eb", "記念物(史跡・名勝・天然記念物)", "史跡", "https://www.city.amakusa.kumamoto.jp/list00807.html"),
    ("a9e8122f6fe8afbb", "記念物(史跡・名勝・天然記念物)", "史跡", "https://www.city.amakusa.kumamoto.jp/list00807.html"),
    ("d82c0832fb13e556", "記念物(史跡・名勝・天然記念物)", "名勝", "https://www.city.amakusa.kumamoto.jp/list00809.html"),
    ("d90b4155f6b64b00", "記念物(史跡・名勝・天然記念物)", "天然記念物", "https://www.city.amakusa.kumamoto.jp/list00812.html"),
]


def extract_names(path):
    html = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'<div class="ttl"><a href="([^"]+)"[^>]*>(.*?)</a></div>', html, re.S):
        href, name = m.groups()
        name = re.sub("<[^>]+>", "", name).strip()
        if name:
            out.append((name, href))
    return out


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "amakusa", "manifest.json"), encoding="utf-8"))
    fetched_by_hash = {v["filename"].split(".")[0]: v["fetched_at"] for v in m.values()}

    out_rows = []
    for filehash, category, subcat, list_url in FILES:
        path = os.path.join(HERE, "cache", "熊本県", "amakusa", f"{filehash}.html")
        fetched_at = fetched_by_hash.get(filehash, "2026-07-12T00:00:00Z")
        for name, detail_url in extract_names(path):
            out_rows.append({
                "pref": "熊本県", "municipality": "天草市", "name": name,
                "category": category, "subcategory": subcat, "designation": "市指定",
                "designated_date": None, "location": None,
                "description": None,
                "source_url": list_url, "source_format": "html", "fetched_at": fetched_at,
            })

    with open(OUT, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
