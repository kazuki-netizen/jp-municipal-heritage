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

try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    BeautifulSoup = None


ROOT = Path(__file__).resolve().parents[2]
PARTS = ROOT / "data" / "akita_parts"
WORK = ROOT / "data" / "akita_work"
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


def domain(url):
    return urllib.parse.urlparse(url).netloc


def can_fetch(url):
    parsed = urllib.parse.urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    if parsed.netloc not in _ROBOTS:
        rp = urllib.robotparser.RobotFileParser()
        robots_url = urllib.parse.urljoin(base, "/robots.txt")
        rp.set_url(robots_url)
        try:
            req = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
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
    with urllib.request.urlopen(req, timeout=40) as r:
        data = r.read()
        ctype = r.headers.get("content-type", "")
    _LAST_FETCH[host] = time.monotonic()
    if dest:
        Path(dest).write_bytes(data)
    if binary:
        return data, ctype
    return decode(data, ctype), ctype


def decode(data, ctype=""):
    m = re.search(r"charset=([\w\-]+)", ctype or "", re.I)
    encs = [m.group(1)] if m else []
    head = data[:4096].decode("ascii", "ignore")
    m = re.search(r"charset=[\"']?([\w\-]+)", head, re.I)
    if m:
        encs.append(m.group(1))
    encs += ["utf-8-sig", "utf-8", "cp932", "euc-jp", "shift_jis"]
    for enc in encs:
        try:
            return data.decode(enc)
        except Exception:
            continue
    return data.decode("utf-8", "replace")


def soup_from_file(path):
    if BeautifulSoup is None:
        raise RuntimeError("BeautifulSoup is not installed in this environment")
    data = Path(path).read_bytes()
    return BeautifulSoup(decode(data), "html.parser")


def soup_from_url(url, local_name=None):
    if BeautifulSoup is None:
        raise RuntimeError("BeautifulSoup is not installed in this environment")
    text, _ = fetch(url)
    if local_name:
        (WORK / local_name).write_text(text, encoding="utf-8")
    return BeautifulSoup(text, "html.parser")


def clean(s):
    if s is None:
        return None
    s = html.unescape(str(s))
    s = re.sub(r"[\u00a0\u3000]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or None


def table_rows(soup):
    rows = []
    for table in soup.find_all("table"):
        trs = []
        for tr in table.find_all("tr"):
            cells = [clean(c.get_text(" ", strip=True)) for c in tr.find_all(["th", "td"])]
            cells = [c for c in cells if c is not None]
            if cells:
                trs.append(cells)
        if trs:
            rows.append(trs)
    return rows


def wareki(s):
    if not s:
        return None
    t = str(s)
    t = t.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    t = t.replace(" ", "").replace("\u3000", "")
    t = t.replace("（", "(").replace("）", ")")
    t = re.sub(r"((?:明治|大正|昭和|平成|令和)(?:元|\d+))\(\d{4}\)", r"\1", t)
    m = re.search(r"(明治|大正|昭和|平成|令和)(元|\d+)年(\d{1,2})月(\d{1,2})日", t)
    if m:
        g, y, mo, d = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
        y = 1 if y == "元" else int(y)
        return f"{GENGO[g] + y:04d}-{mo:02d}-{d:02d}"
    t = re.sub(r"[年月\.]", lambda m: {"年": "-", "月": "-", ".": "-"}[m.group(0)], t)
    m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", t)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", str(s))
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r"(明治|大正|昭和|平成|令和)(元|\d+)年(\d{1,2})月(\d{1,2})日?", t)
    if m:
        g, y, mo, d = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
        y = 1 if y == "元" else int(y)
        return f"{GENGO[g] + y:04d}-{mo:02d}-{d:02d}"
    return None


def normalize_category(subcategory):
    c = subcategory or ""
    norm = c.replace(" ", "").replace("\u3000", "")
    if any(k in norm for k in ["史跡", "名勝", "天然記念物", "記念物"]):
        return "記念物(史跡・名勝・天然記念物)"
    if "無形民俗" in norm or "民俗芸能" in norm or "風俗慣習" in norm:
        return "民俗文化財"
    if "有形民俗" in norm or "民俗" in norm:
        return "民俗文化財"
    if "無形" in norm or "工芸技術" in norm:
        return "無形文化財"
    if any(k in norm for k in ["有形", "建造物", "彫刻", "工芸", "絵画", "絵図", "書跡", "典籍", "古文書", "考古", "歴史資料"]):
        return "有形文化財"
    return "その他"


def row(municipality, name, subcategory, designation, date, location, source_url, source_format, description=None):
    return {
        "pref": "秋田県",
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


def write_jsonl(romaji, rows):
    path = PARTS / f"{romaji}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    validate_jsonl(path)
    return path


def validate_jsonl(path):
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            json.loads(line)


def download_pdf(url, name):
    dest = WORK / name
    fetch(url, dest=dest, binary=True)
    return dest


def pdftotext(path, layout=True):
    args = ["pdftotext"]
    if layout:
        args.append("-layout")
    args += [str(path), "-"]
    return subprocess.check_output(args, text=True, errors="replace")


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))
