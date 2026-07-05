import json
import re
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[2]
PARTS = ROOT / "data" / "miyagi_parts"
WORK = ROOT / "data" / "miyagi_work"
DISC = WORK / "discovery2"
FETCHED_AT = "2026-07-03T23:58:00+09:00"


ORDER = [
    ("sendai", "仙台市"),
    ("ishinomaki", "石巻市"),
    ("osaki", "大崎市"),
    ("tome", "登米市"),
    ("kurihara", "栗原市"),
    ("natori", "名取市"),
    ("tagajo", "多賀城市"),
    ("kesennuma", "気仙沼市"),
    ("iwanuma", "岩沼市"),
    ("tomiya", "富谷市"),
    ("shiroishi", "白石市"),
    ("higashimatsushima", "東松島市"),
    ("shiogama", "塩竈市"),
    ("kakuda", "角田市"),
    ("shibata", "柴田町"),
    ("rifu", "利府町"),
    ("watari", "亘理町"),
    ("taiwa", "大和町"),
    ("ogawara", "大河原町"),
    ("matsushima", "松島町"),
    ("kami", "加美町"),
    ("wakuya", "涌谷町"),
    ("misato", "美里町"),
    ("zao", "蔵王町"),
    ("murata", "村田町"),
    ("kawasaki", "川崎町"),
    ("marumori", "丸森町"),
    ("yamamoto", "山元町"),
    ("shichigahama", "七ヶ浜町"),
    ("osato", "大郷町"),
    ("shikama", "色麻町"),
    ("onagawa", "女川町"),
    ("minamisanriku", "南三陸町"),
    ("shichikashuku", "七ヶ宿町"),
    ("ohira", "大衡村"),
]


def row(
    municipality,
    name,
    category,
    subcategory,
    designation,
    source_url,
    source_format,
    designated_date=None,
    location=None,
    description=None,
):
    return {
        "pref": "宮城県",
        "municipality": municipality,
        "name": clean(name),
        "category": category,
        "subcategory": clean(subcategory) if subcategory else None,
        "designation": designation,
        "designated_date": designated_date,
        "location": clean(location) if location else None,
        "description": clean(description) if description else None,
        "source_url": source_url,
        "source_format": source_format,
        "fetched_at": FETCHED_AT,
    }


def clean(value):
    if value is None:
        return None
    value = str(value).replace("\u3000", " ").replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def era_to_iso(value):
    value = clean(value)
    if not value:
        return None
    value = value.replace("0", "０") if False else value
    m = re.search(r"(明治|大正|昭和|平成|令和)(元|[0-9０-９]+)年([0-9０-９]+)月([0-9０-９]+)日", value)
    if not m:
        return None
    bases = {"明治": 1867, "大正": 1911, "昭和": 1925, "平成": 1988, "令和": 2018}
    year_s = m.group(2)
    year = 1 if year_s == "元" else int(year_s.translate(str.maketrans("０１２３４５６７８９", "0123456789")))
    month = int(m.group(3).translate(str.maketrans("０１２３４５６７８９", "0123456789")))
    day = int(m.group(4).translate(str.maketrans("０１２３４５６７８９", "0123456789")))
    return f"{bases[m.group(1)] + year:04d}-{month:02d}-{day:02d}"


def category_from_subcategory(subcategory):
    subcategory = clean(subcategory) or ""
    if "民俗" in subcategory:
        return "民俗文化財"
    if any(token in subcategory for token in ["史跡", "名勝", "天然記念物", "記念物"]):
        return "記念物(史跡・名勝・天然記念物)"
    if "無形文化財" in subcategory:
        return "無形文化財"
    if subcategory in {"史跡", "名勝", "天然記念物"}:
        return "記念物(史跡・名勝・天然記念物)"
    return "有形文化財"


def write_part(slug, rows):
    PARTS.mkdir(parents=True, exist_ok=True)
    path = PARTS / f"{slug}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for item in rows:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    for line in path.read_text(encoding="utf-8").splitlines():
        json.loads(line)
    return path


