#!/usr/bin/env python3
"""fetch.py — polite downloader for the nationwide 市町村指定文化財 pipeline.

Reads a sources.jsonl (see discover_schema.md), downloads each URL into
pipeline/cache/<pref>/<slug>/, and writes a manifest.json per municipality.

Politeness / correctness guarantees:
  - robots.txt checked per domain (cached), incl. ClaudeBot-specific rules;
    disallowed URLs are skipped and logged, never fetched.
  - >=2s delay enforced per domain between requests.
  - <=40 requests per municipality.
  - retries=2 with backoff on transient failures.
  - idempotent: a URL already cached (keyed by URL hash) is skipped.

Plain `requests` + stdlib only. No API calls here.

Usage:
    python fetch.py <sources.jsonl> [--cache DIR] [--user-agent UA]
"""
import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE = os.path.join(HERE, "cache")
DEFAULT_UA = "bunkazai-collector/1.0 (+https://github.com/; public-data collection; contact: repo owner)"
MIN_DOMAIN_DELAY = 2.0        # seconds between requests to the same domain
MAX_REQS_PER_MUNI = 40
RETRIES = 2
TIMEOUT = 30
CLAUDEBOT_UA = "ClaudeBot"    # also consulted so we honour Claude-specific rules


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def url_hash(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class RobotsCache:
    """Per-domain robots.txt, honoured for both our UA and ClaudeBot."""

    def __init__(self, user_agent):
        self.user_agent = user_agent
        self._cache = {}  # domain -> RobotFileParser | None (None => allow all)

    def _load(self, scheme, netloc):
        robots_url = f"{scheme}://{netloc}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        try:
            resp = requests.get(
                robots_url, timeout=TIMEOUT, headers={"User-Agent": self.user_agent}
            )
            if resp.status_code >= 400:
                # No robots or forbidden robots -> default allow (RFC-ish).
                return None
            rp.parse(resp.text.splitlines())
            return rp
        except requests.RequestException:
            # Unreachable robots -> be conservative but don't hard-block; allow.
            return None

    def allowed(self, url):
        p = urlparse(url)
        key = (p.scheme, p.netloc)
        if key not in self._cache:
            self._cache[key] = self._load(p.scheme, p.netloc)
        rp = self._cache[key]
        if rp is None:
            return True, "no-robots"
        # Must satisfy BOTH our UA and ClaudeBot rules.
        for ua in (self.user_agent, CLAUDEBOT_UA, "*"):
            if not rp.can_fetch(ua, url):
                return False, f"disallowed:{ua}"
        return True, "allowed"


def fetch(sources_path, cache_dir, user_agent):
    robots = RobotsCache(user_agent)
    last_hit = {}  # domain -> monotonic time of last request

    def domain_wait(netloc):
        prev = last_hit.get(netloc)
        if prev is not None:
            elapsed = time.monotonic() - prev
            if elapsed < MIN_DOMAIN_DELAY:
                time.sleep(MIN_DOMAIN_DELAY - elapsed)
        last_hit[netloc] = time.monotonic()

    total_munis = total_ok = total_skip = total_err = 0

    with open(sources_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            src = json.loads(line)
            total_munis += 1
            pref, slug = src["pref"], src["slug"]
            muni_dir = os.path.join(cache_dir, pref, slug)
            os.makedirs(muni_dir, exist_ok=True)
            manifest_path = os.path.join(muni_dir, "manifest.json")
            manifest = {}
            if os.path.exists(manifest_path):
                with open(manifest_path, encoding="utf-8") as mf:
                    manifest = json.load(mf)

            urls = src.get("urls", [])
            if src.get("strategy") == "none" or not urls:
                print(f"[skip] {pref}/{slug}: strategy=none / no urls")
                continue

            reqs_this_muni = 0
            for u in urls:
                url = u["url"]
                fmt = u.get("format", "html")
                h = url_hash(url)

                # idempotent: already cached this URL successfully?
                existing = manifest.get(h)
                if existing and existing.get("http_status") == 200 and \
                        os.path.exists(os.path.join(muni_dir, existing["filename"])):
                    print(f"[cached] {pref}/{slug}: {url}")
                    continue

                if reqs_this_muni >= MAX_REQS_PER_MUNI:
                    print(f"[cap] {pref}/{slug}: hit {MAX_REQS_PER_MUNI} req cap, skipping rest")
                    break

                ok, reason = robots.allowed(url)
                if not ok:
                    print(f"[robots-skip] {pref}/{slug}: {url} ({reason})")
                    manifest[h] = {
                        "url": url, "filename": None, "sha256": None,
                        "fetched_at": now_iso(), "http_status": None,
                        "skipped": reason,
                    }
                    total_skip += 1
                    continue

                netloc = urlparse(url).netloc
                status = None
                content = None
                for attempt in range(RETRIES + 1):
                    domain_wait(netloc)
                    reqs_this_muni += 1
                    try:
                        resp = requests.get(
                            url, timeout=TIMEOUT,
                            headers={"User-Agent": user_agent},
                        )
                        status = resp.status_code
                        if status == 200:
                            content = resp.content
                            break
                        if status in (429, 500, 502, 503, 504) and attempt < RETRIES:
                            time.sleep(2 * (attempt + 1))
                            continue
                        break  # non-retryable HTTP error
                    except requests.RequestException as e:
                        status = f"error:{type(e).__name__}"
                        if attempt < RETRIES:
                            time.sleep(2 * (attempt + 1))
                            continue

                ext = {"html": "html", "csv": "csv", "pdf": "pdf"}.get(fmt, "bin")
                filename = f"{h}.{ext}"
                entry = {
                    "url": url, "filename": filename, "sha256": None,
                    "fetched_at": now_iso(), "http_status": status,
                    "format": fmt,
                }
                if content is not None:
                    path = os.path.join(muni_dir, filename)
                    with open(path, "wb") as out:
                        out.write(content)
                    entry["sha256"] = sha256_file(path)
                    total_ok += 1
                    print(f"[ok] {pref}/{slug}: {url} -> {filename} ({len(content)} B)")
                else:
                    total_err += 1
                    print(f"[fail] {pref}/{slug}: {url} (status={status})")
                manifest[h] = entry

            with open(manifest_path, "w", encoding="utf-8") as mf:
                json.dump(manifest, mf, ensure_ascii=False, indent=2)

    print(f"\n--- fetch summary ---\nmunis={total_munis} ok={total_ok} "
          f"robots-skipped={total_skip} failed={total_err}")


def main():
    ap = argparse.ArgumentParser(description="Polite fetcher for bunkazai sources.")
    ap.add_argument("sources", help="path to a sources.jsonl")
    ap.add_argument("--cache", default=DEFAULT_CACHE, help="cache dir root")
    ap.add_argument("--user-agent", default=DEFAULT_UA)
    args = ap.parse_args()
    if not os.path.exists(args.sources):
        sys.exit(f"sources file not found: {args.sources}")
    fetch(args.sources, args.cache, args.user_agent)


if __name__ == "__main__":
    main()
