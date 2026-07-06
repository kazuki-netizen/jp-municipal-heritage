#!/usr/bin/env python3
"""Phase 2: English-fields generation for bunkazai (parallel i18n file).

Design (agreed policy):
- Output is a PARALLEL file keyed by jmh_id. We NEVER modify the base JSONL.
  One line: {"jmh_id","name_romaji","romaji_confidence":"estimated",
             "name_en","description_en"}
- Copyright rule: description_en is generated ONLY from our structured fields
  (name, category, subcategory, designation, designated_date, municipality,
  location). We do NOT pass or translate the municipal `description` prose, and
  the model must not invent history beyond the given fields.
- Romaji honesty rule: all romaji is model-inferred -> romaji_confidence
  "estimated" (there is no official-reading source in our data yet).
- name_en is a short descriptive English gloss, not a transliteration dup.

Submit-then-exit design (no long-blocking process):
  python pipeline/english_batch.py submit  <in.jsonl> [--out-dir DIR]
      -> creates batch, writes DIR/batch_meta.json, prints batch_id, EXITS.
  python pipeline/english_batch.py collect <batch_id> <in.jsonl> [--out FILE]
      -> if batch ended, writes/validates parallel file and exits 0.
         if still processing, prints status and exits 3 (poll again later).

Chunk size 40 rows per Batch request. Model claude-opus-4-8, max_tokens 16000,
output_config json_schema returning an array of
{jmh_id,name_romaji,name_en,description_en}.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

MODEL = "claude-opus-4-8"
CHUNK = 40
MAX_TOKENS = 16000

# Fields we are allowed to expose to the model (the copyright-safe subset).
# NOTE: `description` (municipal prose) and `source_url` are deliberately excluded.
ALLOWED_FIELDS = [
    "name",
    "category",
    "subcategory",
    "designation",
    "designated_date",
    "municipality",
    "location",
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

Return exactly one object per input record, covering every jmh_id exactly once. Output only the array (the response format is constrained to a JSON array)."""

ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "jmh_id": {"type": "string"},
        "name_romaji": {"type": "string"},
        "name_en": {"type": "string"},
        "description_en": {"type": "string"},
    },
    "required": ["jmh_id", "name_romaji", "name_en", "description_en"],
    "additionalProperties": False,
}

# output_config.format must be an object at top level; wrap the array in a key.
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {"type": "array", "items": ITEM_SCHEMA},
    },
    "required": ["results"],
    "additionalProperties": False,
}


