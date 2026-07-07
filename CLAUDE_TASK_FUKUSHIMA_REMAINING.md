# Task: collect 市町村指定文化財 for assigned Fukushima municipalities

Write data/fukushima_parts/<slug>.jsonl per municipality (schema identical to existing files there — inspect one first). Rules:
- Work STRICTLY SERIALLY, one municipality at a time. Do NOT spawn sub-agents.
- Source priority: open-data CSV → official HTML 一覧 → PDF (use native visual Read with pages; if a PDF is garbled multi-column, save to data/pdf_queue/ and record "needs vision pass" instead of writing corrupted rows) → 例規集別表 → honest zero with evidence.
- designation only 市指定/町指定/村指定; exclude 国/県 (count in notes). 和暦→西暦 ISO. null-over-guess, never fabricate.
- Crawl etiquette (HARD): GET only; ≥2s same-domain delay; ≤40 requests/muni; obey robots.txt incl. agent-specific rules.
- 浜通り（双葉郡等）の避難区域町村は文化財情報が特殊な場合がある。見つからなければ honest zero でよいが、震災後に再整備された公式ページがあることも多いので一度は真剣に探すこと。
- Validate each part file: python3 -c "import json,sys;[json.loads(l) for l in open(sys.argv[1])]" <file>
- Append one coverage row per municipality to notes/coverage-fukushima-remaining.md: | muni | source URL | format | rows | difficulty | note |
Return per-municipality: rows written, source, official-count match if stated, difficulty.
