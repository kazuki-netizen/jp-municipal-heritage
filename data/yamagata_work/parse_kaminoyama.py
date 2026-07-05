import re
import sys

sys.path.append("data/yamagata_work")
from collect_utils import PoliteFetcher, clean_text, make_row, write_jsonl, validate_jsonl


DETAIL_URLS = [
    "https://www.city.kaminoyama.yamagata.jp/soshiki/25/km201301223.html",
    "https://www.city.kaminoyama.yamagata.jp/soshiki/25/km201301224.html",
    "https://www.city.kaminoyama.yamagata.jp/soshiki/25/km201301216.html",
    "https://www.city.kaminoyama.yamagata.jp/soshiki/25/km201301219.html",
    "https://www.city.kaminoyama.yamagata.jp/soshiki/25/km201301218.html",
    "https://www.city.kaminoyama.yamagata.jp/soshiki/25/km201301225.html",
    "https://www.city.kaminoyama.yamagata.jp/soshiki/25/km201301222.html",
    "https://www.city.kaminoyama.yamagata.jp/soshiki/25/km201301227.html",
    "https://www.city.kaminoyama.yamagata.jp/soshiki/25/km201301231.html",
    "https://www.city.kaminoyama.yamagata.jp/soshiki/25/km201301221.html",
    "https://www.city.kaminoyama.yamagata.jp/soshiki/25/220620-rekisisiryo.html",
]


FIELD_KEYS = {"種別", "所在地", "所有者", "員数", "指定年月日"}
SUMMARY_SUBCATEGORY_OVERRIDES = {
    "金生田植踊り": "無形民俗文化財",
    "上山藩鼓笛楽": "無形民俗文化財",
    "高松観音御年越し餅搗き行事": "無形民俗文化財",
}


def html_lines(raw):
    from collect_utils import html_text

    text = html_text(raw).replace("\u200b", "")
    lines = [clean_text(line) for line in text.splitlines()]
    return [line for line in lines if line]


def item_start(line):
    m = re.match(r"^(\d{1,3})\s+(.+)$", line)
    if not m:
        return None
    return int(m.group(1)), clean_text(m.group(2))


def parse_item(number, name, body, source_url, fetched_at):
    if "指定解除" in name:
        return None

    fields = {key: [] for key in FIELD_KEYS}
    desc = []
    current_key = None
    for line in body:
        if line in FIELD_KEYS:
            current_key = line
            continue
        if current_key:
            fields[current_key].append(line)
            current_key = None
            continue
        desc.append(line)

    detail_subcategory = clean_text(" ".join(fields["種別"]))
    subcategory = detail_subcategory
    if subcategory and subcategory.startswith("市・"):
        subcategory = subcategory[2:]
    if name in SUMMARY_SUBCATEGORY_OVERRIDES:
        if subcategory and subcategory != SUMMARY_SUBCATEGORY_OVERRIDES[name]:
            desc.insert(0, f"詳細ページ種別: {subcategory}")
        subcategory = SUMMARY_SUBCATEGORY_OVERRIDES[name]

    description_parts = []
    owner = clean_text(" ".join(fields["所有者"]))
    count = clean_text(" ".join(fields["員数"]))
    if owner:
        description_parts.append(f"所有者: {owner}")
    if count:
        description_parts.append(f"員数: {count}")
    if desc:
        description_parts.append(" ".join(desc))

    return make_row(
        "上山市",
        name,
        subcategory,
        "市指定",
        clean_text(" ".join(fields["指定年月日"])),
        clean_text(" ".join(fields["所在地"])),
        "; ".join(description_parts) if description_parts else None,
        source_url,
        "html",
        fetched_at,
    )


def parse_page(raw, source_url):
    from collect_utils import now_jst

    lines = html_lines(raw)
    try:
        start = next(i for i, line in enumerate(lines) if line == "本文")
    except StopIteration:
        start = 0
    try:
        end = next(i for i, line in enumerate(lines) if line.startswith("このページに関するお問い合わせ先"))
    except StopIteration:
        end = len(lines)

    content = lines[start:end]
    fetched_at = now_jst()
    items = []
    current = None
    body = []
    for line in content:
        started = item_start(line)
        if started:
            if current:
                row = parse_item(current[0], current[1], body, source_url, fetched_at)
                if row:
                    items.append(row)
            current = started
            body = []
            continue
        if current:
            body.append(line)

    if current:
        row = parse_item(current[0], current[1], body, source_url, fetched_at)
        if row:
            items.append(row)
    return items


def main():
    fetcher = PoliteFetcher()
    rows = []
    for url in DETAIL_URLS:
        rows.extend(parse_page(fetcher.fetch(url), url))

    out = "data/yamagata_parts/kaminoyama.jsonl"
    write_jsonl(out, rows)
    validate_jsonl(out)
    print(out, len(rows))
    from collections import Counter

    print(Counter(row["category"] for row in rows))
    print(Counter(row["subcategory"] for row in rows))
    if len(rows) != 75:
        raise SystemExit(f"expected 75 rows, got {len(rows)}")


if __name__ == "__main__":
    main()
