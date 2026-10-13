# Roadmap

An ordered chain of steps, not a schedule. Each step builds on the previous one and fits in one or two sessions. When I sit down to work, I pick the first unchecked step. Calendar blocks are just reminders to start.

**Constraints:** zero cost (local models via Ollama, free Colab/Kaggle GPUs), CPU-only laptop, 4,096-token default context.

**One fixed date:** Step 10 (the FDE project) should be ready to start mid-December, because it needs real people and Christmas is the long window.

---

## Step 1 · Break the model
- [x] Measure tokens, latency and structured outputs (`week-01/llm_metrics.py`)
- [ ] Write a hard extraction case myself: a value that must be computed, numbers written in words, a second company as a distractor
- [ ] Compare `qwen3.5:4b` vs `qwen3.5:9b` on it

**Learn:** where small models fail, and whether size fixes it.
**Done when:** my notes have a 4b vs 9b accuracy table for the hard case.

## Step 2 · First real eval
- [ ] 10 extraction cases (easy, hard, adversarial) stored in `evals/cases.jsonl`
- [ ] One command that prints accuracy per model

**Learn:** the core habit of the whole plan. From here on, every change (prompt, model, harness) gets measured.
**Done when:** the command prints something like `4b: 7/10 · 9b: 9/10`.

## Step 3 · Understand the model from the inside
- [ ] 3Blue1Brown, transformer chapters
- [ ] Karpathy, "Let's build GPT", coding along on Colab or Kaggle
- [ ] Compare how many tokens the same text takes in Spanish vs English

**Learn:** what a token, attention and the context window really are, and why context costs.
**Done when:** a small GPT I trained generates text (`nanogpt/`).

## Step 4 · Tool use: the model calls a function
- [ ] Give the model one tool (calculator or read-file) and let it decide when to call it. Single turn, no loop.

**Learn:** the model never executes anything. It *asks* for a call, and my code runs it.
**Done when:** "what is 1,234 × 5,678?" gets the right answer through the tool.

## Step 5 · Mini-harness v0: my first agent
- [ ] Agent loop from scratch (~200 lines, no frameworks): model requests tools → code runs them → results go back → repeat
- [ ] 3 tools and explicit stop conditions (max steps, max tokens, timeout)

**Learn:** what an agent is under the hood.
**Done when:** it completes a multi-step task on its own (`harness/`).

## Step 6 · Harness v1: safety, context and durability
- [ ] **Least privilege:** each tool gets only the permissions it needs; sandbox to one folder
- [ ] **Human-in-the-loop:** asks for my approval before risky actions
- [ ] **Token budget:** fixed budget per section (instructions, tool schemas, history, retrieved docs) inside the 4,096-token window
- [ ] **Context compaction:** summarize old turns when the budget is exceeded
- [ ] **Checkpointing:** saves its state to a file and can resume after a crash or Ctrl+C

**Learn:** what separates a toy from something deployable. My small context window turns budgeting into a real design exercise.
**Done when:** it survives a long task, asks before writing, and resumes after being killed.

## Step 7 · Model routing (4b → 9b)
- [ ] Router: `qwen3.5:4b` by default, escalate to `qwen3.5:9b` only for hard tasks or low confidence
- [ ] Measure with my evals: quality gained vs latency added, compared to always-4b and always-9b

**Learn:** model cascades and cost/latency trade-offs, the core of LLM system design.
**Done when:** I have a table showing the router beats both single-model baselines on at least one axis.

## Step 8 · My MCP server
- [ ] Package useful tools (e.g. company financial data) as an MCP server, using the official Python SDK
- [ ] Connect it to my harness
- [ ] Optional, one afternoon: a minimal raw JSON-RPC version without the SDK, to understand the protocol

**Learn:** the industry standard for connecting agents to tools and data.
**Done when:** my harness uses my tools through MCP.

## Step 9 · Evaluating the agent
- [ ] 20–30 agent tasks with a golden path (the expected sequence of tool calls)
- [ ] **Trajectory grading:** score each step, not just the final answer, to find *where* it went wrong
- [ ] **LLM-as-judge**, calibrated: check the judge's scores against my own labels on a sample
- [ ] **Prompt-injection cases:** e.g. a document that tries to give the agent orders

**Learn:** how to evaluate agents, which is much harder than evaluating single answers.
**Done when:** I have an accuracy number for my agent and know why it fails when it fails.

## Step 10 · FDE project: case-interview trainer for the Consulting Club
- [ ] Discovery: 3–5 user interviews, current workflow, measurable success criterion
- [ ] One-page design doc + 20 eval cases written **before** coding
- [ ] Prototype on my harness (add RAG with abstention if it needs documents: it should say "I don't have enough information" when retrieval is weak)
- [ ] Deploy to 5–10 real users, trace every session, iterate
- [ ] Case study: problem, architecture, before/after metrics, what failed

**Learn:** everything together, with real people.

---

## Ongoing, at my own pace
- [ ] One system design per week in `notes/system-design/` (~45 min, use the template)
- [ ] One note + one commit per session, even if it's 5 lines
- [ ] Reading notes in `notes/papers/`
- [ ] A public post after steps 5, 7 and 10
- [ ] **Now:** ask the Consulting Club for 5–10 volunteers for step 10

## Out of scope until May
Voice agents, DPO/fine-tuning flywheels, GraphRAG, Temporal/LangGraph, spending real money. Worth knowing as concepts; not worth building yet.
