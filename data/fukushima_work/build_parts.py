import csv
import html
import re
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

from collect_lib import WORK, clean, html_tables, read_jsonl, row, validate_jsonl, wareki, write_jsonl


def read_text(name):
    return (WORK / name).read_text(encoding="utf-8")


def write_fukushima():
    source1 = "https://www.city.fukushima.fukushima.jp/soshiki/7/1032/2/1/1/2473.html"
    source2 = "https://www.city.fukushima.fukushima.jp/soshiki/7/1032/2/1/1/701.html"
    rows = []
    subcats = ["工芸品", "絵画", "彫刻", "考古資料", "建造物", "歴史資料", "旧飯野町指定"]
    for subcat, table in zip(subcats, html_tables(read_text("fukushima_2473.html"))):
        for cells in table[1:]:
            rows.append(row("福島市", cells[0], subcat, "市指定", None, None, source1, "html"))
    tables = html_tables(read_text("fukushima_701.html"))
    for subcat, table in zip(["有形民俗文化財", "有形民俗文化財(旧飯野町指定）", "無形民俗文化財"], tables[:3]):
        for cells in table[1:]:
            rows.append(row("福島市", cells[0], subcat, "市指定", None, None, source2, "html"))
    for cells in tables[3][1:]:
        rows.append(row("福島市", cells[1], cells[0], "市指定", None, None, source2, "html"))
    assert len(rows) == 75, len(rows)
    write_jsonl("fukushima", rows)


def parse_aizuwakamatsu_pdf():
    pdf = WORK / "aizuwakamatsu_bunkazai2025.pdf"
    xml = subprocess.check_output(
        ["pdftohtml", "-xml", "-i", "-f", "3", "-l", "5", str(pdf), "-stdout"],
        text=True,
    )
    root = ET.fromstring(xml)
    items = []
    for page in root.findall("page"):
        page_no = int(page.attrib["number"])
        boxes = []
        for text in page.findall("text"):
            value = "".join(text.itertext()).strip()
            if value:
                boxes.append((int(text.attrib["top"]), int(text.attrib["left"]), html.unescape(value)))

        for side in ["L", "R"]:
            no_x = (70, 90) if side == "L" else (450, 475)
            anchors = []
            for top, left, value in boxes:
                if no_x[0] <= left <= no_x[1] and re.fullmatch(r"\d{1,3}", value):
                    n = int(value)
                    ok = (
                        page_no == 3 and ((side == "L" and 1 <= n <= 30) or (side == "R" and 31 <= n <= 60))
                    ) or (
                        page_no == 4 and ((side == "L" and 61 <= n <= 90) or (side == "R" and 91 <= n <= 120))
                    ) or (page_no == 5 and side == "L" and 121 <= n <= 124)
                    if ok:
                        anchors.append((n, top))
            anchors.sort(key=lambda item: item[1])
            for idx, (n, top) in enumerate(anchors):
                next_top = anchors[idx + 1][1] if idx + 1 < len(anchors) else top + 60
                start, end = top - 10, next_top - 10
                ranges = (
                    {"sub": (90, 165), "name": (166, 315), "qty": (315, 360), "date": (360, 430)}
                    if side == "L"
                    else {"sub": (477, 555), "name": (560, 710), "qty": (710, 745), "date": (747, 820)}
                )
                values = {key: [] for key in ranges}
                for box_top, left, value in boxes:
                    if start <= box_top < end:
                        for key, (x0, x1) in ranges.items():
                            if x0 <= left <= x1:
                                values[key].append((box_top, left, value))

                def joined(key):
                    return clean("".join(value for _, __, value in sorted(values[key])))

                date_text = clean(" ".join(v for v in [joined("qty"), joined("date")] if v))
                items.append(
                    {
                        "n": n,
                        "subcategory": joined("sub"),
                        "name": joined("name"),
                        "date": wareki(date_text),
                    }
                )
    items.sort(key=lambda item: item["n"])
    missing = sorted(set(range(1, 125)) - {item["n"] for item in items})
    if missing:
        raise RuntimeError(f"missing 会津若松市 PDF rows: {missing}")
    overrides = {
        62: "蓬莱山松竹梅鶴亀組盃（慶應二年銘）",
    }
    for item in items:
        if item["n"] in overrides:
            item["name"] = overrides[item["n"]]
        if not item["name"] or not item["subcategory"] or not item["date"]:
            raise RuntimeError(f"bad 会津若松市 row: {item}")
    return items


def write_aizuwakamatsu():
    source = "https://www.city.aizuwakamatsu.fukushima.jp/docs/2012100500043/file_contents/bunkazai2025.pdf"
    rows = [
        row("会津若松市", item["name"], item["subcategory"], "市指定", item["date"], None, source, "pdf")
        for item in parse_aizuwakamatsu_pdf()
    ]
    assert len(rows) == 124, len(rows)
    write_jsonl("aizuwakamatsu", rows)


KORIYAMA_PAGES = [
    ("https://www.city.koriyama.lg.jp/soshiki/43/6971.html", "koriyama_north.html"),
    ("https://www.city.koriyama.lg.jp/soshiki/43/6981.html", "koriyama_old.html"),
    ("https://www.city.koriyama.lg.jp/soshiki/43/6970.html", "koriyama_tamura.html"),
    ("https://www.city.koriyama.lg.jp/soshiki/43/6969.html", "koriyama_nakata.html"),
    ("https://www.city.koriyama.lg.jp/soshiki/43/6972.html", "koriyama_konan.html"),
    ("https://www.city.koriyama.lg.jp/soshiki/43/6973.html", "koriyama_west.html"),
    ("https://www.city.koriyama.lg.jp/soshiki/43/6967.html", "koriyama_other.html"),
    ("https://www.city.koriyama.lg.jp/soshiki/43/6974.html", "koriyama_south.html"),
]


def labelled_fields_from_block(block):
    parts = re.split(r"<h3[^>]*>(.*?)</h3>", block, flags=re.S | re.I)
    fields = {}
    for i in range(1, len(parts), 2):
        key = clean(re.sub(r"<[^>]+>", " ", html.unescape(parts[i])))
        value_html = parts[i + 1]
        match = re.search(r"<p[^>]*>(.*?)</p>", value_html, re.S | re.I)
        value = match.group(1) if match else value_html
        fields[key] = clean(re.sub(r"<[^>]+>", " ", html.unescape(value)))
    return fields


