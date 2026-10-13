# harness

Roadmap steps 4–7. My own agent from scratch, no frameworks, against a local Ollama model with tool calling (`qwen3.5:4b` / `qwen3.5:9b`).

- Step 4: single tool call
- Step 5 (v0): agent loop + 3 tools + stop conditions (max steps, max tokens, timeout)
- Step 6 (v1): least-privilege tools in a sandbox, human approval for risky actions, per-section token budget, context compaction, checkpoint/resume
- Step 7: 4b → 9b model router, measured with evals
