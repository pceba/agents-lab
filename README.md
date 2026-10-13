# agents-lab

My lab for learning LLMs, agents, harness engineering, MCP, evals and system design (Oct 2026 – May 2027).

**Zero cost:** everything runs on local models via [Ollama](https://ollama.com). No API keys, no credit card.

## Structure

| Folder | What goes here | Plan week |
| --- | --- | --- |
| `week-01/` | LLM metrics: tokens, latency, structured outputs | 1 |
| `nanogpt/` | My own GPT trained on Colab or Kaggle (free GPU) | 2 |
| `harness/` | My agent loop from scratch: tools, context, permissions, sandbox | 3–4 |
| `mcp/` | My own MCP server | 5 |
| `evals/` | Eval cases, local LLM-as-judge, results | 6 |
| `notes/system-design/` | One LLM system design per week | 7 → May |
| `notes/papers/` | 5-line summary of each paper or post I read | ongoing |
| `notes/` | Findings from each session | ongoing |

## Setup (Windows)

1. Install Ollama from https://ollama.com and open it (it lives in the system tray).
2. Pull the models:
   ```
   ollama pull qwen3.5:4b
   ollama pull qwen3.5:9b
   ```
3. Run the week 1 script (Python 3.10+ only, no `pip install`):
   ```
   python week-01/llm_metrics.py
   ```

On a CPU-only laptop, use `qwen3.5:4b` day to day and `qwen3.5:9b` for occasional comparisons.

## Week 1 exercises

- [x] Run the script with a model and save the results.
- [x] Compare two model sizes (4b vs 9b): how much accuracy do you gain, and how much speed do you lose?
- [ ] Write a harder extraction case (computed values, numbers in words, two companies) and see where the model breaks.
- [ ] Use `--price-in` and `--price-out` with a provider's public prices to estimate what the same workload would cost in the cloud.
- [x] Write down what surprised you in `notes/`.
