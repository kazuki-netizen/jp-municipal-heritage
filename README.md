# jp-municipal-heritage

**Open data on municipality-designated cultural properties of Japan (市町村指定文化財).**

Japan's nationally- and prefecturally-designated cultural properties are well catalogued,
but the ~1,700 municipalities that also designate their own 文化財 publish those lists in
scattered, inconsistent formats — HTML tables, booklet PDFs, the occasional open-data CSV,
and sometimes nothing at all. This project unifies them into one clean, documented dataset.

**v15: This release adds the complete Chugoku region (鳥取県・島根県・岡山県・広島県・山口県)
— 63,309 designations across 1,071 municipalities (35 prefectures).** The schema is designed to scale nationally
(see [`SCHEMA.md`](SCHEMA.md)).

## Coverage at a glance (v15)

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
| 群馬県 | [`data/gunma.jsonl`](data/gunma.jsonl) | 2,022 | 31 / 35 (草津町・川場村 honest-zero; 高山村 no online list; 3 nav-noise rows removed in v10.1) |
| 茨城県 | [`data/ibaraki.jsonl`](data/ibaraki.jsonl) | 2,263 | 41 / 44 (茨城町・美浦村・五霞町 had no online 市町村指定 list; 北茨城市 city-designated only — 10 of the official 22 which includes 国/県 designations) |
| 埼玉県 | [`data/saitama.jsonl`](data/saitama.jsonl) | 4,236 | 63 / 63 (all covered; 1 editorial-note row removed from 狭山市 in v11.1; さいたま市 433 after collapsing 8 byte-identical rows; 秩父市 194・熊谷市 251・本庄市 110・鴻巣市 88 exceed older published counts because those were partial-category subtotals) |
| 千葉県 | [`data/chiba.jsonl`](data/chiba.jsonl) | 2,229 | 49 / 54 (勝浦市・神崎町・九十九里町・大多喜町 had no online itemized list; 市原市 site requires authenticated SPA API — 0 rows, honest-partial; 睦沢町 6 of official 40, 富津市 60 of official 82 — remainder not published online) |
| 神奈川県 | [`data/kanagawa.jsonl`](data/kanagawa.jsonl) | 1,644 | 30 / 33 (寒川町・中井町・松田町 publish no online itemized list — 松田町 booklet only; 真鶴町 17 of official 112 — only the newest designations are itemized online; 厚木市 re-parsed from XLS 59; 座間市 31 current after 7 revocations) |
| 東京都 | [`data/tokyo.jsonl`](data/tokyo.jsonl) | 2,993 | 62 / 62 (all covered — first prefecture with zero none-published municipalities; 立川市 32 is the verified current city count, the older published 59 mixed in national/metropolitan designations) |
| 新潟県 | [`data/niigata.jsonl`](data/niigata.jsonl) | 2,359 | 28 / 30 (刈羽村・粟島浦村 publish no list; 阿賀町 15 of official 53, 田上町 2, 出雲崎町 1 — remainder not itemized online; 五泉市 45 verified current, the older "103" figure could not be corroborated by any primary source) |
| 山梨県 | [`data/yamanashi.jsonl`](data/yamanashi.jsonl) | 1,288 | 21 / 27 (6 municipalities publish no comprehensive list; 笛吹市 4 of official 62 — no online itemized list exists; 甲斐市 76 exact after recovering the successor PDF of a lost list) |
| 富山県 | [`data/toyama.jsonl`](data/toyama.jsonl) | 946 | 15 / 15 (all covered; 射水市 108 per the city's own current opendata, the older 136 figure is a different aggregation) |
| 石川県 | [`data/ishikawa.jsonl`](data/ishikawa.jsonl) | 2,028 | 18 / 19 (能登町 honest-zero — official count 320 but no itemized public list exists; 穴水町 4 via museum pages; 12 municipalities match official counts exactly) |
| 福井県 | [`data/fukui.jsonl`](data/fukui.jsonl) | 1,507 | 17 / 17 (all covered; 越前町 113 via 織田文化歴史館; 永平寺町 21 via 町勢要覧) |
| 長野県 | [`data/nagano.jsonl`](data/nagano.jsonl) | 3,541 | 60 / 77 (17 small municipalities publish no comprehensive list; 岡谷市 122 via 教育要覧 PDF; 高森町 4 of official 30 — map-only source) |
| 静岡県 | [`data/shizuoka.jsonl`](data/shizuoka.jsonl) | 1,841 | 34 / 35 (河津町 publishes no list; 森町 34 of official 98 — narrative-only sources; 三島市 50 exact via HTML item pages after robots.txt blocked the PDF) |
| 岐阜県 | [`data/gifu.jsonl`](data/gifu.jsonl) | 4,559 | 42 / 42 (all covered — 35 municipalities via the prefectural opendata catalog's standardized municipal-designation CSVs) |
| 愛知県 | [`data/aichi.jsonl`](data/aichi.jsonl) | 3,350 | 45 / 54 (8 municipalities publish no comprehensive list; 一宮市 249 exact after removing 9 prefectural-designation rows; 瀬戸市 7 of official 55 and 常滑市 21 of official 145 — official sites publish representative examples only) |
| 三重県 | [`data/mie.jsonl`](data/mie.jsonl) | 1,698 | 24 / 29 (5 municipalities publish no list; 桑名市 110 recovered by resolving a 2001-era image-map DB's JS mappings; 松阪市 143 — district pages are not certified exhaustive) |
| 滋賀県 | [`data/shiga.jsonl`](data/shiga.jsonl) | 1,382 | 17 / 19 (12 exact official matches incl. 長浜 248 and 東近江 206; 湖南市 honest-zero — official 66 but no itemized public list; 竜王町 publishes no list) |
| 京都府 | [`data/kyoto.jsonl`](data/kyoto.jsonl) | 1,177 | 16 / 26 (9 municipalities publish no list; 京都市 408 recovered from the city DB's static category links; 与謝野町 aggregate-only) |
| 大阪府 | [`data/osaka.jsonl`](data/osaka.jsonl) | 1,262 | 36 / 43 (7 municipalities verified as having zero municipal designations via the prefectural fallback PDFs; 八尾市 2 of official 73 — items live in an external map service) |
| 兵庫県 | [`data/hyogo.jsonl`](data/hyogo.jsonl) | 2,345 | 37 / 41 (14 exact official matches incl. 神戸 125 and 豊岡 251; 養父市・香美町 itemized lists not reachable; 相生市・稲美町 publish no list) |
| 奈良県 | [`data/nara.jsonl`](data/nara.jsonl) | 702 | 30 / 39 (17 exact official matches; 5 municipalities publish no list; 4 more lack designation-level labels) |
| 和歌山県 | [`data/wakayama.jsonl`](data/wakayama.jsonl) | 753 | 17 / 30 (12 municipalities publish no list; 和歌山市 92 exact; 有田川町 2 of official 144; 海南市 JS-rendered site) |
| 鳥取県 | [`data/tottori.jsonl`](data/tottori.jsonl) | 574 | 18 / 19 (5 exact matches incl. 鳥取市 130; 境港市 28 via Wayback — the live site's robots.txt disallows all crawling; 八頭町 publishes no list) |
| 島根県 | [`data/shimane.jsonl`](data/shimane.jsonl) | 891 | 19 / 19 (all covered — 4 no-list towns recovered via the prefectural board of education site; 6 exact matches) |
| 岡山県 | [`data/okayama.jsonl`](data/okayama.jsonl) | 1,559 | 19 / 27 (11 exact matches incl. 倉敷 86 and 真庭 202; 津山市 SPA-only site, 吉備中央町 aggregate-only; 久米南町 has no municipal designation system) |
| 広島県 | [`data/hiroshima.jsonl`](data/hiroshima.jsonl) | 1,943 | 21 / 23 (広島市 109 exact from 13 PDFs; 熊野町 via Wayback after domain expiry; 府中町 verified zero current designations; 大崎上島町 no reachable list) |
| 山口県 | [`data/yamaguchi.jsonl`](data/yamaguchi.jsonl) | 974 | 18 / 19 (8 exact matches incl. 下関 146 and 萩 138; 周防大島町 official 28 but no itemized list) |
| **合計** | [`data/all.geojson`](data/all.geojson) | **63,309** | **1,071 / 1,240** |

## What's here

| Path | Description |
|---|---|
| `data/{pref}.jsonl` | **Canonical datasets.** One JSON object per property. |
| `data/{pref}.csv` | Same columns as the JSONL, UTF-8 **with BOM** so Excel opens it cleanly. |
| `data/{pref}.geojson` | Geocoded points per prefecture (via GSI address search). |
| [`data/all.geojson`](data/all.geojson) | Combined geojson across all fourteen prefectures (Tohoku + Hokkaido + the complete Kanto region). |
| [`SCHEMA.md`](SCHEMA.md) | Field definitions (v1), normalization rules, and the v2 roadmap. |
| [`docs/coverage.md`](docs/coverage.md) | Honest per-municipality coverage — including the zero-yield municipalities and the method used for each. |
| [`docs/sources.md`](docs/sources.md) | Per-municipality source URL, format, and fetch date. |
| [`site/index.html`](site/index.html) | Static Leaflet map of the dataset (prefecture filter included). |
| [`notes/`](notes/) | Working notes from the pilot (schema-fit analysis, raw coverage log). |

## Data at a glance

- **63,309 designations total** across thirty-five prefectures (adding the Chugoku 5).
- **jmh_id**: all rows carry a unique `JMH-XXXXXX-NNNN` identifier; all prior IDs are preserved unchanged (v15 added 5,941 IDs across the Chugoku region; 0 existing IDs changed).
- **Coverage**: 519 municipalities yielded records. Zero-yield municipalities are listed
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
python3 site/build_pages.py           # ~63,309 pages under site/p/
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

**v15: 中国5県（鳥取・島根・岡山・広島・山口）を追加しました。計63,309件、1,071市区町村、35都道府県。**
スキーマは全国展開を見据えて設計しています（[`SCHEMA.md`](SCHEMA.md) 参照）。

### 収録データ（v15）

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
| 群馬県 | `data/gunma.jsonl` | 2,022 | 31 / 35市町村（草津町・川場村 honest-zero；高山村 一覧未公開；甘楽町のナビ由来ノイズ3件をv10.1で除去） |
| 茨城県 | `data/ibaraki.jsonl` | 2,263 | 41 / 44市町村（茨城町・美浦村・五霞町 一覧未公開；北茨城市 市指定のみ10件） |
| 埼玉県 | `data/saitama.jsonl` | 4,236 | 63 / 63市町村（全カバー；狭山市の編集注記1行をv11.1で除去；さいたま市 完全一致行8件を集約し433件；秩父市194・熊谷市251・本庄市110・鴻巣市88は旧公表値が部分集計だったため上回る） |
| 千葉県 | `data/chiba.jsonl` | 2,229 | 49 / 54市町村（勝浦市・神崎町・九十九里町・大多喜町 一覧未公開；市原市 認証付きSPAのため0件；睦沢町 6/40・富津市 60/82 は残りがWeb未公開） |
| 神奈川県 | `data/kanagawa.jsonl` | 1,644 | 30 / 33市町村（寒川町・中井町・松田町 一覧未公開（松田は冊子のみ）；真鶴町 17/112（最新指定分のみWeb公開）；厚木市はXLS再解析59件；座間市は指定解除7件を除く31件） |
| 東京都 | `data/tokyo.jsonl` | 2,993 | 62 / 62市区町村（全カバー＝一覧未公開ゼロの初の都道府県；立川市は現行32件が正で旧公表59は国都込み） |
| 新潟県 | `data/niigata.jsonl` | 2,359 | 28 / 30市町村（刈羽村・粟島浦村は一覧非公開；阿賀町15/53・田上町2・出雲崎町1は原典側で個別名の公開がない分を除く；五泉市45は市の最新一次情報で検証済み） |
| 山梨県 | `data/yamanashi.jsonl` | 1,288 | 21 / 27市町村（6町村は網羅一覧なし；笛吹市は市指定62件の一覧自体が非公開のため4件のみ；甲斐市は後継PDFを発見し公式76件と完全一致） |
| 富山県 | `data/toyama.jsonl` | 946 | 15 / 15市町村（全カバー；射水市108は市の現行オープンデータ準拠） |
| 石川県 | `data/ishikawa.jsonl` | 2,028 | 18 / 19市町（能登町は公式320件だが個別名の公開一覧が存在せず0件；12市町が公式件数と完全一致） |
| 福井県 | `data/fukui.jsonl` | 1,507 | 17 / 17市町（全カバー；越前町113は織田文化歴史館、永平寺町21は町勢要覧より） |
| 長野県 | `data/nagano.jsonl` | 3,541 | 60 / 77市町村（17町村は網羅一覧なし；岡谷市122は教育要覧PDFより；高森町4/30） |
| 静岡県 | `data/shizuoka.jsonl` | 1,841 | 34 / 35市町（河津町は一覧非公開；森町34/98；三島市はrobots.txt制約をHTML個票で回避し公式50件と一致） |
| 岐阜県 | `data/gifu.jsonl` | 4,559 | 42 / 42市町村（全カバー。35自治体は県オープンデータの市町村指定CSVを一次ソースに使用） |
| 愛知県 | `data/aichi.jsonl` | 3,350 | 45 / 54市町村（8町村は網羅一覧なし；一宮市は県指定混入9件を除去し公式249件と一致；瀬戸市7/55・常滑市21/145は公式サイトが代表例のみ公開） |
| 三重県 | `data/mie.jsonl` | 1,698 | 24 / 29市町（5町は網羅一覧なし；桑名市110は2001年製画像マップDBのJS解析で全量回収；松阪市143は地区ページ由来で網羅性未認定） |
| 滋賀県 | `data/shiga.jsonl` | 1,382 | 17 / 19市町（完全一致12：長浜248・東近江206等；湖南市は公式66件だが個別名の公開一覧なし；竜王町は一覧非公開） |
| 京都府 | `data/kyoto.jsonl` | 1,177 | 16 / 26市町村（9町村は一覧非公開；京都市408は市DBの静的カテゴリリンクから回収；与謝野町は集計のみ） |
| 大阪府 | `data/osaka.jsonl` | 1,262 | 36 / 43市町村（7町村は市町村指定0件を府PDFで裏取り；八尾市2/73は外部マップサービスのみ） |
| 兵庫県 | `data/hyogo.jsonl` | 2,345 | 37 / 41市町（完全一致14：神戸125・豊岡251等；養父市・香美町は個別一覧に未到達；相生市・稲美町は一覧非公開） |
| 奈良県 | `data/nara.jsonl` | 702 | 30 / 39市町村（完全一致17；5町村は一覧非公開、4村町は指定区分ラベルなし） |
| 和歌山県 | `data/wakayama.jsonl` | 753 | 17 / 30市町（12町村は一覧非公開；和歌山市92完全一致；有田川町2/144；海南市はJS描画サイト） |
| 鳥取県 | `data/tottori.jsonl` | 574 | 18 / 19市町村（完全一致5：鳥取市130等；境港市28はrobots全面拒否のためWayback経由；八頭町は一覧非公開） |
| 島根県 | `data/shimane.jsonl` | 891 | 19 / 19市町村（全カバー。一覧非公開の4町村も県教育庁サイトで回収；完全一致6） |
| 岡山県 | `data/okayama.jsonl` | 1,559 | 19 / 27市町村（完全一致11：倉敷86・真庭202等；津山市はSPAのみ・吉備中央町は集計のみ；久米南町は町指定制度なし） |
| 広島県 | `data/hiroshima.jsonl` | 1,943 | 21 / 23市町（広島市109完全一致；熊野町はドメイン失効でWayback経由；府中町は現行町指定なしを確認） |
| 山口県 | `data/yamaguchi.jsonl` | 974 | 18 / 19市町（完全一致8：下関146・萩138等；周防大島町は公式28件だが個別一覧非公開） |
| 合計 | `data/all.geojson` | **63,309** | 1,071 / 1,240市区町村 |

- **jmh_id**: 全行に `JMH-XXXXXX-NNNN` 形式の固有IDを付与。v15で中国5県5,941件を追加、既存IDは全件引き継ぎ（変更0件）。
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
