#!/usr/bin/env python3
"""refresh.py — change-detection re-crawl for published prefectures.

Re-fetches the unique source_url set of data/<pref>.jsonl politely and
compares content hashes against a baseline, so only *changed* pages need
re-extraction. This is the cheap periodic-update lane: unchanged pages cost
one GET, changed pages get saved for the extraction pipeline.

Baseline resolution order for each URL:
  1. pipeline/refresh_baseline.json (state from previous refresh runs)
  2. pipeline/cache/<pref>/<slug>/manifest.json sha256 (original collection)
  3. none -> first fetch just establishes the baseline ("baseline" status)

Politeness: same guarantees as fetch.py (robots.txt honoured for our UA and
ClaudeBot, per-domain delay, GET only), with the delay raised to 2.5s.
web.archive.org snapshot URLs are immutable and are skipped ("archive-skip").

Outputs, under pipeline/refresh/<UTC date>/:
  report.jsonl  one row per URL: status, old/new sha, affected row count
  changed/      fetched bodies of changed pages (input for re-extraction)
  summary.json  aggregate counts per prefecture

Usage:
    ./venv/bin/python pipeline/refresh.py iwate miyagi ... [--limit N]
"""
import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import RobotsCache, url_hash, TIMEOUT  # noqa: E402

import requests  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE_DIR = os.path.join(HERE, "cache")
BASELINE_PATH = os.path.join(HERE, "refresh_baseline.json")
UA = ("bunkazai-collector/1.0 "
      "(+https://github.com/kazuki-netizen/jp-municipal-heritage; "
      "refresh pass; contact via repo issues)")
MIN_DOMAIN_DELAY = 2.5
RETRIES = 1


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_cache_baseline(pref_kanji):
    """url_hash -> sha256 from the original collection manifests."""
    out = {}
    pref_dir = os.path.join(CACHE_DIR, pref_kanji)
    if not os.path.isdir(pref_dir):
        return out
    for slug in os.listdir(pref_dir):
        mp = os.path.join(pref_dir, slug, "manifest.json")
        if not os.path.exists(mp):
            continue
        try:
            with open(mp, encoding="utf-8") as f:
                manifest = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        for h, entry in manifest.items():
            if isinstance(entry, dict) and entry.get("sha256"):
                out[h] = entry["sha256"]
    return out


def collect_urls(pref_slug):
    """Unique source_urls of a published prefecture, with row counts."""
    path = os.path.join(ROOT, "data", f"{pref_slug}.jsonl")
    if not os.path.exists(path):
        sys.exit(f"no such published prefecture: {path}")
    urls = {}  # url -> {"rows": n, "pref_kanji": str, "munis": set}
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            u = (r.get("source_url") or "").strip()
            if not u.startswith(("http://", "https://")):
                continue
            e = urls.setdefault(u, {"rows": 0, "pref_kanji": r["pref"], "munis": set()})
            e["rows"] += 1
            e["munis"].add(r.get("municipality") or "")
    return urls


def main():
    ap = argparse.ArgumentParser(description="Change-detection re-crawl.")
    ap.add_argument("prefs", nargs="+", help="published prefecture slugs (e.g. iwate)")
    ap.add_argument("--limit", type=int, default=0, help="max URLs per prefecture (0 = all)")
    args = ap.parse_args()

    run_dir = os.path.join(HERE, "refresh", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    changed_dir = os.path.join(run_dir, "changed")
    os.makedirs(changed_dir, exist_ok=True)
    report_path = os.path.join(run_dir, "report.jsonl")

    baseline = {}
    if os.path.exists(BASELINE_PATH):
        with open(BASELINE_PATH, encoding="utf-8") as f:
            baseline = json.load(f)

    robots = RobotsCache(UA)
    last_hit = {}

    def domain_wait(netloc):
        prev = last_hit.get(netloc)
        if prev is not None:
            wait = MIN_DOMAIN_DELAY - (time.monotonic() - prev)
            if wait > 0:
                time.sleep(wait)
        last_hit[netloc] = time.monotonic()

    summary = {}
    report = open(report_path, "a", encoding="utf-8")

    for pref_slug in args.prefs:
        urls = collect_urls(pref_slug)
        cache_base = {}
        counts = {"unchanged": 0, "changed": 0, "baseline": 0,
                  "error": 0, "robots-skip": 0, "archive-skip": 0}
        items = sorted(urls.items())
        if args.limit:
            items = items[: args.limit]
        for url, meta in items:
            if not cache_base:
                cache_base = load_cache_baseline(meta["pref_kanji"]) or {"": None}
            h = url_hash(url)
            row = {
                "pref": pref_slug, "url": url, "url_hash": h,
                "rows_affected": meta["rows"],
                "municipalities": sorted(m for m in meta["munis"] if m),
                "checked_at": now_iso(),
            }

            if urlparse(url).netloc.endswith("web.archive.org"):
                row["status"] = "archive-skip"   # snapshots are immutable
            else:
                ok, reason = robots.allowed(url)
                if not ok:
                    row["status"], row["detail"] = "robots-skip", reason
                else:
                    old = (baseline.get(h) or {}).get("sha256") or cache_base.get(h)
                    status_code, content = None, None
                    netloc = urlparse(url).netloc
                    for attempt in range(RETRIES + 1):
                        domain_wait(netloc)
                        try:
                            resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": UA})
                            status_code = resp.status_code
                            if status_code == 200:
                                content = resp.content
                                break
                            if status_code in (429, 500, 502, 503, 504) and attempt < RETRIES:
                                time.sleep(3)
                                continue
                            break
                        except requests.RequestException as e:
                            status_code = f"error:{type(e).__name__}"
                            if attempt < RETRIES:
                                time.sleep(3)
                    row["http_status"] = status_code
                    if content is None:
                        row["status"] = "error"
                    else:
                        new_sha = hashlib.sha256(content).hexdigest()
                        row["old_sha256"], row["new_sha256"] = old, new_sha
                        if old is None:
                            row["status"] = "baseline"
                        elif new_sha == old:
                            row["status"] = "unchanged"
                        else:
                            row["status"] = "changed"
                            with open(os.path.join(changed_dir, f"{h}.bin"), "wb") as out:
                                out.write(content)
                        baseline[h] = {"url": url, "sha256": new_sha, "checked_at": now_iso()}

            counts[row["status"]] += 1
            report.write(json.dumps(row, ensure_ascii=False) + "\n")
            report.flush()
            print(f"[{row['status']}] {pref_slug} {url}")
        summary[pref_slug] = {"urls": len(items), **counts}
        # persist baseline after each prefecture so an interrupted run keeps progress
        with open(BASELINE_PATH, "w", encoding="utf-8") as f:
            json.dump(baseline, f, ensure_ascii=False, indent=1)

    report.close()
    with open(os.path.join(run_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("\n--- refresh summary ---")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
