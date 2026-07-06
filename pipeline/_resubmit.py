#!/usr/bin/env python3
"""Resubmit fixed 栃木県 munis as ONE batch with max_tokens=32000.
Reuses PROMPT/SCHEMA/strip logic from extract_batch.py verbatim.
Writes results to out/栃木県/<slug>.jsonl. Robust per-result try/except.
Usage:
  python _resubmit.py submit   # build+submit, print batch id
  python _resubmit.py collect <batch_id>   # collect (safe to re-run)
"""
import os, sys, json, subprocess
from datetime import datetime, timezone

import extract_batch as EB  # reuse PROMPT, RESPONSE_SCHEMA, strip_html, read_doc_text, MODEL

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "out")
PREF = "栃木県"
MAX_TOKENS = 32000
SOURCES = os.path.join(HERE, "sources", "tochigi_final.jsonl")

# Only the munis we fixed / want reprocessed.
TARGETS = ["ashikaga", "sano", "otawara", "nasu", "kanuma", "shimotsuke", "takanezawa"]

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_key():
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    return subprocess.check_output(
        ["security", "find-generic-password", "-s", "ANTHROPIC_API_KEY", "-w"],
        stderr=subprocess.DEVNULL).decode().strip()

def load_meta_and_requests():
    src_by_slug = {}
    for line in open(SOURCES, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        s = json.loads(line)
        src_by_slug[s["slug"]] = s

    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    requests = []
    meta = {}
    for i, slug in enumerate(TARGETS):
        s = src_by_slug[slug]
        muni = s["municipality"]
        d = os.path.join(CACHE, PREF, slug)
        mpath = os.path.join(d, "manifest.json")
        manifest = json.load(open(mpath, encoding="utf-8"))
        bodies, source_urls, fetched = [], [], None
        for k, e in manifest.items():
            if e.get("http_status") != 200 or not e.get("filename"):
                continue
            fmt = e.get("format", "html")
            path = os.path.join(d, e["filename"])
            if not os.path.exists(path):
                continue
            bodies.append(EB.read_doc_text(path, fmt))
            source_urls.append(e["url"])
            fetched = fetched or e.get("fetched_at")
        if not bodies:
            print(f"[skip] {slug}: no bodies")
            continue
        body = "\n\n===\n\n".join(bodies)
        if len(body) > EB.MAX_BODY_CHARS:
            body = body[:EB.MAX_BODY_CHARS]
        cid = f"t{i:02d}_{slug}"[:64]
        meta[cid] = {"pref": PREF, "municipality": muni, "slug": slug,
                     "source_url": source_urls[0], "source_format": "html/csv",
                     "fetched_at": fetched or now_iso(),
                     "official_count": s.get("official_count")}
        requests.append(Request(
            custom_id=cid,
            params=MessageCreateParamsNonStreaming(
                model=EB.MODEL, max_tokens=MAX_TOKENS,
                output_config={"format": {"type": "json_schema", "schema": EB.RESPONSE_SCHEMA}},
                messages=[{"role": "user",
                           "content": EB.PROMPT.format(pref=PREF, municipality=muni, body=body)}],
            )))
        print(f"[req] {cid}: {len(body)} chars body")
    return requests, meta

def submit():
    import anthropic
    os.environ["ANTHROPIC_API_KEY"] = get_key()
    reqs, meta = load_meta_and_requests()
    json.dump(meta, open(os.path.join(HERE, "_resubmit_meta.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    if not reqs:
        print("no requests"); return
    client = anthropic.Anthropic()
    batch = client.messages.batches.create(requests=reqs)
    print("BATCH_ID", batch.id, "status", batch.processing_status)
    open(os.path.join(HERE, "_resubmit_batch_id.txt"), "w").write(batch.id)

def collect(batch_id):
    import anthropic
    os.environ["ANTHROPIC_API_KEY"] = get_key()
    client = anthropic.Anthropic()
    b = client.messages.batches.retrieve(batch_id)
    if b.processing_status != "ended":
        rc = b.request_counts
        print(f"NOT_ENDED status={b.processing_status} proc={rc.processing} ok={rc.succeeded} err={rc.errored}")
        return False
    meta = json.load(open(os.path.join(HERE, "_resubmit_meta.json"), encoding="utf-8"))
    ui = uo = 0
    report = {}
    for result in client.messages.batches.results(batch_id):
        cid = result.custom_id
        m = meta.get(cid, {})
        slug = m.get("slug", cid)
        try:
            if result.result.type != "succeeded":
                err = getattr(result.result, "error", None)
                report[slug] = {"status": result.result.type, "rows": 0, "error": str(err)[:200]}
                print(f"[{slug}] {result.result.type}: {str(err)[:120]}")
                continue
            msg = result.result.message
            ui += msg.usage.input_tokens; uo += msg.usage.output_tokens
            trunc = msg.stop_reason == "max_tokens"
            text = next((x.text for x in msg.content if x.type == "text"), "")
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                report[slug] = {"status": "bad_json", "rows": 0,
                                "truncated": trunc, "raw_len": len(text)}
                print(f"[{slug}] bad_json truncated={trunc} rawlen={len(text)}")
                continue
            rows = parsed.get("rows", [])
            stamped = [{
                "pref": PREF, "municipality": m["municipality"],
                "name": r.get("name"), "category": r.get("category"),
                "subcategory": r.get("subcategory"), "designation": r.get("designation"),
                "designated_date": r.get("designated_date"), "location": r.get("location"),
                "description": r.get("description"), "source_url": m["source_url"],
                "source_format": m["source_format"], "fetched_at": m["fetched_at"],
            } for r in rows]
            pref_dir = os.path.join(OUT, PREF); os.makedirs(pref_dir, exist_ok=True)
            with open(os.path.join(pref_dir, f"{slug}.jsonl"), "w", encoding="utf-8") as f:
                for r in stamped:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            report[slug] = {"status": "succeeded", "rows": len(stamped),
                            "truncated": trunc,
                            "stated_official_count": parsed.get("stated_official_count"),
                            "official_count": m.get("official_count"),
                            "notes": parsed.get("notes", "")[:200]}
            print(f"[{slug}] OK rows={len(stamped)} truncated={trunc} "
                  f"stated={parsed.get('stated_official_count')}")
        except Exception as ex:
            report[slug] = {"status": "collect_exception", "rows": 0, "error": str(ex)[:200]}
            print(f"[{slug}] EXCEPTION {str(ex)[:150]}")
    cost = (ui/1e6*5.0 + uo/1e6*25.0) * 0.5
    report["_cost"] = {"input_tokens": ui, "output_tokens": uo, "batch_cost_usd": round(cost, 4)}
    json.dump(report, open(os.path.join(HERE, "_resubmit_report.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("COST_USD", round(cost, 4), "in", ui, "out", uo)
    return True

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "submit":
        submit()
    elif cmd == "collect":
        collect(sys.argv[2])
