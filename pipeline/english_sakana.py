#!/usr/bin/env python3
"""Generate English metadata (name_romaji / name_en / description_en) via
Sakana fugu-ultra (OpenAI-compatible API). Anthropic-free replacement for
english_batch.py generation; same copyright-safe design.

Usage:
  python pipeline/english_sakana.py data/hokkaido.jsonl --out data/i18n/hokkaido_en.jsonl

Resume-aware: rows whose jmh_id already exists in --out are skipped, and new
results are appended, so re-runs after a crash lose nothing.

Copyright design (identical to english_batch.py):
  - Only structured fields are shown to the model (ALLOWED_FIELDS below);
    municipal prose (`description`) and source_url are never sent.
  - description_en restates structured fields only; no invented history.
  - name_romaji is a best-effort Hepburn reading -> romaji_confidence="estimated".
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from openai import OpenAI

BASE_URL = "https://api.sakana.ai/v1"
MODEL = "fugu-ultra"
CHUNK = 10          # fugu-ultra is a reasoning model; keep chunks small
MAX_TOKENS = 8000   # >=3000 required for fugu-ultra (reasoning overhead)
RETRIES = 3
SLEEP_BETWEEN = 2.0

ALLOWED_FIELDS = [
    "name", "category", "subcategory", "designation",
    "designated_date", "municipality", "location",
]

SYSTEM = (
    "You are a careful bilingual cataloguer creating English metadata for Japanese "
    "cultural properties (bunkazai). You work ONLY from the structured fields given "
    "for each item. You are conservative and never invent facts."
)

RULES = """You will receive a JSON array of cultural-property records. For EACH record, produce an object with these keys: jmh_id, name_romaji, name_en, description_en.

STRICT RULES:
1. COPYRIGHT / NO INVENTED FACTS: Generate description_en using ONLY the fields provided in that record (name, category, subcategory, designation, designated_date, municipality, location). Do NOT add any historical, biographical, artistic, or contextual claim that is not directly derivable from those fields. Many of these are obscure local properties — you have no reliable knowledge of them, so inventing history is the primary error to avoid. If a field is null/missing, simply omit it; never guess a value.

2. description_en: 2-3 short factual sentences. State what the item is (from category/subcategory), its designation status and designating body (from `designation`, e.g. "市指定" = municipally designated, "町指定" = town-designated), the municipality it is located in, and the designation date if present. Do NOT translate or paraphrase any external prose — only restate the given structured fields in fluent English. Do not editorialize ("important", "beautiful", "significant") unless that judgment is literally encoded in a field.

3. name_romaji: Hepburn romanization of the Japanese `name`, using macrons for long vowels (ō, ū, etc.). These readings are your best inference and are NOT verified against any official source. Romanize proper nouns as best you can.

4. name_en: a SHORT descriptive English gloss of the item — a translation/description, NOT a romaji duplicate. Example: 「報恩寺の五百羅漢」 -> "The Five Hundred Rakan of Hōon-ji Temple"; 「木造聖観音立像」 -> "Wooden Standing Statue of the Sacred Avalokiteśvara (Shō-Kannon)". Keep proper-noun place/temple names in romaji within the gloss where natural.

Return exactly one object per input record, covering every jmh_id exactly once. Output ONLY the JSON array — no prose, no markdown fences."""


def get_api_key() -> str:
    env = Path.home() / ".continue" / ".env"
    for line in env.read_text().splitlines():
        if line.startswith("SAKANA_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("SAKANA_API_KEY not found in ~/.continue/.env")


def read_jsonl(path: str) -> list[dict]:
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def project(rows: list[dict]) -> list[dict]:
    """Copyright-safe projection: only ALLOWED_FIELDS, plus jmh_id."""
    out = []
    for r in rows:
        item = {"jmh_id": r["jmh_id"]}
        for k in ALLOWED_FIELDS:
            v = r.get(k)
            if v not in (None, ""):
                item[k] = v
        out.append(item)
    return out


def parse_array(text: str) -> list[dict]:
    """Robustly extract the first JSON array from a model response."""
    s = text.strip()
    if s.startswith("```"):
        s = s.split("```")[1]
        if s.startswith("json"):
            s = s[4:]
    i, j = s.find("["), s.rfind("]")
    if i == -1 or j == -1 or j <= i:
        raise ValueError("no JSON array in response")
    return json.loads(s[i:j + 1])


def validate_chunk(payload: list[dict], results: list[dict]) -> list[dict]:
    want = {p["jmh_id"] for p in payload}
    got = {}
    for r in results:
        jid = r.get("jmh_id")
        if jid not in want:
            raise ValueError(f"unexpected jmh_id {jid}")
        for k in ("name_romaji", "name_en", "description_en"):
            if not isinstance(r.get(k), str) or not r[k].strip():
                raise ValueError(f"{jid}: empty/missing {k}")
        got[jid] = r
    missing = want - set(got)
    if missing:
        raise ValueError(f"missing ids: {sorted(missing)[:5]}...")
    return [got[p["jmh_id"]] for p in payload]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="pref jsonl with jmh_id")
    ap.add_argument("--out", required=True, help="parallel i18n jsonl (appended)")
    ap.add_argument("--limit", type=int, default=0, help="stop after N new rows (0=all)")
    args = ap.parse_args()

    rows = read_jsonl(args.input)
    done: set[str] = set()
    out_path = Path(args.out)
    if out_path.exists():
        done = {r["jmh_id"] for r in read_jsonl(args.out)}
    todo = [r for r in rows if r["jmh_id"] not in done]
    if args.limit:
        todo = todo[: args.limit]
    print(f"input={len(rows)} done={len(done)} todo={len(todo)}")
    if not todo:
        return

    client = OpenAI(base_url=BASE_URL, api_key=get_api_key())
    out_path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with open(out_path, "a") as f:
        for ci in range(0, len(todo), CHUNK):
            payload = project(todo[ci:ci + CHUNK])
            user = RULES + "\n\nRECORDS (JSON array):\n" + json.dumps(payload, ensure_ascii=False)
            last_err = None
            for attempt in range(1, RETRIES + 1):
                try:
                    resp = client.chat.completions.create(
                        model=MODEL, max_tokens=MAX_TOKENS, temperature=0.2,
                        messages=[{"role": "system", "content": SYSTEM},
                                  {"role": "user", "content": user}],
                    )
                    results = validate_chunk(payload, parse_array(resp.choices[0].message.content or ""))
                    for r in results:
                        f.write(json.dumps({
                            "jmh_id": r["jmh_id"],
                            "name_romaji": r["name_romaji"],
                            "romaji_confidence": "estimated",
                            "name_en": r["name_en"],
                            "description_en": r["description_en"],
                        }, ensure_ascii=False) + "\n")
                    f.flush()
                    written += len(results)
                    print(f"chunk {ci // CHUNK}: +{len(results)} (total {written}/{len(todo)})")
                    last_err = None
                    break
                except Exception as e:  # noqa: BLE001 — retry any API/parse failure
                    last_err = e
                    print(f"chunk {ci // CHUNK} attempt {attempt} failed: {type(e).__name__}: {str(e)[:120]}", file=sys.stderr)
                    time.sleep(5 * attempt)
            if last_err is not None:
                print(f"chunk {ci // CHUNK}: giving up after {RETRIES} attempts; continuing", file=sys.stderr)
            time.sleep(SLEEP_BETWEEN)

    print(f"wrote {written} new rows -> {out_path}")


if __name__ == "__main__":
    main()