def parse_koriyama_blocks(text):
    parsed = []
    parts = re.split(r"(<h2[^>]*>.*?</h2>)", text, flags=re.S | re.I)
    for i in range(1, len(parts), 2):
        title = clean(re.sub(r"<[^>]+>", " ", html.unescape(parts[i])))
        match = re.match(r"(\d+)[\.．](.+)", title or "")
        if not match:
            continue
        fields = labelled_fields_from_block(parts[i + 1])
        subcategory = fields.get("種別")
        if subcategory and "市指定" in subcategory:
            parsed.append(
                {
                    "name": clean(match.group(2)),
                    "subcategory": subcategory,
                    "date": wareki(fields.get("指定年月日")),
                    "location": fields.get("所在"),
                    "description": fields.get("解説と行き方・目印") or fields.get("解説"),
                }
            )
    return parsed


def parse_koriyama_tables(text):
    parsed = []
    for table in html_tables(text):
        for cells in table[1:]:
            if len(cells) >= 7:
                if "市指定" in cells[2]:
                    parsed.append(
                        {
                            "name": clean(cells[1].replace("\u200b", "")),
                            "subcategory": cells[2],
                            "date": wareki(cells[3]),
                            "location": cells[4],
                            "description": cells[6],
                        }
                    )
            elif len(cells) >= 6 and "市指定" in cells[2]:
                sub_date = cells[2]
                subcategory = re.sub(r"(明治|大正|昭和|平成|令和).*", "", sub_date).strip()
                parsed.append(
                    {
                        "name": clean(cells[1].replace("\u200b", "")),
                        "subcategory": subcategory,
                        "date": wareki(sub_date),
                        "location": cells[3],
                        "description": cells[5],
                    }
                )
    return parsed


def write_koriyama():
    items = []
    seen = set()
    for source, filename in KORIYAMA_PAGES:
        text = read_text(filename)
        for item in parse_koriyama_tables(text) + parse_koriyama_blocks(text):
            key = (item["name"], item["subcategory"], item["date"])
            if key in seen:
                continue
            seen.add(key)
            items.append((source, item))
    rows = [
        row(
            "郡山市",
            item["name"],
            item["subcategory"],
            "市指定",
            item["date"],
            item["location"],
            source,
            "html",
            item["description"],
        )
        for source, item in items
    ]
    assert len(rows) == 114, len(rows)
    write_jsonl("koriyama", rows)


def write_iwaki():
    source = "https://www.city.iwaki.lg.jp/www/contents/1001000004837/simple/bunkazai.csv"
    with (WORK / "iwaki_bunkazai.csv").open(encoding="cp932", newline="") as f:
        records = list(csv.DictReader(f))
    rows = []
    for record in records:
        subcategory = record["種別"]
        if "市指定" not in subcategory:
            continue
        rows.append(
            row(
                "いわき市",
                record["名称"],
                subcategory,
                "市指定",
                wareki(record["指定年月日"]),
                record["所在地"],
                source,
                "csv",
                f"所有者: {record['所有者']}" if record.get("所有者") else None,
            )
        )
    assert len(rows) == 201, len(rows)
    write_jsonl("iwaki", rows)


def write_shirakawa():
    sources = [
        ("https://www.city.shirakawa.fukushima.jp/sp/page/page001393.html", "shirakawa1.html"),
        ("https://www.city.shirakawa.fukushima.jp/sp/page/page001392.html", "shirakawa2.html"),
    ]
    rows = []
    for source, filename in sources:
        table = html_tables(read_text(filename))[0]
        for cells in table[1:]:
            names = [cells[2]]
            if cells[0] == "22 23":
                names = ["天神乳銀杏", "天神モミ"]
            location = cells[3] if len(cells) >= 5 else None
            date_text = cells[4] if len(cells) >= 5 else cells[3]
            for name in names:
                rows.append(row("白河市", name, cells[1], "市指定", wareki(date_text), location, source, "html"))
    assert len(rows) == 120, len(rows)
    write_jsonl("shirakawa", rows)


def write_sukagawa():
    source = "https://www.city.sukagawa.fukushima.jp/bunka_sports/bunka_geijyutsu/1013435/bunkazai/1-1/index.tree.json"
    items = json_load(WORK / "sukagawa_muni_json.json")
    selected_source = "https://www.city.sukagawa.fukushima.jp/bunka_sports/bunka_geijyutsu/1013435/1016066/1002518.html"
    selected_text = read_text("sukagawa_city.html")
    selected = {}
    for match in re.finditer(r"<h2[^>]*>.*?</h2>", selected_text, re.S | re.I):
        title = clean(re.sub(r"<[^>]+>", "", html.unescape(match.group(0))))
        if not title or not title.startswith("市指定"):
            continue
        if title.startswith("市指定史跡"):
            subcategory, name = "史跡", title.replace("市指定史跡", "", 1)
        elif title.startswith("市指定天然記念物"):
            subcategory, name = "天然記念物", title.replace("市指定天然記念物", "", 1)
        elif title.startswith("市指定有形文化財"):
            rest = title.replace("市指定", "", 1)
            marker = re.match(r"(有形文化財（[^）]+）)(.+)", rest)
            subcategory, name = (marker.group(1), marker.group(2)) if marker else ("有形文化財", rest)
        else:
            continue
        selected[clean(name)] = subcategory
    rows = []
    for item in items:
        name = item["page_name"]
        if name.startswith("【重複】"):
            continue
        subcategory = selected.get(name, "市指定文化財")
        rows.append(row("須賀川市", name, subcategory, "市指定", None, None, source, "html"))
    assert len(rows) == 106, len(rows)
    write_jsonl("sukagawa", rows)


def write_kitakata():
    source = "https://www.city.kitakata.fukushima.jp/uploaded/attachment/51807.pdf"
    text = subprocess.check_output(["pdftotext", "-layout", str(WORK / "kitakata_51807.pdf"), "-"], text=True)
    rows = []
    for line in text.splitlines():
        match = re.match(r"^\s*(\d{1,3})\s+([^\s]+)\s+(.+?)\s{2,}.+?\s+((?:昭和|平成|令和)\d+年\d+月\d+日)", line)
        if not match:
            continue
        number = int(match.group(1))
        if 50 <= number <= 153:
            rows.append(row("喜多方市", match.group(3), match.group(2), "市指定", wareki(match.group(4)), None, source, "pdf"))
    assert len(rows) == 104, len(rows)
    write_jsonl("kitakata", rows)


