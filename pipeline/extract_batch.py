#!/usr/bin/env python3
"""extract_batch.py — Message Batches extraction for cached municipalities.

For each cached municipality in a sources.jsonl:
  - HTML/CSV docs: strip to text, embed in a batch request prompt.
  - PDF docs: NOT batched; the muni is written to out/<pref>/_pdf_queue.jsonl
    marked needs_vision for an interactive (vision) agent to process.

Submits all HTML/CSV requests as ONE Anthropic Message Batch
(claude-opus-4-8, max_tokens=16000, output_config json_schema), polls to
completion, then writes results to out/<pref>/<slug>.jsonl and a per-pref
report (out/<pref>/_report.json).

API key comes from the macOS keychain:
    security find-generic-password -s ANTHROPIC_API_KEY -w
It is read into the environment for the Anthropic client and never printed.

Usage:
    python extract_batch.py <sources.jsonl> [--cache DIR] [--out DIR] [--dry-run]
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE = os.path.join(HERE, "cache")
DEFAULT_OUT = os.path.join(HERE, "out")
MODEL = "claude-opus-4-8"
MAX_TOKENS = 16000

# ---- Row + response JSON schema handed to the model -----------------------

ROW_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        "category": {
            "type": "string",
            "enum": [
                "有形文化財", "無形文化財", "民俗文化財",
                "記念物(史跡・名勝・天然記念物)", "その他",
            ],
        },
        "subcategory": {"type": ["string", "null"]},
        "designation": {"type": "string", "enum": ["市指定", "町指定", "村指定"]},
        "designated_date": {"type": ["string", "null"]},
        "location": {"type": ["string", "null"]},
        "description": {"type": ["string", "null"]},
    },
    "required": [
        "name", "category", "subcategory", "designation",
        "designated_date", "location", "description",
    ],
}

RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "rows": {"type": "array", "items": ROW_SCHEMA},
        "stated_official_count": {"type": ["integer", "null"]},
        "notes": {"type": "string"},
    },
    "required": ["rows", "stated_official_count", "notes"],
}

# ---- The extraction rules (embedded verbatim from SCHEMA.md v1) ------------

PROMPT = """\
あなたは日本の市町村指定文化財（していぶんかざい）の一覧ページから、
構造化データを抽出する専門家です。以下の原文（HTML/CSVをテキスト化したもの）から、
指定文化財を1件ずつ行として抽出してください。

# 抽出対象（designation）
- 抽出して rows に入れるのは **市指定 / 町指定 / 村指定** の文化財のみ。
- **国指定・県（都・道・府）指定は rows に含めない**。ただし原文に「国指定○件」
  「県指定○件」等の記載があれば、市町村指定の件数と合算して原文が主張する総数を
  読み取り、市町村指定分のみの主張件数を stated_official_count に入れること
  （原文が市町村指定の件数だけを明記していればそれを、総数しか無ければ null）。
- designation は必ず市指定/町指定/村指定のいずれか。市→市指定、町→町指定、村→村指定。

# フィールド
- name: 名称。原文どおり。**員数（2体, 20冊, 1棟 等）や指定番号が原文にある場合は
  name または description に必ず残す**。同名の別物件が区別できなくなるのを防ぐため、
  員数・指定番号・附（つけたり）情報を description に折り込むこと。
- category: 文化庁大分類に正規化。次のいずれか1つ:
  有形文化財 / 無形文化財 / 民俗文化財 / 記念物(史跡・名勝・天然記念物) / その他。
  選定保存技術など大分類に収まらないものは その他。
- subcategory: **原文の種別・分類の語をそのまま（verbatim）**。正規化しない
  （例: 彫刻, 無形民俗文化財, 史跡, 風俗慣習）。原文に種別が無ければ null。
- designated_date: 指定年月日。**和暦→西暦に変換し ISO の YYYY-MM-DD**
  （昭和41年10月18日 → 1966-10-18）。年しか無い/日月が欠ける/変換不能/
  ありえない日付（閏年でない年の2月29日 等）は **推測せず null**。
- location: 所在地・保管先。原文どおり。無ければ null。無形技術など場所が無いものは null。
- description: 員数・附・指定番号・備考など。無ければ null。

# 大原則
- **null-over-guess**: 値が原文に無い/曖昧/矛盾するときは、推測せず null。
- 原文に列挙された市町村指定文化財を **漏れなく全件** 行にすること。重複は出さない。
- 出力は指定の JSON スキーマに厳密に従うこと。

以下が対象自治体と原文です。

