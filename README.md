# jp-municipal-heritage

**Open data on municipality-designated cultural properties of Japan (市町村指定文化財).**

Japan's nationally- and prefecturally-designated cultural properties are well catalogued,
but the ~1,700 municipalities that also designate their own 文化財 publish those lists in
scattered, inconsistent formats — HTML tables, booklet PDFs, the occasional open-data CSV,
and sometimes nothing at all. This project unifies them into one clean, documented dataset.

**v9: This release covers all six Tohoku prefectures plus 北海道 and five Kanto prefectures (栃木県・群馬県・茨城県・埼玉県・千葉県): 青森県・岩手県・宮城県・秋田県・山形県・福島県・北海道・栃木県・群馬県・茨城県・埼玉県・千葉県
— 21,997 designations across 427 municipalities (12 prefectures).** The schema is designed to scale nationally
(see [`SCHEMA.md`](SCHEMA.md)).

## Coverage at a glance (v9)

| Prefecture | File | Rows | Municipalities covered / total |
|---|---|---|---|
| 北海道 | [`data/hokkaido.jsonl`](data/hokkaido.jsonl) | 464 | 37 / 179 (note: low online-publication rate) |
| 青森県 | [`data/aomori.jsonl`](data/aomori.jsonl) | 818 | 35 / 40 |
| 岩手県 | [`data/iwate.jsonl`](data/iwate.jsonl) | 1,972 | 32 / 33 |
| 宮城県 | [`data/miyagi.jsonl`](data/miyagi.jsonl) | 1,140 | 32 / 35 |
| 秋田県 | [`data/akita.jsonl`](data/akita.jsonl) | 1,536 | 16 / 25 |
| 山形県 | [`data/yamagata.jsonl`](data/yamagata.jsonl) | 1,719 | 28 / 35 |
| 福島県 | [`data/fukushima.jsonl`](data/fukushima.jsonl) | 2,137 | 46 / 59 |
| 栃木県 | [`data/tochigi.jsonl`](data/tochigi.jsonl) | 1,457 | 16 / 25 (下野市・高根沢町 partial — 個別ページ/CMS形式で一覧取得が限定的) |
| 群馬県 | [`data/gunma.jsonl`](data/gunma.jsonl) | 2,025 | 31 / 35 (草津町・川場村 honest-zero; 高山村 no online list) |
| 茨城県 | [`data/ibaraki.jsonl`](data/ibaraki.jsonl) | 2,263 | 41 / 44 (茨城町・美浦村・五霞町 had no online 市町村指定 list; 北茨城市 city-designated only — 10 of the official 22 which includes 国/県 designations) |
| 埼玉県 | [`data/saitama.jsonl`](data/saitama.jsonl) | 4,237 | 63 / 63 (all covered; さいたま市 433 after collapsing 8 byte-identical rows; 秩父市 194・熊谷市 251・本庄市 110・鴻巣市 88 exceed older published counts because those were partial-category subtotals) |
| 千葉県 | [`data/chiba.jsonl`](data/chiba.jsonl) | 2,229 | 49 / 54 (勝浦市・神崎町・九十九里町・大多喜町 had no online itemized list; 市原市 site requires authenticated SPA API — 0 rows, honest-partial; 睦沢町 6 of official 40, 富津市 60 of official 82 — remainder not published online) |
| **合計** | [`data/all.geojson`](data/all.geojson) | **21,997** | **427 / 510** |

## What's here