def write_soma():
    source = "https://www.city.soma.fukushima.jp/shinososhiki/shogaigakushuka/bunka/digital_museum/bunka_guide/587.html"
    table = html_tables(read_text("soma_about.html"))[2]
    rows = []
    for cells in table[1:]:
        if re.fullmatch(r"[-‐ー―]+", cells[1]) or not cells[3].startswith("市 "):
            continue
        subcategory = cells[3].replace("市 ", "", 1)
        description = f"員数: {cells[2]}" if cells[2] and not re.fullmatch(r"[-‐ー―]+", cells[2]) else None
        rows.append(row("相馬市", cells[1], subcategory, "市指定", None, None, source, "html", description))
    assert len(rows) == 56, len(rows)
    write_jsonl("soma", rows)


def plain_lines_from_html(text):
    plain = html.unescape(re.sub(r"<(script|style).*?</\1>", "", text, flags=re.S | re.I))
    plain = re.sub(r"<br\s*/?>", "\n", plain, flags=re.I)
    plain = re.sub(r"</(p|div|h[1-6]|li)>", "\n", plain, flags=re.I)
    plain = re.sub(r"<[^>]+>", " ", plain)
    return [clean(line) for line in plain.splitlines() if clean(line)]


def write_nihonmatsu():
    source = "https://www.city.nihonmatsu.lg.jp/bunka_sports_syo/bunka_rekishi/shitei_bunka/page001110.html"
    lines = plain_lines_from_html(read_text("nihonmatsu_city.html"))
    heading_re = r"^(有形文化財 \[[^]]+\]|有形民俗文化財|無形民俗文化財|史跡|名勝|天然記念物)$"
    start = lines.index("[凡例]") + 4
    end = lines.index("このページの内容に関するお問い合わせ先")
    rows = []
    subcategory = None
    i = start
    while i < end:
        line = lines[i]
        if re.fullmatch(heading_re, line):
            subcategory = line
            i += 1
            continue
        if subcategory and i + 1 < end and wareki(lines[i + 1].split("／")[0]):
            name = line.split(" ／")[0]
            detail = lines[i + 1].split("／")
            location = detail[1] if len(detail) > 1 else None
            owner = detail[2] if len(detail) > 2 else None
            rows.append(
                row(
                    "二本松市",
                    name,
                    subcategory,
                    "市指定",
                    wareki(detail[0]),
                    location,
                    source,
                    "html",
                    f"所有者(管理団体): {owner}" if owner else None,
                )
            )
            i += 2
            continue
        i += 1
    assert len(rows) == 122, len(rows)
    write_jsonl("nihonmatsu", rows)


def write_tamura():
    source = "https://www.city.tamura.lg.jp/soshiki/30/bunkazai.html"
    table = html_tables(read_text("tamura_page.html"))[2]
    rows = []
    for cells in table[1:]:
        if len(cells) == 6:
            _, subcategory, name, count, location, date_text = cells
        else:
            _, subcategory, name, location, date_text = cells
            count = None
        rows.append(
            row(
                "田村市",
                name,
                subcategory,
                "市指定",
                wareki(date_text),
                location,
                source,
                "html",
                f"員数: {count}" if count else None,
            )
        )
    assert len(rows) == 114, len(rows)
    write_jsonl("tamura", rows)


def write_minamisoma():
    source = "https://www.city.minamisoma.lg.jp/portal/sections/61/6150/61501/4/1328.html"
    table = html_tables(read_text("minamisoma_page.html"))[3]
    rows = []
    for cells in table[1:]:
        if len(cells) == 7:
            _, name, kind, detail, date_text, location, owner = cells
            subcategory = detail
        else:
            _, name, kind, date_text, location, owner = cells
            subcategory = kind
        rows.append(
            row(
                "南相馬市",
                name,
                subcategory,
                "市指定",
                wareki(date_text),
                location,
                source,
                "html",
                f"所有者等: {owner}" if owner else None,
            )
        )
    assert len(rows) == 106, len(rows)
    write_jsonl("minamisoma", rows)


def write_date():
    source = "https://www.city.fukushima-date.lg.jp/soshiki/87/17882.html"
    tables = html_tables(read_text("date_17882.html"))
    rows = []
    for table in tables[7:10]:
        for cells in table[1:]:
            rows.append(row("伊達市", cells[1], cells[0], "市指定", None, cells[2], source, "html"))
    assert len(rows) == 105, len(rows)
    write_jsonl("date", rows)


def write_motomiya():
    source = "https://www.city.motomiya.lg.jp/site/kanko/239.html"
    table = html_tables(read_text("motomiya_239.html"))[0]
    rows = []
    for cells in table[1:]:
        _, name, subcategory, location, *middle, date_text = cells
        description = " / ".join(middle) if middle else None
        rows.append(row("本宮市", name, subcategory, "市指定", wareki(date_text), location, source, "html", description))
    assert len(rows) == 68, len(rows)
    write_jsonl("motomiya", rows)


def write_koori():
    write_jsonl("koori", [])


def write_kunimi():
    write_jsonl("kunimi", [])


def write_kawamata():
    kasuga = "https://www.town.kawamata.lg.jp/site/chosei-shisetsu/bunkazai-ka-kasuga.html"
    meganebashi = "https://www.town.kawamata.lg.jp/site/chosei-shisetsu/bunkazai-meganebashi.html"
    kenmunohi = "https://www.town.kawamata.lg.jp/site/chosei-shisetsu/bunkazai-kenmunohi.html"
    rows = [
        row("川俣町", "春日神社 拝殿・本殿・摂社", "有形文化財", "町指定", None, "福島県伊達郡川俣町字宮前37番地", kasuga, "html"),
        row("川俣町", "春日神社 大ケヤキ", "天然記念物", "町指定", None, "福島県伊達郡川俣町字宮前37番地", kasuga, "html"),
        row("川俣町", "大清水機織御前堂旧跡地", "名勝", "町指定", None, "福島県伊達郡川俣町字東大清水22", meganebashi, "html"),
        row("川俣町", "旧壁沢川石橋", "有形文化財", "町指定", None, "福島県伊達郡川俣町字東大清水22", meganebashi, "html"),
        row("川俣町", "中島の石塔婆（建武の碑）", "史跡", "町指定", None, "福島県伊達郡川俣町字中島14番地", kenmunohi, "html"),
    ]
    write_jsonl("kawamata", rows)


