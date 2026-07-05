import csv
import os
import re
import subprocess
from collections import defaultdict

from collect_utils import clean_text, make_row, now_jst, validate_jsonl, write_jsonl


BASE_URL = "https://www.city.tsuruoka.lg.jp/bunka/rekishi/shitei-bunka-ichiran.files/"
PDF_DIR = "data/yamagata_work/tsuruoka_pdfs"
SOURCE_PAGE = "https://www.city.tsuruoka.lg.jp/bunka/rekishi/shitei-bunka-ichiran.html"

SPECS = [
    ("01_structures.pdf", "建造物", True, 11),
    ("02_paintings.pdf", "絵画", True, 30),
    ("03_sculptures.pdf", "彫刻", True, 62),
    ("04_crafts.pdf", "工芸品", True, 52),
    ("05_calligraphies.pdf", "書跡", True, 29),
    ("06_books.pdf", "典籍", True, 3),
    ("07_documents.pdf", "古文書", True, 41),
    ("08_archeological_artifacts.pdf", "考古資料", True, 14),
    ("09_historical_materials.pdf", "歴史資料", True, 45),
    ("10_intangible_folk_cultural_properties.pdf", "無形民俗文化財", False, 8),
    ("11_tangible_folk_cultural_properties.pdf", "有形民俗文化財", True, 15),
    ("13_historic_sites.pdf", "史跡", False, 24),
    ("12_places_of_scenic_beauty.pdf", "名勝", False, 0),
    ("14_natural_monuments.pdf", "天然記念物", False, 26),
]

STATUS = {"国宝", "国特別", "国指定", "国重文", "県指定", "市指定"}
REGIONS = {"鶴岡", "藤島", "羽黒", "櫛引", "朝日", "温海", "庄内町"}


def tsv_words(path):
    data = subprocess.check_output(["pdftotext", "-tsv", path, "-"], text=True)
    rows = csv.DictReader(data.splitlines(), delimiter="\t")
    words = []
    for row in rows:
        if row["level"] != "5":
            continue
        text = row["text"].strip()
        if not text or text.startswith("###"):
            continue
        words.append({
            "page": int(row["page_num"]),
            "x": float(row["left"]),
            "y": float(row["top"]),
            "w": float(row["width"]),
            "text": text,
        })
    return words


def same_line(words, page, y, x1, x2, tol=3.5):
    return [
        w for w in words
        if w["page"] == page and x1 <= w["x"] <= x2 and abs(w["y"] - y) <= tol
    ]


def find_anchors(words):
    anchors = []
    for w in words:
        if not re.fullmatch(r"\d{1,3}", w["text"]):
            continue
        if not (60 <= w["x"] <= 100 and w["y"] > 70):
            continue
        stat = same_line(words, w["page"], w["y"], 105, 150)
        stat_text = "".join(s["text"] for s in sorted(stat, key=lambda x: x["x"]))
        if stat_text not in STATUS:
            continue
        date_words = same_line(words, w["page"], w["y"], 145, 220)
        date = " ".join(s["text"] for s in sorted(date_words, key=lambda x: x["x"]))
        anchors.append({
            "page": w["page"],
            "no": int(w["text"]),
            "y": w["y"],
            "status": stat_text,
            "date": date,
        })
    return sorted(anchors, key=lambda a: (a["page"], a["y"], a["no"]))


def line_key(y):
    return round(y / 4) * 4


def join_parts(parts):
    s = clean_text(" ".join(p for p in parts if p))
    if not s:
        return None
    s = re.sub(r"\s+", " ", s).strip()
    return s


def split_item_words(item_words, has_count):
    lines = defaultdict(list)
    for w in item_words:
        if w["x"] < 220:
            continue
        if w["text"] in {"指定文化財目録", "指定文化財一覧", "番号", "区分", "指定年月日", "名称", "名", "称", "員数", "所在地域", "鶴岡市教育委員会"}:
            continue
        lines[line_key(w["y"])].append(w)

    name_parts, count_parts, region_parts = [], [], []
    for _, line_words in sorted(lines.items()):
        line_words = sorted(line_words, key=lambda x: x["x"])
        name_line, count_line, region_line = [], [], []
        for w in line_words:
            x = w["x"]
            t = w["text"]
            if has_count:
                if x >= 510:
                    region_line.append(t)
                elif x >= 455:
                    count_line.append(t)
                else:
                    name_line.append(t)
            else:
                if x >= 450 or t in REGIONS:
                    region_line.append(t)
                else:
                    name_line.append(t)
        if name_line:
            name_parts.append(" ".join(name_line))
        if count_line:
            count_parts.append(" ".join(count_line))
        if region_line:
            region_parts.append(" ".join(region_line))
    return join_parts(name_parts), join_parts(count_parts), join_parts(region_parts)


def parse_pdf(filename, subcategory, has_count):
    path = os.path.join(PDF_DIR, filename)
    words = tsv_words(path)
    anchors = find_anchors(words)
    by_page = defaultdict(list)
    for a in anchors:
        by_page[a["page"]].append(a)

    parsed = []
    for page, page_anchors in by_page.items():
        page_words = [w for w in words if w["page"] == page]
        page_anchors = sorted(page_anchors, key=lambda a: a["y"])
        for idx, anchor in enumerate(page_anchors):
            prev_y = page_anchors[idx - 1]["y"] if idx else 60
            next_y = page_anchors[idx + 1]["y"] if idx + 1 < len(page_anchors) else 830
            top = (prev_y + anchor["y"]) / 2
            bottom = (anchor["y"] + next_y) / 2
            item_words = [w for w in page_words if top <= w["y"] < bottom]
            name, count, region = split_item_words(item_words, has_count)
            parsed.append({
                "no": anchor["no"],
                "status": anchor["status"],
                "date": anchor["date"],
                "name": name,
                "count": count,
                "region": region,
                "subcategory": subcategory,
                "source_url": BASE_URL + filename,
            })
    return sorted(parsed, key=lambda r: r["no"])


def main():
    fetched = now_jst()
    all_rows = []
    for filename, subcategory, has_count, expected in SPECS:
        parsed = parse_pdf(filename, subcategory, has_count)
        city = [r for r in parsed if r["status"] == "市指定"]
        if len(city) != expected:
            raise SystemExit(f"{filename}: expected {expected} city rows, got {len(city)}")
        for item in city:
            desc = f"員数: {item['count']}" if item["count"] else None
            all_rows.append(make_row(
                "鶴岡市",
                item["name"],
                item["subcategory"],
                "市指定",
                item["date"],
                item["region"],
                desc,
                item["source_url"],
                "pdf",
                fetched,
            ))
    if len(all_rows) != 360:
        raise SystemExit(f"expected 360 total, got {len(all_rows)}")
    write_jsonl("data/yamagata_parts/tsuruoka.jsonl", all_rows)
    validate_jsonl("data/yamagata_parts/tsuruoka.jsonl")
    print(len(all_rows))


if __name__ == "__main__":
    main()
