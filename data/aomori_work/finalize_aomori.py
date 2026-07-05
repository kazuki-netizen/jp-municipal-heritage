import html
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from collect_lib import PARTS, ROOT, WORK, row, validate_jsonl, wareki, write_jsonl


MUNICIPALITIES = [
    ("aomori", "青森市"),
    ("hirosaki", "弘前市"),
    ("hachinohe", "八戸市"),
    ("kuroishi", "黒石市"),
    ("goshogawara", "五所川原市"),
    ("towada", "十和田市"),
    ("misawa", "三沢市"),
    ("mutsu", "むつ市"),
    ("tsugaru", "つがる市"),
    ("hirakawa", "平川市"),
    ("hiranai", "平内町"),
    ("imabetsu", "今別町"),
    ("yomogita", "蓬田村"),
    ("sotogahama", "外ヶ浜町"),
    ("ajigasawa", "鰺ヶ沢町"),
    ("fukaura", "深浦町"),
    ("nishimeya", "西目屋村"),
    ("fujisaki", "藤崎町"),
    ("owani", "大鰐町"),
    ("inakadate", "田舎館村"),
    ("itayanagi", "板柳町"),
    ("tsuruta", "鶴田町"),
    ("nakadomari", "中泊町"),
    ("noheji", "野辺地町"),
    ("shichinohe", "七戸町"),
    ("rokunohe", "六戸町"),
    ("yokohama", "横浜町"),
    ("tohoku", "東北町"),
    ("rokkasho", "六ヶ所村"),
    ("oirase", "おいらせ町"),
    ("oma", "大間町"),
    ("higashidori", "東通村"),
    ("kazamaura", "風間浦村"),
    ("sai", "佐井村"),
    ("sannohe", "三戸町"),
    ("gonohe", "五戸町"),
    ("takko", "田子町"),
    ("nanbu", "南部町"),
    ("hashikami", "階上町"),
    ("shingo", "新郷村"),
]


def clean(s):
    if s is None:
        return None
    s = html.unescape(str(s))
    s = re.sub(r"[\u3000\xa0]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or None


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def promote(romaji, source_name):
    rows = read_jsonl(ROOT / "data" / source_name)
    write_jsonl(romaji, rows)


def short_date(s):
    if not s:
        return None
    t = str(s).strip()
    t = re.sub(r"\(.*?\)", "", t)
    m = re.search(r"(\d{4})[./-](\d{1,2})[./-](\d{1,2})", t)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r"([MTSHR])(\d+)[.年](\d{1,2})[.月](\d{1,2})", t, re.I)
    if m:
        base = {"M": 1867, "T": 1911, "S": 1925, "H": 1988, "R": 2018}[m.group(1).upper()]
        return f"{base + int(m.group(2)):04d}-{int(m.group(3)):02d}-{int(m.group(4)):02d}"
    return wareki(t)


