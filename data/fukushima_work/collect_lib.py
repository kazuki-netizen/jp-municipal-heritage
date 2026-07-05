import csv
import datetime as _dt
import html
import json
import re
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PARTS = ROOT / "data" / "fukushima_parts"
WORK = ROOT / "data" / "fukushima_work"
PDF_QUEUE = ROOT / "data" / "pdf_queue"

PARTS.mkdir(exist_ok=True)
WORK.mkdir(exist_ok=True)
PDF_QUEUE.mkdir(exist_ok=True)

FETCHED_AT = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds")
USER_AGENT = "CodexBot/1.0 (+GET-only cultural-property research)"

_ROBOTS = {}
_LAST_FETCH = {}
_COUNT = {}

GENGO = {"明治": 1867, "大正": 1911, "昭和": 1925, "平成": 1988, "令和": 2018}


def clean(s):
    if s is None:
        return None
    s = html.unescape(str(s))
    s = re.sub(r"[\u00a0\u3000]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or None


def domain(url):
    return urllib.parse.urlparse(url).netloc


def decode(data, ctype=""):
    m = re.search(r"charset=([\w\-]+)", ctype or "", re.I)
    encs = [m.group(1)] if m else []
    head = data[:4096].decode("ascii", "ignore")
    m = re.search(r"charset=[\"']?([\w\-]+)", head, re.I)
    if m:
        encs.append(m.group(1))
    encs += ["utf-8-sig", "utf-8", "cp932", "shift_jis", "euc-jp"]
    for enc in encs:
        try:
            return data.decode(enc)
        except Exception:
            pass
    return data.decode("utf-8", "replace")


def can_fetch(url):
    parsed = urllib.parse.urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    if parsed.netloc not in _ROBOTS:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urllib.parse.urljoin(base, "/robots.txt"))
        try:
            req = urllib.request.Request(rp.url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20) as r:
                raw = r.read()
                ctype = r.headers.get("content-type", "")
            rp.parse(decode(raw, ctype).splitlines())
        except Exception:
            rp.parse([])
        _ROBOTS[parsed.netloc] = rp
    return _ROBOTS[parsed.netloc].can_fetch(USER_AGENT, url)


def fetch(url, dest=None, binary=False, max_per_domain=40):
    host = domain(url)
    if not can_fetch(url):
        raise RuntimeError(f"robots disallow: {url}")
    _COUNT[host] = _COUNT.get(host, 0) + 1
    if _COUNT[host] > max_per_domain:
        raise RuntimeError(f"domain request cap exceeded for {host}: {url}")
    last = _LAST_FETCH.get(host)
    if last is not None:
        delay = 2.1 - (time.monotonic() - last)
        if delay > 0:
            time.sleep(delay)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=50) as r:
        data = r.read()
        ctype = r.headers.get("content-type", "")
    _LAST_FETCH[host] = time.monotonic()
    if dest:
        Path(dest).write_bytes(data)
    if binary:
        return data, ctype
    return decode(data, ctype), ctype


def wareki(s):
    if not s:
        return None
    t = str(s)
    t = t.replace(" ", "").replace("\u3000", "")
    t = t.replace("（", "(").replace("）", ")")
    t = re.sub(r"((?:明治|大正|昭和|平成|令和)(?:元|\d+))\(\d{4}\)", r"\1", t)
    m = re.search(r"(明治|大正|昭和|平成|令和)(元|\d+)年(\d{1,2})月(\d{1,2})日", t)
    if m:
        g, y, mo, d = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
        y = 1 if y == "元" else int(y)
        return f"{GENGO[g] + y:04d}-{mo:02d}-{d:02d}"
    m = re.search(r"(明治|大正|昭和|平成|令和)(元|\d+)[.年/](\d{1,2})[.月/](\d{1,2})", t)
    if m:
        g, y, mo, d = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
        y = 1 if y == "元" else int(y)
        return f"{GENGO[g] + y:04d}-{mo:02d}-{d:02d}"
    m = re.search(r"([MTSHR])\.?(\d+)[.年/](\d{1,2})[.月/](\d{1,2})", t, re.I)
    if m:
        base = {"M": 1867, "T": 1911, "S": 1925, "H": 1988, "R": 2018}[m.group(1).upper()]
        return f"{base + int(m.group(2)):04d}-{int(m.group(3)):02d}-{int(m.group(4)):02d}"
    m = re.search(r"(\d{4})[年./-](\d{1,2})[月./-](\d{1,2})日?", t)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return None


def normalize_category(subcategory):
    c = subcategory or ""
    if any(k in c for k in ["史跡", "名勝", "天然記念物", "記念物", "植物", "池沼", "古墳"]):
        return "記念物(史跡・名勝・天然記念物)"
    if "無形民俗" in c or "民俗芸能" in c or "風俗慣習" in c:
        return "民俗文化財"
    if "有形民俗" in c or "民俗" in c:
        return "民俗文化財"
    if "無形" in c:
        return "無形文化財"
    if any(k in c for k in ["有形", "建造物", "建造", "彫刻", "工芸", "絵画", "書跡", "典籍", "古文書", "考古", "歴史資料"]):
        return "有形文化財"
    return "その他"


def row(municipality, name, subcategory, designation, date, location, source_url, source_format, description=None):
    return {
        "pref": "福島県",
        "municipality": municipality,
        "name": clean(name),
        "category": normalize_category(subcategory),
        "subcategory": clean(subcategory),
        "designation": designation,
        "designated_date": date if date else None,
        "location": clean(location),
        "description": clean(description),
        "source_url": source_url,
        "source_format": source_format,
        "fetched_at": FETCHED_AT,
    }


def validate_jsonl(path):
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            json.loads(line)


def write_jsonl(romaji, rows):
    path = PARTS / f"{romaji}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    validate_jsonl(path)
    return path


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def pdftotext(path, layout=True):
    args = ["pdftotext"]
    if layout:
        args.append("-layout")
    args += [str(path), "-"]
    return subprocess.check_output(args, text=True, errors="replace")


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def strip_tags(fragment):
    text = re.sub(r"<(br|BR)\s*/?>", "\n", fragment)
    text = re.sub(r"<[^>]+>", " ", text)
    return clean(text)


def html_tables(text):
    tables = []
    for table in re.findall(r"<table\b.*?</table>", text, flags=re.S | re.I):
        rows = []
        for tr in re.findall(r"<tr\b.*?</tr>", table, flags=re.S | re.I):
            cells = []
            for c in re.findall(r"<t[dh]\b.*?</t[dh]>", tr, flags=re.S | re.I):
                cells.append(strip_tags(c))
            cells = [c for c in cells if c is not None]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables
