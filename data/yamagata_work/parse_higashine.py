import re
import sys
from collections import Counter
from html.parser import HTMLParser

sys.path.append("data/yamagata_work")
from collect_utils import PoliteFetcher, clean_text, make_row, validate_jsonl, write_jsonl


SOURCE_URL = "https://www.city.higashine.yamagata.jp/section_list/section021/3348"
MONUMENT_SUBCATEGORIES = {
    "里見景佐の御霊屋": "史跡",
    "若木山防空壕": "史跡",
    "泉郷春日神社のモミ": "天然記念物",
    "猪野沢のヒイラギ": "天然記念物",
}


class ElementParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.current = None
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag in ("h2", "h3", "h4", "p"):
            self.current = tag
            self.parts = []
        elif tag == "br" and self.current:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1
        if self.current == tag:
            text = clean_text("".join(self.parts))
            if text:
                self.elements.append((tag, text))
            self.current = None
            self.parts = []

    def handle_data(self, data):
        if not self.skip and self.current:
            self.parts.append(data)


def parse_elements(raw):
    parser = ElementParser()
    parser.feed(raw)
    return parser.elements


def description_and_date(text):
    m = re.search(r"認定年月日\s*([^ ]+年\s*[0-9０-９]+月\s*[0-9０-９]+日)", text)
    if not m:
        return None, text
    date = m.group(1)
    desc = clean_text((text[: m.start()] + text[m.end() :]).strip())
    return date, desc


def main():
    raw = PoliteFetcher().fetch(SOURCE_URL)
    elements = parse_elements(raw)

    rows = []
    active_h2 = None
    active_h3 = None
    current_name = None
    fetched_at = None
    from collect_utils import now_jst

    fetched_at = now_jst()
    for tag, text in elements:
        if tag == "h2":
            active_h2 = text
            active_h3 = None
            current_name = None
            continue
        if tag == "h3":
            active_h3 = text
            current_name = None
            continue
        if tag == "h4":
            current_name = text
            continue
        if tag != "p" or not current_name or "認定年月日" not in text:
            continue

        if active_h2 == "市指定有形文化財":
            subcategory = active_h3
        elif active_h2 == "市指定無形民俗文化財":
            subcategory = "無形民俗文化財"
        elif active_h2 == "市指定史跡名勝天然記念物":
            subcategory = active_h3 or MONUMENT_SUBCATEGORIES.get(current_name)
        else:
            current_name = None
            continue

        date, desc = description_and_date(text)
        rows.append(
            make_row(
                "東根市",
                current_name,
                subcategory,
                "市指定",
                date,
                None,
                desc,
                SOURCE_URL,
                "html",
                fetched_at,
            )
        )
        current_name = None

    out = "data/yamagata_parts/higashine.jsonl"
    write_jsonl(out, rows)
    validate_jsonl(out)
    print(out, len(rows))
    print(Counter(row["category"] for row in rows))
    print(Counter(row["subcategory"] for row in rows))
    if len(rows) != 32:
        raise SystemExit(f"expected 32 rows, got {len(rows)}")


if __name__ == "__main__":
    main()
