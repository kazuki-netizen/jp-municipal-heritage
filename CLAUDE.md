# CLAUDE.md — jp-municipal-heritage (bunkazai)

このファイルはこのリポジトリを独立した Claude Code プロジェクトとして扱う際の運用指示書。作業前に必ず読むこと。

## 1. プロジェクト概要

全47都道府県の市区町村指定文化財（市町村が独自に指定する文化財、国指定・県指定は対象外）を統一スキーマで収録したオープンデータセット。

- 収録件数: 78,515件（1,375市区町村、v17.1時点）
- ライセンス: データは **CC-BY-4.0**（`data/` `docs/` `notes/`）、コード（`site/`）は **MIT**
- 本番: https://jp-municipal-heritage.vercel.app
- GitHub: https://github.com/kazuki-netizen/jp-municipal-heritage（リモート名 `origin`）
- 詳細な収録方針・カバレッジは `README.md`、フィールド定義は `SCHEMA.md`、API仕様は `API.md` を参照。

## 2. アーキテクチャ

```
pipeline/sources/<pref>*.jsonl   … Discovery結果（自治体一覧、未指定含む）
pipeline/cache/<都道府県>/       … fetch.py の生キャッシュ
pipeline/out/<都道府県>/*.jsonl  … 抽出班の出力（jmh_id はまだ無い）
        ↓ 正規化マージ（category正規化・dedup・muni_codes付与）
data/<pref>.jsonl                … ★正（canonical）。jmh_id 付与済み
        ↓ site/build_data.py（geocode含む）
data/<pref>.csv / data/<pref>.geojson / data/all.geojson
        ↓ site/build_pages.py
site/p/**                        … 詳細ページ（78,515ページ）
        ↓ site/build_api.py
api/v1/index.json, prefectures/<slug>.json, municipalities/<code>.json
        ↓
Vercel 静的配信（vercel.json: /api,/data は CORS全許可 + 1h cache）
```

`pipeline/` はスクレイプ〜抽出側の作業領域（`sources/` discovery、`cache/` 生データ、`out/` 抽出結果、`scratch_*.py` は使い捨てビルドスクリプト）。`data/<pref>.jsonl` に正規化マージされて初めて「正」になる。

英語レイヤー（i18n）は別経路: `pipeline/i18n_prep.py` → `data/i18n/<pref>_en.jsonl`（parallel file、jmh_id で紐付け）。詳細は5節。

## 3. 絶対ルール

**(a) 公開済みIDは変更禁止。** `data/<pref>.jsonl` の `jmh_id`（`JMH-XXXXXX-NNNN`）は一度公開したら不変。公開済み県を再マージ・gap-fill する場合は **「git HEAD復元 + 内容キー差分追記 + 新規行のみ assign_ids」** 方式を使うこと。`pipeline/out/` の抽出結果には jmh_id が付いていないため、単純上書きマージは既存IDを消失させる（過去に近畿5県+岡山で実際に事故が発生し、git復元で回復した実例あり）。

**(b) build後は必ず全数検算する。**
- 全県で unresolved（dropped, muni_code未解決）= 0
- `rows == ids(jmh_id付与数) == geojson features == pages` が一致

**(c) `vercel deploy` は `--archive=tgz` 必須。**
```bash
npx -y vercel@latest deploy --prod --yes --archive=tgz
```

**(d) スクレイピングは受動的のみ。** GETのみ・自治体サイトあたり最低 2.5秒以上の間隔・robots.txt 遵守・能動スキャン/認証試行は一切行わない（ユーザーの全プロジェクト共通の絶対制約でもある）。robots.txt で禁止されたパスは取得を見送り、その旨を coverage に明記する（例: 一自治体分をクロール見送りにした実績あり）。

**(e) `build_data.py` の多重起動禁止。** 実行前に `ps aux | grep build_data` で生存確認。単県モード（`build_data.py <pref>`）は `data/all.geojson` を上書きしてしまう罠があるため、全県ビルドと混在させない。

## 4. よく使うコマンド