| Path | Description |
|---|---|
| `data/{pref}.jsonl` | **Canonical datasets.** One JSON object per property. |
| `data/{pref}.csv` | Same columns as the JSONL, UTF-8 **with BOM** so Excel opens it cleanly. |
| `data/{pref}.geojson` | Geocoded points per prefecture (via GSI address search). |
| [`data/all.geojson`](data/all.geojson) | Combined geojson across all twelve prefectures (Tohoku + Hokkaido + five Kanto prefectures). |
| [`SCHEMA.md`](SCHEMA.md) | Field definitions (v1), normalization rules, and the v2 roadmap. |
| [`docs/coverage.md`](docs/coverage.md) | Honest per-municipality coverage — including the zero-yield municipalities and the method used for each. |
| [`docs/sources.md`](docs/sources.md) | Per-municipality source URL, format, and fetch date. |
| [`site/index.html`](site/index.html) | Static Leaflet map of the dataset (prefecture filter included). |
| [`notes/`](notes/) | Working notes from the pilot (schema-fit analysis, raw coverage log). |

## Data at a glance

- **21,997 designations total** across twelve prefectures (Tohoku 6 + Hokkaido + Tochigi + Gunma + Ibaraki + Saitama + Chiba).
- **jmh_id**: all rows carry a unique `JMH-XXXXXX-NNNN` identifier; all prior IDs are preserved unchanged (v9 added 2,229 Chiba IDs using JMH-12xxxx prefix; 0 existing IDs changed).
- **Coverage**: 427 municipalities yielded records. Zero-yield municipalities are listed
  in [`docs/coverage.md`](docs/coverage.md) with the reason for each.

## Design principles

- **Honest coverage over inflated counts.** Zero-yield municipalities and known gaps are
  documented, not silently dropped.
- **null over guess.** Absent, ambiguous, or internally-inconsistent source values are stored
  as `null`, never inferred (see `SCHEMA.md`).
- **Verbatim source wording preserved** in `subcategory`; only the major class (`category`) is
  normalized to the Agency for Cultural Affairs taxonomy.
- **Respect the sources.** robots.txt was honored (one municipality's list was left uncrawled
  as a result); source provenance is recorded per row.

## Using the map locally

The map reads `data/all.geojson` via `fetch`, so serve the repo root over HTTP:

```bash
python3 -m http.server 8000
# then open http://localhost:8000/site/index.html
```

To regenerate the derived files (CSV, per-pref geojson, all.geojson) from the canonical JSONLs:

```bash
python3 site/build_data.py            # rebuild csv + geojson for all prefs (geocodes as needed, cached)
python3 site/build_data.py --csv-only # rebuild only the csv (no network)
python3 site/build_data.py iwate      # rebuild only one prefecture
```

To assign JMH IDs to new rows (idempotent — existing IDs never change):

```bash
python3 site/assign_ids.py            # process all six prefectures
```

To regenerate detail pages:

```bash
python3 site/build_pages.py           # ~21,997 pages under site/p/
```

Geocoding uses the read-only public address-search API of the Geospatial Information Authority
of Japan (国土地理院 / GSI), with a polite delay and an on-disk cache
(`site/geocode_cache.json`) so re-runs make no redundant requests.

## License

- **Data** (`data/`, `docs/`, `notes/`, and the dataset files) — **CC-BY-4.0**. See [`LICENSE`](LICENSE).
- **Code** (`site/`) — **MIT**. See [`site/LICENSE`](site/LICENSE).

Suggested attribution:
> jp-municipal-heritage (Tohoku 6-pref), CC-BY-4.0, kazuki-netizen — compiled from Japanese municipal
> open sources listed in `docs/sources.md`.

Underlying source materials remain the responsibility of the originating municipalities.

---

## 日本語

### jp-municipal-heritage — 日本の市町村指定文化財のオープンデータ

国指定・県指定の文化財はよく整備されていますが、全国約1,700の市町村が独自に指定する文化財の一覧は、
HTML表・冊子PDF・稀にオープンデータCSV……と形式がバラバラで、そもそも公開されていない自治体もあります。
本プロジェクトは、それらを統一された、出典明記のデータセットにまとめます。

**v9: 東北6県（青森・岩手・宮城・秋田・山形・福島）＋北海道＋関東5県（栃木・群馬・茨城・埼玉・千葉）が対象です。計21,997件、427市町村、12都道府県。**
スキーマは全国展開を見据えて設計しています（[`SCHEMA.md`](SCHEMA.md) 参照）。

