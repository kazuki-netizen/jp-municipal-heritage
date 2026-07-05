import csv
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser
from urllib import robotparser


JST = timezone(timedelta(hours=9))


def now_jst():
    return datetime.now(JST).replace(microsecond=0).isoformat()


def clean_text(value):
    if value is None:
        return None
    value = html.unescape(str(value))
    value = value.replace("\u3000", " ")
    value = re.sub(r"[\r\n\t]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def major_category(subcategory):
    s = clean_text(subcategory) or ""
    if any(x in s for x in ("史跡", "名勝", "天然記念物", "記念物")):
        return "記念物(史跡・名勝・天然記念物)"
    if any(x in s for x in ("民俗", "風俗慣習", "民俗芸能")):
        return "民俗文化財"
    if "無形" in s:
        return "無形文化財"
    if any(x in s for x in ("選定保存技術", "保存技術")):
        return "その他"
    return "有形文化財"


ERA_START = {
    "明治": 1868,
    "大正": 1912,
    "昭和": 1926,
    "平成": 1989,
    "令和": 2019,
}


def _era_year(era, year_text):
    year = 1 if year_text == "元" else int(year_text)
    return ERA_START[era] + year - 1


def parse_date(value):
    s = clean_text(value)
    if not s:
        return None
    s = s.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    s = s.replace("（", "(").replace("）", ")")
    m = re.search(r"(明治|大正|昭和|平成|令和)\s*([0-9]+|元)\s*年\s*([0-9]{1,2})\s*月\s*([0-9]{1,2})\s*日", s)
    if m:
        y = _era_year(m.group(1), m.group(2))
        mo = int(m.group(3))
        d = int(m.group(4))
        try:
            return datetime(y, mo, d).date().isoformat()
        except ValueError:
            return None
    short_eras = {"明": "明治", "大": "大正", "昭": "昭和", "平": "平成", "令": "令和"}
    m = re.search(r"(明|大|昭|平|令)\s*([0-9]+|元)\s*[./]\s*([0-9]{1,2})\s*[./]\s*([0-9]{1,2})", s)
    if m:
        y = _era_year(short_eras[m.group(1)], m.group(2))
        mo = int(m.group(3))
        d = int(m.group(4))
        try:
            return datetime(y, mo, d).date().isoformat()
        except ValueError:
            return None
    m = re.search(r"(明治|大正|昭和|平成|令和)\s*([0-9]+|元)\s*[./]\s*([0-9]{1,2})\s*[./]\s*([0-9]{1,2})", s)
    if m:
        y = _era_year(m.group(1), m.group(2))
        mo = int(m.group(3))
        d = int(m.group(4))
        try:
            return datetime(y, mo, d).date().isoformat()
        except ValueError:
            return None
    m = re.search(r"([0-9]{4})\s*年\s*([0-9]{1,2})\s*月\s*([0-9]{1,2})\s*日", s)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date().isoformat()
        except ValueError:
            return None
    m = re.search(r"([0-9]{4})[-/.]([0-9]{1,2})[-/.]([0-9]{1,2})", s)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date().isoformat()
        except ValueError:
            return None
    return None


def make_row(municipality, name, subcategory, designation, date, location, description, source_url, source_format, fetched_at=None):
    subcategory = clean_text(subcategory)
    return {
        "pref": "山形県",
        "municipality": municipality,
        "name": clean_text(name),
        "category": major_category(subcategory),
        "subcategory": subcategory,
        "designation": designation,
        "designated_date": parse_date(date) if date else None,
        "location": clean_text(location),
        "description": clean_text(description),
        "source_url": source_url,
        "source_format": source_format,
        "fetched_at": fetched_at or now_jst(),
    }


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            if not row.get("name"):
                raise ValueError(f"missing name in {path}: {row}")
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def validate_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            json.loads(line)


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag in ("br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1
        if tag in ("p", "div", "li", "tr", "h1", "h2", "h3", "h4"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    def text(self):
        text = "".join(self.parts)
        lines = [clean_text(line) for line in text.splitlines()]
        return "\n".join(line for line in lines if line)


def html_text(raw):
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    p = TextExtractor()
    p.feed(raw)
    return p.text()


class TableExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self._table = None
        self._row = None
        self._cell = None
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        if tag == "table":
            self._table = []
        elif self._table is not None and tag == "tr":
            self._row = []
        elif self._row is not None and tag in ("td", "th"):
            self._cell = []
        elif self._cell is not None and tag == "br":
            self._cell.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(clean_text("".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None and self._table is not None:
            if any(cell for cell in self._row):
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            if self._table:
                self.tables.append(self._table)
            self._table = None

    def handle_data(self, data):
        if not self._skip and self._cell is not None:
            self._cell.append(data)


def html_tables(raw):
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    p = TableExtractor()
    p.feed(raw)
    return p.tables


class PoliteFetcher:
    def __init__(self, cache_dir="data/yamagata_work/cache", user_agent="jp-municipal-heritage-research/1.0"):
        self.cache_dir = cache_dir
        self.user_agent = user_agent
        self.last_request = {}
        self.counts = {}
        self.robots = {}
        os.makedirs(cache_dir, exist_ok=True)

    def _domain(self, url):
        return urllib.parse.urlparse(url).netloc

    def _cache_path(self, url):
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", url)
        return os.path.join(self.cache_dir, safe[:220])

    def _sleep(self, domain):
        last = self.last_request.get(domain)
        if last is not None:
            wait = 2.1 - (time.time() - last)
            if wait > 0:
                time.sleep(wait)

    def _robot(self, url):
        parsed = urllib.parse.urlparse(url)
        root = f"{parsed.scheme}://{parsed.netloc}"
        if root in self.robots:
            return self.robots[root]
        robots_url = urllib.parse.urljoin(root, "/robots.txt")
        rp = robotparser.RobotFileParser()
        rp.set_url(robots_url)
        try:
            self._sleep(parsed.netloc)
            with urllib.request.urlopen(urllib.request.Request(robots_url, headers={"User-Agent": self.user_agent}), timeout=20) as res:
                data = res.read().decode("utf-8", errors="replace").splitlines()
            rp.parse(data)
            self.last_request[parsed.netloc] = time.time()
        except Exception:
            rp.parse([])
        self.robots[root] = rp
        return rp

    def fetch(self, url, binary=False, refresh=False):
        domain = self._domain(url)
        path = self._cache_path(url)
        if not refresh and os.path.exists(path):
            mode = "rb" if binary else "r"
            with open(path, mode, encoding=None if binary else "utf-8", errors=None if binary else "replace") as f:
                return f.read()
        rp = self._robot(url)
        if not rp.can_fetch(self.user_agent, url) or not rp.can_fetch("*", url):
            raise RuntimeError(f"robots disallow: {url}")
        self.counts[domain] = self.counts.get(domain, 0) + 1
        if self.counts[domain] > 40:
            raise RuntimeError(f"request cap exceeded for {domain}")
        self._sleep(domain)
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with urllib.request.urlopen(req, timeout=30) as res:
            data = res.read()
        self.last_request[domain] = time.time()
        with open(path, "wb") as f:
            f.write(data)
        if binary:
            return data
        enc = "utf-8"
        ctype = res.headers.get_content_charset()
        if ctype:
            enc = ctype
        else:
            head = data[:4096].decode("ascii", errors="ignore")
            m = re.search(r"charset=[\"']?([A-Za-z0-9._-]+)", head, re.I)
            if m:
                enc = m.group(1)
        return data.decode(enc, errors="replace")


def read_csv_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        validate_jsonl(arg)
        print(f"ok {arg}")
