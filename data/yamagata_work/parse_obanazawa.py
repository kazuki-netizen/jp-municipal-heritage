import re
import sys
from collections import Counter

sys.path.append("data/yamagata_work")
from collect_utils import PoliteFetcher, clean_text, html_tables, html_text, make_row, validate_jsonl, write_jsonl


SOURCE_URL = "https://www.city.obanazawa.yamagata.jp/kosodate-bunka/rekishi-bunka/bunkazai-iseki/566"
HEADING_MAP = {
    "【建造物の部】": "建造物",
    "【絵画の部】": "絵画",
    "【彫刻の部】": "彫刻",
    "【史跡の部】": "史跡",
    "【工芸の部】": "工芸品",
    "【古文書の部】": "古文書",
    "【考古資料の部】": "考古資料",
    "【天然記念物】": "天然記念物",
    "【無形文化財】": "無形文化財",
}


def parse_field(line):
    m = re.match(r"^(所在地|員数|数|指定年月日)\s*[:：]\s*(.+)$", line)
    if m:
        return m.group(1), clean_text(m.group(2))
    return None, None


def desc_from_count(count, location=None):
    parts = []
    if count:
        parts.append(f"員数: {count}")
    if location and "※" in location:
        parts.append("※芭蕉、清風歴史資料館に寄託")
    return "; ".join(parts) if parts else None


def parse_list_rows(raw, fetched_at):
    lines = [clean_text(line) for line in html_text(raw).splitlines()]
    lines = [line for line in lines if line]
    start = lines.index("市指定文化財")
    end = lines.index("文化財件数")

    rows = []
    current_subcategory = None
    current_name = None
    fields = {}
    skip_table = False
    for line in lines[start + 1 : end]:
        if line in HEADING_MAP:
            current_subcategory = HEADING_MAP[line]
            current_name = None
            fields = {}
            skip_table = current_subcategory == "古文書"
            continue
        if skip_table or line in ("資料名", "所在地", "員数", "指定年月日", "※芭蕉、清風歴史資料館に寄託"):
            continue
        key, value = parse_field(line)
        if key:
            fields[key] = value
            if key == "指定年月日" and current_name:
                count = fields.get("員数") or fields.get("数")
                rows.append(
                    make_row(
                        "尾花沢市",
                        current_name,
                        current_subcategory,
                        "市指定",
                        value,
                        fields.get("所在地"),
                        desc_from_count(count),
                        SOURCE_URL,
                        "html",
                        fetched_at,
                    )
                )
                current_name = None
                fields = {}
            continue
        if current_subcategory:
            current_name = line
            fields = {}
    return rows


def parse_document_table(raw, fetched_at):
    table = html_tables(raw)[0]
    rows = []
    for r in table[1:]:
        if len(r) < 4:
            continue
        name, location, count, date = r[:4]
        loc = clean_text((location or "").replace("※", "").strip())
        rows.append(
            make_row(
                "尾花沢市",
                name,
                "古文書",
                "市指定",
                date,
                loc,
                desc_from_count(count, location),
                SOURCE_URL,
                "html",
                fetched_at,
            )
        )
    return rows


def main():
    raw = PoliteFetcher().fetch(SOURCE_URL)
    from collect_utils import now_jst

    fetched_at = now_jst()
    rows = parse_list_rows(raw, fetched_at) + parse_document_table(raw, fetched_at)
    out = "data/yamagata_parts/obanazawa.jsonl"
    write_jsonl(out, rows)
    validate_jsonl(out)
    print(out, len(rows))
    print(Counter(row["category"] for row in rows))
    print(Counter(row["subcategory"] for row in rows))
    if len(rows) != 34:
        raise SystemExit(f"expected 34 rows, got {len(rows)}")


if __name__ == "__main__":
    main()
