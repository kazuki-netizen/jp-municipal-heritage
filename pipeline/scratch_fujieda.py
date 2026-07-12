import csv, json, re

SRC = "https://opendata.pref.shizuoka.jp/dataset/9750/resource/66369/222143_cultural_property.csv"
FETCHED = "2026-07-12T04:45:00Z"
PREF = "静岡県"
MUNI = "藤枝市"

CAT_MAP = {
    "有形文化財": "有形文化財",
    "無形文化財": "無形文化財",
    "有形民俗文化財": "民俗文化財",
    "無形民俗文化財": "民俗文化財",
    "史跡": "記念物",
    "天然記念物": "記念物",
    "名勝": "記念物",
}

rows_out = []
with open("/Users/miyazakihitohata/bunkazai/pipeline/cache/静岡県/fujieda/cultural_property.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        bunrui = row["文化財分類"].split(";")[0].strip()
        if not bunrui.startswith("市指定"):
            continue
        orig_subtype = bunrui.replace("市指定", "")
        kind = row["種類"].strip()
        cat = CAT_MAP.get(orig_subtype)
        if cat is None:
            cat = "その他"
        subcat = kind if kind else orig_subtype
        name = row["名称"].strip()
        date = row["文化財指定日"].strip()
        iso = date if re.match(r'^\d{4}-\d{2}-\d{2}$', date) else None
        loc = row["住所"].strip()
        owner = row["所有者等"].strip()
        count = row["員数（数）"].strip()
        unit = row["員数（単位）"].strip()
        desc_parts = []
        if owner:
            desc_parts.append(f"所有者等：{owner}")
        if count:
            desc_parts.append(f"員数：{count}{unit}".strip())
        desc = "　".join(desc_parts) if desc_parts else None
        rows_out.append({
            "pref": PREF,
            "municipality": MUNI,
            "name": name,
            "category": cat,
            "subcategory": subcat,
            "designation": "市指定",
            "designated_date": iso,
            "location": loc,
            "description": desc,
            "source_url": SRC,
            "source_format": "csv",
            "fetched_at": FETCHED,
        })

out_path = "/Users/miyazakihitohata/bunkazai/pipeline/out/静岡県/fujieda.jsonl"
with open(out_path, "w", encoding="utf-8") as f:
    for r in rows_out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"wrote {len(rows_out)} rows to {out_path}")