def html_tables(path):
    text = Path(path).read_text(encoding="utf-8")
    tables = []
    for table in re.findall(r"<table\b.*?</table>", text, flags=re.S | re.I):
        rows = []
        for tr in re.findall(r"<tr\b.*?</tr>", table, flags=re.S | re.I):
            cells = []
            for c in re.findall(r"<t[dh]\b.*?</t[dh]>", tr, flags=re.S | re.I):
                s = html.unescape(re.sub(r"<[^>]+>", " ", c))
                s = re.sub(r"[\u3000\xa0]+", " ", s)
                s = re.sub(r"\s+", " ", s).strip()
                cells.append(s)
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def write_sotogahama():
    source = "https://www.town.sotogahama.lg.jp/bunka/bunka/files/bunkazaiichiran_20250926.pdf"
    specs = [
        ("武者絵懸額", "有形文化財", "1995-12-18", "外ヶ浜町蟹田大平山元"),
        ("付合い句懸額", "有形文化財", "1995-12-18", "外ヶ浜町蟹田田ノ沢"),
        ("漁労懸額", "有形文化財", "1995-12-18", "外ヶ浜町蟹田塩越"),
        ("赤平清兵衛塔", "有形文化財", "1995-12-18", "外ヶ浜町蟹田塩越"),
        ("蟹田奉行所跡", "史跡", "1995-12-18", "外ヶ浜町蟹田上蟹田"),
        ("外ケ浜道跡（あかふら峠）", "史跡", "1995-12-18", "外ヶ浜町蟹田塩越"),
        ("鍛冶屋の一本松", "名勝", "1995-12-18", "外ヶ浜町蟹田鰐ヶ淵"),
        ("皀莢", "名勝", "1995-12-18", "外ヶ浜町蟹田小国山崎"),
        ("専念寺山門と仁王尊像", "有形文化財", "2002-05-10", "外ヶ浜町蟹田下蟹田"),
        ("外ケ浜道跡（観瀾山下）", "史跡", "2002-05-10", "外ヶ浜町蟹田中師宮本"),
        ("東風留舘跡", "史跡", "2002-05-10", "外ヶ浜町蟹田塩越"),
        ("観音菩薩坐像", "有形文化財", "1989-03-31", "外ヶ浜町平舘門の沢"),
        ("推定樹齢600年の黒松「長寿の松」", "天然記念物", "2001-08-02", "外ヶ浜町平舘田の沢"),
        ("夫婦松", "天然記念物", "2001-08-02", "外ヶ浜町平舘田の沢"),
        ("藤嶋の藤", "天然記念物", "1985-02-01", "外ヶ浜町宇鉄藤嶋"),
        ("荒馬", "無形民俗文化財", "1985-02-01", "外ヶ浜町三厩増川"),
        ("太刀振", "無形民俗文化財", "2008-03-19", "外ヶ浜町三厩下平5-1（外ヶ浜町立三厩中学校）"),
        ("平舘陣屋跡（お仮屋）", "史跡", "2018-03-31", "外ヶ浜町平舘門の沢"),
    ]
    write_jsonl(
        "sotogahama",
        [row("外ヶ浜町", name, subcat, "町指定", date, loc, source, "pdf") for name, subcat, date, loc in specs],
    )


def write_ajigasawa():
    source = "https://www.town.ajigasawa.lg.jp/kyoiku_shogai/bunka_rekishi/bunkazai/ajigasawabunkazai.html"
    table = html_tables(WORK / "ajigasawa_bunkazai.html")[2]
    rows = []
    for cells in table:
        if not cells[0].isdigit():
            continue
        name = clean(cells[1].replace("（外部サイト）", ""))
        rows.append(row("鰺ヶ沢町", name, cells[2], "町指定", wareki(cells[5]), cells[4], source, "html"))
    write_jsonl("ajigasawa", rows)