def write_otama():
    base = "https://www.vill.otama.fukushima.jp/kankou_shiseki/shiteibunkazai"
    rows = [
        row("大玉村", "十楽院のカヤの木", "天然記念物", "村指定", "1977-07-14", "大玉村玉井字馬喰内", f"{base}/jurakuin_kaya/", "html"),
        row("大玉村", "相応寺薬師如来三尊像(薬師如来・日光・月光菩薩)", "有形文化財", "村指定", None, "大玉村玉井字南町", f"{base}/sououji/", "html"),
        row("大玉村", "十楽院鉄造観音菩薩立像(伝馬頭観音立像)", "有形文化財", "村指定", None, "大玉村玉井字馬喰内", f"{base}/juurakuin/", "html"),
        row("大玉村", "日枝神社三十六歌仙絵馬", "有形文化財", "村指定", None, "大玉村大山上ノ台13", f"{base}/hiejinja/", "html"),
        row("大玉村", "相応寺薬師堂十二神将", "有形文化財", "村指定", None, "大玉村玉井字南町", f"{base}/sououjiyakushidou/", "html"),
        row("大玉村", "本揃の田植踊", "無形民俗文化財", "村指定", None, "大玉村玉井字本揃", f"{base}/tamaimotozoro/", "html"),
        row("大玉村", "神原田神社十二神楽", "無形民俗文化財", "村指定", None, "大玉村大山字六社山14", f"{base}/kamiharadajuunikagura/", "html"),
        row("大玉村", "玉井二区太鼓台運行", "無形民俗文化財", "村指定", None, "大玉村玉井字午房内", f"{base}/tamainiku/", "html"),
        row("大玉村", "温石古墳", "史跡", "村指定", None, "大玉村大山字東地内", f"{base}/onsekikohun/", "html"),
        row("大玉村", "玉井の井戸", "史跡", "村指定", None, "大玉村玉井字南町", f"{base}/tamainoido/", "html"),
        row("大玉村", "相応寺のしだれ桜", "天然記念物", "村指定", "2009-07-01", "大玉村玉井字南町", f"{base}/sououji_shidarezakura/", "html"),
        row("大玉村", "神原田神社の絵馬", "有形文化財", "村指定", "2014-12-22", "大玉村大山字六社山14", f"{base}/kamiharadajinjanoema/", "html"),
        row("大玉村", "玉井神社の三十六歌仙絵馬", "有形文化財", "村指定", "2014-12-22", "大玉村玉井字午房内", f"{base}/tamaijinjanoema/", "html"),
        row("大玉村", "天王下八坂神社の三十六歌仙絵馬", "有形文化財", "村指定", "2014-12-22", "大玉村玉井字天王下", f"{base}/tenougeyasakajinja/", "html"),
        row("大玉村", "木造徳溢大師坐像", "有形文化財", "村指定", None, "大玉村玉井字南町188番地", f"{base}/mokuzoutokuitutaishizazou/", "html"),
        row("大玉村", "戰死三十一人墓", "史跡", "村指定", None, "大玉村玉井字権現目11", f"{base}/sennshisannjyuuitininnhaka/", "html"),
        row("大玉村", "福島県民会規則", "有形文化財(歴史資料)", "村指定", None, "福島県安達郡大玉村玉井字西庵183番地(あだたらふるさとホール内)", f"{base}/hukushimakenminkaikisoku/", "html"),
        row("大玉村", "小名倉山の「石造大日如来坐像」及び「石造龍樹菩薩坐像」", "有形文化財彫刻", "村指定", "2024-12-19", "大玉村玉井字小名倉山18番地4 日吉神社境内", f"{base}/ishidukuri/", "html"),
    ]
    assert len(rows) == 18, len(rows)
    write_jsonl("otama", rows)


def write_kagamiishi():
    source = "https://www.town.kagamiishi.fukushima.jp/kanko/"
    rows = [
        row("鏡石町", "笠地蔵", "町指定文化財", "町指定", None, "鏡石町中央54", source, "html"),
        row("鏡石町", "西光寺のたらようの木", "天然記念物", "町指定", None, "鏡石町鏡沼76", source, "html"),
    ]
    write_jsonl("kagamiishi", rows)


