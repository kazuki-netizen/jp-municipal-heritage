# Task: Collect 市町村指定文化財 for Miyagi Prefecture (宮城県)

Collect municipality-designated cultural properties for the 35 municipalities of 宮城県, one part file per municipality, into `data/miyagi_parts/<romaji>.jsonl`.

**Already done — SKIP these:** 岩沼市 (iwanuma.jsonl), 大和町 (taiwa.jsonl).

## Output schema (one JSON object per line; match data/iwate.jsonl exactly)

```json
{"pref":"宮城県","municipality":"仙台市","name":"...","category":"有形文化財","subcategory":"彫刻","designation":"市指定","designated_date":"1966-10-18","location":"...","description":null,"source_url":"https://...","source_format":"html","fetched_at":"2026-07-03T20:00:00+09:00"}
```

- `category`: normalize to 文化庁大分類 (有形文化財/無形文化財/民俗文化財/記念物(史跡・名勝・天然記念物)/その他). Keep the municipality's original wording in `subcategory`.
- `designation`: 市指定 / 町指定 / 村指定 only. EXCLUDE 国指定・県指定・国登録 rows (count them in the coverage notes instead).
- Dates: 和暦→西暦 ISO (YYYY-MM-DD). If the source has no date, use null — **never guess, never fabricate any field**.
- `source_format`: html | pdf | reiki | csv.

## Method per municipality (in this order)

1. Municipal open-data catalog CSV (best case).
2. Official HTML 一覧 page (search: "○○市 指定文化財 一覧").
3. PDF list: try `pdftotext -layout`. **If the PDF is a booklet / multi-column layout and the text comes out interleaved or garbled, do NOT write corrupted rows** — save the PDF to `data/pdf_queue/` and record the municipality as "needs vision pass" in the coverage notes.
4. 例規集の別表.
5. Nothing online → honest zero, record what you checked.

## Crawl etiquette (HARD RULES)

- GET requests only. Never submit forms, never authenticate.
- Sleep ≥2 seconds between requests to the same domain. Max 40 requests per municipal site.
- Check robots.txt per domain first and obey it (including agent-specific rules).

## Quality gates

- Cross-check your row count against any officially stated total on the source page; record match/mismatch per municipality.
- After each part file: validate with `python3 -c "import json,sys; [json.loads(l) for l in open(sys.argv[1])]" <file>`.
- When all municipalities are done: merge all part files into `data/miyagi.jsonl`, validate, and write `notes/coverage-miyagi.md` — a per-municipality table (municipality | source URL | format | rows | missed estimate | difficulty | note) in the same style as `notes/coverage.md`, plus totals and 国/県 counts observed.

## Do not touch

`data/iwate.*`, `site/`, `README.md`, git state (no commits), anything outside this repo.
