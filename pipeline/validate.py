#!/usr/bin/env python3
"""validate.py — schema check, dedup, and coverage table for pipeline output.

Reads out/<pref>/<slug>.jsonl files, validates each row against the v1 schema,
removes exact full-record duplicates, compares row counts against the
stated_official_count recorded in out/<pref>/_report.json, and emits a coverage
table in Markdown (out/coverage.md).

Usage:
    python validate.py [--out DIR]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "out")

CATEGORIES = {
    "有形文化財", "無形文化財", "民俗文化財",
    "記念物(史跡・名勝・天然記念物)", "その他",
}
DESIGNATIONS = {"市指定", "町指定", "村指定"}
REQUIRED = [
    "pref", "municipality", "name", "category", "subcategory", "designation",
    "designated_date", "location", "description", "source_url",
    "source_format", "fetched_at",
]
DATE_RE = __import__("re").compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_row(r):
    errs = []
    for k in REQUIRED:
        if k not in r:
            errs.append(f"missing:{k}")
    if r.get("category") not in CATEGORIES:
        errs.append(f"bad-category:{r.get('category')}")
    if r.get("designation") not in DESIGNATIONS:
        errs.append(f"bad-designation:{r.get('designation')}")
    d = r.get("designated_date")
    if d is not None and not DATE_RE.match(d):
        errs.append(f"bad-date:{d}")
    for nullable in ("subcategory", "location", "description", "designated_date"):
        v = r.get(nullable, None)
        if v is not None and not isinstance(v, str):
            errs.append(f"nonstr:{nullable}")
    if not r.get("name"):
        errs.append("empty-name")
    return errs


def load_report(pref_dir):
    p = os.path.join(pref_dir, "_report.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f).get("municipalities", {})


def main():
    ap = argparse.ArgumentParser(description="Validate + coverage for bunkazai out/.")
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()
    out_dir = args.out

    coverage = []   # rows for the markdown table
    total_rows = total_dupes = total_errs = 0

    for pref in sorted(os.listdir(out_dir)):
        pref_dir = os.path.join(out_dir, pref)
        if not os.path.isdir(pref_dir):
            continue
        report = load_report(pref_dir)
        for fn in sorted(os.listdir(pref_dir)):
            if not fn.endswith(".jsonl") or fn.startswith("_"):
                continue
            slug = fn[:-6]
            path = os.path.join(pref_dir, fn)
            rows = []
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        rows.append(json.loads(line))

            # full-record dedup
            seen = set()
            deduped = []
            for r in rows:
                key = json.dumps(r, ensure_ascii=False, sort_keys=True)
                if key in seen:
                    continue
                seen.add(key)
                deduped.append(r)
            dupes = len(rows) - len(deduped)

            # rewrite file deduped
            if dupes:
                with open(path, "w", encoding="utf-8") as f:
                    for r in deduped:
                        f.write(json.dumps(r, ensure_ascii=False) + "\n")

            # schema errors
            n_err = 0
            for r in deduped:
                e = validate_row(r)
                if e:
                    n_err += 1

            rep = report.get(slug, {})
            stated = rep.get("stated_official_count")
            official = rep.get("official_count_source")
            expected = stated if stated is not None else official
            n = len(deduped)
            if expected:
                pct = f"{100*n/expected:.0f}%"
            else:
                pct = "—"

            coverage.append({
                "pref": pref, "slug": slug, "rows": n,
                "dupes": dupes, "errors": n_err,
                "stated": stated, "official": official,
                "coverage": pct,
            })
            total_rows += n
            total_dupes += dupes
            total_errs += n_err

    # ----- markdown -----
    lines = [
        "# Coverage",
        "",
        f"Total rows: **{total_rows}** · duplicates removed: {total_dupes} · "
        f"rows with schema errors: {total_errs}",
        "",
        "| Pref | Muni (slug) | Rows | Dupes | Schema errs | Stated | Official | Coverage |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for c in coverage:
        lines.append(
            f"| {c['pref']} | {c['slug']} | {c['rows']} | {c['dupes']} | "
            f"{c['errors']} | {c['stated'] if c['stated'] is not None else '—'} | "
            f"{c['official'] if c['official'] is not None else '—'} | {c['coverage']} |"
        )
    md = "\n".join(lines) + "\n"

    with open(os.path.join(out_dir, "coverage.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print(md)

    if total_errs:
        print(f"WARNING: {total_errs} rows failed schema validation.", file=sys.stderr)


if __name__ == "__main__":
    main()
