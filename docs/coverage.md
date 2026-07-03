# Coverage — 岩手県 市町村指定文化財

Snapshot date: 2026-07-03. Dataset: `data/iwate.jsonl` (**1,778 rows**).
All rows are 市町村指定 only; 国指定・県指定 were excluded from the dataset (but counted in the
"national/prefectural counts" section below for context).

This page is deliberately honest about what was **not** captured. The per-municipality table
below includes zero-yield municipalities and the method used for each — that transparency is the
point of the dataset. A count that hides its gaps is not trustworthy; this one shows them.

## Per-municipality table (ordered by population)

| # | Municipality | Source (definitive list) | Format | Extracted | Likely missed | Difficulty | Notes |
|---|---|---|---|---:|---:|---|---|
| 1 | 盛岡市 | city HP 市指定文化財 page | html | 181 | ~1 | easy | Full inline list; official count 182. All dates parsed. |
| 2 | 奥州市 | **open-data CSV** (opendata/5/3100) | html(csv) | 227 | 0 | **easy** | Best case: CC-BY CSV w/ lat-long, 員数, dates. Matches official 227 exactly. |
| 3 | 一関市 | booklet PDF `一関の文化財 P32-101` + 令和2以降 PDF | pdf | 156 | 0 | **medium** (vision re-extraction) | Re-extracted via native visual PDF reading — the earlier text pass corrupted the 2-column layout (only 96/156 kept, 43 lost dates). Vision pass got all 140 市指定 in the booklet (items 43–182; 1–42 are 国/県指定) + 16 in the 令和2以降 supplement. **All 156 rows have dates (100%).** Merged city (7 旧町村). |
| 4 | 北上市 | **open-data CSV** (opendata 18879) | html(csv) | 117 | ~3 | easy | CC-BY CSV. Official 120; 3 rows had combined 分類 labels. |
| 5 | 花巻市 | city HP 市指定文化財 page | html | 237 | 0 | easy | Full inline list, all categories, dates parsed. Largest single-page list. |
| 6 | 宮古市 | 6 area PDFs under /group/39/ | pdf | 102 | 0 | medium | List split across 6 area/theme PDFs. Official 101 (102 = チョウセンアカシジミ counted as 3 basins). |
| 7 | 紫波町 | town list PDF `bunkazai_list_2022` | pdf | 84 | 0 | easy | Clean single-table PDF (R4.4.8). Matches official 84. |
| 8 | 大船渡市 | 指定文化財一覧 PDF (archive) | pdf | 68 | 0 | medium | List PDF found only via archive-page raw HTML. Matches official 68. |
| 9 | 雫石町 | town HP list (docs/2016011300013) | html | 25 | 0 | easy | Full HTML table incl. dates. |
| 10 | 久慈市 | list PDF `kujicityculturalpropertieslist_1` | pdf | 62 | 0 | easy | 2-page PDF (R7.4.1). Matches official 62. |
| 11 | 釜石市 | city HP (docs/2025052700041) | html | 68 | 0 | easy | HTML list, dates parsed. |
| 12 | 矢巾町 | town HP (2016021600011) | html | 40 | 0 | medium | List complete BUT **no 指定年月日 published** → all 40 dates null. |
| 13 | 二戸市 | 埋文センター page (edu.city.ninohe ~maibun) | html | 73 | 0 | medium | Rich list BUT **no dates on page** → all 73 dates null. Non-https legacy host. |
| 14 | 遠野市 | city HP (index.cfm/48,14077) | html | 122 | 0 | easy | Large HTML list, dates parsed. |
| 15 | 八幡平市 | 八幡平市博物館 site (hachimantai.or.jp) | html | 49 | 0 | easy | List on affiliated museum domain, not city HP. |
| 16 | 陸前高田市 | city HP (2662.html) | html | 48 | 0 | easy | HTML list, dates parsed. |
| 17 | 葛巻町 | **none found** | none | 0 | unknown | **impossible** | No online 町指定一覧. Only 県指定 items surfaced. |
| 18 | 金ケ崎町 | 観光サイト rekishi-list | html | 2 | **~15?** | hard | Only 2 町指定 captured from a tourism list; a full register likely exists offline. Under-covered — flag for revisit. |
| 19 | 洋野町 | 洋野ヒストリア (search-only archive) | none | 0 | unknown | **impossible** | Digital archive is search-driven only; no flat list to fetch. Items exist (e.g. 角浜駒踊り) but not enumerable via GET. |
| 20 | 山田町 | town HP (docs/7164) | html | 7 | few | medium | Small HTML list. |
| 21 | 滝沢市 | city HP (contents-13253) | html | 17 | 0 | easy | 市制2014→市指定. HTML list. 1 null date. |
| 22 | 一戸町 | town HP (bunkazaikakari/1/935) | html | 46 | 0 | easy | HTML list w/ descriptions and dates. |
| 23 | 大槌町 | 指定文化財一覧表 PDF (R2.11.28) | pdf | 33 | 0 | easy | Clean single-table PDF. 1 invalid source date (樅の木) → null. |
| 24 | 軽米町 | none found | none | 0 | unknown | hard | No online 町指定 register; only 県指定 seen. |
| 25 | 岩泉町 | none found | none | 0 | unknown | hard | Site relaunched 2023, old URLs 404. Only 国3/県2 online. |
| 26 | 平泉町 | none found | none | 0 | unknown | hard | World-Heritage town; web presence is entirely 国/県. Town designations exist but no published 一覧. |
| 27 | 岩手町 | town HP (shiteibunkazai) | none(blocked) | 0 | **~19** | **impossible** | List of ~19 町指定 EXISTS but robots.txt disallows the crawler (`Disallow: /`). Respected → not crawled. Recoverable by a human/other UA. |
| 28 | 九戸村 | none found | none | 0 | unknown | hard | Only narrative pages; no 村指定 register online. |
| 29 | 西和賀町 | none found | none | 0 | unknown | hard | JS SPA; 文化財 page an empty stub. Only 国3/県1 online. |
| 30 | 住田町 | town HP (kanko/bunkazai) | html | 7 | few | medium | 2 有形 + 5 無形民俗. **No dates published** → all 7 null. |
| 31 | 野田村 | village HP + per-item PDFs | html+pdf | 5 | 0 | easy | Clean list, one PDF per item; dates/locations extracted. |
| 32 | 田野畑村 | none found | none | 0 | ~0 | hard | No 村指定 list online; notable items are 県指定. |
| 33 | 普代村 | village HP (fudaikyo/bunkazai) | html | 2 | 0 | medium | 2 村指定 天然記念物 (TLS/encoding quirks worked around). |

