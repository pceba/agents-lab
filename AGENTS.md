# agents-lab: instructions for coding agents

Project rules for agents-lab, shared by Claude Code and OpenCode. Global rules (session protocol, handoff, context hygiene) apply too.

## What this repo is
Pablo's lab for learning LLMs, agents, harness engineering, MCP, evals and system design (Oct 2026 to May 2027). The plan is in `ROADMAP.md`: an ordered chain of steps, always work on the first unchecked one unless told otherwise.

## Hard constraints
- **Zero cost.** Code in this repo runs on local models via Ollama (main pair: `qwen3.5:4b` and `gemma4:e4b-it-qat`; `qwen3.5:9b` only for occasional comparisons). Never add paid APIs, API keys or credit-card services to the project code.
- **CPU-only Windows laptop**, 4,096-token default context. Keep things light.
- **No frameworks for the harness** (no LangChain, LangGraph, etc.). The point is to build it from scratch to learn.
- Python 3.10+, standard library first. Ask before adding a dependency.

## Structure
| Folder | Purpose |
| --- | --- |
| `week-01/` | LLM metrics script and results |
| `evals/` | Eval cases (`cases.jsonl`) and graders |
| `nanogpt/` | Small GPT trained on free Colab/Kaggle GPUs |
| `harness/` | Agent built from scratch: tools, budget, permissions, checkpoints, routing |
| `mcp/` | Own MCP server |
| `notes/` | Session findings; `notes/system-design/` and `notes/papers/` |

## Project-specific working notes
- Measure changes with the evals once they exist (roadmap step 2 onward).
- Never commit `results/`, model checkpoints or anything in `.gitignore`.
- The roadmap is `ROADMAP.md`: tick boxes there when a step is done.

Session protocol, handoff and context rules are global (`~/.config/opencode/AGENTS.md` and `~/.claude/CLAUDE.md`).
