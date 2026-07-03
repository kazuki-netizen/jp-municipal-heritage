#!/usr/bin/env python3
"""Build derived data artifacts for jp-municipal-heritage.

Generates, from data/iwate.jsonl (the canonical source, never modified):
  - data/iwate.csv      : same columns, UTF-8 with BOM (Excel-friendly)
  - data/iwate.geojson  : geocoded points (GSI address geocoder)

Geocoding uses the Geospatial Information Authority of Japan (GSI) public
address-search API (read-only GET). Results are cached in site/geocode_cache.json
so re-runs make zero network requests for already-resolved addresses.

Usage:
  python3 site/build_data.py            # build csv + geojson (geocode as needed)
  python3 site/build_data.py --csv-only # build only the csv (no network)
"""
import csv
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "iwate.jsonl")
CSV_OUT = os.path.join(ROOT, "data", "iwate.csv")
GEOJSON_OUT = os.path.join(ROOT, "data", "iwate.geojson")
CACHE = os.path.join(ROOT, "site", "geocode_cache.json")

COLUMNS = [
    "pref", "municipality", "name", "category", "subcategory",
    "designation", "designated_date", "location", "description",
    "source_url", "source_format", "fetched_at",
]

GSI_URL = "https://msearch.gsi.go.jp/address-search/AddressSearch"
DELAY_SEC = 0.5  # polite delay between geocode requests


def load_rows():
    rows = []
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_csv(rows):
    # UTF-8 with BOM so Excel (Japanese Windows) opens it without mojibake.
    with io.open(CSV_OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in COLUMNS})
    print("wrote", CSV_OUT, "(%d rows)" % len(rows))


def load_cache():
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=0, sort_keys=True)


def geocode(query, cache):
    """Return [lon, lat] or None. Cached by exact query string.

    Cache stores None (as null) for queries that returned no match, so
    unresolvable addresses are not re-requested on subsequent runs.
    """
    if query in cache:
        return cache[query]
    url = GSI_URL + "?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(url, headers={"User-Agent": "jp-municipal-heritage/1.0 (open data build)"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("  geocode error for %r: %s" % (query, e), file=sys.stderr)
        return None  # transient error: do NOT cache, allow retry next run
    coord = None
    if isinstance(data, list) and data:
        coord = data[0].get("geometry", {}).get("coordinates")
    cache[query] = coord
    time.sleep(DELAY_SEC)
    return coord


def geocode_query(row):
    """Best geocoding query for a row.

    Prefer the full location string; if absent, fall back to the
    municipality name so every row still lands somewhere plausible
    (municipality centroid) rather than being dropped from the map.

    Some municipalities (花巻・宮古・紫波・遠野…) publish location at 大字/地区
    granularity only ("桜町", "太田"), with no municipality prefix. Geocoding
    those bare strings matches same-named places in other prefectures, so we
    prefix the prefecture + municipality when the string does not already
    start with either.
    """
    loc = row.get("location")
    if loc:
        pref = row.get("pref") or ""
        muni = row.get("municipality") or ""
        if (muni and muni in loc) or (pref and loc.startswith(pref)):
            q = loc
        else:
            q = pref + muni + loc
        return q, "location"
    # Municipality centroid fallback — prefix the prefecture so a bare
    # municipality name (e.g. "山田町", which also exists in Hokkaido) does
    # not match a same-named place in another prefecture.
    muni = row.get("municipality")
    pref = row.get("pref") or ""
    if muni:
        return pref + muni, "municipality"
    return (pref or None), "municipality"


def build_geojson(rows):
    cache = load_cache()
    features = []
    resolved = 0
    approx = 0
    unresolved = 0
    for i, r in enumerate(rows):
        q, level = geocode_query(r)
        coord = geocode(q, cache) if q else None
        if coord is None and level == "location":
            # Retry at municipality centroid so the point still appears.
            # Prefix the prefecture to avoid cross-prefecture name collisions.
            muni = r.get("municipality")
            q2 = ((r.get("pref") or "") + muni) if muni else None
            if q2:
                coord = geocode(q2, cache)
                if coord is not None:
                    level = "municipality"
        if coord is None:
            unresolved += 1
        elif level == "location":
            resolved += 1
        else:
            approx += 1
        if coord is None:
            continue
        props = {k: r.get(k) for k in COLUMNS}
        props["geo_precision"] = "address" if level == "location" else "municipality"
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [coord[0], coord[1]]},
            "properties": props,
        })
        if (i + 1) % 200 == 0:
            print("  ...%d/%d rows processed" % (i + 1, len(rows)))
            save_cache(cache)
    save_cache(cache)
    fc = {"type": "FeatureCollection", "features": features}
    with open(GEOJSON_OUT, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False)
    print("wrote", GEOJSON_OUT)
    print("  address-precise: %d  municipality-approx: %d  unresolved(dropped): %d  total features: %d"
          % (resolved, approx, unresolved, len(features)))


def main():
    rows = load_rows()
    build_csv(rows)
    if "--csv-only" not in sys.argv:
        build_geojson(rows)


if __name__ == "__main__":
    main()