def parse_kami():
    source = "https://www.town.kami.miyagi.jp/kanko_sports_bunka/rekishi_bunkazai/1176.html"
    soup = BeautifulSoup((DISC / "www_town_kami_miyagi_jp_kanko_sports_bunka_rekishi_bunkazai_1176_html_").read_text(encoding="utf-8", errors="replace"), "html.parser")
    rows = []
    table = soup.find_all("table")[4]
    for tr in table.find_all("tr")[1:]:
        cells = [clean(c.get_text(" ", strip=True)) for c in tr.find_all(["td", "th"])]
        if len(cells) < 3:
            continue
        subcategory, name, date = cells[:3]
        rows.append(
            row(
                "加美町",
                name,
                category_from_subcategory(subcategory),
                subcategory,
                "町指定",
                source,
                "html",
                designated_date=era_to_iso(date),
            )
        )
    return rows


def parse_minamisanriku():
    source = "https://www.town.minamisanriku.miyagi.jp/bunka-sports/rekishi-bunkazai/1/6494.html"
    soup = BeautifulSoup((DISC / "www_town_minamisanriku_miyagi_jp_bunka-sports_rekishi-bunkazai_1_6494_html_").read_text(encoding="utf-8", errors="replace"), "html.parser")
    rows = []
    tables = soup.find_all("table")
    for idx in [3, 4, 5]:
        for tr in tables[idx].find_all("tr")[1:]:
            cells = [clean(c.get_text(" ", strip=True)) for c in tr.find_all(["td", "th"])]
            if len(cells) < 5:
                continue
            subcategory, name, location, owner, date = cells[:5]
            rows.append(
                row(
                    "南三陸町",
                    name,
                    category_from_subcategory(subcategory),
                    subcategory,
                    "町指定",
                    source,
                    "html",
                    designated_date=era_to_iso(date),
                    location=location,
                    description=f"所有者等: {owner}" if owner else None,
                )
            )
    return rows


def zao_rows():
    source_old = "https://www.dokitan.com/sitei/"
    source_new = "http://www.town.zao.miyagi.jp/section/shougaigakushu/bunkazai/bunkazai2025-1.html"
    old_items = [
        ("刈田嶺神社 拝殿", "有形文化財 建造物"),
        ("刈田嶺神社 随身門", "有形文化財 建造物"),
        ("奥平家住宅", "有形文化財 建造物"),
        ("刈田嶺神社 絵馬", "有形文化財 美術工芸品 絵画"),
        ("敬明講図（絵馬）", "有形文化財 美術工芸品 絵画"),
        ("太刀", "有形文化財 美術工芸品 刀剣"),
        ("三尊堂舎", "有形文化財 美術工芸品 工芸品"),
        ("願行寺遺跡出土土偶", "有形文化財 美術工芸品 考古資料"),
        ("高野家文書", "有形文化財 美術工芸品 古文書"),
        ("白鳥古碑群", "有形文化財 美術工芸品 古碑"),
        ("高野倫兼遺訓碑", "有形文化財 美術工芸品 古碑"),
        ("八雲神社神楽", "民俗文化財 無形民俗文化財 民俗芸能"),
        ("白山神社神楽", "民俗文化財 無形民俗文化財 民俗芸能"),
        ("榊流東根神楽", "民俗文化財 無形民俗文化財 民俗芸能"),
        ("平沢榊流神楽", "民俗文化財 無形民俗文化財 民俗芸能"),
        ("刈田嶺神社神楽", "民俗文化財 無形民俗文化財 民俗芸能"),
        ("小村崎榊流法印神楽", "民俗文化財 無形民俗文化財 民俗芸能"),
        ("小村崎田植踊", "民俗文化財 無形民俗文化財 民俗芸能"),
        ("小村崎春駒", "民俗文化財 無形民俗文化財 民俗芸能"),
        ("達磨講石造物（玉石・宮宿卵・安産達磨尊）", "民俗文化財 有形民俗文化財 信仰関係"),
        ("白九頭龍古墳", "記念物 史跡"),
        ("岩崎山金窟址", "記念物 史跡"),
        ("曲竹一里塚 附 古碑群", "記念物 史跡"),
        ("安養寺参道跡保存地区", "記念物 史跡"),
        ("遠刈田製鉄所 高炉跡", "記念物 史跡"),
        ("根返しの桜", "記念物 天然記念物"),
    ]
    rows = [
        row("蔵王町", name, category_from_subcategory(sub), sub, "町指定", source_old, "html")
        for name, sub in old_items
    ]
    rows.extend(
        [
            row("蔵王町", "日吉神社本殿", "有形文化財", "有形文化財（建造物）", "町指定", source_new, "html", "2025-11-10", "大字平沢字三本槻79"),
            row("蔵王町", "鎌倉沢の甌穴群", "記念物(史跡・名勝・天然記念物)", "天然記念物", "町指定", source_new, "html", "2025-11-10", "大字平沢字鎌倉沢地内"),
            row("蔵王町", "円田珪藻土", "記念物(史跡・名勝・天然記念物)", "天然記念物", "町指定", source_new, "html", "2025-11-10", "鎌倉沢標識地（大字平沢字二本木地内）・堀の内川標識地（大字円田字鳥山地内）"),
            row("蔵王町", "遠刈田のちゃせんこ", "民俗文化財", "無形民俗文化財（風俗慣習）", "町指定", source_new, "html", "2025-11-10", "遠刈田ちゃせんこ保存会"),
        ]
    )
    return rows