def write_imabetsu():
    base = "https://www.town.imabetsu.lg.jp/education/bunka/"
    specs = [
        ("今別荒馬", "無形民俗文化財", "1980-02-01", "〒030-1502 今別町大字今別字今別", "arauma.html"),
        ("大川平荒馬", "無形民俗文化財", "1980-02-01", "〒030-1505 今別町大字大川平", "arauma.html"),
        ("二股荒馬", "無形民俗文化財", "1986-07-26", "〒030-1505 今別町大字大川平字二股", "arauma.html"),
        ("大銀杏の木", "有形文化財－天然記念物", "1980-02-01", "〒030-1505 今別町大字大川平字村元", "ginnan.html"),
        ("大開城跡", "有形文化財－史跡", "1981-05-11", "〒030-1505 今別町大川平字西大川平山国有林", "oobiraki.html"),
        ("今別八幡宮狛犬2対", "有形文化財－彫刻", "1986-05-01", "〒030-1502 今別町大字今別字今別", "hachiman.html"),
        ("貞伝上人作石佛", "有形文化財－彫刻", "1986-05-01", "〒030-1502 今別町大字今別字今別119", "ishi.html"),
        ("善導大師・圓光大師の座像", "有形文化財－彫刻", "1990-03-30", "〒030-1501 今別町大字浜名字浜名", "zazou.html"),
        ("鉦鼓", "有形文化財－工芸品", "1990-03-30", "〒030-1501 今別町大字浜名字浜名", "shoko.html"),
        ("石仏薬師如来像", "有形文化財－彫刻", "1990-03-30", "〒030-1502 今別町大字今別字西田", "nyorai.html"),
        ("愍栄上人作観音像", "有形文化財－彫刻", "1990-03-30", "〒030-1505 今別町大字大川平字二股", "kannon.html"),
        ("阿弥陀如来像貞伝金仏（貞伝万体仏）", "有形文化財－彫刻", "2018-04-27", None, "2018-0601-0930-1.html"),
        ("船絵馬", "有形文化財－民俗文化財", "1990-03-30", "〒030-1513 今別町大字袰月字袰村元", "ema.html"),
        ("ホウノキ", "有形文化財－天然記念物", "1990-03-20", "〒030-1501 今別町大字浜名字浜名", "hounoki.html"),
        ("ハリギリ", "有形文化財－天然記念物", "2017-05-30", "〒030-1504 今別町大字鍋田字関口1", "harigiri.html"),
    ]
    write_jsonl(
        "imabetsu",
        [row("今別町", name, subcat, "町指定", date, loc, base + slug, "html") for name, subcat, date, loc, slug in specs],
    )


def write_inakadate():
    source = "http://www.vill.inakadate.lg.jp/docs/2012022300370/"
    names = [
        "垂柳獅子踊り",
        "田舎舘城址",
        "サイカチ大樹",
        "二本柳一族の墓碑",
        "中村喜時の資料と家筋関係資料",
        "極楽寺大日堂文書",
        "エゾエノキ大樹",
        "嘉暦の古碑",
        "二津屋の板碑",
        "中村喜時著「耕作噺」",
    ]
    write_jsonl("inakadate", [row("田舎館村", name, None, "村指定", None, None, source, "html") for name in names])


def write_yokohama():
    source = "https://www.town.yokohama.lg.jp/index.cfm/16,1549,17,128,html"
    specs = [
        ("岩倉不動尊", "史跡", "S58.9.20"),
        ("牛ノ沢舘跡", "史跡", "S58.9.20"),
        ("桧木在八幡神社 海浜殖生自然林", "天然記念物", "S60.3.20"),
        ("神明宮跡地大ケヤキ", "天然記念物", "S61.8.29"),
        ("下北の能舞（塚名平神楽会）", "無形民俗", "H11.2.23"),
        ("横浜町の獅子舞（浜町神楽会）", "無形民俗", "H11.2.23"),
        ("横浜町の神楽（舘町神楽会）", "無形民俗", "H14.7.9"),
        ("横浜町の神楽（新丁神楽会）", "無形民俗", "H14.7.9"),
        ("横浜町の南部手踊り（横浜町南部手踊保存会）", "無形民俗", "H14.7.9"),
        ("八幡神社 社殿", "有形", "H30.4.1"),
        ("八幡神社 神幸祭", "無形民俗", "H30.4.1"),
        ("ホオジロザメの歯の有孔装身具", "有形", "R5.3.1"),
        ("獣面突起付土器", "有形", "R5.3.1"),
    ]
    write_jsonl(
        "yokohama",
        [row("横浜町", name, subcat, "町指定", short_date(date), None, source, "html") for name, subcat, date in specs],
    )


