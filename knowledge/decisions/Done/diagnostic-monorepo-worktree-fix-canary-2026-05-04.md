# Bellows — Monorepo Worktree Fix Live Canary
**Date:** 2026-05-04 | **Tier:** Small | **Test Scope:** N/A | **Execution:** Step 1 (DEV)

## How to Run This Plan

This plan is dispatched by Bellows automatically once deposited. No manual bootstrap needed. Bellows watches `bellows/knowledge/decisions/` and will claim this file on the next scan cycle (within ~30 seconds).

**The canary's purpose:** confirm the monorepo worktree fix shipped today (commit `06aa938`) actually executes correctly when Bellows dispatches a bellows-self plan. Three observable signals to confirm:
1. Bellows terminal logs the warning `Bellows: ⚠ bellows has no project-local .git — running in-place without worktree isolation`
2. The plan reaches `verdict-pending-*` state cleanly (no `worktree_teardown` gate failure)
3. The verdict request appears in `bellows/verdicts/pending/` with `Pause Reason Code: auto_close_disabled`

The agent's deliverable is trivial — the canary's value is in the dispatch lifecycle, not the agent's findings.

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> You are the Bellows Developer. Skip specialist file and glossary reads — this is a read-only smoke verification, no domain interpretation required. Use `read_text_file` to read `bellows/bellows.py` lines 525-535 and lines 560-565. Confirm two things by visual inspection: (1) the line at or near 528 contains `os.path.exists(os.path.join(project_path, ".git"))` (the new monorepo detection); (2) the line at or near 562 contains the sentinel check `if wt_path == project_path:` followed by an early `return` (the no-op teardown). Deposit a findings file at `bellows/knowledge/research/monorepo-worktree-canary-findings-2026-05-04.md` with: (a) one-line confirmation of detection presence with the exact line number where you found it, (b) one-line confirmation of sentinel presence with the exact line number where you found it, (c) one-line confirmation that the agent's `cwd` during this step's execution is `bellows/` (not a worktree subdirectory) — verify by running `pwd` via bash and including the literal output. Do NOT modify any code. Do NOT run tests. Do NOT commit anything. After the findings file, run the standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/monorepo-worktree-canary-findings-2026-05-04.md`
