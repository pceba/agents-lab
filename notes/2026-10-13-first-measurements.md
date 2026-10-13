# 2026-10-13 · First measurements with a local LLM

**Setup:** Ollama on Windows, 16 GB RAM laptop, 100% CPU (no GPU), 4,096-token context. Models: `qwen3.5:4b` and `qwen3.5:9b`.

## What I learned

1. **Uncontrolled reasoning may never finish.** With thinking mode on, `qwen3.5:4b` spent over 10 minutes "thinking" about a one-sentence question. With `--think=false` it answered in 30 s. A harness always needs a token cap, timeouts, and a deliberate choice about when to let the model reason.

2. **The prompt is the biggest latency lever.** Same model, same question:

   | | Vague prompt | Precise prompt |
   | --- | --- | --- |
   | Tokens generated | 223 | 26 |
   | Generation time | 29.0 s | 4.5 s |
   | Follows the format | No | Yes |
   | Correct | No | Yes (generic) |

   The model doesn't get faster: it writes less. Fewer output tokens = less time and less cost.

3. **On CPU, reading context is expensive.** It reads ~23 tokens/s and generates ~6 tokens/s. A 3,000-token prompt would take ~2 minutes just to be read. For the harness: short context and few calls.

4. **Cold start.** After a few idle minutes, Ollama unloads the model and the next call pays ~15 s of load time.

5. **"Valid JSON" doesn't measure the model.** With a schema, Ollama constrains generation, so the JSON is always well formed. What measures the model is whether the values are right: 4/4 correct, but on an easy case (numbers appear literally in the text). One case is not an eval.

## Script results (`llm_metrics.py --runs 2`, qwen3.5:4b, thinking off)

| Test | Tokens in | Tokens out | TTFT | Latency | Speed | Quality |
| --- | --- | --- | --- | --- | --- | --- |
| Text | 44 | 172 | 2.5 s | 33.8 s | 5.5 tok/s | — |
| JSON | 141 | 138 | 2.3 s | 26.0 s | 5.8 tok/s | JSON 2/2, numbers 4/4 |

Note: these runs used the Spanish version of the prompts; the script is now in English, so token counts will differ slightly.

## Next

- Hard extraction case (computed values, numbers in words, two companies) and compare 4b vs 9b.
- Turn it into a 10-case mini-eval.