def write_sai():
    source = "https://www.vill.sai.lg.jp/about-saimura/history-culture/"
    specs = [
        ("廻船卸客帳 一帖", "有形文化財（歴史資料）"),
        ("鉄扇 一柄", "有形文化財（歴史資料）"),
        ("菅江真澄直筆 三葉", "有形文化財（書籍）"),
        ("菅江真澄直筆 一葉", "有形文化財（書籍）"),
        ("蓑虫山人の書 一幅", "有形文化財（書籍）"),
        ("勝海舟の書 ニ幅", "有形文化財（書籍）"),
        ("蓑虫山人の絵 三帖", "有形文化財（絵画）"),
        ("蓑虫山人の絵 六帖", "有形文化財（絵画）"),
        ("オシラサマ 二躯", "有形文化財（信仰）"),
    ]
    write_jsonl("sai", [row("佐井村", name, subcat, "村指定", None, None, source, "html") for name, subcat in specs])


def write_noheji():
    specs = [
        ("野辺地の山車行事", "無形民俗文化財", "https://www.town.noheji.aomori.jp/kanko/spot/0175"),
        ("客船帳", "有形文化財", "https://www.town.noheji.aomori.jp/kanko/spot/824"),
        ("西光寺のしだれ桜", "天然記念物", "https://www.town.noheji.aomori.jp/kanko/spot/375"),
        ("松尾芭蕉の句碑", "有形文化財", "https://www.town.noheji.aomori.jp/kanko/spot/371"),
        ("花鳥号銅像", "有形文化財", "https://www.town.noheji.aomori.jp/kanko/spot/370"),
        ("本州最北にあるエドヒガン", "天然記念物", "https://www.town.noheji.aomori.jp/kanko/spot/369"),
        ("常夜燈", "史跡", "https://www.town.noheji.aomori.jp/kanko/spot/293"),
    ]
    write_jsonl("noheji", [row("野辺地町", name, subcat, "町指定", None, None, source, "html") for name, subcat, source in specs])


def takko_field(block, pattern):
    lines = block.splitlines()
    for i, line in enumerate(lines):
        if re.search(pattern, line):
            val = line.split("／", 1)[1].strip() if "／" in line else ""
            j = i + 1
            while j < len(lines):
                nxt = lines[j].strip()
                if not nxt or "／" in nxt or nxt.startswith("★") or nxt.startswith("■"):
                    break
                val += " " + nxt
                j += 1
            return clean(val)
    return None


def takko_subcategory(raw):
    raw = clean(raw)
    if raw is None:
        return None
    m = re.search(r"（([^）]+)）", raw)
    if m:
        return m.group(1)
    return raw.replace("町指定", "").replace("文化財", "").strip() or raw


def write_takko():
    url_map = {
        "chokoku": "https://www.town.takko.lg.jp/index.cfm/11,154,34,159,html",
        "shiryo": "https://www.town.takko.lg.jp/index.cfm/11,155,34,159,html",
        "shiseki": "https://www.town.takko.lg.jp/index.cfm/11,156,34,159,html",
        "kenzo": "https://www.town.takko.lg.jp/index.cfm/11,157,34,159,html",
        "mukei": "https://www.town.takko.lg.jp/index.cfm/11,158,34,159,html",
    }
    rows = []
    for key, source in url_map.items():
        text = (WORK / f"takko_{key}.txt").read_text(encoding="utf-8")
        for block in re.split(r"(?=★)", text):
            if not block.lstrip().startswith("★"):
                continue
            first = clean(block.splitlines()[0].replace("★", ""))
            subcat = takko_subcategory(takko_field(block, r"種\s*別"))
            date = short_date(takko_field(block, r"(?:指定|選定)年月日"))
            loc = takko_field(block, r"所\s*在\s*地")
            rows.append(row("田子町", first, subcat, "町指定", date, loc, source, "pdf"))
    write_jsonl("takko", rows)


def write_hashikami():
    rows = [
        row(
            "階上町",
            "栁沢家のアサダ",
            "天然記念物",
            "町指定",
            "2017-03-27",
            "角柄折字柳平",
            "https://www.town.hashikami.lg.jp/index.cfm/6,8,80,html",
            "html",
        ),
        row(
            "階上町",
            "道仏神楽",
            "無形民俗文化財",
            "町指定",
            "2008-03-21",
            None,
            "https://www.town.hashikami.lg.jp/index.cfm/6,1400,80,html",
            "html",
        ),
    ]
    write_jsonl("hashikami", rows)


