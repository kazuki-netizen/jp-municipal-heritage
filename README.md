# jp-municipal-heritage

**Open data on municipality-designated cultural properties of Japan (市町村指定文化財).**

Japan's nationally- and prefecturally-designated cultural properties are well catalogued,
but the ~1,700 municipalities that also designate their own 文化財 publish those lists in
scattered, inconsistent formats — HTML tables, booklet PDFs, the occasional open-data CSV,
and sometimes nothing at all. This project unifies them into one clean, documented dataset.

**This release covers Iwate Prefecture (岩手県): `data/iwate.jsonl`, 1,778 designations
across 24 of 33 municipalities.** More prefectures are planned; the schema is designed to
scale nationally (see [`SCHEMA.md`](SCHEMA.md)).

## What's here

| Path | Description |
|---|---|
| [`data/iwate.jsonl`](data/iwate.jsonl) | **Canonical dataset.** One JSON object per property (1,778 rows). |
| [`data/iwate.csv`](data/iwate.csv) | Same columns as the JSONL, UTF-8 **with BOM** so Excel opens it cleanly. |
| [`data/iwate.geojson`](data/iwate.geojson) | Geocoded points for the map (via GSI address search). |
| [`SCHEMA.md`](SCHEMA.md) | Field definitions (v1), normalization rules, and the v2 roadmap. |
| [`docs/coverage.md`](docs/coverage.md) | Honest per-municipality coverage — including the 9 zero-yield municipalities and the method used for each. |
| [`docs/sources.md`](docs/sources.md) | Per-municipality source URL, format, and fetch date. |
| [`site/index.html`](site/index.html) | Static Leaflet map of the dataset. |
| [`notes/`](notes/) | Working notes from the pilot (schema-fit analysis, raw coverage log). |

## Data at a glance

- **1,778 designations** — `市指定` 1,527 / `町指定` 244 / `村指定` 7.
- **Categories** (文化庁大分類): 有形文化財 760 · 民俗文化財 545 · 記念物(史跡・名勝・天然記念物) 468 · 無形文化財 4 · その他 1.
- **Date coverage**: 1,655 / 1,778 rows (93%) carry a normalized 西暦 designation date. Missing dates
  are almost all cases where the *source itself* publishes none — documented, not hidden.
- **Coverage**: 24 / 33 municipalities yielded records. The 9 that did not are listed explicitly
  in [`docs/coverage.md`](docs/coverage.md) with the reason for each — that transparency is the
  point of the dataset.

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

The map reads `data/iwate.geojson` via `fetch`, so serve the repo root over HTTP:

```bash
python3 -m http.server 8000
# then open http://localhost:8000/site/index.html
```

To regenerate the derived files (`iwate.csv`, `iwate.geojson`) from the canonical JSONL:

```bash
python3 site/build_data.py            # rebuild csv + geojson (geocodes as needed, cached)
python3 site/build_data.py --csv-only # rebuild only the csv (no network)
```

Geocoding uses the read-only public address-search API of the Geospatial Information Authority
of Japan (国土地理院 / GSI), with a polite delay and an on-disk cache
(`site/geocode_cache.json`) so re-runs make no redundant requests.

## License

- **Data** (`data/`, `docs/`, `notes/`, and the dataset files) — **CC-BY-4.0**. See [`LICENSE`](LICENSE).
- **Code** (`site/`) — **MIT**. See [`site/LICENSE`](site/LICENSE).

Suggested attribution:
> jp-municipal-heritage (Iwate), CC-BY-4.0, kazuki-netizen — compiled from Japanese municipal
> open sources listed in `docs/sources.md`.

Underlying source materials remain the responsibility of the originating municipalities.

---

## 日本語

### jp-municipal-heritage — 日本の市町村指定文化財のオープンデータ

国指定・県指定の文化財はよく整備されていますが、全国約1,700の市町村が独自に指定する文化財の一覧は、
HTML表・冊子PDF・稀にオープンデータCSV……と形式がバラバラで、そもそも公開されていない自治体もあります。
本プロジェクトは、それらを統一された、出典明記のデータセットにまとめます。

**本リリースは岩手県が対象です（`data/iwate.jsonl`、33市町村中24市町村・計1,778件）。**
スキーマは全国展開を見据えて設計しています（[`SCHEMA.md`](SCHEMA.md) 参照）。

### 収録データ

- **1,778件** — 市指定 1,527 / 町指定 244 / 村指定 7。
- **大分類**: 有形文化財 760 / 民俗文化財 545 / 記念物 468 / 無形文化財 4 / その他 1。
- **指定年月日**: 1,778件中1,655件（93%）を西暦へ正規化。欠損の大半は「出典自体が日付を掲載していない」
  ケースで、[`docs/coverage.md`](docs/coverage.md) に明記しています。
- **カバレッジ**: 24/33市町村。データが得られなかった9市町村も理由付きで明示しています。

### 方針

- **件数を盛らず、欠損を正直に開示する**（0件の市町村・既知の欠落も記載）。
- **推測しない（null-over-guess）**: 出典に無い・曖昧・矛盾する値は推定せず `null`。
- **原表記の保持**: `subcategory` は各自治体の種別表記をそのまま保存。正規化は大分類（`category`）のみ。
- **出典の尊重**: robots.txt を遵守（結果として1自治体の一覧は取得を見送り）。行ごとに出典を記録。

### 地図の閲覧（ローカル）

地図は `fetch` で `data/iwate.geojson` を読むため、リポジトリ直下をHTTPで配信してください：

```bash
python3 -m http.server 8000
# http://localhost:8000/site/index.html を開く
```

派生ファイル（CSV / GeoJSON）の再生成は `python3 site/build_data.py`。
ジオコーディングは国土地理院（GSI）の住所検索API（読み取りのみ）を、待機時間とキャッシュ付きで利用します。

### ライセンス

- **データ**（`data/` `docs/` `notes/`）— **CC-BY-4.0**（[`LICENSE`](LICENSE)）。
- **コード**（`site/`）— **MIT**（[`site/LICENSE`](site/LICENSE)）。

表示例：
> jp-municipal-heritage (Iwate), CC-BY-4.0, kazuki-netizen — `docs/sources.md` 記載の各市町村の公開情報より作成。
