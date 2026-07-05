import re
import sys
from collections import Counter

sys.path.append("data/yamagata_work")
from collect_utils import PoliteFetcher, clean_text, html_text, make_row, validate_jsonl, write_jsonl


SOURCE_URL = "https://www.city.tendo.yamagata.jp/tourism/history/sisiteibunkazai.html"
CATEGORY_HEADINGS = {
    "建造物",
    "絵画",
    "彫刻",
    "工芸品",
    "書跡",
    "考古資料",
    "歴史資料",
    "天然記念物",
    "民俗資料",
}
FIELD_KEYS = ("所在地", "所有者", "概要", "製作年代", "指定の区分")


def name_key(value):
    return re.sub(r"\s+", "", (value or "").replace("（", "(").replace("）", ")"))


def clean_item_name(text):
    text = clean_text(text.lstrip("・"))
    revoked = "指定解除" in text
    text = re.sub(r"\s*令和[0-9０-９]+年[0-9０-９]+月[0-9０-９]+日\s*指定解除.*$", "", text)
    text = re.sub(r"\s*令和[0-9０-９]+年[0-9０-９]+月[0-9０-９]+日\s*指定解除.*$", "", text)
    return clean_text(text), revoked


def collect_items(lines):
    items = []
    current_category = None
    started = False
    for line in lines:
        if line in CATEGORY_HEADINGS:
            current_category = line
            started = True
            continue
        if started and line.startswith("・") and current_category:
            name, revoked = clean_item_name(line)
            items.append({"name": name, "subcategory": current_category, "revoked": revoked})
            continue
        if started and items and line == items[0]["name"]:
            break
    return items


def parse_sections(lines, items):
    all_names = [item["name"] for item in items]
    positions = []
    search_start = 0
    for name in all_names:
        try:
            key = name_key(name)
            idx = next(i for i in range(search_start, len(lines)) if name_key(lines[i]) == key)
        except StopIteration:
            positions.append(None)
            continue
        positions.append(idx)
        search_start = idx + 1

    rows = []
    fetched_at = None
    from collect_utils import now_jst

    fetched_at = now_jst()
    for pos, item in zip(positions, items):
        if pos is None:
            raise ValueError(f"detail heading not found: {item['name']}")
        next_positions = [p for p in positions if p is not None and p > pos]
        end = min(next_positions) if next_positions else len(lines)
        section = lines[pos + 1 : end]
        fields = {}
        desc = []
        for line in section:
            matched = False
            for key in FIELD_KEYS:
                if line.startswith(key):
                    fields[key] = clean_text(line[len(key) :])
                    matched = True
                    break
            if matched:
                continue
            desc.append(line)

        if item["revoked"]:
            continue

        designation_text = fields.get("指定の区分") or ""
        if "民俗" in designation_text:
            subcategory = designation_text.replace("市指定", "")
        elif "天然記念物" in designation_text:
            subcategory = "天然記念物"
        else:
            subcategory = item["subcategory"]

        description_parts = []
        for key in ("所有者", "概要", "製作年代"):
            if fields.get(key):
                description_parts.append(f"{key}: {fields[key]}")
        if desc:
            description_parts.append(" ".join(desc))

        rows.append(
            make_row(
                "天童市",
                item["name"],
                subcategory,
                "市指定",
                None,
                fields.get("所在地"),
                "; ".join(description_parts) if description_parts else None,
                SOURCE_URL,
                "html",
                fetched_at,
            )
        )
    return rows


def main():
    raw = PoliteFetcher().fetch(SOURCE_URL)
    lines = [clean_text(line) for line in html_text(raw).splitlines()]
    lines = [line for line in lines if line]
    items = collect_items(lines)
    rows = parse_sections(lines, items)
    out = "data/yamagata_parts/tendo.jsonl"
    write_jsonl(out, rows)
    validate_jsonl(out)
    print(out, len(rows))
    print(Counter(row["category"] for row in rows))
    print(Counter(row["subcategory"] for row in rows))
    if len(rows) != 57:
        raise SystemExit(f"expected 57 active rows, got {len(rows)}")


if __name__ == "__main__":
    main()
