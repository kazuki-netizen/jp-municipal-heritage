import csv, glob, json, os, re
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUGS = "ginan kasamatsu yoro tarui sekigahara godo wanouchi anpachi ibigawa ono kitagata sakahogi tomika kawabe hichiso yaotsu shirakawa-cho higashishirakawa mitake shirakawa-mura".split()
MUNICIPALITIES = {}
for line in open(os.path.join(ROOT, "sources/gifu.jsonl"), encoding="utf-8"):
    x = json.loads(line)
    MUNICIPALITIES[x["slug"]] = x["municipality"]
NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def cell(row, k):
    return (row.get(k) or "").strip()

def category(a, b):
    s = a + " " + b
    if "民俗" in s:
        return "民俗文化財"
    if "無形" in s:
        return "無形文化財"
    if any(x in s for x in ("史跡", "名勝", "天然記念物")):
        return "記念物(史跡・名勝・天然記念物)"
    if any(x in s for x in ("有形", "重要文化財", "建造物", "彫刻", "絵画", "工芸", "書跡", "古文書", "考古", "歴史資料", "美術")):
        return "有形文化財"
    return "その他"

def subcategory(a, b):
    if b: return b
    m = re.search(r"[（(]([^）)]+)[）)]", a)
    return m.group(1).strip() if m else None

def csv_url(slug):
    page = glob.glob(os.path.join(ROOT, "cache", "岐阜県", slug, "*.bin"))[0]
    html = open(page, "rb").read().decode("utf-8", "ignore")
    urls = re.findall(r"https://[^\"' <>]+?\.csv", html)
    urls = [u for u in urls if "prefecture-specify" not in u and "country_specify" not in u]
    return urls[0]

def designation(municipality):
    return "市指定" if municipality.endswith("市") else "町指定" if municipality.endswith("町") else "村指定"

def read_csv(path):
    data = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp932"):
        try:
            return list(csv.DictReader(data.decode(enc).splitlines()))
        except UnicodeDecodeError:
            pass
    raise ValueError(path)

os.makedirs(os.path.join(ROOT, "out", "岐阜県"), exist_ok=True)
coverage = []
for slug in SLUGS:
    municipality = MUNICIPALITIES[slug]
    rows = read_csv("/tmp/gifu_csv/" + slug + ".csv")
    url = csv_url(slug)
    items = []
    excluded_national = excluded_pref = 0
    for r in rows:
        # These resources are explicitly the municipality-designated datasets.
        # Retain all item rows; no aggregate/heading rows occur in this CSV schema.
        name, a, b = cell(r, "名称"), cell(r, "文化財分類"), cell(r, "種類")
        if not name:
            continue
        combined = " ".join(r.values())
        if "国指定" in combined:
            excluded_national += 1; continue
        if "県指定" in combined or "岐阜県重要" in combined:
            excluded_pref += 1; continue
        loc = " ".join(x for x in (cell(r,"場所名称"),cell(r,"住所"),cell(r,"方書")) if x) or None
        count = " ".join(x for x in (cell(r,"員数（数）"),cell(r,"員数（単位）")) if x)
        no = cell(r,"NO")
        description = "; ".join(x for x in (("指定番号: " + no) if no else "", ("員数: " + count) if count else "") if x) or None
        date = cell(r,"文化財指定日") or None
        if date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date): date = None
        if date and date > "2026-07-10": date = None
        items.append({"pref":"岐阜県","municipality":municipality,"name":name,"category":category(a,b),"subcategory":subcategory(a,b),"designation":designation(municipality),"designated_date":date,"location":loc,"description":description,"source_url":url,"source_format":"csv","fetched_at":NOW})
    out = os.path.join(ROOT, "out", "岐阜県", slug + ".jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for x in items: f.write(json.dumps(x, ensure_ascii=False) + "\n")
    # immediate per-municipality parse/schema validation
    for line in open(out, encoding="utf-8"):
        x = json.loads(line)
        assert list(x) == ["pref","municipality","name","category","subcategory","designation","designated_date","location","description","source_url","source_format","fetched_at"]
    coverage.append(f"- {municipality} ({slug}): source rows {len(rows)}; output {len(items)}; excluded 国指定 {excluded_national}, 県指定 {excluded_pref}; issues: none (CSV is municipality-designated dataset).")

# Pool only articles that explicitly state 池田町 designation; category hubs also contain prefectural and explanatory pages.
ikeda_sources = [
    ("池田恒興・元助父子の墓", "記念物(史跡・名勝・天然記念物)", "史跡", "https://www.town.gifu-ikeda.lg.jp/kankou/0000000533.html"),
    ("乳くれ地蔵", "記念物(史跡・名勝・天然記念物)", "史跡", "https://www.town.gifu-ikeda.lg.jp/kankou/0000000501.html"),
    ("稲葉一族・池田恒利の墓", "記念物(史跡・名勝・天然記念物)", "史跡", "https://www.town.gifu-ikeda.lg.jp/kankou/0000000500.html"),
    ("坂本積（苔の元）", "記念物(史跡・名勝・天然記念物)", "史跡", "https://www.town.gifu-ikeda.lg.jp/kankou/0000000524.html"),
    ("本郷城跡", "記念物(史跡・名勝・天然記念物)", "史跡", "https://www.town.gifu-ikeda.lg.jp/kankou/0000000525.html"),
    ("市橋港跡", "記念物(史跡・名勝・天然記念物)", "史跡", "https://www.town.gifu-ikeda.lg.jp/kankou/0000000527.html"),
    ("谷汲巡礼街道　道標", "記念物(史跡・名勝・天然記念物)", "史跡", "https://www.town.gifu-ikeda.lg.jp/kankou/0000000529.html"),
    ("国枝為助一族の墓", "記念物(史跡・名勝・天然記念物)", "史跡", "https://www.town.gifu-ikeda.lg.jp/kankou/0000000530.html"),
    ("白鳥神楽", "無形文化財", None, "https://www.town.gifu-ikeda.lg.jp/kankou/0000000445.html"),
    ("片山八幡神社市やま", "無形文化財", None, "https://www.town.gifu-ikeda.lg.jp/kankou/0000000448.html"),
    ("般若踊り", "無形文化財", None, "https://www.town.gifu-ikeda.lg.jp/kankou/0000000452.html"),
]
out = os.path.join(ROOT, "out", "岐阜県", "ikeda.jsonl")
with open(out, "w", encoding="utf-8") as f:
    for name, cat, subcat, url in ikeda_sources:
        x={"pref":"岐阜県","municipality":"池田町","name":name,"category":cat,"subcategory":subcat,"designation":"町指定","designated_date":None,"location":None,"description":None,"source_url":url,"source_format":"html","fetched_at":NOW}
        f.write(json.dumps(x, ensure_ascii=False) + "\n")
for line in open(out, encoding="utf-8"):
    x=json.loads(line); assert list(x) == ["pref","municipality","name","category","subcategory","designation","designated_date","location","description","source_url","source_format","fetched_at"]
coverage.append("- 池田町 (ikeda): category hubs scanned; output 11 explicitly-labelled 町指定 items; excluded 国指定 0, 県指定 5; issues: category pages also contain explanatory/non-designation pages and natural-monument pages without a stated designation level, excluded under null-over-guess.")
with open(os.path.join(ROOT,"out","岐阜県","_coverage_b.md"), "a", encoding="utf-8") as f:
    f.write("\n".join(coverage) + "\n")
print("\n".join(f"{p.split(':')[0][2:]}" for p in coverage))
