# Design NN · <system name>

**Date:**
**Prompt (as in an interview):** e.g. "Design an assistant that answers HR questions for 5,000 employees using internal documents".

## 1. Requirements
- Users and volume (requests/day, peaks):
- What a "good" answer is and how it's measured:
- Acceptable latency:
- Constraints (privacy, on-premise data, budget):

## 2. Architecture
Diagram (boxes and arrows) + one sentence per component.

## 3. Key decisions and trade-offs
| Decision | Options | Choice | Why |
| --- | --- | --- | --- |
| Model | large / small / routing | | |
| Knowledge | long context / RAG / fine-tuning | | |
| Orchestration | fixed workflow / agent / multi-agent | | |
| Tools | which ones, with what permissions | | |

## 4. Cost and latency (rough numbers)
- Tokens per request (input / output):
- Cost per request and per month:
- Caching, batching, small model for easy steps:

## 5. Reliability
- Evals before launch:
- Guardrails and escalation to a human:
- Observability (traces, metrics, alerts):

## 6. What I'd change at 10x users