def ogawara_rows():
    source = "https://www.town.ogawara.miyagi.jp/1800.htm"
    return [
        row("大河原町", "繁昌院 阿弥陀如来坐像", "有形文化財", "重要文化財", "町指定", source, "html", "1977-09-06", "繁昌院"),
        row("大河原町", "小山田やすとこ", "民俗文化財", "無形民俗文化財", "町指定", source, "html", "1977-09-06"),
        row("大河原町", "堤神楽", "民俗文化財", "無形民俗文化財", "町指定", source, "html", "1977-09-06"),
    ]


def marumori_rows():
    source = "https://www.town.marumori.miyagi.jp/education/detail.php?content=69"
    items = [
        ("駒場ケ瀧不動尊仁王門", "有形文化財", "丸森町字不動"),
        ("西円寺十王", "有形文化財", "丸森町字漆原"),
        ("法傳寺欄間の龍", "有形文化財", "丸森町字虚空蔵中"),
        ("瑞雲寺前机", "有形文化財", "金山字鬼形"),
        ("瑞雲寺霊膳", "有形文化財", "金山字鬼形"),
        ("阿弥陀堂", "有形文化財", "筆甫字和田"),
        ("四ツ足門", "有形文化財", "大内字桜田"),
        ("諏訪神社本殿", "有形文化財", "大内字諏訪"),
        ("鹿島神社所蔵黒漆五枚胴具足", "有形文化財", "小斎字日向"),
        ("鹿島神社奉納和算額", "有形文化財", "小斎字日向"),
        ("宗吽院文書", "有形文化財", "舘矢間木沼"),
        ("大蔵寺仏像35体", "有形文化財", "大張大蔵字市ノ沢"),
        ("丸森ばやし", "無形民俗文化財", "丸森地区"),
        ("上滝十二神楽", "無形民俗文化財", "丸森上滝地区"),
        ("田林神楽", "無形民俗文化財", "金山田林地区"),
        ("鎮神武天皇御祭礼神楽", "無形民俗文化財", "筆甫地区"),
        ("大内山伏神楽", "無形民俗文化財", "大内西向地区"),
        ("青葉神代神楽", "無形民俗文化財", "大内青葉地区"),
        ("奉射祭（やぶさめ）", "無形民俗文化財", "小斎地区"),
        ("松掛神楽", "無形民俗文化財", "舘矢間松掛地区"),
        ("立石", "天然記念物", "丸森町字泉"),
        ("笠松", "天然記念物", "丸森町字笠松"),
        ("うばひがん桜", "天然記念物", "筆甫字和田"),
        ("老杉", "天然記念物", "大内字青葉西"),
        ("金山城址", "史跡", "金山字黒森"),
        ("佐野製糸工場関連墓群", "史跡", "金山字上片山"),
        ("旗巻古戦場", "史跡", "大内字青葉上"),
        ("中島家廟所", "史跡", "金山字鬼形"),
    ]
    return [
        row("丸森町", name, category_from_subcategory(sub), sub, "町指定", source, "html", location=location)
        for name, sub, location in items
    ]


