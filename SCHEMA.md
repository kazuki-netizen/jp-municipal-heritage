# SCHEMA (v1)

`data/{pref}.jsonl` (e.g. `hokkaido.jsonl`, `iwate.jsonl`, `miyagi.jsonl`, `aomori.jsonl`, `akita.jsonl`, `yamagata.jsonl`, `fukushima.jsonl`, `tochigi.jsonl`, `gunma.jsonl`, `ibaraki.jsonl`, `saitama.jsonl`, `chiba.jsonl`) is
[JSON Lines](https://jsonlines.org/): one JSON object per line,
one municipality-designated cultural property (市町村指定文化財) per object. UTF-8.
`data/{pref}.csv` has the identical columns (UTF-8 with BOM). `data/{pref}.geojson`
and `data/all.geojson` (combined, all twelve prefectures) carry the same fields inside each
feature's `properties`, plus a derived `geo_precision`.

## Fields (v1)

| Field | Type | Null? | Description |
|---|---|---|---|
| `pref` | string | no | Prefecture name (Japanese). One of `北海道`, `青森県`, `岩手県`, `宮城県`, `秋田県`, `山形県`, `福島県`, `栃木県`, `群馬県`, `茨城県`, `埼玉県`, `千葉県` in this (v9) release. |
| `municipality` | string | no | City/town/village that made the designation (市町村). |
| `name` | string | no | Official name of the property (名称), as published by the source. |
| `category` | string | no | Cultural-property **major class**, normalized to the Agency for Cultural Affairs (文化庁) taxonomy — see "Normalization rules" below. One of: `有形文化財`, `無形文化財`, `民俗文化財`, `記念物(史跡・名勝・天然記念物)`, `その他`. |
| `subcategory` | string | yes | The source's own 種別/分類 wording (e.g. `彫刻`, `無形民俗文化財`, `史跡`), preserved verbatim. **Not** normalized across municipalities — see rule 4. |
| `designation` | string | no | Designating authority level: `市指定` / `町指定` / `村指定`. (National `国指定` and prefectural `県指定` items are **excluded** from this dataset by scope.) |
| `designated_date` | string \| null | yes | Designation date (指定年月日) as ISO `YYYY-MM-DD`, converted from 和暦. `null` when the source publishes no date or the date was unrecoverable — see rule 2 and rule "null-over-guess". |
| `location` | string \| null | yes | Location/address or custodian as published (所在地). Granularity varies by source (full address ↔ 大字 only ↔ holding institution). `null` for placeless items (e.g. a 無形 technique) or where the source omits it. |
| `description` | string \| null | yes | Free-text notes from the source (員数/附 items, remarks). `null` when absent. |
| `source_url` | string | no | URL of the definitive list the row was extracted from. |
| `source_format` | string | no | `html` or `pdf` (open-data CSVs were fetched as `html` portal pages; noted in `docs/sources.md`). |
| `fetched_at` | string | no | ISO 8601 UTC timestamp when the source was fetched. |

### Derived field (geojson only)

| Field | Type | Description |
|---|---|---|
| `geo_precision` | string | `address` if the point was geocoded from the full `location` string; `municipality` if `location` was missing/unresolvable and the point falls back to the municipality centroid. |

## Normalization rules

1. **category → 文化庁大分類.** Each source's 種別 is mapped to one Agency-for-Cultural-Affairs
   major class. `有形文化財`, `無形文化財`, `民俗文化財`, `記念物(史跡・名勝・天然記念物)`.
   Conservation techniques (選定保存技術, e.g. 雫石亀甲織) do not fit any 大分類 and are mapped
   to `その他`. The source's finer label is kept verbatim in `subcategory`.
2. **和暦 → 西暦.** Japanese-era dates (昭和41年10月18日) are converted to ISO `YYYY-MM-DD`
   (`1966-10-18`). Where only a year is published, or the day/month is absent, the date is
   set `null` rather than zero-padded to a fabricated day.
3. **null-over-guess.** When a value is absent, ambiguous, or internally inconsistent in the
   source, the field is `null` — never inferred. Example: 大槌町「小鎚神社の樅の木 昭和4年2月29日」
   (1929 was not a leap year → an impossible date) is stored as `null`, not silently "corrected".
4. **subcategory is verbatim, not normalized.** The same concept appears across municipalities
   as `民俗芸能` / `無形民俗文化財` / `風俗慣習` etc. v1 preserves each source's exact wording
   so nothing is lost; a controlled `subcategory` vocabulary is deferred to v2.
5. **quantity embedded, not structured.** 員数 (counts like "2体", "20冊") and 附 (attached
   items) are kept inside `name`/`description` where the source wrote them; there is no
   dedicated numeric field in v1 (see roadmap).

## Roadmap (v2 candidate fields)

Derived from the Iwate pilot's schema-fit analysis (`notes/schema-issues.md`). These recurred
often enough nationally to justify first-class fields but were out of scope for v1:

- **`count` (int) + `count_unit` (str) + `attached` (list).** Nearly every official designation
  notice carries an 員数 column ("2体", "20冊", "1棟") and 附 (tsuketari) sub-items
  ("附 棟札13枚"). v1 leaves these embedded in `name`/`description`; v2 should structure them.
- **`designation_id` (1-to-many) + `bundle` (bool).** A single official designation can span
  multiple physical objects or dates (宮古 チョウセンアカシジミ = 3 basins/dates under one species;
  花巻「…一括」bundles). Name↔designation is not 1:1; v2 needs a stable designation id that maps
  to N rows and a flag marking explicit 一括 bundles.
- **`date_source_quality` (enum: published / reconstructed / lost-in-extraction).** So coverage
  of *dates* is measurable separately from coverage of *items*. In the pilot, missing dates come
  from two very different causes — the source never published one vs. a PDF layout that destroyed
  it on extraction — and only the latter is a fixable data-quality gap.
- **`source_authority` (enum: opendata-csv / official-site / affiliated-site / archive).** Open-data
  CC-BY CSVs (奥州・北上) are schema-rich and authoritative; a tourism list (金ケ崎) is weak. A
  provenance-quality field lets consumers weight rows and lets a national effort prioritize sources.

Further v2 considerations logged in `notes/schema-issues.md`: splitting `location` into
`address` / `holder` / `lat` / `lon`; an `is_technique` flag for 選定保存技術; and
`status` (active/rescinded) + `status_date` + `supersedes` for 追加指定/指定解除 events that a
nationwide, archive-touching run will encounter (none appear in this current-snapshot pilot).
