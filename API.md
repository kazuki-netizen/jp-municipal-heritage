# jp-municipal-heritage — Static JSON API (v1)

A read-only, CDN-cached JSON API over the jp-municipal-heritage dataset: 78,515
municipality-designated cultural properties (市町村指定文化財) across all 47
Japanese prefectures. Every endpoint is a static file served from Vercel's edge
with `Access-Control-Allow-Origin: *`. **An API key is required** for
`/api/*` — signup is free, instant, and needs only an email address (see
[Authentication](#authentication)). Bulk files under `/data/*` and the map site
remain keyless.

日本語: 全国47都道府県・78,515件の市町村指定文化財データを、静的JSON API
（Vercel静的配信＋CDNキャッシュ、CORS全オリジン許可）として公開しています。
`/api/*` の利用には**APIキーが必要**です（メールアドレスを登録すると無料で即時発行
—下記「Authentication」参照）。`/data/*` の一括ダウンロードと地図サイトはキー不要です。

## Base URL

```
https://jp-municipal-heritage.vercel.app
```

## Authentication

All `/api/v1/*` endpoints require an API key. Get one instantly — no
dashboard, no payment. When email delivery is configured, the key is sent to
your inbox (which doubles as address verification); otherwise it is returned
directly in the response. Either use the web form at
<https://jp-municipal-heritage.vercel.app/site/apikey.html> or curl:

```bash
# 1. Sign up (returns your key immediately)
curl -s -X POST https://jp-municipal-heritage.vercel.app/api/signup \
  -H "content-type: application/json" \
  -d '{"email": "you@example.com"}'
```

```json
{
  "email": "you@example.com",
  "key": "eW91QGV4YW1wbGUuY29tLj...",
  "usage": {
    "header": "x-api-key: <key>",
    "query": "?key=<key>",
    "example": "curl -s -H \"x-api-key: <key>\" https://jp-municipal-heritage.vercel.app/api/v1/index.json"
  }
}
```

```bash
# 2. Call the API with the key (header — recommended)
curl -s -H "x-api-key: $KEY" \
  https://jp-municipal-heritage.vercel.app/api/v1/index.json

# ...or as a query parameter
curl -s "https://jp-municipal-heritage.vercel.app/api/v1/index.json?key=$KEY"
```

Details / notes:

- **Instant issuance, no verification email (v1 trade-off).** The email is
  format-checked only. Signing up again with the same email always returns the
  same key, so a lost key is recovered by simply signing up again.
- The key is a signed token that encodes your email address (base64url) — treat
  it as semi-private and don't publish it. Prefer the `x-api-key` header over
  `?key=` so the key doesn't end up in URL logs and caches.
- Requests without a valid key get `401` with a machine-readable pointer:

  ```json
  { "error": "Missing API key. ...", "signup": "/api/signup", "docs": "https://github.com/kazuki-netizen/jp-municipal-heritage/blob/main/API.md" }
  ```

- Only `/api/*` is protected. `/data/*` (bulk JSONL/CSV/GeoJSON) and the map
  site need no key.

日本語: `/api/v1/*` の全エンドポイントでAPIキーが必要です。
`POST /api/signup` にJSONボディ `{"email": "..."}` を送ると、その場でキーが
返ります（v1の割り切りとして**確認メールは送信されません**。メールは形式チェック
のみ）。同じメールアドレスで再登録すると常に同じキーが返るため、キーを紛失した
場合は再登録してください。キーは `x-api-key` ヘッダ（推奨）または `?key=`
クエリで送ります。キーにはメールアドレスがbase64urlで埋め込まれているため、
公開の場に貼らないでください。キー無しのリクエストは上記形式の `401`
（`signup` / `docs` フィールド付き）を返します。`/data/*` と地図サイトは
引き続きキー不要です。

## Endpoints

### `GET /api/v1/index.json`

Dataset overview: total row count and the list of all 47 prefectures with their
row counts and drill-down URLs.

```bash
curl -s -H "x-api-key: $KEY" https://jp-municipal-heritage.vercel.app/api/v1/index.json
```

```json
{
  "dataset": "jp-municipal-heritage",
  "license": "CC-BY-4.0",
  "total": 78515,
  "generated_at": "2026-07-13T01:25:37Z",
  "prefectures": [
    { "name_ja": "岩手県", "slug": "iwate", "rows": 1972, "en_available": true, "url": "/api/v1/prefectures/iwate.json" },
    "..."
  ],
  "docs": "/API.md"
}
```

### `GET /api/v1/prefectures/<slug>.json`

One prefecture, broken down by municipality. `slug` is the romanized prefecture
name used throughout this repo (`iwate`, `aomori`, `tokyo`, `okinawa`, ...) — see
the `slug` field in `index.json` for the full list.

```bash
curl -s -H "x-api-key: $KEY" https://jp-municipal-heritage.vercel.app/api/v1/prefectures/iwate.json
```

```json
{
  "pref": "岩手県",
  "rows": 1972,
  "municipalities": [
    { "name": "盛岡市", "muni_code": "032018", "rows": 181, "url": "/api/v1/municipalities/032018.json" },
    "..."
  ]
}
```

### `GET /api/v1/municipalities/<key>.json`

Full records for one municipality. `<key>` is the 6-digit JIS local government
code (`032018` = Morioka City). In the current dataset **every municipality
resolves to a code**; if a future row cannot be resolved, its key falls back to
an ASCII-safe form `<pref_slug>--u<utf8-hex of municipality name>` and its
`muni_code` field is `null`. Either way, use the `url` field from the parent
prefecture endpoint rather than constructing keys yourself.

日本語: `<key>` は原則6桁の全国地方公共団体コードです。現行データでは全自治体が
コード解決済みです。将来コード未解決の自治体が出た場合は
`<県slug>--u<自治体名のUTF-8 hex>` 形式のASCIIキーになり、`muni_code` は
`null` になります。キーは自前で組み立てず、県エンドポイントの `url` を使って
ください。

```bash
curl -s -H "x-api-key: $KEY" https://jp-municipal-heritage.vercel.app/api/v1/municipalities/032018.json | python3 -m json.tool | head -30
```

```json
{
  "municipality": "盛岡市",
  "pref": "岩手県",
  "muni_code": "032018",
  "count": 181,
  "items": [
    {
      "pref": "岩手県",
      "municipality": "盛岡市",
      "name": "報恩寺の五百羅漢",
      "category": "有形文化財",
      "subcategory": "彫刻",
      "designation": "市指定",
      "designated_date": "1966-10-18",
      "location": "盛岡市名須川町",
      "description": null,
      "source_url": "https://www.city.morioka.iwate.jp/...",
      "source_format": "html",
      "fetched_at": "2026-07-03T08:24:52Z",
      "jmh_id": "JMH-032018-0003",
      "en": {
        "name_romaji": "Hōonji no Gohyaku Rakan",
        "romaji_confidence": "estimated",
        "name_en": "Five Hundred Arhats of Hōon-ji Temple",
        "description_en": "A Buddhist sculpture (tangible cultural property) held at Nasukawa-chō in Morioka City. It was municipally designated by Morioka City on 1966-10-18."
      }
    }
  ]
}
```

The `en` block is present only for prefectures with an English translation
layer (`data/i18n/*_en.jsonl` — 20 prefectures as of this writing; check the
`en_available` flag per prefecture in `index.json`). Rows without a translation
simply omit the key — do not assume its presence.

**Romanization caveat:** `name_romaji` carries
`"romaji_confidence": "estimated"` — readings of proper nouns (temple, place,
and personal names) were machine-estimated, not verified against official
readings. Treat romaji as a best-effort aid, not an authoritative reading.

日本語: `en` ブロックは英語レイヤー整備済みの県にのみ付きます（`index.json` の
`en_available` で確認可能）。`name_romaji` の読みは機械推定
（`romaji_confidence: "estimated"`）であり、寺社名・地名・人名の公式な読みを
保証しません。

Field definitions for every item (`category`, `designation`, normalization
rules, etc.) are in [`SCHEMA.md`](SCHEMA.md).

## Bulk download

For large pulls, skip the per-municipality endpoint and fetch the source files
directly — same data, no per-request overhead:

```bash
# one prefecture, JSON Lines
curl -s https://jp-municipal-heritage.vercel.app/data/iwate.jsonl

# all prefectures, geocoded points (GeoJSON)
curl -s https://jp-municipal-heritage.vercel.app/data/all.geojson
```

`/data/*` is CORS-open (`Access-Control-Allow-Origin: *`) and, unlike `/api/*`,
requires **no API key**.
See [`SCHEMA.md`](SCHEMA.md) for the full file list (`data/{pref}.jsonl`,
`data/{pref}.csv`, `data/{pref}.geojson`).

## Caching

`/api/*` responses are served with `Cache-Control: public, max-age=3600` — the
API is a build-time snapshot (`generated_at` in `index.json`), not a live
database. Re-fetch `index.json` if you need to detect updates.

## License

**CC-BY-4.0.** Attribution required. Suggested credit line:

> Cultural property data: jp-municipal-heritage (https://github.com/kazuki-netizen/jp-municipal-heritage), CC-BY-4.0.

See [`LICENSE`](LICENSE) for the full text. This covers the data only — API
tooling under `site/` is MIT-licensed (`site/LICENSE`).