def get_api_key() -> str:
    out = subprocess.run(
        ["security", "find-generic-password", "-s", "ANTHROPIC_API_KEY", "-w"],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def read_rows(in_path: str) -> list[dict]:
    rows = []
    with open(in_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield i // n, seq[i:i + n]


def build_payload(rows: list[dict]) -> list[dict]:
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


def make_request(custom_id: str, payload: list[dict]) -> Request:
    user_content = (
        RULES
        + "\n\nRECORDS (JSON array):\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    return Request(
        custom_id=custom_id,
        params=MessageCreateParamsNonStreaming(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM,
            output_config={
                "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}
            },
            messages=[{"role": "user", "content": user_content}],
        ),
    )


def cmd_submit(args):
    client = anthropic.Anthropic(api_key=get_api_key())
    rows = read_rows(args.in_path)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Resume mode: only submit rows whose jmh_id is not already in --resume-from
    # (the partial parallel file). Lets us re-run just the missing rows after a
    # transient failure (e.g. mid-batch credit exhaustion) without redoing work.
    if args.resume_from and os.path.exists(args.resume_from):
        done = set()
        with open(args.resume_from) as f:
            for line in f:
                line = line.strip()
                if line:
                    done.add(json.loads(line)["jmh_id"])
        before = len(rows)
        rows = [r for r in rows if r["jmh_id"] not in done]
        print(f"resume: {len(done)} already done, {len(rows)}/{before} remaining")
        if not rows:
            print("nothing to submit")
            return

    requests = []
    chunk_map = {}  # custom_id -> list of jmh_ids (for validation later)
    for idx, chunk in chunks(rows, CHUNK):
        cid = f"chunk-{idx:04d}"
        requests.append(make_request(cid, build_payload(chunk)))
        chunk_map[cid] = [r["jmh_id"] for r in chunk]

    batch = client.messages.batches.create(requests=requests)
    meta = {
        "batch_id": batch.id,
        "in_path": os.path.abspath(args.in_path),
        "n_rows": len(rows),
        "n_requests": len(requests),
        "chunk_size": CHUNK,
        "model": MODEL,
        "chunk_map": chunk_map,
    }
    (out_dir / "batch_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"batch_id={batch.id}")
    print(f"status={batch.processing_status} requests={len(requests)} rows={len(rows)}")
    print(f"meta written to {out_dir / 'batch_meta.json'}")


def cmd_collect(args):
    client = anthropic.Anthropic(api_key=get_api_key())
    batch = client.messages.batches.retrieve(args.batch_id)
    if batch.processing_status != "ended":
        rc = batch.request_counts
        print(f"status={batch.processing_status} "
              f"processing={rc.processing} succeeded={rc.succeeded} "
              f"errored={rc.errored}")
        sys.exit(3)  # not done yet; caller polls again

    rows = read_rows(args.in_path)
    by_id = {r["jmh_id"]: r for r in rows}
    all_ids = set(by_id.keys())

    collected: dict[str, dict] = {}
    errors = []
    for result in client.messages.batches.results(args.batch_id):
        rtype = result.result.type
        if rtype != "succeeded":
            errors.append((result.custom_id, rtype))
            continue
        msg = result.result.message
        # output_config guarantees first text block is valid JSON per schema.
        text = next((b.text for b in msg.content if b.type == "text"), None)
        if text is None:
            errors.append((result.custom_id, "no_text_block"))
            continue
        data = json.loads(text)
        for item in data["results"]:
            jid = item["jmh_id"]
            collected[jid] = {
                "jmh_id": jid,
                "name_romaji": item["name_romaji"],
                "romaji_confidence": "estimated",
                "name_en": item["name_en"],
                "description_en": item["description_en"],
            }

    # ---- validation ----
    covered = set(collected.keys())
    missing = all_ids - covered
    extra = covered - all_ids
    empties = []
    for jid, obj in collected.items():
        for k in ("name_romaji", "name_en", "description_en"):
            if not str(obj.get(k, "")).strip():
                empties.append((jid, k))

    print("=== VALIDATION ===")
    print(f"source rows: {len(all_ids)}")
    print(f"covered: {len(covered)}")
    print(f"missing (not covered): {len(missing)}")
    if missing:
        print("  missing ids:", sorted(missing)[:20])
    print(f"extra (unknown jmh_id): {len(extra)}")
    if extra:
        print("  extra ids:", sorted(extra)[:20])
    print(f"request errors: {len(errors)}")
    if errors:
        print("  errors:", errors[:20])
    print(f"empty fields: {len(empties)}")
    if empties:
        print("  empties:", empties[:20])

    # Write output only when coverage is complete and clean.
    out_path = args.out or os.path.join(
        os.path.dirname(args.in_path), "i18n",
        os.path.basename(args.in_path).replace(".jsonl", "_en.jsonl"),
    )
    Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)

    # Merge with any existing partial output (resume runs append cleanly).
    merged = dict(collected)
    if args.merge and os.path.exists(out_path):
        with open(out_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                merged.setdefault(obj["jmh_id"], obj)

    # Emit in source order for determinism.
    with open(out_path, "w") as f:
        for r in rows:
            jid = r["jmh_id"]
            if jid in merged:
                f.write(json.dumps(merged[jid], ensure_ascii=False) + "\n")
    n_written = sum(1 for r in rows if r["jmh_id"] in merged)
    print(f"wrote {n_written} lines -> {out_path} "
          f"(this batch: {len(collected)}; merged total: {len(merged)})")

    # Re-evaluate coverage against the merged file, not just this batch.
    final_missing = all_ids - set(merged.keys())
    print(f"final coverage: {len(merged)}/{len(all_ids)}  missing={len(final_missing)}")
    ok = not final_missing and not extra and not errors and not empties
    print("RESULT:", "OK" if ok else "INCOMPLETE")
    sys.exit(0 if ok else 4)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("submit")
    ps.add_argument("in_path")
    ps.add_argument("--out-dir", default="pipeline/out")
    ps.add_argument("--resume-from", default=None,
                    help="partial *_en.jsonl; only submit rows not already in it")
    ps.set_defaults(func=cmd_submit)

    pc = sub.add_parser("collect")
    pc.add_argument("batch_id")
    pc.add_argument("in_path")
    pc.add_argument("--out", default=None)
    pc.add_argument("--merge", action="store_true",
                    help="merge into existing --out file (resume runs)")
    pc.set_defaults(func=cmd_collect)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
