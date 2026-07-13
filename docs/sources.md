> **⚠️ Historical snapshot (v1, Iwate only).** Source listing for the initial
> 2026-07-03 Iwate release. Current per-row provenance is in the `source_url`
> field of each record in `data/<pref>.jsonl`.

# Sources — 岩手県 市町村指定文化財

Per-municipality provenance for `data/iwate.jsonl`. One row per municipality that
yielded ≥1 record. All sources were fetched **2026-07-03** (see each row's
`fetched_at` in the data for the exact timestamp). Municipalities with no
extractable source are listed at the bottom as honest negatives.

Only 市町村指定 (municipality-designated) items were collected; 国指定 / 県指定 were
excluded by scope. Extraction method and quality caveats are in `docs/coverage.md`.

## Municipalities with records

| Municipality | Rows | Format | Source (definitive list) URL |
|---|---:|---|---|
| 盛岡市 | 181 | html | https://www.city.morioka.iwate.jp/kankou/kankou/1037106/rekishi/1009335/1009358/1009359.html |
| 奥州市 | 227 | html (open-data CSV) | https://www.city.oshu.iwate.jp/opendata/5/3100.html |
| 一関市 | 156 | pdf (booklet + supplement) | https://www.city.ichinoseki.iwate.jp/uploads/public/archive_0000001892_00/20130906-092028.pdf |
| 北上市 | 117 | html (open-data CSV) | https://www.city.kitakami.iwate.jp/life/soshikikarasagasu/toshipromotionka/jouhouseisakusuishinshitsu/1_1/opendata/18879.html |
| 花巻市 | 237 | html | https://www.city.hanamaki.iwate.jp/bunkasports/bunka/1019886/bunkazai/1002085.html |
| 宮古市 | 102 | pdf (6 area PDFs) | https://www.city.miyako.iwate.jp/material/files/group/39/miyakoiki.pdf |
| 紫波町 | 84 | pdf | https://img.japandx.co.jp/shiwatown/shiwa-town/material/files/group/14/bunkazai_list_2022.pdf |
| 大船渡市 | 68 | pdf | https://www.city.ofunato.iwate.jp/uploads/contents/archive_0000003767_00/25_指定文化財一覧（HP掲載用　４月１日時点）%20(1).pdf |
| 雫石町 | 25 | html | https://www.town.shizukuishi.iwate.jp/docs/2016011300013/ |
| 久慈市 | 62 | pdf | https://www.city.kuji.lg.jp/material/files/group/46/kujicityculturalpropertieslist_1.pdf |
| 釜石市 | 68 | html | https://www.city.kamaishi.iwate.jp/docs/2025052700041/ |
| 矢巾町 | 40 | html | https://www.town.yahaba.iwate.jp/soshiki/kyouiku/manabi/2016021600011/ |
| 二戸市 | 73 | html | http://www.edu.city.ninohe.iwate.jp/~maibun/siteibunkazai.html |
| 遠野市 | 122 | html | https://www.city.tono.iwate.jp/index.cfm/48,14077,303,html |
| 八幡平市 | 49 | html (affiliated museum site) | https://www.hachimantai.or.jp/bunkazai/index.html |
| 陸前高田市 | 48 | html | https://www.city.rikuzentakata.iwate.jp/soshiki/kyouikusoumuka/bunkazaigakari/1/1/2662.html |
| 一戸町 | 46 | html | https://www.town.ichinohe.iwate.jp/soshikikarasagasu/sekaiisanka/bunkazaikakari/1/935.html |
| 金ケ崎町 | 2 | html (tourism list) | https://www.comeon-kanegasaki.jp/rekishi-list/ |
| 滝沢市 | 17 | html | https://www.city.takizawa.iwate.jp/about-takizawa/bunka-geijutsu/sitei-bunkazai/contents-13252 |
| 山田町 | 7 | html | https://www.town.yamada.iwate.jp/docs/7164.html |
| 大槌町 | 33 | pdf | https://www.town.otsuchi.iwate.jp/fs/2/3/0/2/3/3/_/____________R2.11.28___.pdf |
| 野田村 | 5 | pdf | https://www.vill.noda.iwate.jp/material/files/group/27/1918download.pdf |
| 普代村 | 2 | html | https://vill.fudai.iwate.jp/fudaikyo/bunkazai.html |
| 住田町 | 7 | html | https://www.town.sumita.iwate.jp/kanko/bunkazai.html |

**Total: 24 municipalities, 1,778 records.**

### Source-format notes

- **Open-data CSV (奥州・北上)** — the gold standard: CC-BY portal CSVs carrying lat/long,
  員数, and dates. The `source_url` points at the open-data portal HTML page hosting the CSV
  (hence `source_format: html` in the data). Counts match the official register exactly.
- **一関市** was re-extracted from the booklet PDF *page images* (native visual reading), not
  text extraction, after the two-column text layout corrupted the earlier pass. Items are numbered
  43–182 in-document (1–42 are 国/県指定, absent from this PDF) plus a 令和2以降 supplement.
- **宮古市** list is split across 6 area/theme PDFs under `/material/files/group/39/`;
  `source_url` cites the 宮古地区 PDF as the representative entry point.
- **八幡平市** records come from the affiliated museum domain (`hachimantai.or.jp`), not the
  city HP, which does not host a flat list.
- **二戸市** uses a legacy non-HTTPS host (`edu.city.ninohe.iwate.jp`); its list carries no dates.

## Municipalities with no extractable source (zero-yield, honest negatives)

These 9 municipalities produced **0 records**. Kept explicit so the coverage figure is
not a silent truncation — see `docs/coverage.md` for the reason in each case.

| Municipality | Reason |
|---|---|
| 葛巻町 | No online 町指定 register found (only 県指定 surfaced). |
| 軽米町 | No online 町指定 register found. |
| 岩泉町 | Site relaunched 2023; old URLs 404. Only 国/県 online. |
| 平泉町 | Web presence is entirely 国/県 (World Heritage); no published 町指定 一覧. |
| 岩手町 | A ~19-item list EXISTS but robots.txt disallows the crawler (`Disallow: /`) — respected, not crawled. Human-recoverable. |
| 九戸村 | No 村指定 register online; narrative pages only. |
| 西和賀町 | JS SPA; 文化財 page is an empty stub. Only 国/県 online. |
| 田野畑村 | No 村指定 list online; notable items are 県指定. |
| 洋野町 | Digital archive is search-only; no flat list enumerable via GET. |
