"""Merge wave-1 prefecture outputs (out/<県名>/*.jsonl) into data/<pref>.jsonl.

Normalizes category to 文化庁大分類, drops byte-duplicates, flags nav-noise names.
"""
import json, glob, os, re, sys

PREFS = {
    "新潟県": "niigata", "山梨県": "yamanashi", "富山県": "toyama",
    "石川県": "ishikawa", "福井県": "fukui", "長野県": "nagano", "静岡県": "shizuoka",
}
CAT_MAP = {
    "記念物": "記念物(史跡・名勝・天然記念物)",
    "民俗資料": "民俗文化財",
    "無形民俗文化財": "民俗文化財",
    "有形民俗文化財": "民俗文化財",
}
ALLOWED_CAT = {"有形文化財", "無形文化財", "民俗文化財", "記念物(史跡・名勝・天然記念物)", "その他"}
ALLOWED_DESIG = {"市指定", "町指定", "村指定", "区指定"}
NAV_PAT = re.compile(r"(ページ|一覧|メニュー|サイトマップ|お問い合わせ|ホーム|こちら|PDF|ダウンロード|Copyright|検索)")

root = os.path.expanduser("~/bunkazai")
total = 0
for pref, en in PREFS.items():
    seen = set()
    rows = []
    suspicious = []
    for f in sorted(glob.glob(f"{root}/pipeline/out/{pref}/*.jsonl")):
        for line in open(f):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            assert r["pref"] == pref, (f, r.get("pref"))
            cat = CAT_MAP.get(r["category"], r["category"])
            if cat not in ALLOWED_CAT:
                sys.exit(f"bad category {r['category']} in {f}")
            r["category"] = cat
            if r["designation"] not in ALLOWED_DESIG:
                sys.exit(f"bad designation {r['designation']} in {f}")
            name = (r.get("name") or "").strip()
            if not name:
                sys.exit(f"empty name in {f}")
            if NAV_PAT.search(name) and len(name) < 25:
                suspicious.append((r["municipality"], name))
            key = json.dumps(r, ensure_ascii=False, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            rows.append(r)
    out = f"{root}/data/{en}.jsonl"
    with open(out, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    total += len(rows)
    print(f"{pref}: {len(rows)} rows -> data/{en}.jsonl; suspicious names: {len(suspicious)}")
    for m, n in suspicious[:15]:
        print(f"   ? {m}: {n}")
print("TOTAL:", total)
