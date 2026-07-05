import os
import re
import subprocess
import sys
from collections import Counter

sys.path.append("data/yamagata_work")
from collect_utils import PoliteFetcher, clean_text, make_row, validate_jsonl, write_jsonl


SOURCE_URL = "https://www.city.nagai.yamagata.jp/material/files/group/36/chiikikeikaku_siryouhen.pdf"
PDF_PATH = "data/yamagata_work/nagai_chiikikeikaku_siryouhen.pdf"
TXT_PATH = "data/yamagata_work/nagai_chiikikeikaku_siryouhen.txt"

SUBCATEGORIES = [
    "動物・植物・地質鉱物",
    "美術工芸品(書跡･典籍)",
    "美術工芸品(考古資料)",
    "美術工芸品(歴史資料)",
    "美術工芸品(古文書)",
    "美術工芸品(彫刻)",
    "美術工芸品(絵画)",
    "無形の民俗文化財",
    "工芸技術",
    "建造物",
    "遺跡",
]


def ensure_text():
    if not os.path.exists(PDF_PATH):
        data = PoliteFetcher().fetch(SOURCE_URL, binary=True)
        with open(PDF_PATH, "wb") as f:
            f.write(data)
    if not os.path.exists(TXT_PATH):
        subprocess.run(["pdftotext", "-layout", PDF_PATH, TXT_PATH], check=True)


def split_row(line, pending):
    line = re.sub(r"\s+", " ", line).strip()
    m = re.match(r"^(\d+)\s+市指定\s+(有形文化財|無形文化財|民俗文化財|記念物)\s+(.+)$", line)
    if not m:
        return None

    number = int(m.group(1))
    major = m.group(2)
    rest = m.group(3)

    date_match = re.search(r"(明治|大正|昭和|平成|令和)\d+年\d+月\d+日$", rest)
    if not date_match:
        raise ValueError(f"no date in row {number}: {line}")
    date = date_match.group(0)
    rest = rest[: date_match.start()].strip()

    subcat = None
    for candidate in SUBCATEGORIES:
        if rest.startswith(candidate):
            subcat = candidate
            rest = rest[len(candidate) :].strip()
            break
    if not subcat:
        raise ValueError(f"no subcategory in row {number}: {line}")

    cols = [clean_text(x) for x in re.split(r"\s{2,}", rest) if clean_text(x)]
    if len(cols) < 2:
        cols = [clean_text(x) for x in rest.rsplit(" ", 1)]
    location = cols[-1]
    name = clean_text(" ".join(cols[:-1]))
    if pending:
        name = clean_text(f"{pending} {name}")

    return {
        "number": number,
        "name": name,
        "subcategory": f"{major}（{subcat}）",
        "location": location,
        "date": date,
    }


def main():
    ensure_text()
    text = open(TXT_PATH, encoding="utf-8").read()
    start = text.index("40 市指定")
    end = text.index("長井市未指定文化財一覧", start)
    section = text[start:end]

    rows = []
    pending = None
    fetched_at = None
    from collect_utils import now_jst

    fetched_at = now_jst()
    for raw_line in section.splitlines():
        line = raw_line.rstrip()
        if not clean_text(line):
            continue
        if re.match(r"^\s*\d+\s+市指定\s+", line):
            parsed = split_row(line, pending)
            pending = None
            if parsed:
                rows.append(
                    make_row(
                        "長井市",
                        parsed["name"],
                        parsed["subcategory"],
                        "市指定",
                        parsed["date"],
                        parsed["location"],
                        None,
                        SOURCE_URL,
                        "pdf",
                        fetched_at,
                    )
                )
            continue

        cleaned = clean_text(line)
        if cleaned and not any(skip in cleaned for skip in ("選定", "番号", "区分", "種 別", "名称", "所在地")):
            pending = cleaned

    out = "data/yamagata_parts/nagai.jsonl"
    write_jsonl(out, rows)
    validate_jsonl(out)
    print(out, len(rows))
    print(Counter(row["category"] for row in rows))
    print(Counter(row["subcategory"] for row in rows))
    if len(rows) != 80:
        raise SystemExit(f"expected 80 rows, got {len(rows)}")


if __name__ == "__main__":
    main()
