# agents-lab

My lab for learning LLMs, agents, harness engineering, MCP, evals and system design (Oct 2026 – May 2027).

**Zero cost:** everything runs on local models via [Ollama](https://ollama.com). No API keys, no credit card.

What I'm working on next: see **[ROADMAP.md](ROADMAP.md)**.

## Structure

| Folder | What goes here | Roadmap step |
| --- | --- | --- |
| `week-01/` | LLM metrics: tokens, latency, structured outputs | 1 |
| `evals/` | Eval cases, trajectory grading, local LLM-as-judge | 2, 9 |
| `nanogpt/` | My own GPT trained on Colab or Kaggle (free GPU) | 3 |
| `harness/` | My agent from scratch: tools, token budget, permissions, checkpoints, routing | 4–7 |
| `mcp/` | My own MCP server | 8 |
| `notes/system-design/` | One LLM system design per week | ongoing |
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

Optional: use `--price-in` and `--price-out` with a provider's public prices to estimate what the same workload would cost in the cloud.
