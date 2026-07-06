#!/usr/bin/env python3
"""One-off refetch of missing list/detail subpages into cache/栃木県/<slug>/.
Respects >=2s delay, caps per-muni requests, updates manifest.json.
Usage: python _refetch.py <slug> <url1> <url2> ...
"""
import sys, os, json, time, hashlib, subprocess
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "栃木県")
DELAY = 2.5
CAP = 40

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def hkey(url):
    return hashlib.sha256(url.encode()).hexdigest()[:16]

def fetch(url):
    # curl with UA, follow redirects, 20s timeout
    p = subprocess.run(
        ["curl", "-sL", "-m", "20", "-A",
         "Mozilla/5.0 (bunkazai-dataset research; contact redacted@example.com)",
         "-w", "%{http_code}", "-o", "/tmp/_rf.body", url],
        capture_output=True, text=True)
    code = p.stdout.strip()[-3:] if p.stdout.strip() else "000"
    data = b""
    if os.path.exists("/tmp/_rf.body"):
        with open("/tmp/_rf.body", "rb") as f:
            data = f.read()
    return code, data

def main():
    slug = sys.argv[1]
    urls = sys.argv[2:]
    d = os.path.join(CACHE, slug)
    os.makedirs(d, exist_ok=True)
    mpath = os.path.join(d, "manifest.json")
    manifest = json.load(open(mpath, encoding="utf-8")) if os.path.exists(mpath) else {}
    urls = urls[:CAP]
    for i, url in enumerate(urls):
        k = hkey(url)
        fname = f"{k}.html"
        code, data = fetch(url)
        ok = code == "200" and len(data) > 200
        if ok:
            with open(os.path.join(d, fname), "wb") as f:
                f.write(data)
            sha = hashlib.sha256(data).hexdigest()
            manifest[k] = {"url": url, "filename": fname, "sha256": sha,
                           "fetched_at": now_iso(), "http_status": 200, "format": "html"}
            print(f"[ok] {code} {len(data)}B {url}")
        else:
            print(f"[skip] {code} {len(data)}B {url}")
        if i < len(urls) - 1:
            time.sleep(DELAY)
    json.dump(manifest, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[done] {slug}: manifest now {len(manifest)} entries")

if __name__ == "__main__":
    main()
