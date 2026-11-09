# Progress

Current state of the work, for handing off between Claude Code and OpenCode. Update it with `/handoff`.

**Last updated:** 2026-11-09 by Claude (setup)

## Current step
Roadmap step 1 · Break the model

## Done
- `week-01/llm_metrics.py`: tokens, latency and structured outputs measured (results in `week-01/results/`, notes in `notes/2026-10-13-first-measurements.md`)

## Next task
Write a hard extraction case: a value that must be computed, numbers written in words, and a second company as a distractor. Then compare `qwen3.5:4b` vs `qwen3.5:9b` on it.

## In progress / open threads
- None

## Decisions and gotchas
- Shared agent instructions live in `AGENTS.md`; `CLAUDE.md` just imports it.
