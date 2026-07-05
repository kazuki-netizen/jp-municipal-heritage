# jp-municipal-heritage

**Open data on municipality-designated cultural properties of Japan (市町村指定文化財).**

Japan's nationally- and prefecturally-designated cultural properties are well catalogued,
but the ~1,700 municipalities that also designate their own 文化財 publish those lists in
scattered, inconsistent formats — HTML tables, booklet PDFs, the occasional open-data CSV,
and sometimes nothing at all. This project unifies them into one clean, documented dataset.

**v3: This release covers all six Tohoku prefectures: 青森県・岩手県・宮城県・秋田県・山形県・福島県
— 8,975 designations across 172 municipalities.** The schema is designed to scale nationally
(see [`SCHEMA.md`](SCHEMA.md)).

## Coverage at a glance (v3)

| Prefecture | File | Rows | Municipalities covered / total |
|---|---|---|---|
| 青森県 | [`data/aomori.jsonl`](data/aomori.jsonl) | 725 | 28 / 40 |
| 岩手県 | [`data/iwate.jsonl`](data/iwate.jsonl) | 1,778 | 24 / 33 |
| 宮城県 | [`data/miyagi.jsonl`](data/miyagi.jsonl) | 1,140 | 32 / 35 |
| 秋田県 | [`data/akita.jsonl`](data/akita.jsonl) | 1,530 | 15 / 25 |
| 山形県 | [`data/yamagata.jsonl`](data/yamagata.jsonl) | 1,666 | 27 / 35 |
| 福島県 | [`data/fukushima.jsonl`](data/fukushima.jsonl) | 2,136 | 46 / 59 |
| **合計** | [`data/all.geojson`](data/all.geojson) | **8,975** | **172 / 227** |

## What's here

| Path | Description |
|---|---|
| `data/{pref}.jsonl` | **Canonical datasets.** One JSON object per property. |
| `data/{pref}.csv` | Same columns as the JSONL, UTF-8 **with BOM** so Excel opens it cleanly. |
| `data/{pref}.geojson` | Geocoded points per prefecture (via GSI address search). |
| [`data/all.geojson`](data/all.geojson) | Combined geojson across all six Tohoku prefectures. |
| [`SCHEMA.md`](SCHEMA.md) | Field definitions (v1), normalization rules, and the v2 roadmap. |
| [`docs/coverage.md`](docs/coverage.md) | Honest per-municipality coverage — including the zero-yield municipalities and the method used for each. |
| [`docs/sources.md`](docs/sources.md) | Per-municipality source URL, format, and fetch date. |
| [`site/index.html`](site/index.html) | Static Leaflet map of the dataset (prefecture filter included). |
| [`notes/`](notes/) | Working notes from the pilot (schema-fit analysis, raw coverage log). |

## Data at a glance

- **8,975 designations total** across all six Tohoku prefectures.
- **jmh_id**: all rows carry a unique `JMH-XXXXXX-NNNN` identifier; all v2 IDs (Iwate/Miyagi/Aomori)
  are preserved unchanged.
- **Coverage**: 172 / 227 municipalities yielded records. Zero-yield municipalities are listed
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
python3 site/build_pages.py           # ~8,975 pages under site/p/
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

**v3: 東北6県（青森・岩手・宮城・秋田・山形・福島）が対象です。計8,975件、172市町村。**
スキーマは全国展開を見据えて設計しています（[`SCHEMA.md`](SCHEMA.md) 参照）。

### 収録データ（v3）

| 県 | ファイル | 件数 | カバレッジ |
|---|---|---|---|
| 青森県 | `data/aomori.jsonl` | 725 | 28 / 40市町村 |
| 岩手県 | `data/iwate.jsonl` | 1,778 | 24 / 33市町村 |
| 宮城県 | `data/miyagi.jsonl` | 1,140 | 32 / 35市町村 |
| 秋田県 | `data/akita.jsonl` | 1,530 | 15 / 25市町村 |
| 山形県 | `data/yamagata.jsonl` | 1,666 | 27 / 35市町村 |
| 福島県 | `data/fukushima.jsonl` | 2,136 | 46 / 59市町村 |
| 合計 | `data/all.geojson` | **8,975** | 172 / 227市町村 |

- **jmh_id**: 全行に `JMH-XXXXXX-NNNN` 形式の固有IDを付与。v2までの岩手・宮城・青森のIDは完全に引き継ぎ。
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