def write_shingo():
    source = "https://www.vill.shingo.aomori.jp/public/ikujikyouiku/kyouiku_main/page-27153/"
    table = html_tables(WORK / "shingo_bunkazai.html")[2]
    rows = []
    for cells in table:
        if not cells[0].startswith("第") or cells[4]:
            continue
        name = "三嶽神社御神木欅" if cells[1] == "三嶽神社御木欅" else cells[1]
        rows.append(row("新郷村", name, cells[2], "村指定", short_date(cells[3]), cells[5], source, "html"))
    write_jsonl("shingo", rows)


def write_sannohe():
    source = "https://www.town.sannohe.aomori.jp/soshiki/kyouikuiinkaijimukyoku/rekishi_bunka/1/1767.html"
    write_jsonl(
        "sannohe",
        [
            row(
                "三戸町",
                "弘法大師坐像",
                None,
                "町指定",
                None,
                "三戸町同心町字諏訪内",
                source,
                "html",
                description="悟真寺ページ内で江戸時代（町指定文化財）と記載。指定年月日・種別は未掲載。",
            )
        ],
    )


def merge_all():
    merged = []
    missing = []
    for romaji, _ in MUNICIPALITIES:
        path = PARTS / f"{romaji}.jsonl"
        if not path.exists():
            missing.append(romaji)
            continue
        validate_jsonl(path)
        merged.extend(read_jsonl(path))
    if missing:
        raise RuntimeError(f"missing part files: {missing}")
    out = ROOT / "data" / "aomori.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for r in merged:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    validate_jsonl(out)
    return merged


