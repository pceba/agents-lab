# agents-lab: instructions for coding agents

Read this file and `PROGRESS.md` before doing anything. These instructions are shared by Claude Code and OpenCode.

## What this repo is
Pablo's lab for learning LLMs, agents, harness engineering, MCP, evals and system design (Oct 2026 to May 2027). The plan is in `ROADMAP.md`: an ordered chain of steps, always work on the first unchecked one unless told otherwise.

## Hard constraints
- **Zero cost.** Code in this repo runs on local models via Ollama (`qwen3.5:4b` by default, `qwen3.5:9b` for comparisons). Never add paid APIs, API keys or credit-card services to the project code.
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

## How to work
- Pablo is learning: explain the *why* of each change briefly, don't just dump code.
- Small steps. Propose a plan first, then implement one piece at a time.
- Measure changes with the evals once they exist (roadmap step 2 onward).
- Code, comments, commit messages and repo docs in **English**.
- Never commit `.env`, `results/`, model checkpoints or anything listed in `.gitignore`.
- Commit after each meaningful step with a clear message.

## Handoff between tools
Pablo switches between Claude Code and OpenCode (free models) when usage limits run out.
- `PROGRESS.md` is the single source of truth for the current state. Keep it updated.
- `/handoff` saves the state before switching; `/continue` picks it up.
