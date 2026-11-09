---
description: Save the current state to PROGRESS.md and commit, before switching tools
---
I'm about to switch to another coding agent (or I'm running out of usage). Prepare a clean handoff:

1. Update `PROGRESS.md` so another agent with zero context can continue:
   - **Last updated:** today's date and the tool/model you are
   - **Current step:** the roadmap step we are on
   - **Done:** what was completed in this session (files and what they do)
   - **Next task:** the single next concrete task, specific enough to start right away
   - **In progress / open threads:** anything half-done, failing tests, open questions
   - **Decisions and gotchas:** choices made and why, things that didn't work
   Keep it short. Replace stale content instead of appending forever.
2. If the roadmap changed (a box got done), tick it in `ROADMAP.md`.
3. Run `git status`, then commit all work with a clear message (never commit ignored files).
4. Reply with a 3-line summary of where we are and what's next.

Extra notes from me: $ARGUMENTS
