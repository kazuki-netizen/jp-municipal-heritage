#!/usr/bin/env python3
"""gt_diff.py — ground-truth precision/recall for the 6 Tohoku test munis.

Compares pipeline output (out/<pref>/<slug>.jsonl) against the reviewed dataset
(data/<pref-romaji>.jsonl) by municipality, on row counts and property names.

precision = |matched names| / |extracted names|
recall    = |matched names| / |reviewed names|

Name matching is on a normalized name (whitespace/full-width-space stripped),
which is the field a human reviewer would use to tell two items apart.

Usage:
    python gt_diff.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")
DATA = os.path.join(REPO, "data")

# (pref, slug, municipality-jp, reviewed-file)
GT = [
    ("岩手県", "ninohe",   "二戸市", "iwate.jsonl"),
    ("岩手県", "yahaba",   "矢巾町", "iwate.jsonl"),
    ("岩手県", "kamaishi", "釜石市", "iwate.jsonl"),
    ("岩手県", "yamada",   "山田町", "iwate.jsonl"),
    ("福島県", "tanagura", "棚倉町", "fukushima.jsonl"),
    ("福島県", "ishikawa", "石川町", "fukushima.jsonl"),
]


def norm(s):
    if not s:
        return ""
    s = re.sub(r"[\s　]+", "", s)
    return s.strip()


def load_reviewed(fname, muni):
    path = os.path.join(DATA, fname)
    names = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            o = json.loads(line)
            if o.get("municipality") == muni:
                names.append(norm(o.get("name")))
    return names


def load_extracted(pref, slug):
    path = os.path.join(OUT, pref, f"{slug}.jsonl")
    names = []
    if not os.path.exists(path):
        return names
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                names.append(norm(json.loads(line).get("name")))
    return names


def main():
    tot_match = tot_ext = tot_rev = 0
    rows = []
    for pref, slug, muni, fname in GT:
        rev = load_reviewed(fname, muni)
        ext = load_extracted(pref, slug)
        rev_set, ext_set = set(rev), set(ext)
        matched = rev_set & ext_set
        prec = len(matched) / len(ext_set) if ext_set else 0.0
        rec = len(matched) / len(rev_set) if rev_set else 0.0
        rows.append((muni, len(rev), len(ext), len(matched), prec, rec))
        tot_match += len(matched)
        tot_ext += len(ext_set)
        tot_rev += len(rev_set)

    print(f"{'Muni':<8} {'reviewed':>9} {'extracted':>10} {'matched':>8} "
          f"{'precision':>10} {'recall':>8}")
    for muni, nr, ne, nm, p, r in rows:
        print(f"{muni:<8} {nr:>9} {ne:>10} {nm:>8} {p:>10.1%} {r:>8.1%}")
    tp = tot_match / tot_ext if tot_ext else 0.0
    tr = tot_match / tot_rev if tot_rev else 0.0
    print("-" * 60)
    print(f"{'TOTAL':<8} {tot_rev:>9} {tot_ext:>10} {tot_match:>8} "
          f"{tp:>10.1%} {tr:>8.1%}")
    print(f"\nrow-name match (recall) total: {tr:.1%}  target >= 95%")


if __name__ == "__main__":
    main()