def write_tenei():
    base = "https://www.vill.tenei.fukushima.jp/soshiki/8"
    overview = f"{base}/bunnkazai.html"
    rows = [
        row("天栄村", "薬師瑠璃光如来座像", "天栄村指定文化財", "村指定", None, None, overview, "html"),
        row("天栄村", "温泉八幡神社本堂", "建造", "村指定", "1982-09-01", "福島県岩瀬郡天栄村湯本字高寺56-1", f"{base}/onnsenhatimanzinnzya01.html", "html"),
        row("天栄村", "武隈神社本堂", "建造", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字大里字宮下", f"{base}/takekumazinnzya01.html", "html"),
        row("天栄村", "豊香島神社本堂", "建造", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字宮ノ前49", f"{base}/toyokasimazinnzya01.html", "html"),
        row("天栄村", "稚児橋史跡", "史跡", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字下松本字稚児橋54-3", f"{base}/tigohasisiseki01.html", "html"),
        row("天栄村", "牛ヶ城址", "史跡", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字大里字向館", f"{base}/takekumazinnzya01.html", "html"),
        row("天栄村", "板小屋遺跡", "史跡", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字田良尾字鎌房山国有林", f"{base}/itagoyaiseki01.html", "html"),
        row("天栄村", "二木の松遺跡", "史跡", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字大里字二木松146", f"{base}/hutakinomatuiseki01.html", "html"),
        row("天栄村", "津室館城跡", "史跡", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字飯豊字春日山", f"{base}/toyokasimazinnzya01.html", "html"),
        row("天栄村", "板宮神社", "史跡", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字白子字中屋敷53", f"{base}/itamiyazinnzya01.html", "html"),
        row("天栄村", "御鍋神社", "史跡", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字湯本字国有林地内", f"{base}/onabezinnzya01.html", "html"),
        row("天栄村", "羽黒山磨崖仏", "史跡", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字大里字羽黒山3", f"{base}/haguroyamamagaibutu01.html", "html"),
        row("天栄村", "横内板碑群", "史跡", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字下松本字池上山27", f"{base}/yokoutiitahigunn01.html", "html"),
        row("天栄村", "青龍寺観世音堂の大檜", "植物", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字牧之内字竜生34", f"{base}/seiryuuzikannzeonndououhinoki01.html", "html"),
        row("天栄村", "吉祥院境内の枝垂れ桜", "植物", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字白小字中屋敷29", f"{base}/kissyouinnkeidainoedataresakura01.html", "html"),
        row("天栄村", "湧井の清水", "池沼", "村指定", "1982-09-01", "福島県岩瀬郡天栄村大字牧之内字京谷原6", f"{base}/wakuinosimizu01.html", "html"),
        row("天栄村", "大日如来座像", "彫刻", "村指定", "1987-05-15", "福島県岩瀬郡天栄村大字湯本字居平50", f"{base}/dainitinyoraizazzou01.html", "html"),
        row("天栄村", "木造聖観音菩薩立像と厨子", "彫刻", "村指定", "1987-05-15", "福島県岩瀬郡天栄村大字牧之内字竜生", f"{base}/mokuzouseikannnonnbosatorituzoutozusi01.html", "html"),
        row("天栄村", "薬師如来座像及び脇侍二菩薩立像", "彫刻", "村指定", "1987-05-15", "福島県岩瀬郡天栄村大字上松本権現森1", f"{base}/yakusinyoraizazou01.html", "html"),
        row("天栄村", "栄林寺の伏鉦", "天栄村指定文化財", "村指定", None, None, overview, "html"),
        row("天栄村", "栄林寺の涅槃図", "天栄村指定文化財", "村指定", None, None, overview, "html"),
    ]
    assert len(rows) == 21, len(rows)
    write_jsonl("tenei", rows)


def write_shimogo():
    source = "https://www.town.shimogo.fukushima.jp/childcare/bunkazai/640.html"
    table = html_tables(read_text("shimogo_town_culture.html"))[2]
    rows = [
        row("下郷町", cells[2], cells[1], "町指定", wareki(cells[3]), cells[4], source, "html")
        for cells in table[1:]
    ]
    assert len(rows) == 29, len(rows)
    write_jsonl("shimogo", rows)


def write_minamiaizu():
    source = "https://www.town.minamiaizu.lg.jp/material/files/group/15/bunnkazaijyouhou.pdf"
    items = [
        ("旧山王茶屋", "建造物", "奥会津博物館", "南会津町"),
        ("照国寺の山門", "建造物", "古町字小沼", "金光山照国寺"),
        ("旧斎藤家住宅", "建造物", "奥会津博物館（南郷館）", "南会津町"),
        ("宮本熊野神社鰐口", "美術工芸品", "田島字宮本", "熊野神社"),
        ("木製燈籠", "美術工芸品", "福米沢字宮前", "雲閇山常楽院"),
        ("田中権現鰐口", "美術工芸品", "福米沢", "個人"),
        ("木造千手観音坐像", "美術工芸品", "田島字後原", "千手院養命山慈恩寺"),
        ("石造子安観音(マリア観音)坐像", "美術工芸品", "福米沢字宮前", "雲閇山常楽院"),
        ("木造如活禅師坐像", "美術工芸品", "中荒井", "個人"),
        ("木造聖徳太子立像", "美術工芸品", "藤生字上山崎", "富貴山藤生寺"),
        ("木造日光菩薩立像", "美術工芸品", "田島字本町", "金光山安楽院薬師寺"),
        ("木造月光菩薩立像", "美術工芸品", "田島字本町", "金光山安楽院薬師寺"),
        ("木造日海坐像", "美術工芸品", "田島字本町", "金光山安楽院薬師寺"),
        ("木造広目天立像", "美術工芸品", "田島字本町", "金光山安楽院薬師寺"),
        ("木造多聞天立像", "美術工芸品", "田島字本町", "金光山安楽院薬師寺"),
        ("木造仁王立像", "美術工芸品", "田島字愛宕山", "上町坪"),
        ("細井家漆工品", "美術工芸品", "奥会津博物館", "南会津町"),
        ("両界種字曼荼羅", "美術工芸品", "糸沢字居平", "熊野山龍福寺"),
        ("両界尊形曼荼羅", "美術工芸品", "糸沢字居平", "熊野山龍福寺"),
        ("熊野縁起絵巻物", "美術工芸品", "田島字宮本", "熊野神社"),
        ("田島祇園祭復興願", "美術工芸品", "田島字宮本", "田出宇賀神社"),
        ("算額（永田鷲神社）", "美術工芸品", "永田字鷲山", "熊野神社"),
        ("龍福寺の杉戸絵及び障壁画群", "美術工芸品", "糸沢字居平", "熊野山龍福寺"),
        ("湯ノ花二荒山神社御正躰", "美術工芸品", "湯ノ花", "湯ノ花区"),
        ("井桁鹿島神社御正躰", "美術工芸品", "井桁", "鹿島神社"),
        ("木造阿弥陀如来立像", "美術工芸品", "湯ノ花", "光雲山光照寺"),
        ("木造阿弥陀如来坐像", "美術工芸品", "塩ノ原", "千楽山泉光寺"),
        ("木造阿弥陀如来立像", "美術工芸品", "八総", "滋録山自源寺"),
        ("星家不動明王立像及び二童子立像", "美術工芸品", "前沢", "南会津町"),
        ("星運吉算額 (熊野神社奉納)", "美術工芸品", "熨斗戸", "鹿島神社、伊与戸区"),
        ("星運吉算額 (鹿島神社奉納)", "美術工芸品", "熨斗戸", "鹿島神社、熨斗戸区"),
        ("森戸虚空蔵菩薩堂石造供養塔婆", "美術工芸品", "森戸", "森戸区"),
        ("法然大師", "美術工芸品", "古町字東居平", "成宝山善導寺"),
        ("善導大師", "美術工芸品", "古町字東居平", "成宝山善導寺"),
        ("華鬘 (善導寺)", "美術工芸品", "古町字東居平", "成宝山善導寺"),
        ("銅鐘 (善導寺)", "美術工芸品", "古町字東居平", "成宝山善導寺"),
        ("阿弥陀如来立像", "美術工芸品", "古町字小沼", "金光山照国寺"),
        ("観音立像", "美術工芸品", "古町字小沼", "金光山照国寺"),
        ("薬師如来立像", "美術工芸品", "古町字小沼", "金光山照国寺"),
        ("華鬘 (照国寺)", "美術工芸品", "古町字小沼", "金光山照国寺"),
        ("銅鐘 (照国寺)", "美術工芸品", "古町字小沼", "金光山照国寺"),
        ("銅鏡", "美術工芸品", "古町字小沼", "金光山照国寺"),
        ("涅槃図", "美術工芸品", "古町字小沼", "金光山照国寺"),
        ("板碑", "美術工芸品", "小塩", "小塩区"),
        ("古剣道防具", "美術工芸品", "古町（伊南武道館）", "個人"),
        ("備州長船助次の刀剣", "美術工芸品", "福島県立博物館", "南会津町"),
        ("槍銘奥州住綱房", "美術工芸品", "古町字小沼", "金光山照国寺"),
        ("金銅釣燈籠", "美術工芸品", "古町字東居平", "成宝山善導寺"),
        ("正観音像", "美術工芸品", "下山", "南照山観音寺"),
        ("大橋三十三観音像", "美術工芸品", "大橋", "大橋区"),
        ("大日如来坐像", "美術工芸品", "下山", "南照山観音寺"),
        ("酒井真吉古鏡コレクション", "美術工芸品", "奥会津博物館（南郷館）", "南会津町"),
        ("木造如来形坐像", "美術工芸品", "鴇巣", "鴇巣区"),
        ("銅製鰐口", "美術工芸品", "富山", "富山区"),
        ("木造大日如来坐像", "美術工芸品", "片貝", "明玉山不動寺"),
        ("聖観音厨子", "美術工芸品", "片貝", "明玉山不動寺"),
        ("奉額絵馬", "美術工芸品", "片貝", "明玉山不動寺"),
        ("石神堂の板碑", "美術工芸品", "山口", "台板橋区"),
        ("寺前遺跡出土品（深鉢形土器：３点）", "考古資料", "奥会津博物館", "南会津町"),
        ("黄檗円通詩偈及び龍水如活禅師添書", "歴史資料", "中荒井", "個人"),
        ("明暦の過去帳", "歴史資料", "静川字西の沢口", "松見山南泉寺"),
        ("寛文の旦那帳", "歴史資料", "静川字西の沢口", "松見山南泉寺"),
        ("町公事免許判物", "歴史資料", "田島", "個人"),
        ("御蔵入三十三観音十七番札所高野観音堂巡礼札", "歴史資料", "高野字岩下通", "金光山安楽院薬師寺"),
        ("江戸期の医学書（妊孕内景図）", "歴史資料", "松戸原", "個人"),
        ("御蔵入三十三観音十七番札所塩ノ原泉光寺観音堂巡礼札", "歴史資料", "塩ノ原", "千楽山泉光寺"),
        ("戊辰戦争資料（駕籠、陣羽織等）", "歴史資料", "古町字小沼", "金光山照国寺"),
        ("山内家文書", "歴史資料", "奥会津博物館", "個人"),
        ("江戸時代の制札", "歴史資料", "下山", "個人"),
        ("萬事覚書帳", "歴史資料", "大橋", "個人"),
        ("如活禅師遺品及び資料", "歴史資料", "静川", "個人"),
        ("細井家郵便資料", "歴史資料", "奥会津博物館", "南会津町"),
        ("染屋(旧杉原家住宅) (染色関係資料)", "歴史資料", "奥会津博物館", "南会津町"),
        ("親鸞聖人繪傳及び関係文書", "歴史資料", "静川字西の沢口", "松見山南泉寺"),
        ("大政官贋壱両札銅製原版", "歴史資料", "静川字西の沢口", "松見山南泉寺"),
        ("湯ノ花の舞台", "重要有形民俗文化財", "湯ノ花区", "湯ノ花区"),
        ("青柳の組み立て式舞台", "重要有形民俗文化財", "青柳", "個人"),
        ("小正月の火祭り行事 針生の歳の神", "重要有形民俗文化財", "針生", "針生区"),
        ("藤生鋏山の山焼き", "重要有形民俗文化財", "藤生", "藤生区"),
        ("古町のまつり", "重要無形民俗文化財", "古町", "廣瀬神社、氏子総代、古町区"),
        ("小塩の神楽", "重要無形民俗文化財", "小塩", "小塩芸能保存会"),
        ("田部原一里塚", "史跡", "田島字田部原", "南会津町、田部原第一区"),
        ("如活禅師佛塔並びに墳墓", "史跡", "中荒井", "70名共有"),
        ("田部原館跡", "史跡", "田島字田部原", "南会津町"),
        ("長沼盛秀墓群", "史跡", "田島字寺前", "興國山徳昌寺"),
        ("寿林の墓", "史跡", "田島", "個人"),
        ("室井杢左衛門の五輪塔", "史跡", "田島", "個人"),
        ("保城木地師集落跡", "史跡", "森戸", "高杖原区"),
        ("駒寄城跡", "史跡", "古町", "25名共有"),
        ("南山木地師戸板集落跡", "史跡", "東", "3名共有"),
        ("河原崎城跡", "史跡", "和泉田", "37名共有"),
        ("山口の道標", "史跡", "山口", "53名共有"),
        ("十三仏塚", "史跡", "大新田", "南会津町"),
        ("大新田の庚申塔群", "史跡", "大新田", "大新田区"),
        ("下塩江五本松", "天然記念物", "塩江字上坪", "下塩江区"),
        ("萩野風穴", "天然記念物", "糸沢字萩野山", "羽塩区"),
        ("黒岩湿原", "天然記念物", "針生字昼滝山", "針生区"),
        ("藤生熊野神社男杉・女杉", "天然記念物", "藤生字上平", "藤生熊野神社"),
        ("鴫山城跡イチイの木", "天然記念物", "田島", "489名共有"),
        ("如活禅師墓地イチイの木", "天然記念物", "中荒井", "70名共有"),
        ("鹿島神社のトチの木", "天然記念物", "井桁", "鹿島神社"),
        ("照国寺のイチイの木", "天然記念物", "古町", "金光山照国寺"),
        ("北野神社大杉", "天然記念物", "大新田", "北野神社"),
        ("宮床湿原", "天然記念物", "宮床", "宮床区共有"),
    ]
    rows = [
        row("南会津町", name, subcategory, "町指定", None, location, source, "pdf", f"所有者: {owner}")
        for name, subcategory, location, owner in items
    ]
    assert len(rows) == 104, len(rows)
    write_jsonl("minamiaizu", rows)


def write_kitashiobara():
    write_jsonl("kitashiobara", [])


def write_nishiaizu():
    source = "https://www.town.nishiaizu.fukushima.jp/soshiki/10/896.html"
    table = html_tables(read_text("nishiaizu_7.html"))[2]
    rows = [
        row("西会津町", cells[2], cells[1], "町指定", wareki(cells[3]), None, source, "html")
        for cells in table[1:]
    ]
    assert len(rows) == 38, len(rows)
    write_jsonl("nishiaizu", rows)


def write_bandai():
    write_jsonl("bandai", [])


def write_inawashiro():
    source = "https://www.town.inawashiro.fukushima.jp/uploaded/attachment/5271.pdf"
    items = [
        ("聖観音座像", "彫刻", "猪苗代町大字川桁字村北2347番地", "観音寺"),
        ("麓山神社本殿厨子", "建造物", "猪苗代町大字千代田字村ノ内丙177番地", "北高野区"),
        ("算額", "工芸品", "猪苗代町大字中小松字西浜甲1615番地", "小平潟天満宮"),
        ("板碑（釜井）", "建造物", "猪苗代町大字長田字西畑91番地", "釜井区"),
        ("板碑（島田）", "建造物", "猪苗代町大字磐里字島田前2852番地", "島田区"),
        ("一位", "天然記念物", "猪苗代町大字蚕養字山根乙573番地", "天徳寺"),
        ("大鹿桜", "天然記念物", "猪苗代町字西峯6203番地", "磐椅神社"),
        ("三忠碑", "史跡", "猪苗代町大字長田字長田439番地", "猪苗代町"),
        ("平盛胤の墓", "史跡", "猪苗代町大字八幡字水上5840番地", "内野区"),
        ("五輪塔", "建造物", "猪苗代町字五輪地内", "猪苗代町"),
        ("旧山内家住宅", "建造物", "猪苗代町字古城跡7150番地2", "猪苗代町"),
        ("吾妻山大権現額", "工芸品", "猪苗代町大字若宮字上町甲1463番地", "吾妻山神社"),
        ("観音寺山門", "建造物", "猪苗代町大字川桁字村北2332番地2", "観音寺"),
        ("小平潟天満宮本殿", "建造物", "猪苗代町大字中小松字西浜甲1615番地", "小平潟天満宮"),
        ("楊枝一里塚", "史跡", "猪苗代町大字壷楊字一里塚地内", "個人"),
        ("大原観音の松", "天然記念物", "猪苗代町大字若宮字大原丙261番地1", "大原区"),
        ("白津からかさ松", "天然記念物", "猪苗代町大字八幡字高原5024番地", "白津区"),
        ("百目貫の公孫樹", "天然記念物", "猪苗代町大字磐里字百目貫687番地1", "百目貫区"),
        ("鳥居杉", "天然記念物", "猪苗代町字西峯6203番地", "磐椅神社"),
        ("西峯遺跡", "史跡", "猪苗代町字西峯6195番地ほか", "個人"),
        ("麓山神社左右大臣", "工芸品", "猪苗代町大字関都字権現山2119番地", "麓山神社"),
        ("鹿島神社宝篋印塔", "建造物", "猪苗代町大字金田字六角3624番地", "個人"),
        ("蟹沢湿原", "天然記念物", "猪苗代町大字翁沢・菖花地内", "蟹沢区"),
        ("御上覧場一里塚", "史跡", "猪苗代町大字長田字長田114番地", "個人"),
        ("磐椅神社彩色三十六歌仙", "工芸品", "猪苗代町字西峯6199番地", "磐椅神社"),
        ("上祢次の辛夷", "天然記念物", "猪苗代町字林南1518番地10", "上祢次区"),
        ("西久保彼岸獅子舞", "無形民俗文化財", "猪苗代町大字磐根字西久保地内", "西久保彼岸獅子保存会"),
        ("保科正之公墳墓", "史跡", "猪苗代町字見祢山2番地", "土津神社"),
        ("土津霊神之碑", "建造物", "猪苗代町字見祢山3番地", "土津神社"),
        ("朝日向聖観音座像", "彫刻", "猪苗代町大字八幡字若宮84番地1", "内野区"),
        ("堀切の姥神像", "彫刻", "猪苗代町大字三郷字下太子堂305番地", "伯父ヶ倉区"),
        ("都沢の公孫樹", "天然記念物", "猪苗代町大字関都字堂脇2667番地1", "都沢区"),
        ("旧二本松街道松並木", "史跡", "猪苗代町大字長田字長田439番地", "猪苗代町"),
        ("猪苗代盛國書状", "書跡", "猪苗代町大字三郷字舘ノ内8291番地1", "隣松院"),
        ("土津神社境石", "建造物", "猪苗代町字赤埴山1番地1", "土津神社"),
        ("（伝）空海筆應額", "工芸品", "猪苗代町字見祢山3番地", "土津神社"),
        ("西円寺喚鐘", "工芸品", "猪苗代町字新町4899番地", "西円寺"),
        ("小平潟天満宮所蔵信仰資料", "有形民俗文化財", "猪苗代町大字中小松字西浜甲1615番地", "小平潟天満宮"),
        ("岡越後書状", "古文書", "猪苗代町大字堅田字廻谷地2505番地", "個人"),
    ]
    rows = [
        row("猪苗代町", name, subcategory, "町指定", None, location, source, "pdf", f"所有者・管理者: {owner}")
        for name, subcategory, location, owner in items
    ]
    assert len(rows) == 39, len(rows)
    write_jsonl("inawashiro", rows)


def write_aizubange():
    source = "https://www.town.aizubange.fukushima.jp/soshiki/30/285.html"
    tables = html_tables(read_text("aizubange_8.html"))
    type_map = {"彫": "彫刻", "建": "建造物", "絵": "絵画", "歴": "歴史資料"}
    rows = []
    for cells in tables[6][1:]:
        rows.append(
            row(
                "会津坂下町",
                cells[1],
                type_map.get(cells[0], cells[0]),
                "町指定",
                wareki(cells[3]),
                cells[4],
                source,
                "html",
                f"員数: {cells[2]} / 所有者(管理団体): {cells[5]}",
            )
        )
    for cells in tables[7][1:]:
        rows.append(row("会津坂下町", cells[0], "重要無形民俗文化財", "町指定", wareki(cells[1]), cells[2], source, "html", f"保存団体: {cells[3]}"))
    for cells in tables[8][1:]:
        rows.append(row("会津坂下町", cells[0], "重要有形民俗文化財", "町指定", wareki(cells[2]), cells[3], source, "html", f"員数: {cells[1]} / 所有者: {cells[4]}"))
    for cells in tables[9][1:]:
        rows.append(row("会津坂下町", cells[0], "史跡", "町指定", wareki(cells[1]), cells[2], source, "html", f"所有者: {cells[3]}"))
    for cells in tables[10][1:]:
        rows.append(row("会津坂下町", cells[0], "天然記念物", "町指定", wareki(cells[1]), cells[2], source, "html", f"所有者: {cells[3]}"))
    assert len(rows) == 27, len(rows)
    write_jsonl("aizubange", rows)


def write_yugawa():
    source = "https://www.vill.yugawa.fukushima.jp/site/kyoiku-top/bunkazai.html"
    table = html_tables(read_text("yugawa_8.html"))[0]
    rows = []
    for cells in table[1:]:
        if "村指定" not in cells[1]:
            continue
        subcategory = re.sub(r"（村指定）", "", cells[1])
        rows.append(row("湯川村", cells[2], subcategory, "村指定", None, None, source, "html", f"識別: {cells[0]}"))
    assert len(rows) == 26, len(rows)
    write_jsonl("yugawa", rows)


def write_yanaizu():
    source = "https://www.town.yanaizu.fukushima.jp/docs/2021100100016/"
    table = html_tables(read_text("yanaizu_7.html"))[2]
    rows = [
        row("柳津町", cells[1], cells[0], "町指定", wareki(cells[2]), None, source, "html")
        for cells in table[1:]
    ]
    assert len(rows) == 14, len(rows)
    write_jsonl("yanaizu", rows)


def write_mishima():
    write_jsonl("mishima", [])


def kaneyama_subcategory(name):
    if any(k in name for k in ["辛夷", "老杉", "キマダラルリツバメ"]):
        return "天然記念物"
    if any(k in name for k in ["城跡", "館跡", "経塚", "古墳", "一里塚", "碑", "屋敷跡"]):
        return "史跡"
    if any(k in name for k in ["縄文土器", "弥生土器"]):
        return "考古資料"
    if "住宅" in name:
        return "建造物"
    if "涅槃図" in name:
        return "絵画"
    if "道祖神" in name:
        return "有形民俗文化財"
    return "彫刻"


def write_kaneyama():
    category_url = "https://www.town.kaneyama.fukushima.jp/site/kanko/list34-97.html"
    category_html = read_text("kaneyama_5.html")
    links = []
    seen = set()
    for match in re.finditer(r"<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", category_html, re.S | re.I):
        href = html.unescape(match.group(1))
        label = clean(re.sub(r"<[^>]+>", " ", html.unescape(match.group(2))))
        source = urllib.parse.urljoin(category_url, href)
        if "/site/kanko/201207" in source and source not in seen:
            seen.add(source)
            links.append((label, source))
    rows = []
    for idx, (label, source) in enumerate(links):
        text = read_text(f"kaneyama_item_{idx:02d}.html")
        plain = clean(re.sub(r"<[^>]+>", " ", html.unescape(text)))
        location = None
        match = re.search(r"所在\s+(.+?)(?:\s+説明|このページに関するお問い合わせ先)", plain or "")
        if match:
            location = match.group(1)
        name = clean(re.sub(r"（[^）]*）", "", label))
        rows.append(row("金山町", name, kaneyama_subcategory(name), "町指定", None, location, source, "html"))
    assert len(rows) == 22, len(rows)
    write_jsonl("kaneyama", rows)


def write_showa():
    write_jsonl("showa", [])


def write_aizumisato():
    source = "https://www.town.aizumisato.fukushima.jp/gyosei/kanko_bunka_sports/2/3783.html"
    tables = html_tables(read_text("aizumisato_9.html"))
    subcats = ["絵画", "彫刻", "工芸品", "歴史資料", "無形民俗文化財", "史跡", "天然記念物"]
    rows = []
    for subcategory, table in zip(subcats, tables):
        for cells in table[1:]:
            rows.append(row("会津美里町", cells[0], subcategory, "町指定", wareki(cells[1]), cells[2], source, "html"))
    assert len(rows) == 78, len(rows)
    write_jsonl("aizumisato", rows)


def write_nishigo():
    source = "https://www.vill.nishigo.fukushima.jp/kanko_bunka_sports/rekishi_bunkazai/bunkazai/1191.html"
    table = html_tables(read_text("nishigo_10.html"))[1]
    rows = []
    for cells in table[1:]:
        description = f"備考: {cells[4]}" if len(cells) > 4 else None
        rows.append(row("西郷村", cells[1], cells[0], "村指定", wareki(cells[3]), cells[2], source, "html", description))
    assert len(rows) == 12, len(rows)
    write_jsonl("nishigo", rows)


def write_hinoemata():
    write_jsonl("hinoemata", [])


def write_tadami():
    write_jsonl("tadami", [])


def json_load(path):
    import json

    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    write_fukushima()
    write_aizuwakamatsu()
    write_koriyama()
    write_iwaki()
    write_shirakawa()
    write_sukagawa()
    write_kitakata()
    write_soma()
    write_nihonmatsu()
    write_tamura()
    write_minamisoma()
    write_date()
    write_motomiya()
    write_koori()
    write_kunimi()
    write_kawamata()
    write_otama()
    write_kagamiishi()
    write_tenei()
    write_shimogo()
    write_hinoemata()
    write_tadami()
    write_minamiaizu()
    write_kitashiobara()
    write_nishiaizu()
    write_bandai()
    write_inawashiro()
    write_aizubange()
    write_yugawa()
    write_yanaizu()
    write_mishima()
    write_kaneyama()
    write_showa()
    write_aizumisato()
    write_nishigo()