## Totals

- **Municipalities with ≥1 extracted entry: 24 / 33 (73%)**
- **Municipalities with a usable online list: 26 / 33** (岩手町 has a list but robots-blocked; 金ケ崎 under-covered)
- **Municipalities with nothing extractable: 9** — 葛巻・軽米・岩泉・平泉・岩手・九戸・西和賀・田野畑・洋野 (7 no list, 1 robots-blocked, 1 search-only archive).
- **Total properties extracted: 1,778.**
- Format mix of extracted rows: **html 1,268 (71%) / pdf 510 (29%)**. By *municipality's primary source*: HTML list ≈ 15 munis, PDF list ≈ 7 munis (宮古・紫波・大船渡・久慈・大槌・野田・一関), open-data CSV = 2 munis (奥州・北上), none = 9 munis.
- Category mix: 有形文化財 760 / 民俗文化財 545 / 記念物(史跡・名勝・天然記念物) 468 / 無形文化財 4 / その他 1.
- **Date coverage: 1,655 / 1,778 rows have a normalized 西暦 date (93%).** 123 nulls concentrate in 二戸(73, source has no dates), 矢巾(40, source has no dates), 住田(7, no dates), 金ケ崎(2), 滝沢(1). 一関 has 0 nulls after vision re-extraction.

## National / prefectural counts observed (excluded from dataset)

盛岡 国29/県69 · 奥州 国39/県51 · 北上 国16/県34 · 宮古 国14/県12 · 紫波 国3/県18 · 大船渡 国9/県12 ·
雫石 国23/県3 · 久慈 国2/県6 · 岩泉 国3/県2 · 平泉 国多数(特別史跡4・国宝金色堂・重文複数) ·
岩手町 国1/県3 · 九戸 国1(根反の大珪化木) · 西和賀 国3/県1 · 住田 国8/県3 · 普代 国1(鵜鳥神楽).

## Method notes

- **Booklet / 2-column PDFs → read the page images, not the text.** Text extraction interleaves
  columns and corrupts names and dates (the original text pass lost ~30% of 一関). Native visual
  PDF reading (render each page, read it, ≤20 pages/request) recovered all 156 一関 items with
  100% date coverage. For booklet PDFs, go straight to vision.
- **Open-data CSVs (奥州・北上) are the gold standard** — schema-rich (lat/long, 員数, dates),
  CC-BY, zero parsing risk. Check every municipality's open-data portal FIRST.
- **robots.txt was respected.** 岩手町's ~19-item list was left uncrawled because the site
  disallows the crawler. It is human-recoverable and is counted as a known gap, not a silent one.

## Known quality caveats

- **一関市**: re-extracted to 156 rows via vision (was a lossy 96-row floor). 140 市指定 in the main
  booklet (内部通し番号 43–182; 1–42 = 国/県指定, absent from the PDF) + 16 in the 令和2以降 supplement.
  All 156 have dates. No external official 市指定 count was locatable within the crawl budget, so the
  contiguous in-document numbering (43–182, no gaps) + the supplement's own R2–R7 sequence serves as
  the count check. No entries were unreadable.
- **金ケ崎町**: only 2 rows captured — almost certainly incomplete; needs a revisit with a better source.
- **二戸・矢巾・住田**: complete item lists but **zero dates** (sources don't publish them) — not an
  extraction failure.
- **岩手町**: ~19 items are recoverable but were left out to respect a crawler-specific robots.txt rule.

## Skipped / zero-yield municipalities (explicit)

葛巻町, 軽米町, 岩泉町, 平泉町, 岩手町(robots), 九戸村, 西和賀町, 田野畑村, 洋野町(search-only) — 9 total, 0 rows.
These are honest negatives, not silent truncations.
