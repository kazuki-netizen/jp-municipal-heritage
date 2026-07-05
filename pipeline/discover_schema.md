# sources.jsonl format (pipeline/sources/*.jsonl)

The nationwide collection pipeline is driven by **sources files** in
[JSON Lines](https://jsonlines.org/): one municipality per line. `fetch.py` reads
a sources file, downloads the listed URLs into `pipeline/cache/<pref>/<slug>/`,
and `extract_batch.py` turns each cached municipality into one Anthropic Message
Batch request. One line = one municipality (市町村) = one designating authority.

```json
{
  "pref": "岩手県",
  "municipality": "二戸市",
  "slug": "ninohe",
  "urls": [
    {"url": "http://www.edu.city.ninohe.iwate.jp/~maibun/siteibunkazai.html",
     "format": "html", "note": "埋文センター 市指定文化財一覧"}
  ],
  "strategy": "html",
  "official_count": 73
}
```

## Fields

| Field | Type | Req | Description |
|---|---|---|---|
| `pref` | string | yes | Prefecture name in Japanese (e.g. `岩手県`). |
| `municipality` | string | yes | City/town/village that made the designation (市町村), Japanese. |
| `slug` | string | yes | ASCII slug, unique within a prefecture. Used for cache/out paths (`cache/<pref>/<slug>/`, `out/<pref>/<slug>.jsonl`). Romaji of the municipality (e.g. `ninohe`, `yahaba`). |
| `urls` | array | yes | One or more source documents. May be `[]` when `strategy` is `none`. Each entry: |
| &nbsp;&nbsp;`url` | string | yes | Absolute URL of the definitive designation list. |
| &nbsp;&nbsp;`format` | string | yes | `html` \| `pdf` \| `csv`. Drives extraction routing (see below). |
| &nbsp;&nbsp;`note` | string | no | Human note on what the doc is (page title, section). |
| `strategy` | string | yes | How this municipality is sourced: `opendata` (CC-licensed open-data CSV portal), `html` (a plain designation-list web page), `pdf` (a PDF notice/list), `reiki` (例規集 / ordinance database page), `none` (no public list found — placeholder; skipped by fetch). |
| `official_count` | int \| null | yes | The count the source itself *states* it holds (e.g. "市指定文化財 73件"), when published; else `null`. Used only for coverage reconciliation in `validate.py` — never as ground truth for extraction. |

## Extraction routing (extract_batch.py)

- `format: "html"` / `format: "csv"` → the document text is **stripped to plain
  text and embedded in the batch prompt**. These are submitted to the Message
  Batches API (`claude-opus-4-8`, 50% cheaper, async).
- `format: "pdf"` → **NOT batched.** PDFs need vision; per-page-PNG batching is
  expensive and the Batches API can't take large images cheaply. The muni is
  written to `out/<pref>/_pdf_queue.jsonl` marked `"needs_vision": true`, for an
  interactive agent (with Read/vision) to process separately. `extract_batch.py`
  skips it in the batch.

## Row schema produced (per the reviewed dataset, SCHEMA.md v1)

Each batch request returns
`{"rows": [<row>], "stated_official_count": int|null, "notes": str}` where each
`<row>` carries the eight extraction fields:

```json
{
  "name": "…（員数・指定番号を含めて重複しない名称）",
  "category": "有形文化財|無形文化財|民俗文化財|記念物(史跡・名勝・天然記念物)|その他",
  "subcategory": "彫刻",           // source's own 種別 verbatim, or null
  "designation": "市指定|町指定|村指定",
  "designated_date": "1966-10-18", // ISO, 和暦→西暦, or null (null-over-guess)
  "location": "…",                 // or null
  "description": "…（員数/附/指定番号 remarks）"  // or null
}
```

`pref`, `municipality`, `source_url`, `source_format`, `fetched_at` are stamped
onto each row by the pipeline (from sources.jsonl + the fetch manifest), so the
model does not need to emit them. The exact extraction rules the model is given
live in `extract_batch.py` (PROMPT): 国指定/県指定 excluded from rows but counted
toward `stated_official_count`; only 市/町/村指定 kept; 文化庁大分類 normalization
keeping the source label in `subcategory`; 和暦→西暦; null-over-guess; 指定番号/員数
folded into `description` so same-name items stay distinct.