自治体: {pref} {municipality}
--- 原文ここから ---
{body}
--- 原文ここまで ---
"""

MAX_BODY_CHARS = 120_000  # keep prompts well under context; huge lists are rare


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_api_key():
    """Read ANTHROPIC_API_KEY from the macOS keychain. Never printed."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    try:
        key = subprocess.check_output(
            ["security", "find-generic-password", "-s", "ANTHROPIC_API_KEY", "-w"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except subprocess.CalledProcessError:
        sys.exit("ANTHROPIC_API_KEY not found in keychain or environment.")
    if not key:
        sys.exit("ANTHROPIC_API_KEY resolved empty.")
    return key


def strip_html(raw):
    """Very light HTML->text: drop script/style, tags, collapse whitespace."""
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", raw)
    raw = re.sub(r"(?i)</td>", "\t", raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r"\n\s*\n\s*\n+", "\n\n", raw)
    return raw.strip()


def read_doc_text(path, fmt):
    with open(path, "rb") as f:
        data = f.read()
    # decode: try utf-8, then cp932/shift_jis (common on JP municipal sites)
    text = None
    for enc in ("utf-8", "cp932", "shift_jis", "euc_jp"):
        try:
            text = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        text = data.decode("utf-8", errors="replace")
    if fmt == "html":
        text = strip_html(text)
    return text


def build_requests(sources_path, cache_dir, out_dir):
    """Return (batch_requests, meta_by_id, pdf_queue_by_pref)."""
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    batch_requests = []
    meta = {}                 # custom_id -> {pref, municipality, slug, source_url, source_format, fetched_at, official_count}
    pdf_queue = {}            # pref -> [entries]

    with open(sources_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            src = json.loads(line)
            pref, slug, muni = src["pref"], src["slug"], src["municipality"]
            muni_dir = os.path.join(cache_dir, pref, slug)
            manifest_path = os.path.join(muni_dir, "manifest.json")
            if not os.path.exists(manifest_path):
                print(f"[no-cache] {pref}/{slug}: no manifest, run fetch.py first")
                continue
            with open(manifest_path, encoding="utf-8") as mf:
                manifest = json.load(mf)

            # Gather text bodies from html/csv docs; route pdf to the queue.
            bodies = []
            source_urls = []
            fmts = set()
            fetched_at = None
            has_pdf = False
            for h, entry in manifest.items():
                if entry.get("http_status") != 200 or not entry.get("filename"):
                    continue
                fmt = entry.get("format", "html")
                if fmt == "pdf":
                    has_pdf = True
                    pdf_queue.setdefault(pref, []).append({
                        "pref": pref, "municipality": muni, "slug": slug,
                        "source_url": entry["url"], "source_format": "pdf",
                        "cache_path": os.path.join(muni_dir, entry["filename"]),
                        "fetched_at": entry.get("fetched_at"),
                        "official_count": src.get("official_count"),
                        "needs_vision": True,
                    })
                    continue
                path = os.path.join(muni_dir, entry["filename"])
                if not os.path.exists(path):
                    continue
                bodies.append(read_doc_text(path, fmt))
                source_urls.append(entry["url"])
                fmts.add("html" if fmt in ("html", "csv") else fmt)
                fetched_at = fetched_at or entry.get("fetched_at")

            if not bodies:
                if has_pdf:
                    print(f"[pdf-queue] {pref}/{slug}: PDF-only, queued for vision")
                else:
                    print(f"[empty] {pref}/{slug}: no usable cached docs")
                continue

            body = "\n\n===\n\n".join(bodies)
            if len(body) > MAX_BODY_CHARS:
                body = body[:MAX_BODY_CHARS]

            # custom_id must match ^[a-zA-Z0-9_-]{1,64}$ (ASCII only). Slugs are
            # ASCII; disambiguate across prefectures with a numeric index.
            custom_id = f"m{len(meta):04d}_{slug}"[:64]
            meta[custom_id] = {
                "pref": pref, "municipality": muni, "slug": slug,
                "source_url": source_urls[0],
                "source_format": "html",
                "fetched_at": fetched_at or now_iso(),
                "official_count": src.get("official_count"),
            }
            batch_requests.append(Request(
                custom_id=custom_id,
                params=MessageCreateParamsNonStreaming(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    output_config={
                        "format": {
                            "type": "json_schema",
                            "schema": RESPONSE_SCHEMA,
                        }
                    },
                    messages=[{
                        "role": "user",
                        "content": PROMPT.format(pref=pref, municipality=muni, body=body),
                    }],
                ),
            ))

    return batch_requests, meta, pdf_queue


def write_pdf_queue(pdf_queue, out_dir):
    for pref, entries in pdf_queue.items():
        pref_dir = os.path.join(out_dir, pref)
        os.makedirs(pref_dir, exist_ok=True)
        qpath = os.path.join(pref_dir, "_pdf_queue.jsonl")
        with open(qpath, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        print(f"[pdf-queue] {pref}: {len(entries)} entries -> {qpath}")


def run(sources_path, cache_dir, out_dir, dry_run):
    import anthropic

    batch_requests, meta, pdf_queue = build_requests(sources_path, cache_dir, out_dir)
    os.makedirs(out_dir, exist_ok=True)
    write_pdf_queue(pdf_queue, out_dir)

    if not batch_requests:
        print("No HTML/CSV requests to batch.")
        return

    print(f"\nPrepared {len(batch_requests)} batch requests "
          f"({len(pdf_queue)} prefs have PDF-queued munis).")
    if dry_run:
        print("[dry-run] not submitting.")
        return

    os.environ["ANTHROPIC_API_KEY"] = get_api_key()
    client = anthropic.Anthropic()

    batch = client.messages.batches.create(requests=batch_requests)
    print(f"[batch] created {batch.id} status={batch.processing_status}")

    while True:
        batch = client.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        rc = batch.request_counts
        print(f"[batch] {batch.processing_status} "
              f"processing={rc.processing} succeeded={rc.succeeded} errored={rc.errored}")
        time.sleep(20)

    # Collect results keyed by custom_id.
    rows_by_pref = {}   # pref -> {slug -> [rows]}
    report = {}         # pref -> {slug -> {...}}
    usage_in = usage_out = 0
    cache_read = cache_write = 0
    n_ok = n_err = 0

    for result in client.messages.batches.results(batch.id):
        cid = result.custom_id
        m = meta.get(cid)
        rtype = result.result.type
        if rtype != "succeeded":
            n_err += 1
            if m:
                report.setdefault(m["pref"], {})[m["slug"]] = {
                    "status": rtype, "rows": 0,
                }
            print(f"[result] {cid}: {rtype}")
            continue
        n_ok += 1
        msg = result.result.message
        u = msg.usage
        usage_in += u.input_tokens
        usage_out += u.output_tokens
        cache_read += getattr(u, "cache_read_input_tokens", 0) or 0
        cache_write += getattr(u, "cache_creation_input_tokens", 0) or 0

        text = next((b.text for b in msg.content if b.type == "text"), "")
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            report.setdefault(m["pref"], {})[m["slug"]] = {
                "status": "bad_json", "rows": 0,
            }
            print(f"[result] {cid}: bad JSON")
            continue

        stamped = []
        for r in parsed.get("rows", []):
            stamped.append({
                "pref": m["pref"], "municipality": m["municipality"],
                "name": r.get("name"),
                "category": r.get("category"),
                "subcategory": r.get("subcategory"),
                "designation": r.get("designation"),
                "designated_date": r.get("designated_date"),
                "location": r.get("location"),
                "description": r.get("description"),
                "source_url": m["source_url"],
                "source_format": m["source_format"],
                "fetched_at": m["fetched_at"],
            })
        rows_by_pref.setdefault(m["pref"], {})[m["slug"]] = stamped
        report.setdefault(m["pref"], {})[m["slug"]] = {
            "status": "succeeded",
            "rows": len(stamped),
            "stated_official_count": parsed.get("stated_official_count"),
            "official_count_source": m["official_count"],
            "notes": parsed.get("notes", ""),
        }

    # Write per-muni jsonl and per-pref report.
    for pref, slugs in rows_by_pref.items():
        pref_dir = os.path.join(out_dir, pref)
        os.makedirs(pref_dir, exist_ok=True)
        for slug, rows in slugs.items():
            with open(os.path.join(pref_dir, f"{slug}.jsonl"), "w", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ----- cost -----
    # claude-opus-4-8: $5/1M in, $25/1M out. Batches API = 50% off.
    in_cost = usage_in / 1_000_000 * 5.0
    out_cost = usage_out / 1_000_000 * 25.0
    cr_cost = cache_read / 1_000_000 * 0.5      # ~0.1x input
    cw_cost = cache_write / 1_000_000 * 6.25    # ~1.25x input
    batch_cost = (in_cost + out_cost + cr_cost + cw_cost) * 0.5

    for pref, slugs in report.items():
        pref_dir = os.path.join(out_dir, pref)
        os.makedirs(pref_dir, exist_ok=True)
        with open(os.path.join(pref_dir, "_report.json"), "w", encoding="utf-8") as f:
            json.dump({
                "batch_id": batch.id,
                "municipalities": slugs,
            }, f, ensure_ascii=False, indent=2)

    summary = {
        "batch_id": batch.id,
        "requests": len(batch_requests),
        "succeeded": n_ok, "errored": n_err,
        "usage": {
            "input_tokens": usage_in, "output_tokens": usage_out,
            "cache_read_input_tokens": cache_read,
            "cache_creation_input_tokens": cache_write,
        },
        "batch_cost_usd": round(batch_cost, 4),
    }
    with open(os.path.join(out_dir, "_batch_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n--- batch summary ---")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser(description="Batch extraction for bunkazai.")
    ap.add_argument("sources", help="path to a sources.jsonl")
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--dry-run", action="store_true", help="build requests but don't submit")
    args = ap.parse_args()
    if not os.path.exists(args.sources):
        sys.exit(f"sources file not found: {args.sources}")
    run(args.sources, args.cache, args.out, args.dry_run)


if __name__ == "__main__":
    main()
