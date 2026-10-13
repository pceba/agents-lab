"""
Week 1 · Measuring an LLM from the inside: tokens, latency and structured outputs.

Runs 100% locally with Ollama (free, no API keys).
Uses only the Python standard library: nothing to pip install.

Usage:
    python llm_metrics.py                       # both tests with the default model
    python llm_metrics.py --model qwen3.5:9b    # another model
    python llm_metrics.py --runs 5              # more runs for more reliable medians
    python llm_metrics.py --only text           # free-text test only
    python llm_metrics.py --only json           # structured-output test only
    python llm_metrics.py --think on            # with reasoning mode (slower)

What it measures:
    - Input (prompt) and output (completion) tokens
    - Time to first token (TTFT): what the user perceives as "how long until it starts"
    - Total latency and generation speed (tokens/second)
    - Whether the structured output matches the requested JSON schema, and whether the values are right
    - Optional equivalent cost: with --price-in / --price-out (USD per million tokens)
      you can estimate what the same workload would cost with a paid provider. Locally it is 0.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "qwen3.5:4b"

TEXT_PROMPT = (
    "In 5 sentences, explain to a business audience what an LLM's context window is "
    "and why it matters when designing an agent."
)

# Consulting-style case: extract structured data from free text.
COMPANY_TEXT = (
    "Lácteos del Norte S.L. is a dairy cooperative from Asturias founded in 1987. "
    "In 2025 it had revenue of 142 million euros, 6% more than the previous year, "
    "with 410 employees. Its CEO, Marta Iglesias, wants to move into plant-based "
    "drinks, but is worried about rising milk prices, pressure from private labels "
    "and a lack of digital talent."
)

COMPANY_SCHEMA = {
    "type": "object",
    "properties": {
        "company": {"type": "string"},
        "sector": {"type": "string"},
        "founded_year": {"type": "integer"},
        "revenue_eur_millions": {"type": "number"},
        "growth_pct": {"type": "number"},
        "employees": {"type": "integer"},
        "risks": {"type": "array", "items": {"type": "string"}},
        "opportunity": {"type": "string"},
    },
    "required": [
        "company",
        "sector",
        "founded_year",
        "revenue_eur_millions",
        "growth_pct",
        "employees",
        "risks",
        "opportunity",
    ],
}

# Ground truth to check whether the model got it right (your first mini-eval).
EXPECTED_COMPANY = {
    "founded_year": 1987,
    "revenue_eur_millions": 142,
    "growth_pct": 6,
    "employees": 410,
}

# Reasoning ("thinking") mode. Models like qwen3.5 think before answering; in small
# models that reasoning can run very long or loop forever. Off by default: change it with --think.
THINK: bool | None = False

# Cap on generated tokens per answer: a safety net against infinite loops.
MAX_TOKENS = 1024


# --------------------------------------------------------------------------- #
# Minimal Ollama client (native /api/chat API, streaming)
# --------------------------------------------------------------------------- #

def check_ollama(host: str, model: str) -> None:
    """Exit with a clear message if Ollama is not running or the model is missing."""
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=5) as r:
            models = [m["name"] for m in json.load(r).get("models", [])]
    except (urllib.error.URLError, ConnectionError, TimeoutError):
        sys.exit(
            f"Can't reach Ollama at {host}.\n"
            "1) Install it from https://ollama.com\n"
            "2) Start it (on Windows it lives in the system tray)\n"
            f"3) Download the model: ollama pull {model}"
        )
    if not any(m == model or m.split(":")[0] == model for m in models):
        sys.exit(
            f"Model '{model}' is not downloaded. Run: ollama pull {model}\n"
            f"Models you have: {', '.join(models) or '(none)'}"
        )


def _open(host: str, body: dict):
    request = urllib.request.Request(
        f"{host}/api/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    return urllib.request.urlopen(request, timeout=600)


def chat(host: str, model: str, messages: list[dict], schema: dict | None = None,
         temperature: float = 0.0) -> dict:
    """Call /api/chat with streaming and return the text plus metrics."""
    body = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": temperature, "num_predict": MAX_TOKENS},
    }
    if schema is not None:
        body["format"] = schema  # structured outputs: Ollama accepts a JSON schema
    if THINK is not None:
        body["think"] = THINK

    start = time.perf_counter()
    ttft = None
    parts: list[str] = []
    thinking: list[str] = []
    final: dict = {}

    try:
        response = _open(host, body)
    except urllib.error.HTTPError as e:
        # Models without a reasoning mode may reject the "think" field: retry without it.
        if e.code == 400 and "think" in body:
            body.pop("think")
            start = time.perf_counter()
            response = _open(host, body)
        else:
            raise

    with response as r:
        for line in r:
            if not line.strip():
                continue
            chunk = json.loads(line)
            message = chunk.get("message", {})
            thinking.append(message.get("thinking", ""))
            content = message.get("content", "")
            if content and ttft is None:
                ttft = time.perf_counter() - start
            parts.append(content)
            if chunk.get("done"):
                final = chunk
                break

    total = time.perf_counter() - start
    tokens_out = final.get("eval_count", 0)
    eval_s = final.get("eval_duration", 0) / 1e9

    return {
        "text": "".join(parts),
        "thinking_chars": len("".join(thinking)),
        "hit_token_cap": final.get("done_reason") == "length",
        "tokens_in": final.get("prompt_eval_count", 0),
        "tokens_out": tokens_out,
        "ttft_s": ttft if ttft is not None else total,
        "latency_s": total,
        "model_load_s": final.get("load_duration", 0) / 1e9,
        "tokens_per_s": tokens_out / eval_s if eval_s > 0 else 0.0,
    }


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #

def text_test(host: str, model: str) -> dict:
    r = chat(host, model, [{"role": "user", "content": TEXT_PROMPT}], temperature=0.7)
    r["test"] = "text"
    return r


def json_test(host: str, model: str) -> dict:
    messages = [
        {
            "role": "system",
            "content": "You are a consulting analyst. Extract the data from the text. "
                       "Reply only with JSON that matches the schema.",
        },
        {"role": "user", "content": COMPANY_TEXT},
    ]
    r = chat(host, model, messages, schema=COMPANY_SCHEMA)
    r["test"] = "json"

    try:
        data = json.loads(r["text"])
        missing = [k for k in COMPANY_SCHEMA["required"] if k not in data]
        correct = sum(
            1 for k, v in EXPECTED_COMPANY.items()
            if isinstance(data.get(k), (int, float)) and abs(data[k] - v) < 1e-6
        )
        r["valid_json"] = not missing
        r["missing_fields"] = missing
        r["correct"] = f"{correct}/{len(EXPECTED_COMPANY)}"
    except json.JSONDecodeError:
        r["valid_json"] = False
        r["missing_fields"] = COMPANY_SCHEMA["required"]
        r["correct"] = f"0/{len(EXPECTED_COMPANY)}"
    return r


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #

def equivalent_cost(r: dict, price_in: float, price_out: float) -> float:
    return (r["tokens_in"] * price_in + r["tokens_out"] * price_out) / 1_000_000


def summary(results: list[dict], price_in: float, price_out: float) -> None:
    for test in ("text", "json"):
        rows = [r for r in results if r["test"] == test]
        if not rows:
            continue
        # The first run includes loading the model into memory: it is reported separately.
        warm = rows[1:] or rows
        med = lambda k: statistics.median(r[k] for r in warm)  # noqa: E731

        print(f"\n=== Test: {test} · {len(rows)} runs ===")
        print(f"Input tokens   (median) : {med('tokens_in'):.0f}")
        print(f"Output tokens  (median) : {med('tokens_out'):.0f}")
        print(f"TTFT           (median) : {med('ttft_s'):.2f} s")
        print(f"Total latency  (median) : {med('latency_s'):.2f} s")
        print(f"Speed          (median) : {med('tokens_per_s'):.1f} tokens/s")
        print(f"Model load (1st run)    : {rows[0]['model_load_s']:.2f} s")
        print(f"Thinking       (median) : {med('thinking_chars'):.0f} chars")
        capped = sum(r["hit_token_cap"] for r in rows)
        if capped:
            print(f"Hit the token cap       : {capped}/{len(rows)} (raise --max-tokens or use --think off)")
        print("Actual cost (local)     : 0.00 USD")
        if price_in or price_out:
            c = statistics.median(equivalent_cost(r, price_in, price_out) for r in warm)
            print(f"Equivalent cost/call    : {c:.6f} USD (at your reference prices)")
        if test == "json":
            valid = sum(r["valid_json"] for r in rows)
            print(f"Valid JSON              : {valid}/{len(rows)}")
            print(f"Correct numbers         : {', '.join(r['correct'] for r in rows)}")

    last_json = next((r for r in reversed(results) if r["test"] == "json"), None)
    if last_json:
        print("\nLast structured output:")
        print(last_json["text"])


def main() -> None:
    p = argparse.ArgumentParser(description="Measure tokens, latency and structured outputs of a local LLM.")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--only", choices=["text", "json"])
    p.add_argument("--price-in", type=float, default=0.0, help="USD per million input tokens (reference)")
    p.add_argument("--price-out", type=float, default=0.0, help="USD per million output tokens (reference)")
    p.add_argument("--think", choices=["off", "on", "default"], default="off",
                   help="Model reasoning mode (off by default)")
    p.add_argument("--max-tokens", type=int, default=1024, help="Cap on tokens per answer")
    a = p.parse_args()

    global THINK, MAX_TOKENS
    THINK = {"off": False, "on": True, "default": None}[a.think]
    MAX_TOKENS = a.max_tokens

    check_ollama(a.host, a.model)
    tests = [text_test, json_test]
    if a.only:
        tests = [text_test] if a.only == "text" else [json_test]

    results = []
    for test in tests:
        for i in range(a.runs):
            print(f"{test.__name__} · run {i + 1}/{a.runs}...", flush=True)
            r = test(a.host, a.model)
            r.update({"model": a.model, "run": i + 1})
            results.append(r)

    summary(results, a.price_in, a.price_out)

    folder = Path(__file__).parent / "results"
    folder.mkdir(exist_ok=True)
    path = folder / f"metrics-{a.model.replace(':', '_')}-{datetime.now():%Y%m%d-%H%M%S}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nResults saved to {path}")


if __name__ == "__main__":
    main()