def watari_rows():
    source = "https://www.town.watari.miyagi.jp/common/img/content/content_20260407_093050.pdf"
    items = [
        ("伊達実氏霊屋", "有形文化財（建造物）", "字泉ケ入87-2（大雄寺）"),
        ("伊達実元霊屋", "有形文化財（建造物）", "字泉ケ入87-2（大雄寺）"),
        ("湊神社社殿", "有形文化財（建造物）", "荒浜字水倉113-2"),
        ("安福河伯神社本殿", "有形文化財（建造物）", "逢隈田沢字堰下220"),
        ("萬松山大雄寺山門", "有形文化財（建造物）", "字泉ケ入93（大雄寺）"),
        ("亘理領主伊達氏歴代墓所", "史跡", "字泉ケ入87-2（大雄寺）"),
        ("亘理枡取り舞", "無形民俗文化財（芸能）", "亘理地区"),
        ("牛袋法印神楽", "無形民俗文化財（芸能）", "逢隈牛袋地区"),
        ("亘理獅子舞", "無形民俗文化財（芸能）", "亘理地区"),
    ]
    return [
        row("亘理町", name, category_from_subcategory(sub), sub, "町指定", source, "pdf", location=location)
        for name, sub, location in items
    ]


def rifu_rows():
    source = "https://www.town.rifu.miyagi.jp/gyosei/soshikikarasagasu/syougai/bunka/3558.html"
    items = [
        ("朝顔形埴輪", "有形文化財（考古資料）", "郷楽遺跡"),
        ("直刀ほか鉄製品一式", "有形文化財（考古資料）", "川袋古墳群"),
        ("軒丸瓦", "有形文化財（考古資料）", "大貝窯跡"),
    ]
    return [
        row("利府町", name, "有形文化財", sub, "町指定", source, "html", location=location)
        for name, sub, location in items
    ]


def yamamoto_rows():
    source = "https://www.town.yamamoto.miyagi.jp/soshiki/20/26854.html"
    return [
        row("山元町", "大條家茶室 此君亭", "有形文化財", "有形文化財（建造物）", "町指定", source, "html", location="山元町坂元字舘下／坂本要害（蓑首城）三ノ丸跡")
    ]


def zero_rows():
    return {
        "tomiya": [],
        "shichikashuku": [],
        "kawasaki": [],
        "shichigahama": [],
        "osato": [],
        "misato": [],
    }


def write_new_parts():
    generators = {
        "zao": zao_rows,
        "ogawara": ogawara_rows,
        "marumori": marumori_rows,
        "watari": watari_rows,
        "rifu": rifu_rows,
        "yamamoto": yamamoto_rows,
        "kami": parse_kami,
        "minamisanriku": parse_minamisanriku,
    }
    counts = {}
    for slug, func in generators.items():
        rows = func()
        write_part(slug, rows)
        counts[slug] = len(rows)
    for slug, rows in zero_rows().items():
        write_part(slug, rows)
        counts[slug] = 0
    return counts


def load_dataeye_coverage():
    path = WORK / "dataeye_coverage.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def count_lines(path):
    return sum(1 for _ in path.open(encoding="utf-8"))


