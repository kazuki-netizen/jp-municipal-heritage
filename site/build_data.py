#!/usr/bin/env python3
"""Build derived data artifacts for jp-municipal-heritage.

Generates, from data/{pref}.jsonl (canonical sources, never modified):
  - data/{pref}.csv      : same columns, UTF-8 with BOM (Excel-friendly)
  - data/{pref}.geojson  : geocoded points (GSI address geocoder)
  - data/all.geojson     : combined points across all prefectures

Geocoding uses the Geospatial Information Authority of Japan (GSI) public
address-search API (read-only GET). Results are cached in site/geocode_cache.json
so re-runs make zero network requests for already-resolved addresses.

Outlier detection: all points are validated against a generous Tohoku bounding box.
Points outside the box get municipality-centroid fallback before being dropped.

Bounding box (generous Tohoku all-6-pref + surrounds):
  lat: 36.7 - 41.7 N
  lon: 139.1 - 142.2 E

Usage:
  python3 site/build_data.py            # build csv + geojson for all prefs
  python3 site/build_data.py iwate      # build only one pref
  python3 site/build_data.py --csv-only # build only csv (no network)
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
CACHE = os.path.join(ROOT, "site", "geocode_cache.json")

PREFS = ["iwate", "miyagi", "aomori", "akita", "yamagata", "fukushima"]

COLUMNS = [
    "pref", "municipality", "name", "category", "subcategory",
    "designation", "designated_date", "location", "description",
    "source_url", "source_format", "fetched_at", "jmh_id",
]

GSI_URL = "https://msearch.gsi.go.jp/address-search/AddressSearch"
DELAY_SEC = 0.5  # polite delay between geocode requests

# Generous Tohoku bounding box (lat N, lon E) — covers all 6 prefectures
BBOX = {"lat_min": 36.7, "lat_max": 41.7, "lon_min": 139.1, "lon_max": 142.2}


def load_rows(pref):
    src = os.path.join(ROOT, "data", pref + ".jsonl")
    rows = []
    with open(src, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_csv(rows, pref):
    csv_out = os.path.join(ROOT, "data", pref + ".csv")
    with io.open(csv_out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in COLUMNS})
    print("wrote", csv_out, "(%d rows)" % len(rows))


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
    req = urllib.request.Request(
        url, headers={"User-Agent": "jp-municipal-heritage/1.0 (open data build)"}
    )
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


def in_bbox(coord):
    """Return True if [lon, lat] coord falls within BBOX."""
    if coord is None:
        return False
    lon, lat = coord[0], coord[1]
    return (BBOX["lat_min"] <= lat <= BBOX["lat_max"] and
            BBOX["lon_min"] <= lon <= BBOX["lon_max"])


def geocode_query(row):
    """Best geocoding query for a row.

    Prefer the full location string; if absent, fall back to the
    municipality name so every row still lands somewhere plausible
    (municipality centroid) rather than being dropped from the map.

    Some municipalities publish location at 大字/地区 granularity only
    ("桜町", "太田"), with no municipality prefix. Geocoding those bare
    strings matches same-named places in other prefectures, so we prefix
    the prefecture + municipality when the string does not already start
    with either.
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
    # municipality name does not match a same-named place in another prefecture.
    muni = row.get("municipality")
    pref = row.get("pref") or ""
    if muni:
        return pref + muni, "municipality"
    return (pref or None), "municipality"


def build_geojson_for_pref(rows, pref, cache):
    """Geocode rows and return (features, stats_dict).

    Out-of-bbox points get a municipality-centroid fallback before being
    reported as outliers.
    """
    features = []
    resolved = 0
    approx = 0
    unresolved = 0
    outliers_fixed = 0
    outliers_dropped = 0

    for i, r in enumerate(rows):
        q, level = geocode_query(r)
        coord = geocode(q, cache) if q else None

        # If location-level geocode is out of bbox, try municipality fallback
        if coord is not None and level == "location" and not in_bbox(coord):
            muni = r.get("municipality")
            pref_name = r.get("pref") or ""
            q2 = (pref_name + muni) if muni else None
            if q2:
                coord2 = geocode(q2, cache)
                if coord2 is not None and in_bbox(coord2):
                    print("  outlier fixed via muni fallback: %s / %s [%.4f,%.4f]->[%.4f,%.4f]"
                          % (r.get("municipality"), r.get("name"), coord[1], coord[0],
                             coord2[1], coord2[0]))
                    coord = coord2
                    level = "municipality"
                    outliers_fixed += 1
                else:
                    print("  outlier dropped (no bbox fix): %s / %s [%.4f,%.4f]"
                          % (r.get("municipality"), r.get("name"), coord[1], coord[0]))
                    outliers_dropped += 1
                    coord = None

        if coord is None and level == "location":
            # Retry at municipality centroid
            muni = r.get("municipality")
            q2 = ((r.get("pref") or "") + muni) if muni else None
            if q2:
                coord = geocode(q2, cache)
                if coord is not None:
                    level = "municipality"

        if coord is None:
            unresolved += 1
            continue

        # Final bbox check
        if not in_bbox(coord):
            print("  final outlier dropped: %s / %s [%.4f,%.4f]"
                  % (r.get("municipality"), r.get("name"), coord[1], coord[0]))
            unresolved += 1
            continue

        if level == "location":
            resolved += 1
        else:
            approx += 1

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

    stats = {
        "resolved": resolved,
        "approx": approx,
        "unresolved": unresolved,
        "outliers_fixed": outliers_fixed,
        "outliers_dropped": outliers_dropped,
        "features": len(features),
    }
    return features, stats


def build_geojson(pref_rows_map, cache):
    """Build per-pref geojson files and combined all.geojson."""
    all_features = []

    for pref, rows in pref_rows_map.items():
        geojson_out = os.path.join(ROOT, "data", pref + ".geojson")
        print("geocoding %s (%d rows)..." % (pref, len(rows)))
        features, stats = build_geojson_for_pref(rows, pref, cache)
        save_cache(cache)

        fc = {"type": "FeatureCollection", "features": features}
        with open(geojson_out, "w", encoding="utf-8") as f:
            json.dump(fc, f, ensure_ascii=False)
        print("wrote", geojson_out)
        print("  address-precise: %(resolved)d  municipality-approx: %(approx)d  "
              "unresolved(dropped): %(unresolved)d  outliers-fixed: %(outliers_fixed)d  "
              "total features: %(features)d" % stats)

        all_features.extend(features)

    # Combined
    all_out = os.path.join(ROOT, "data", "all.geojson")
    fc_all = {"type": "FeatureCollection", "features": all_features}
    with open(all_out, "w", encoding="utf-8") as f:
        json.dump(fc_all, f, ensure_ascii=False)
    print("wrote", all_out, "(%d features total)" % len(all_features))


def main():
    csv_only = "--csv-only" in sys.argv
    pref_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    targets = pref_args if pref_args else PREFS

    pref_rows_map = {}
    for pref in targets:
        src = os.path.join(ROOT, "data", pref + ".jsonl")
        if not os.path.exists(src):
            print("WARNING: not found:", src)
            continue
        rows = load_rows(pref)
        pref_rows_map[pref] = rows
        build_csv(rows, pref)

    if not csv_only:
        cache = load_cache()
        build_geojson(pref_rows_map, cache)


if __name__ == "__main__":
    main()