### 収録データ（v9）

| 道県 | ファイル | 件数 | カバレッジ |
|---|---|---|---|
| 北海道 | `data/hokkaido.jsonl` | 464 | 37 / 179市町村（※公開率低め） |
| 青森県 | `data/aomori.jsonl` | 818 | 35 / 40市町村 |
| 岩手県 | `data/iwate.jsonl` | 1,972 | 32 / 33市町村 |
| 宮城県 | `data/miyagi.jsonl` | 1,140 | 32 / 35市町村 |
| 秋田県 | `data/akita.jsonl` | 1,536 | 16 / 25市町村 |
| 山形県 | `data/yamagata.jsonl` | 1,719 | 28 / 35市町村 |
| 福島県 | `data/fukushima.jsonl` | 2,137 | 46 / 59市町村 |
| 栃木県 | `data/tochigi.jsonl` | 1,457 | 16 / 25市町村（下野市・高根沢町 一部のみ：個別ページ/CMS形式で一覧取得が限定的） |
| 群馬県 | `data/gunma.jsonl` | 2,025 | 31 / 35市町村（草津町・川場村 honest-zero；高山村 一覧未公開） |
| 茨城県 | `data/ibaraki.jsonl` | 2,263 | 41 / 44市町村（茨城町・美浦村・五霞町 一覧未公開；北茨城市 市指定のみ10件） |
| 埼玉県 | `data/saitama.jsonl` | 4,237 | 63 / 63市町村（全カバー；さいたま市 完全一致行8件を集約し433件；秩父市194・熊谷市251・本庄市110・鴻巣市88は旧公表値が部分集計だったため上回る） |
| 千葉県 | `data/chiba.jsonl` | 2,229 | 49 / 54市町村（勝浦市・神崎町・九十九里町・大多喜町 一覧未公開；市原市 認証付きSPAのため0件；睦沢町 6/40・富津市 60/82 は残りがWeb未公開） |
| 合計 | `data/all.geojson` | **21,997** | 427 / 510市町村 |

- **jmh_id**: 全行に `JMH-XXXXXX-NNNN` 形式の固有IDを付与。v9で千葉県2,229件追加（JMH-12xxxx形式）、既存IDは全件引き継ぎ（変更0件）。
- **カバレッジ**: データが得られなかった市町村も理由付きで [`docs/coverage.md`](docs/coverage.md) に明示しています。

### 方針

- **件数を盛らず、欠損を正直に開示する**（0件の市町村・既知の欠落も記載）。
- **推測しない（null-over-guess）**: 出典に無い・曖昧・矛盾する値は推定せず `null`。
- **原表記の保持**: `subcategory` は各自治体の種別表記をそのまま保存。正規化は大分類（`category`）のみ。
- **出典の尊重**: robots.txt を遵守（結果として1自治体の一覧は取得を見送り）。行ごとに出典を記録。

### 地図の閲覧（ローカル）

地図は `fetch` で `data/all.geojson` を読むため、リポジトリ直下をHTTPで配信してください：

```bash
python3 -m http.server 8000
# http://localhost:8000/site/index.html を開く
```

派生ファイル（CSV / GeoJSON / all.geojson）の再生成は `python3 site/build_data.py`。
ジオコーディングは国土地理院（GSI）の住所検索API（読み取りのみ）を、待機時間とキャッシュ付きで利用します。

### ライセンス

- **データ**（`data/` `docs/` `notes/`）— **CC-BY-4.0**（[`LICENSE`](LICENSE)）。
- **コード**（`site/`）— **MIT**（[`site/LICENSE`](site/LICENSE)）。

表示例：
> jp-municipal-heritage (Tohoku 6-pref), CC-BY-4.0, kazuki-netizen — `docs/sources.md` 記載の各市町村の公開情報より作成。
