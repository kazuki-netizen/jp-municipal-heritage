#!/usr/bin/env python3
"""Prepare copyright-safe chunk files for agent-based English generation.

Projects rows (minus municipal prose / source_url) into chunk files so that a
generation agent NEVER sees the copyrighted description text. Skips rows
already covered in the parallel i18n file (resume-aware).

Usage:
  python pipeline/i18n_prep.py data/aomori.jsonl --i18n data/i18n/aomori_en.jsonl \
      --workdir pipeline/i18n_work/aomori [--chunk 40]
"""
import argparse
import json
from pathlib import Path

ALLOWED_FIELDS = [
    "name", "category", "subcategory", "designation",
    "designated_date", "municipality", "location",
]


def read_jsonl(path):
    rows = []
    p = Path(path)
    if not p.exists():
        return rows
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--i18n", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--chunk", type=int, default=40)
    args = ap.parse_args()

    rows = read_jsonl(args.input)
    done = {r["jmh_id"] for r in read_jsonl(args.i18n)}
    todo = [r for r in rows if r["jmh_id"] not in done]

    wd = Path(args.workdir)
    wd.mkdir(parents=True, exist_ok=True)
    # clear stale chunks so a re-prep never leaves old work behind
    for old in wd.glob("chunk_*.json"):
        old.unlink()
    for old in wd.glob("out_*.jsonl"):
        old.unlink()

    n = 0
    for ci in range(0, len(todo), args.chunk):
        chunk = []
        for r in todo[ci:ci + args.chunk]:
            item = {"jmh_id": r["jmh_id"]}
            for k in ALLOWED_FIELDS:
                v = r.get(k)
                if v not in (None, ""):
                    item[k] = v
            chunk.append(item)
        (wd / f"chunk_{ci // args.chunk:03d}.json").write_text(
            json.dumps(chunk, ensure_ascii=False, indent=1))
        n += 1
    print(f"input={len(rows)} done={len(done)} todo={len(todo)} chunks={n} -> {wd}")


if __name__ == "__main__":
    main()
