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

## Session protocol (automatic, both tools)
Pablo switches between Claude Code and OpenCode (free models) when usage limits run out. `PROGRESS.md` is the single source of truth for the current state and is loaded automatically at the start of every session. There is no need for him to type `/continue` or `/handoff`; don't suggest them.

**When a session starts** (first message, whatever it is):
1. Use the `PROGRESS.md` already in your context; do not ask Pablo to explain where we are.
2. Run `git status --short` and `git log --oneline -3` to check nothing changed since the last handoff.
3. Open with a 2-line status (current step + next task), then answer his message.

**When Pablo wants to stop**: if he says anything like "cerramos", "lo dejamos aquí", "me voy", "handoff", "wrap up", "close", or you are clearly near your usage or context limit:
- **If files changed this session:**
  1. Rewrite `PROGRESS.md` (under ~40 lines): last updated (date + tool/model), current step, done this session, the single next task, open threads, decisions and gotchas. Replace stale content; don't append forever.
  2. Tick finished boxes in `ROADMAP.md`. Longer findings go to `notes/YYYY-MM-DD-topic.md`, not to `PROGRESS.md`.
  3. Commit everything with a clear message (never ignored files).
  4. Reply with a 3-line summary.
- **If nothing changed** (clean `git status`, only reading/talking): don't commit. If the session produced a decision or insight worth keeping, add it to `PROGRESS.md` and commit; otherwise just confirm in one line that the state is saved and what the next task is.

## Context hygiene
- One task per session. When a task is done and committed, suggest starting a fresh session instead of continuing a long one.
- Explore narrowly: to look at a folder, list only that folder (not the whole repo recursively); read specific files, line ranges or grep results. Never dump whole folders or large result files into context.
- Don't paste long command output back; summarize it.
- Durable knowledge goes to files (`PROGRESS.md`, `notes/`), not to the chat: the chat is disposable.
