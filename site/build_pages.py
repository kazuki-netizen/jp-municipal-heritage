#!/usr/bin/env python3
"""Build static detail pages for all jp-municipal-heritage records.

Reads all {pref}.jsonl and the corresponding {pref}.geojson (for coordinates),
writes one HTML page per jmh_id under site/p/{jmh_id}.html.

Usage:
  python3 site/build_pages.py            # build pages for all prefs
  python3 site/build_pages.py iwate      # build only one pref
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "site", "p")

PREFS = ["iwate", "miyagi", "aomori", "akita", "yamagata", "fukushima", "hokkaido", "tochigi", "gunma", "ibaraki", "saitama", "chiba", "kanagawa"]

LEAFLET_CSS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
LEAFLET_CSS_INTEGRITY = "sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
LEAFLET_JS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
LEAFLET_JS_INTEGRITY = "sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="


def load_coords(pref):
    """Build (municipality, name) -> [lon, lat] from per-pref geojson."""
    geojson = os.path.join(ROOT, "data", pref + ".geojson")
    if not os.path.exists(geojson):
        return {}
    with open(geojson, encoding="utf-8") as f:
        fc = json.load(f)
    coords = {}
    for feat in fc.get("features", []):
        p = feat.get("properties", {})
        key = (p.get("municipality", ""), p.get("name", ""))
        if key not in coords:
            coords[key] = feat["geometry"]["coordinates"]
    return coords


def esc(s):
    if s is None:
        return ""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def render(row, coords):
    name = row.get("name", "")
    jmh_id = row.get("jmh_id", "")
    municipality = row.get("municipality", "")
    pref = row.get("pref", "")
    category = row.get("category", "")
    subcategory = row.get("subcategory", "")
    designation = row.get("designation", "")
    designated_date = row.get("designated_date", "")
    location = row.get("location", "")
    description = row.get("description")
    source_url = row.get("source_url", "")
    source_format = row.get("source_format", "")
    fetched_at = (row.get("fetched_at") or "")[:10]

    coord = coords.get((municipality, name))
    has_map = coord is not None
    lon, lat = (coord[0], coord[1]) if has_map else (0, 0)

    desc_text = esc(description) if description else "公式解説は未公開です。"

    cite = f'"{esc(name)}" ({esc(jmh_id)}), jp-municipal-heritage, CC-BY 4.0, retrieved {fetched_at}.'

    leaflet_head = ""
    mini_map_html = ""
    if has_map:
        leaflet_head = f"""  <link rel="stylesheet" href="{LEAFLET_CSS}" integrity="{LEAFLET_CSS_INTEGRITY}" crossorigin="" />"""
        mini_map_html = f"""
  <div id="mini-map"></div>
  <script src="{LEAFLET_JS}" integrity="{LEAFLET_JS_INTEGRITY}" crossorigin=""></script>
  <script>
    var m = L.map('mini-map').setView([{lat}, {lon}], 15);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(m);
    L.marker([{lat}, {lon}]).addTo(m);
  </script>"""

    subcategory_row = ""
    if subcategory:
        subcategory_row = f"\n      <dt>小分類</dt><dd>{esc(subcategory)}</dd>"
    location_row = ""
    if location:
        location_row = f"\n      <dt>所在地</dt><dd>{esc(location)}</dd>"

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(name)} — jp-municipal-heritage</title>
  <link rel="stylesheet" href="../style.css">
{leaflet_head}
</head>
<body>
  <nav><a href="../index.html">← マップへ戻る</a></nav>
  <main>
    <h1>{esc(name)}</h1>
    <p class="jmh-id">{esc(jmh_id)}</p>
    <dl class="meta">
      <dt>都道府県</dt><dd>{esc(pref)}</dd>
      <dt>市町村</dt><dd>{esc(municipality)}</dd>
      <dt>指定区分</dt><dd>{esc(designation)}</dd>
      <dt>大分類</dt><dd>{esc(category)}</dd>{subcategory_row}
      <dt>指定年月日</dt><dd>{esc(designated_date) or "不明"}</dd>{location_row}
    </dl>
    <section class="description">
      <h2>解説</h2>
      <p>{desc_text}</p>
    </section>
    <section class="source">
      <h2>出典</h2>
      <p><a href="{esc(source_url)}" target="_blank" rel="noopener">{esc(source_url)}</a><br>
      形式: {esc(source_format)} &middot; 取得日: {fetched_at}</p>
    </section>
    <section class="cite">
      <h2>引用</h2>
      <div class="cite-block">{cite}</div>
    </section>
  </main>{mini_map_html}
</body>
</html>
"""


def process_pref(pref):
    src = os.path.join(ROOT, "data", pref + ".jsonl")
    if not os.path.exists(src):
        print("WARNING: not found:", src)
        return 0, 0

    rows = []
    with open(src, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    coords = load_coords(pref)
    written = 0
    skipped = 0
    for row in rows:
        jmh_id = row.get("jmh_id")
        if not jmh_id:
            skipped += 1
            continue
        html = render(row, coords)
        path = os.path.join(OUT_DIR, jmh_id + ".html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        written += 1

    return written, skipped


def purge_stale(live_ids):
    """Remove site/p/*.html files whose stem is not in live_ids.

    Only touches files matching the JMH-XXXXXX-NNNN pattern to avoid
    accidentally deleting unrelated files.
    """
    import re
    pattern = re.compile(r"^JMH-\d{6}-\d{4}\.html$")
    purged = 0
    for fname in os.listdir(OUT_DIR):
        if not pattern.match(fname):
            continue
        stem = fname[:-5]  # strip .html
        if stem not in live_ids:
            os.remove(os.path.join(OUT_DIR, fname))
            print("  purged stale page: %s" % fname)
            purged += 1
    return purged


def main():
    pref_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    purge = "--purge" in sys.argv or not pref_args  # purge by default on full run
    targets = pref_args if pref_args else PREFS

    os.makedirs(OUT_DIR, exist_ok=True)
    total_written = 0
    total_skipped = 0
    live_ids = set()

    for pref in targets:
        written, skipped = process_pref(pref)
        print("%s: wrote %d pages" % (pref, written))
        if skipped:
            print("  skipped %d rows with no jmh_id" % skipped)
        total_written += written
        total_skipped += skipped

    # Collect all live IDs from ALL prefs (not just targets) for purge
    if purge:
        for pref in PREFS:
            src = os.path.join(ROOT, "data", pref + ".jsonl")
            if not os.path.exists(src):
                continue
            with open(src, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        r = json.loads(line)
                        jid = r.get("jmh_id")
                        if jid:
                            live_ids.add(jid)
        purged = purge_stale(live_ids)
        if purged:
            print("--- purged %d stale pages" % purged)

    print("--- total: wrote %d pages to site/p/" % total_written)
    if total_skipped:
        print("  skipped %d rows with no jmh_id" % total_skipped)


if __name__ == "__main__":
    main()