def coverage_rows(counts):
    notes = {
        "aomori": ("青森市オープンデータCSV", "csv", "0?", "easy", "CSVから市指定31件を抽出。国・県・登録を除外。"),
        "hirosaki": ("弘前市HP 市指定文化財一覧", "html", "few", "medium", "既存抽出118件。"),
        "hachinohe": ("八戸市HP 指定文化財一覧", "html", "few", "medium", "既存抽出66件。"),
        "kuroishi": ("黒石市HP カテゴリ別一覧", "html", "few", "medium", "既存抽出34件。"),
        "goshogawara": ("五所川原市HP 指定文化財一覧", "html", "few", "medium", "既存抽出23件。"),
        "towada": ("十和田市HP 指定文化財一覧", "html", "few", "medium", "既存抽出31件。"),
        "misawa": ("三沢市HP/PDF", "html+pdf", "few", "medium", "既存抽出22件。"),
        "mutsu": ("むつ市HP 個別PDF", "pdf", "few", "medium", "既存抽出28件。"),
        "tsugaru": ("つがる市HP", "html", "few", "medium", "既存抽出14件。"),
        "hirakawa": ("平川市HP 指定文化財一覧", "html", "few", "medium", "既存抽出71件。"),
        "hiranai": ("平内町HP 町文化財", "html", "1解除除外", "easy", "現行8件。解除済み1件を除外。"),
        "imabetsu": ("今別町HP 文化財個別ページ", "html", "0?", "medium", "町指定日が別記された県指定荒馬を町指定日で収録。県指定のみ2件は除外。"),
        "yomogita": ("none found", "none", "unknown", "hard", "公式歴史・観光ページ確認、村指定一覧なし。"),
        "sotogahama": ("外ヶ浜町 指定文化財一覧PDF", "pdf", "0", "easy", "PDF内の町指定18件を抽出。県・国行を除外。"),
        "ajigasawa": ("鰺ヶ沢町HP 指定文化財一覧", "html", "0", "easy", "町指定セクションNo.6-52の47件。国1・県4を除外。"),
        "fukaura": ("none found", "none", "unknown", "hard", "公式観光・歴史カテゴリに町指定一覧なし。"),
        "nishimeya": ("none found", "none", "unknown", "hard", "公式文化ページ確認、村指定一覧なし。"),
        "fujisaki": ("none found", "none", "unknown", "hard", "公式ガイド・教育・例規系ページを確認、町指定一覧なし。"),
        "owani": ("none found", "none", "unknown", "hard", "公式観光・教育ページに町指定一覧なし。"),
        "inakadate": ("田舎館村HP 文化財の状況", "html", "0?", "medium", "村指定名のみ10件。日付・種別・所在地は未掲載。国1・県3を除外。"),
        "itayanagi": ("板柳町HP 指定文化財一覧", "html", "few", "medium", "既存抽出18件。"),
        "tsuruta": ("鶴田町観光サイト", "html", "unknown", "hard", "町指定と明記された1件のみ。公式町サイトに平面一覧なし。"),
        "nakadomari": ("none found", "none", "unknown", "hard", "公式文化財ページは方針テキストのみで一覧なし。"),
        "noheji": ("野辺地町観光文化ページ", "html", "unknown", "hard", "町指定ラベルがある個別観光ページ7件のみ。全台帳は未確認。"),
        "shichinohe": ("none found", "none", "unknown", "hard", "公式・観光検索確認、町指定一覧なし。"),
        "rokunohe": ("none found", "none", "unknown", "hard", "公式文化施設カテゴリ確認、町指定一覧なし。"),
        "yokohama": ("横浜町HP 各種指定文化財", "html", "0", "easy", "町指定13件。国1・県3を除外。"),
        "tohoku": ("東北町HP 日本中央の碑", "html", "unknown", "hard", "町指定と明記された1件のみ。全台帳は未確認。"),
        "rokkasho": ("none found", "none", "unknown", "hard", "公式文化関連ページに村指定一覧なし。"),
        "oirase": ("おいらせ町HP 個別ページ", "html", "unknown", "hard", "既存抽出3件。全台帳は未確認。"),
        "oma": ("none found", "none", "unknown", "hard", "公式教育・観光ページに町指定一覧なし。"),
        "higashidori": ("東通村HP 民俗芸能ページ", "html", "unknown", "hard", "公式ページは国・県指定のみで村指定なし。"),
        "kazamaura": ("none found", "none", "unknown", "hard", "公式歴史・観光ページに村指定一覧なし。"),
        "sai": ("佐井村HP 歴史・文化", "html", "0?", "medium", "村指定9件。国3・県4を除外。日付・所在地は未掲載。"),
        "sannohe": ("三戸町HP 町の歴史と文化財", "html", "unknown", "hard", "明示的な町指定1件のみ。多くのリンクは県重宝・国登録等。"),
        "gonohe": ("五戸町HP 文化財", "html", "unknown", "hard", "町指定と明記された2件のみ。全台帳は未確認。"),
        "takko": ("田子町HP 町指定文化財PDF群", "pdf", "0", "easy", "5分類PDFから33件。国2・県6を除外。"),
        "nanbu": ("南部町HP 文化財CSV/一覧", "csv", "few", "medium", "既存抽出78件。"),
        "hashikami": ("階上町HP 文化財カテゴリ", "html", "0?", "medium", "町指定2件。国3・県7を除外。"),
        "shingo": ("新郷村HP 文化財表", "html", "0", "easy", "解除済み4件を除外し現行21件。国登録2・県1を除外。"),
    }
    lines = []
    for i, (romaji, name) in enumerate(MUNICIPALITIES, 1):
        source, fmt, missed, difficulty, note = notes[romaji]
        lines.append(f"| {i} | {name} | {source} | {fmt} | {counts.get(romaji, 0)} | {missed} | {difficulty} | {note} |")
    return lines