```bash
# ID付与（site/assign_ids.py の PREFS 定数は47県に更新済み。build_data.py と同一の並び）
python3 site/assign_ids.py                      # デフォルトPREFS（全47県）
python3 site/assign_ids.py iwate okinawa         # 対象県を明示

# 派生ファイル再生成（csv/geojson、geocodeはGSI住所検索APIをキャッシュ付きで利用）
python3 site/build_data.py                       # 全県
python3 site/build_data.py --csv-only            # ネットワーク無し、csvのみ
python3 site/build_data.py iwate                 # 単県（all.geojsonを上書きする点に注意）

# 詳細ページ生成
python3 site/build_pages.py

# 静的API生成
python3 site/build_api.py

# スキーマ検証（out/配下、正式マージ前のチェック）
python3 pipeline/validate.py

# ポライトフェッチ（robots.txt遵守・delay内蔵）
./venv/bin/python pipeline/fetch.py pipeline/sources/<pref>_fetch.jsonl \
  --user-agent "bunkazai-collector/1.0 (+https://github.com/kazuki-netizen/jp-municipal-heritage; public cultural-property data; contact via repo issues)"

# デプロイ
git add data/ site/ api/ docs/ README.md SCHEMA.md API.md
git commit -m "..."
git push origin main
npx -y vercel@latest deploy --prod --yes --archive=tgz
# デプロイ後は内容ベースで本番確認する（curlでindex.jsonのtotal/prefecturesを実際に見る）
```

BBOXは全国化済み（`site/build_data.py` の `BBOX = {"lat_min": 24.0, "lat_max": 45.6, "lon_min": 122.5, "lon_max": 146.0}`）。新規に沖縄以西・以南の離島等を扱う場合のみ見直しが必要。

## 5. i18n運用

英語メタデータレイヤーは著作権上の理由から、原文（自治体サイトの説明文）をモデルに渡さず、構造化フィールド（name/category/subcategory/designation/designated_date/municipality/location）のみから再生成する方式。

```bash
python3 pipeline/i18n_prep.py data/<pref>.jsonl \
  --i18n data/i18n/<pref>_en.jsonl \
  --workdir pipeline/i18n_work/<pref> --chunk 40
```

- 生成は sonnet班（1体あたり約200行=5チャンク目安）で並列実行し、`pipeline/i18n_work/<pref>/chunk_*.json` に出力。
- stitch（結合）時に: (1) `description_en` のISO日付表記（例 "designated on 1957-07-20"）をspelled-out形式に正規化 (2) jmh_id突合で欠落・重複がないか検証 → 一致したら `data/i18n/<pref>_en.jsonl` にcommit。
- **stitch班は突合不一致があれば書き込まず停止するのが正しい仕様**。無理に不一致のまま書き込まないこと。
- `romaji_confidence` は常に `"estimated"`（公式な読みのソースが無いため機械推定であることを明示）。
- **prepは必ず最新の `data/<pref>.jsonl` に対して行う。** gap-fillで対象県のデータが後から変わると、prep後にstitch突合が止まる（愛知で実際に発生）。i18n着手前に、その県が最新マージ後かを確認すること。
- サブエージェントは **sonnetのみ**（Fable本人は指示のみ、生成そのものには使わない）。

## 6. 未完了タスク

- **i18n未着手の県（約28県）**: `data/i18n/` に `<pref>_en.jsonl` が存在しない県。存在確認は
  ```bash
  comm -23 <(ls data/*.jsonl | xargs -n1 basename | sed 's/\.jsonl$//' | sort) \
           <(ls data/i18n/*_en.jsonl | xargs -n1 basename | sed 's/_en\.jsonl$//' | sort)
  ```
  で都度取得すること（本ファイルに固定列挙すると陳腐化するため）。着手時はユーザーの一時停止指示（岐阜・愛知チャンク生成後にstitch未実施のまま停止した経緯あり）を再確認してから進める。
- **品質パス項目**: 原典データそのものの異常（誤字・矛盾する指定日・重複疑いのある同名物件等）。名寄せは機械的には行わない方針（同名の正当な別物件が多数存在するため）。
- **honest-partial自治体**: 一覧が部分公開・集計のみ・非公開の自治体は各都道府県ごとの `pipeline/out/<都道府県>/_coverage*.md` および `docs/coverage.md` に理由付きで記録されている。追加照会・gap-fillを行う際はまずここを確認する。

## 7. モデル運用

- サブエージェントは **sonnet** を既定とする。
- **Fable本人が直接手を動かすのは API 関連作業のみ**（`pipeline/english_batch.py` 等のAPI呼び出し設計・デバッグ）。データ抽出・マージ・ビルド・デプロイ作業は原則サブエージェント（sonnet）に委譲する。
