#!/usr/bin/env python3
"""Build static JSON API v1 for jp-municipal-heritage.

Reads data/{pref}.jsonl (47 prefectures) and data/i18n/{pref}_en.jsonl
(where present) and writes a static, CDN-friendly JSON tree under apidata/v1/
(served publicly as /api/v1/ via a rewrite in vercel.json; the api/ directory
itself is reserved for Vercel serverless functions such as api/signup.ts):

  apidata/v1/index.json
  apidata/v1/prefectures/<slug>.json
  apidata/v1/municipalities/<key>.json

<key> is the 6-digit JIS municipality code when it can be resolved via
site/muni_codes.json ("pref+municipality" key preferred, bare municipality
key as fallback). When no code resolves, the key falls back to
"<pref_slug>--u<utf8-hex of municipality name>" — pure ASCII so the file
name and its URL are byte-identical (no percent-encoding ambiguity on the
CDN). As of the current dataset every municipality resolves to a code, so
no fallback keys are emitted; the builder errors on duplicate keys.

Usage:
  python3 site/build_api.py
"""
import json
import os
import sys
from collections import OrderedDict
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
I18N_DIR = os.path.join(DATA_DIR, "i18n")
API_DIR = os.path.join(ROOT, "apidata", "v1")

PREFS = [
    "hokkaido", "aomori", "iwate", "miyagi", "akita", "yamagata", "fukushima",
    "ibaraki", "tochigi", "gunma", "saitama", "chiba", "tokyo", "kanagawa",
    "niigata", "toyama", "ishikawa", "fukui", "yamanashi", "nagano", "gifu",
    "shizuoka", "aichi", "mie", "shiga", "kyoto", "osaka", "hyogo", "nara",
    "wakayama", "tottori", "shimane", "okayama", "hiroshima", "yamaguchi",
    "tokushima", "kagawa", "ehime", "kochi", "fukuoka", "saga", "nagasaki",
    "kumamoto", "oita", "miyazaki", "kagoshima", "okinawa",
]


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_muni_codes():
    path = os.path.join(ROOT, "site", "muni_codes.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def resolve_muni_code(muni_codes, pref_ja, municipality):
    combo = pref_ja + municipality
    if combo in muni_codes:
        return muni_codes[combo]
    if municipality in muni_codes:
        return muni_codes[municipality]
    return None


def main():
    muni_codes = load_muni_codes()

    os.makedirs(os.path.join(API_DIR, "prefectures"), exist_ok=True)
    os.makedirs(os.path.join(API_DIR, "municipalities"), exist_ok=True)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    index_prefectures = []
    total_rows = 0
    written_muni_files = 0
    seen_keys = set()

    for slug in PREFS:
        pref_path = os.path.join(DATA_DIR, slug + ".jsonl")
        if not os.path.exists(pref_path):
            print(f"WARNING: missing {pref_path}", file=sys.stderr)
            continue
        rows = load_jsonl(pref_path)
        if not rows:
            print(f"WARNING: empty {pref_path}", file=sys.stderr)
            continue
        pref_ja = rows[0]["pref"]

        # i18n lookup: jmh_id -> {name_romaji, name_en, description_en}
        i18n_path = os.path.join(I18N_DIR, slug + "_en.jsonl")
        i18n = {}
        if os.path.exists(i18n_path):
            for o in load_jsonl(i18n_path):
                i18n[o["jmh_id"]] = {
                    "name_romaji": o.get("name_romaji"),
                    "romaji_confidence": o.get("romaji_confidence"),
                    "name_en": o.get("name_en"),
                    "description_en": o.get("description_en"),
                }

        # group rows by municipality, preserving first-seen order
        by_muni = OrderedDict()
        for row in rows:
            m = row["municipality"]
            by_muni.setdefault(m, []).append(row)

        muni_summaries = []
        for municipality, muni_rows in by_muni.items():
            muni_code = resolve_muni_code(muni_codes, pref_ja, municipality)
            if muni_code:
                key = muni_code
            else:
                key = f"{slug}--u{municipality.encode('utf-8').hex()}"
            if key in seen_keys:
                print(f"ERROR: duplicate municipality key {key} "
                      f"({pref_ja} {municipality})", file=sys.stderr)
                sys.exit(1)
            seen_keys.add(key)

            items = []
            for row in muni_rows:
                item = dict(row)
                en = i18n.get(row["jmh_id"])
                if en:
                    item["en"] = en
                items.append(item)

            muni_obj = {
                "municipality": municipality,
                "pref": pref_ja,
                "muni_code": muni_code,
                "count": len(items),
                "items": items,
            }
            muni_file = os.path.join(API_DIR, "municipalities", f"{key}.json")
            with open(muni_file, "w", encoding="utf-8") as f:
                json.dump(muni_obj, f, ensure_ascii=False, separators=(",", ":"))
            written_muni_files += 1

            muni_summaries.append({
                "name": municipality,
                "muni_code": muni_code,
                "rows": len(muni_rows),
                "url": f"/api/v1/municipalities/{key}.json",
            })

        pref_obj = {
            "pref": pref_ja,
            "rows": len(rows),
            "municipalities": muni_summaries,
        }
        pref_file = os.path.join(API_DIR, "prefectures", f"{slug}.json")
        with open(pref_file, "w", encoding="utf-8") as f:
            json.dump(pref_obj, f, ensure_ascii=False, separators=(",", ":"))

        total_rows += len(rows)
        index_prefectures.append({
            "name_ja": pref_ja,
            "slug": slug,
            "rows": len(rows),
            "en_available": bool(i18n),
            "url": f"/api/v1/prefectures/{slug}.json",
        })

    index_obj = {
        "dataset": "jp-municipal-heritage",
        "license": "CC-BY-4.0",
        "total": total_rows,
        "generated_at": generated_at,
        "prefectures": index_prefectures,
        "docs": "/API.md",
    }
    index_file = os.path.join(API_DIR, "index.json")
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_obj, f, ensure_ascii=False, separators=(",", ":"))

    print(f"prefectures written: {len(index_prefectures)}")
    print(f"municipality files written: {written_muni_files}")
    print(f"total rows (index): {total_rows}")

    # --- validation ---
    validate()


def validate():
    muni_dir = os.path.join(API_DIR, "municipalities")
    files = [f for f in os.listdir(muni_dir) if f.endswith(".json")]
    item_total = 0
    for fn in files:
        path = os.path.join(muni_dir, fn)
        with open(path, encoding="utf-8") as f:
            obj = json.load(f)
        item_total += len(obj["items"])

    # parse-check every json file under api/
    parsed = 0
    for dirpath, _dirnames, filenames in os.walk(API_DIR):
        for fn in filenames:
            if not fn.endswith(".json"):
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8") as f:
                json.load(f)
            parsed += 1

    print(f"validation: municipality files={len(files)}, items total={item_total}, json files parsed OK={parsed}")
    if item_total != 78515:
        print(f"VALIDATION FAILED: item total {item_total} != 78515", file=sys.stderr)
        sys.exit(1)
    print("VALIDATION OK: items total == 78515")


if __name__ == "__main__":
    main()
