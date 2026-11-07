"""Extract a Profile from every speech or platform text with the LLM.

python -m pipeline.extract.run_batch --slice30 | --all | --candidates
"""

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from pipeline.extract.verify import verify_dims

ROOT = Path(__file__).resolve().parents[2]
DIMENSIONS = json.loads((ROOT / "contracts/dimensions.json").read_text())
DIM_IDS = [d["id"] for d in DIMENSIONS]
PROMPT_VERSION = "v1"
PROMPT_TEMPLATE = (ROOT / f"contracts/prompt/extract_{PROMPT_VERSION}.md").read_text()
OUT = ROOT / "data/interim/extract"
CACHE = OUT / "cache"
INGEST = ROOT / "data/interim/ingest"
# shortcut: 16k tokens approximated as 64k characters, upgrade if a tokenizer is wired in
MAX_CHARS = 64_000

SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "stance": {"type": ["number", "null"], "minimum": -1, "maximum": 1},
        "salience": {"type": "number", "minimum": 0, "maximum": 1},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "evidence": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
    },
    "required": ["stance", "salience", "confidence", "evidence"],
    "additionalProperties": False,
}
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {d: SCORE_SCHEMA for d in DIM_IDS},
    "required": DIM_IDS,
    "additionalProperties": False,
}
PROMPT = PROMPT_TEMPLATE.replace(
    "{{DIMENSIONS}}",
    "\n".join(
        f"- `{d['id']}` ({d['label']}): −1 = {d['minus']}; +1 = {d['plus']}"
        for d in DIMENSIONS
    ),
)


def load_env():
    env = ROOT / ".env.local"
    if env.is_file():
        for line in env.read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep and not line.startswith("#"):
                os.environ.setdefault(key.strip(), value.strip())


def call_llm(text: str, model: str) -> dict:
    """One structured-output call through the local Claude Code CLI."""
    # shortcut: only the claude-cli provider exists; add an API client if the batch moves off this laptop
    if os.environ.get("LLM_PROVIDER", "claude-cli") != "claude-cli":
        sys.exit("LLM_PROVIDER must be claude-cli")
    cmd = [
        "claude", "-p", "--model", model, "--output-format", "json",
        "--tools", "", "--no-session-persistence", "--setting-sources", "",
        "--system-prompt", PROMPT, "--json-schema", json.dumps(OUTPUT_SCHEMA),
    ]  # fmt: skip
    start = time.time()
    proc = subprocess.run(
        cmd, check=False, input=text, capture_output=True, text=True, timeout=900
    )
    try:
        res = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"claude exit {proc.returncode}: {proc.stderr[-500:]}")
    if res.get("is_error") or not isinstance(res.get("structured_output"), dict):
        raise RuntimeError(f"claude error: {str(res.get('result'))[:500]}")
    usage = res.get("usage", {})
    return {
        "dims": res["structured_output"],
        "tokens_in": sum(
            usage.get(k, 0)
            for k in (
                "input_tokens",
                "cache_creation_input_tokens",
                "cache_read_input_tokens",
            )
        ),
        "tokens_out": usage.get("output_tokens", 0),
        "seconds": round(time.time() - start, 1),
    }


def extract(text: str, model: str, use_cache: bool = True, retries: int = 3) -> dict:
    """Raw LLM result for text, cached by prompt, model and text."""
    text = text[:MAX_CHARS]
    # the full prompt (which names its version) goes in the key so prompt edits invalidate the cache
    key = hashlib.sha1(f"{PROMPT}\0{model}\0{text}".encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if use_cache and path.is_file():
        return json.loads(path.read_text()) | {"status": "cached"}
    for attempt in range(retries):
        try:
            result = call_llm(text, model)
            break
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(10 * 2**attempt)
    if use_cache:  # a retest must not replace the first run that profiles.json used
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result))
    return result | {"status": "ok"}