def write_coverage(rows):
    counts = Counter()
    for romaji, name in MUNICIPALITIES:
        path = PARTS / f"{romaji}.jsonl"
        counts[romaji] = sum(1 for _ in path.open(encoding="utf-8"))

    fmt_mix = Counter(r["source_format"] for r in rows)
    cat_mix = Counter(r["category"] for r in rows)
    date_count = sum(1 for r in rows if r.get("designated_date"))
    active_munis = sum(1 for c in counts.values() if c)
    total = len(rows)
    notes_dir = ROOT / "notes"
    notes_dir.mkdir(exist_ok=True)
    lines = [
        "# Coverage — 青森県 市町村指定文化財",
        "",
        f"Snapshot date: 2026-07-04. Dataset: `data/aomori.jsonl` (**{total:,} rows**).",
        "All rows are 市町村指定 only; 国指定・県指定・国登録 rows were excluded from the dataset and counted below when observed.",
        "",
        "This page is deliberately honest about incomplete web coverage. Some small municipalities publish only tourism item pages or no flat municipal register online; those are marked as hard/unknown instead of silently treated as complete.",
        "",
        "## Per-municipality table",
        "",
        "| # | Municipality | Source (definitive list) | Format | Extracted | Likely missed | Difficulty | Notes |",
        "|---|---|---|---|---:|---:|---|---|",
        *coverage_rows(counts),
        "",
        "## Totals",
        "",
        f"- **Municipalities with ≥1 extracted entry: {active_munis} / 40 ({active_munis / 40:.0%})**",
        f"- **Total municipal-designated properties extracted: {total:,}.**",
        "- Format mix of extracted rows: "
        + " / ".join(f"{k} {v:,}" for k, v in sorted(fmt_mix.items())),
        "- Category mix: "
        + " / ".join(f"{k} {v:,}" for k, v in sorted(cat_mix.items())),
        f"- **Date coverage: {date_count:,} / {total:,} rows have a normalized 西暦 date ({date_count / total:.0%}).**",
        "",
        "## National / prefectural counts observed (excluded from dataset)",
        "",
        "青森市 CSV non-municipal rows 53（国・県・登録混在） · 鰺ヶ沢 国1/県4 · 外ヶ浜 県2/国3 · 横浜 国1/県3 · 田舎館 国1/県3 · 佐井 国3/県4 · 田子 国2/県6 · 階上 国3/県7 · 新郷 国登録2/県1 · 三戸 observed 国2+/県6+.",
        "",
        "## Known quality caveats",
        "",
        "- 野辺地町・東北町・鶴田町・五戸町・三戸町は、公式サイト上で町指定と明記された個別ページだけを収録しており、完全な台帳がオンラインにあるとは確認できていない。",
        "- 田舎館村・佐井村は公式ページが名称リストのみで、指定年月日・所在地の未掲載項目が多い。",
        "- 藤崎・蓬田・深浦・西目屋・大鰐・中泊・七戸・六戸・六ヶ所・大間・東通・風間浦は、公式ページを確認した範囲で市町村指定一覧を発見できなかったため honest zero とした。",
        "- 解除済みとして明記された行は収録しなかった（平内1、新郷4など）。",
        "",
    ]
    (notes_dir / "coverage-aomori.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    promote("hiranai", "aomori_part_hiranai.jsonl")
    promote("gonohe", "aomori_part_gonohe.jsonl")
    promote("tsuruta", "aomori_part_tsuruta.jsonl")

    write_sotogahama()
    write_ajigasawa()
    write_imabetsu()
    write_inakadate()
    write_yokohama()
    write_sai()
    write_noheji()
    write_takko()
    write_hashikami()
    write_shingo()
    write_sannohe()

    for romaji in [
        "yomogita",
        "fukaura",
        "nishimeya",
        "fujisaki",
        "owani",
        "nakadomari",
        "shichinohe",
        "rokunohe",
        "rokkasho",
        "oma",
        "higashidori",
        "kazamaura",
    ]:
        write_jsonl(romaji, [])

    rows = merge_all()
    write_coverage(rows)
    print(f"merged {len(rows)} rows across {len(MUNICIPALITIES)} municipalities")


if __name__ == "__main__":
    main()
