#!/usr/bin/env python3
import sys, os, json, hashlib, subprocess, datetime, urllib.request, urllib.error

def main():
    url = sys.argv[1]
    slug_dir = sys.argv[2]
    fmt = sys.argv[3]
    os.makedirs(slug_dir, exist_ok=True)
    manifest_path = os.path.join(slug_dir, "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        manifest = json.load(open(manifest_path))

    h = hashlib.sha256(url.encode()).hexdigest()[:16]
    ext = "pdf" if fmt == "pdf" else "html"
    filename = f"{h}.{ext}"
    filepath = os.path.join(slug_dir, filename)

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; bunkazai-research/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            status = resp.status
    except urllib.error.HTTPError as e:
        print(f"FAIL {url} status={e.code}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL {url} error={e}")
        sys.exit(1)

    with open(filepath, "wb") as f:
        f.write(data)

    sha256 = hashlib.sha256(data).hexdigest()
    manifest[h] = {
        "url": url,
        "filename": filename,
        "sha256": sha256,
        "fetched_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "http_status": status,
        "format": fmt,
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"OK {url} -> {filepath} ({len(data)} bytes)")

if __name__ == "__main__":
    main()