def subjects(mode: str) -> list[dict]:
    if mode == "candidates":
        df = pd.read_csv(INGEST / "platforms.csv", dtype=str)
        return [
            {
                "id": r.candidate_id,
                "kind": "candidate",
                "name": r.name,
                "state": r.state,
                "party": r.party,
                "term_start": int(r.candidate_id[-4:]),
                "path": r.text_path,
                "type": "platform",
                "year": int(r.retrieved_at[:4]),
                "url": r.url,
            }
            for r in df.itertuples()
        ]
    df = pd.read_csv(INGEST / "terms.csv", dtype=str)
    if mode == "slice30":
        df = df[df.t0 == "2007"]
    return [
        {
            "id": r.term_id,
            "kind": "historical",
            "name": r.name,
            "state": r.state,
            "party": r.party,
            "term_start": int(r.t0),
            "path": r.speech_path,
            "type": r.speech_type,
            "year": int(r.t0),
            "url": r.source_url,
        }
        for r in df.itertuples()
    ]


def build(subject: dict, model: str) -> tuple[dict | None, dict]:
    text_path = Path(subject["path"])
    text = (text_path if text_path.is_absolute() else ROOT / text_path).read_text()
    log = {"id": subject["id"], "tokens_in": 0, "tokens_out": 0, "seconds": 0}
    try:
        raw = extract(text, model)
    except Exception as e:  # noqa: BLE001 - one failed text must not stop the batch
        print(f"{subject['id']}: {e}", file=sys.stderr)
        return None, log | {"status": "error", "verify_rate": ""}
    # quotes may only come from the part of the text the model saw
    dims, kept, given = verify_dims(raw["dims"], text[:MAX_CHARS])
    profile = {
        "id": subject["id"],
        "kind": subject["kind"],
        "name": subject["name"],
        "state": subject["state"],
        "party": subject["party"],
        "term_start": subject["term_start"],
        "source": {
            "type": subject["type"],
            "year": subject["year"],
            "url": subject["url"],
            "sha1": hashlib.sha1(text.encode()).hexdigest(),
        },
        "dims": {d: dims[d] for d in DIM_IDS},
        "extractor": {"model": model, "prompt_version": PROMPT_VERSION},
    }
    return profile, log | {
        "status": raw["status"],
        "tokens_in": raw["tokens_in"],
        "tokens_out": raw["tokens_out"],
        "seconds": raw["seconds"],
        "verify_rate": round(kept / given, 4) if given else "",
        "kept": kept,
        "given": given,
    }


def main():
    from jsonschema import Draft7Validator

    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--slice30", action="store_const", dest="mode", const="slice30")
    mode.add_argument("--all", action="store_const", dest="mode", const="all")
    mode.add_argument(
        "--candidates", action="store_const", dest="mode", const="candidates"
    )
    args = parser.parse_args()
    load_env()
    model = os.environ.get("LLM_MODEL_BATCH") or "haiku"
    workers = int(os.environ.get("LLM_CONCURRENCY") or 8)

    todo = subjects(args.mode)
    print(f"{len(todo)} texts, model {model}, {workers} at once", file=sys.stderr)
    with ThreadPoolExecutor(workers) as pool:
        results = list(pool.map(lambda s: build(s, model), todo))

    OUT.mkdir(parents=True, exist_ok=True)
    profiles_path = OUT / "profiles.json"
    profiles = {}
    if profiles_path.is_file():
        profiles = {p["id"]: p for p in json.loads(profiles_path.read_text())}
    profiles |= {p["id"]: p for p, _ in results if p}
    merged = [profiles[k] for k in sorted(profiles)]
    schema = json.loads((ROOT / "contracts/schemas/profiles.schema.json").read_text())
    Draft7Validator(schema).validate(merged)
    profiles_path.write_text(json.dumps(merged, indent=1, ensure_ascii=False) + "\n")

    log_path = OUT / "extract_log.csv"
    fields = ["id", "status", "tokens_in", "tokens_out", "seconds", "verify_rate"]
    fields += ["kept", "given"]
    new = not log_path.is_file()
    with log_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fields, extrasaction="ignore")
        if new:
            writer.writeheader()
        writer.writerows(log for _, log in results)

    kept = sum(log.get("kept", 0) for _, log in results)
    given = sum(log.get("given", 0) for _, log in results)
    failed = sum(p is None for p, _ in results)
    print(
        f"wrote {len(merged)} profiles; {failed} failed; "
        f"verify rate {kept}/{given} = {kept / max(given, 1):.3f}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
