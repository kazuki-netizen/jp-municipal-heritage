#!/usr/bin/env python3
"""Idempotent JMH ID minter.

Assigns JMH-XXXXXX-NNNN identifiers to all rows lacking one, across all
prefecture JSONL files.  Existing IDs are never changed.  Run multiple
times safely.

Usage:
  python3 site/assign_ids.py            # process iwate + miyagi + aomori
  python3 site/assign_ids.py iwate      # process only one file (by pref name)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "muni_codes.json")

PREFS = ["iwate", "miyagi", "aomori", "akita", "yamagata", "fukushima", "hokkaido", "tochigi"]


def load_codes():
    with open(CODES, encoding="utf-8") as f:
        return json.load(f)


def sort_key(row):
    date = row.get("designated_date") or "9999"
    return (date, row.get("name") or "")


def process_file(src, codes, serial_max_global):
    """Assign IDs to rows in *src* that lack one.

    serial_max_global is a shared dict so serials are globally unique across
    all files processed in one run.  Returns (rows, assigned, missing_codes).
    """
    rows = []
    with open(src, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    # Absorb existing IDs into the global serial tracker
    for row in rows:
        jid = row.get("jmh_id")
        if jid:
            m = re.match(r"JMH-(\d{6})-(\d{4})", jid)
            if m:
                mcode, serial = m.group(1), int(m.group(2))
                serial_max_global[mcode] = max(serial_max_global.get(mcode, 0), serial)

    # Group rows needing an id
    needs_id = {}
    for i, row in enumerate(rows):
        if not row.get("jmh_id"):
            muni = row.get("municipality", "")
            needs_id.setdefault(muni, []).append(i)

    assigned = 0
    missing_code = set()
    for muni, indices in needs_id.items():
        # Try pref-prefixed key first (handles same-name municipalities in different prefs,
        # e.g. 伊達市 exists in both Fukushima and Hokkaido).
        # Determine pref from first row with this municipality.
        pref_name = rows[indices[0]].get("pref", "") if indices else ""
        mcode = codes.get(pref_name + muni) or codes.get(muni)
        if not mcode:
            missing_code.add(muni)
            continue
        indices.sort(key=lambda i: sort_key(rows[i]))
        next_serial = serial_max_global.get(mcode, 0) + 1
        for i in indices:
            rows[i]["jmh_id"] = "JMH-%s-%04d" % (mcode, next_serial)
            serial_max_global[mcode] = next_serial
            next_serial += 1
            assigned += 1

    with open(src, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return rows, assigned, missing_code


def main():
    codes = load_codes()
    targets = sys.argv[1:] if len(sys.argv) > 1 else PREFS

    serial_max_global = {}
    total_assigned = 0
    total_rows = 0

    for pref in targets:
        src = os.path.join(ROOT, "data", pref + ".jsonl")
        if not os.path.exists(src):
            print("WARNING: file not found:", src)
            continue
        rows, assigned, missing = process_file(src, codes, serial_max_global)
        total_assigned += assigned
        total_rows += len(rows)
        print("%s: assigned %d new ids, %d rows total" % (pref, assigned, len(rows)))
        if missing:
            print("  WARNING: no code for municipalities:", sorted(missing))

    print("--- total: assigned %d, %d rows across %d files" % (total_assigned, total_rows, len(targets)))


if __name__ == "__main__":
    main()