def merge_parts():
    out = ROOT / "data" / "miyagi.jsonl"
    with out.open("w", encoding="utf-8") as dest:
        for slug, _municipality in ORDER:
            part = PARTS / f"{slug}.jsonl"
            if not part.exists():
                raise FileNotFoundError(part)
            with part.open(encoding="utf-8") as src:
                for line in src:
                    if line.strip():
                        json.loads(line)
                        dest.write(line)
    for line in out.read_text(encoding="utf-8").splitlines():
        json.loads(line)
    return out


def write_coverage():
    dataeye = load_dataeye_coverage()
    rows_by_slug = {slug: count_lines(PARTS / f"{slug}.jsonl") for slug, _ in ORDER}
    rows_total = sum(rows_by_slug.values())
    extracted_munis = sum(1 for count in rows_by_slug.values() if count > 0)
    manual_excluded = {
        "角田市": {"national": 5, "pref": 6, "registered": 2},
        "岩沼市": {"national": 3, "pref": 3, "registered": 1},
        "富谷市": {"national": 0, "pref": 0, "registered": 1},
        "利府町": {"national": 0, "pref": 0, "registered": 0},
        "亘理町": {"national": 2, "pref": 8, "registered": 0},
        "大和町": {"national": 4, "pref": 4, "registered": 0},
        "大河原町": {"national": 1, "pref": 0, "registered": 1},
        "加美町": {"national": 5, "pref": 7, "registered": 2},
        "美里町": {"national": 0, "pref": 0, "registered": 0},
        "蔵王町": {"national": 1, "pref": 3, "registered": 0},
        "川崎町": {"national": 0, "pref": 0, "registered": 0},
        "丸森町": {"national": 0, "pref": 3, "registered": 2},
        "山元町": {"national": 0, "pref": 0, "registered": 0},
        "七ヶ浜町": {"national": 1, "pref": 0, "registered": 0},
        "大郷町": {"national": 0, "pref": 0, "registered": 0},
        "色麻町": {"national": 1, "pref": 2, "registered": 0},
        "女川町": {"national": 0, "pref": 1, "registered": 0},
        "南三陸町": {"national": 2, "pref": 5, "registered": 1},
        "七ヶ宿町": {"national": 0, "pref": 0, "registered": 0},
    }
    sources = {
        "仙台市": ("https://miyagi.dataeye.jp/resources/903", "csv", "0", "easy", "Open-data CSV. 市登録 rows were excluded because task scope is designated only."),
        "石巻市": ("https://miyagi.dataeye.jp/resources/32363", "csv", "0", "easy", "Open-data CSV; municipal rows extracted, 国/県/登録 excluded."),
        "大崎市": ("https://miyagi.dataeye.jp/resources/496", "csv", "0", "easy", "Open-data CSV; 国登録 rows excluded."),
        "登米市": ("https://miyagi.dataeye.jp/resources/32596", "csv", "0", "easy", "Open-data CSV; 市指定有形文化財 rows extracted."),
        "栗原市": ("https://miyagi.dataeye.jp/resources/1393", "csv", "0", "easy", "Open-data CSV; all 市指定 classes extracted."),
        "名取市": ("https://miyagi.dataeye.jp/resources/1200", "csv", "0", "easy", "Open-data CSV; all 市指定 classes extracted."),
        "多賀城市": ("https://miyagi.dataeye.jp/resources/718", "csv", "0", "easy", "Open-data CSV; all 市指定 classes extracted."),
        "気仙沼市": ("https://miyagi.dataeye.jp/resources/916", "csv", "0", "easy", "Open-data CSV; all 市指定 classes extracted."),
        "岩沼市": ("https://www.city.iwanuma.miyagi.jp/kanko/bunkazai/shitei-ichiran.html", "html", "0", "done", "Already completed before this task; file was left unchanged."),
        "富谷市": ("https://www.tomiya-city.miyagi.jp/bunka/rekishi/", "html", "unknown", "hard", "Official history/culture page and sitemap checked; no municipal-designated list found."),
        "白石市": ("https://miyagi.dataeye.jp/resources/1189", "csv", "0", "medium", "Open-data CSV; ambiguous 指定有形文化財 rows treated as city-designated after official page context."),
        "東松島市": ("https://miyagi.dataeye.jp/resources/736", "csv", "0", "easy", "Open-data CSV; all 市指定 rows extracted."),
        "塩竈市": ("https://miyagi.dataeye.jp/resources/866", "csv", "0", "easy", "Open-data CSV; all 市指定 rows extracted."),
        "角田市": ("https://www.city.kakuda.lg.jp/soshiki/31/1108.html", "html", "0", "easy", "Official HTML table; city rows match table count."),
        "柴田町": ("https://miyagi.dataeye.jp/resources/32930", "csv", "0", "medium", "Open-data CSV; unprefixed 史跡/天然記念物 included as town rows because県 rows were separately labeled."),
        "利府町": ("https://www.town.rifu.miyagi.jp/gyosei/soshikikarasagasu/syougai/bunka/3558.html", "html", "unknown", "medium", "Museum exhibit page identifies red/marked entries as 町指定; three explicit town-designated exhibit items extracted, no full register found."),
        "亘理町": ("https://www.town.watari.miyagi.jp/common/img/content/content_20260407_093050.pdf", "pdf", "0", "easy", "Clean PDF table; rows 11-19 are町指定, 国/県 rows excluded."),
        "大和町": ("https://www.town.taiwa.miyagi.jp/soshiki/shogaigakushu/bunkazai/1123.html", "html", "0", "done", "Already completed before this task; file was left unchanged."),
        "大河原町": ("https://www.town.ogawara.miyagi.jp/1800.htm", "html", "0", "easy", "Official page lists three 町指定 items; 国指定 and 国登録 items excluded."),
        "松島町": ("https://miyagi.dataeye.jp/resources/854", "csv", "0", "medium", "Open-data CSV had many blank rows; 101町指定文化財 rows extracted."),
        "加美町": ("https://www.town.kami.miyagi.jp/kanko_sports_bunka/rekishi_bunkazai/1176.html", "html", "0", "easy", "Official HTML tables; table 町指定文化財 extracted, 国/国登録/国選択/県 tables excluded."),
        "涌谷町": ("https://miyagi.dataeye.jp/resources/919", "csv", "0", "medium", "Open-data Excel resource parsed via workbook XML; town-designated rows extracted."),
        "美里町": ("https://www.town.misato.miyagi.jp/06kyoiku/education/2014-0912-1110-32.html", "html", "unknown", "hard", "Official education pages checked; no municipal-designated list found online."),
        "蔵王町": ("https://www.town.zao.miyagi.jp/kurashi_guide/kyoiku_bunka/rekisitobunkazai/index.html", "html", "0", "medium", "Official town page links the external町指定 list and announces four 2025 additions; total 30 matches official statement."),
        "村田町": ("https://miyagi.dataeye.jp/resources/263", "csv", "0", "easy", "Open-data CSV;町指定 rows extracted, one ambiguous class excluded."),
        "川崎町": ("https://www.town.kawasaki.miyagi.jp/life/4/21/", "html", "unknown", "hard", "Official history/culture category checked; no municipal-designated list found."),
        "丸森町": ("https://www.town.marumori.miyagi.jp/education/detail.php?content=69", "html", "0", "easy", "Official page states町指定28; extracted all 28 listed items."),
        "山元町": ("https://www.town.yamamoto.miyagi.jp/soshiki/20/26854.html", "html", "unknown", "medium", "Official page for one町指定 cultural property; no full register found."),
        "七ヶ浜町": ("https://www.shichigahama.com/history/index.html", "html", "unknown", "hard", "Official history/museum pages checked; no municipal-designated list found."),
        "大郷町": ("https://www.town.miyagi-osato.lg.jp/soshiki/kyouiku/kyoikuinkai-niteigijioku.html", "html", "unknown", "hard", "Official pages checked; no municipal-designated list found online."),
        "色麻町": ("https://www.town.shikama.miyagi.jp/soshiki/shakai_kyoiku/8/461.html", "html", "unknown", "medium", "Only one町指定 item found on official source; no full list found."),
        "女川町": ("https://www.town.onagawa.miyagi.jp/03_00_09.html", "html", "unknown", "medium", "Official narrative page yielded three町指定 items; dates not published."),
        "南三陸町": ("https://www.town.minamisanriku.miyagi.jp/bunka-sports/rekishi-bunkazai/1/6494.html", "html", "0", "easy", "Official full list page; town tables extracted, 国/国登録/県 tables excluded."),
        "七ヶ宿町": ("https://town.shichikashuku.miyagi.jp/", "html", "unknown", "hard", "Official site and sitemap checked; no municipal-designated list found."),
        "大衡村": ("https://miyagi.dataeye.jp/resources/1032", "csv", "0", "easy", "Open-data CSV; all村指定 rows extracted."),
    }
    lines = [
        "# Coverage - 宮城県 市町村指定文化財",
        "",
        "Snapshot date: 2026-07-03. Dataset: `data/miyagi.jsonl`.",
        "All rows are 市町村指定 only; 国指定・県指定・国登録 rows were excluded from the dataset and counted where observed.",
        "",
        "## Per-municipality table",
        "",
        "| # | Municipality | Source URL | Format | Rows | Missed estimate | Difficulty | Note |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for idx, (slug, municipality) in enumerate(ORDER, start=1):
        source, fmt, missed, difficulty, note = sources[municipality]
        lines.append(f"| {idx} | {municipality} | {source} | {fmt} | {rows_by_slug[slug]} | {missed} | {difficulty} | {note} |")
    observed = {}
    national = pref = registered = 0
    for municipality, payload in dataeye.items():
        ex = payload.get("excluded", {})
        observed[municipality] = ex
    for municipality, ex in manual_excluded.items():
        observed[municipality] = ex
    for ex in observed.values():
        national += int(ex.get("national", 0))
        pref += int(ex.get("pref", 0))
        registered += int(ex.get("registered", 0))
    csv_rows = sum(rows_by_slug[s] for s, m in ORDER if sources[m][1] == "csv")
    html_rows = sum(rows_by_slug[s] for s, m in ORDER if sources[m][1] == "html")
    pdf_rows = sum(rows_by_slug[s] for s, m in ORDER if sources[m][1] == "pdf")
    lines.extend(
        [
            "",
            "## Totals",
            "",
            f"- Municipalities with >=1 extracted entry: {extracted_munis} / 35 ({extracted_munis / 35:.0%}).",
            f"- Total properties extracted: {rows_total}.",
            f"- Format mix by row: csv {csv_rows} / html {html_rows} / pdf {pdf_rows}.",
            "- Zero-row municipalities: 富谷市, 美里町, 川崎町, 七ヶ浜町, 大郷町, 七ヶ宿町.",
            f"- National / prefectural / registered counts observed and excluded: 国 {national}, 県 {pref}, 登録 {registered}.",
            "",
            "## National / prefectural counts observed",
            "",
        ]
    )
    parts = []
    for _slug, municipality in ORDER:
        ex = observed.get(municipality, {})
        parts.append(f"{municipality} 国{int(ex.get('national', 0))}/県{int(ex.get('pref', 0))}/登録{int(ex.get('registered', 0))}")
    lines.append(" · ".join(parts) + ".")
    (ROOT / "notes" / "coverage-miyagi.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    counts = write_new_parts()
    merged = merge_parts()
    write_coverage()
    print("generated", json.dumps(counts, ensure_ascii=False, sort_keys=True))
    print("merged", merged, count_lines(merged))


if __name__ == "__main__":
    main()
