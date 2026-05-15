# Bellows — Post-Relocation Restart Canary
**Date:** 2026-05-15 | **Tier:** Small | **Test Scope:** smoke | **Execution:** Step 1 (DOC) | **pause_for_verdict:** after_step_1

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-post-relocation-restart-canary-2026-05-15.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

## CEO Context

Post-2026-05-14 governance-root relocation (Desktop/GitHub → Developer/GitHub), yesterday's session-end fixes patched two hardcoded paths in Bellows code (`bellows/planner.py:13` GOVERNANCE_ROOT, `bellows/verdict.py:60-75` path-strip blocks). Bellows daemon was restarted today (2026-05-15). This canary confirms:

1. The daemon's planner.py code can resolve PLANNER_TEMPLATE.md at the new path (no FileNotFoundError on dispatch)
2. The full plan lifecycle works end-to-end (claim → dispatch → execute → deposit → gate → verdict cycle)
3. Worktree creation in the new submodule arrangement works (post-2026-05-15 submodule conversion gave Bellows its own `.git`; standard worktree path now applies)

This canary uses no parser-bait — it is a relocation smoke test, not a parser-fix verification. A successful pass closes NEXT_SESSION's "Bellows safe to restart" item and provides empirical evidence on Q2/Fix-b (worktree creation in submodule arrangement).

---
---

## STEP 1 — Bellows Documentation Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-post-relocation-restart-canary-2026-05-15.md", "bellows/knowledge/decisions/in-progress-executable-post-relocation-restart-canary-2026-05-15.md")`. You are the Bellows Documentation Analyst. Skip the specialist file and domain glossary reads — this is a trivial markdown-deposit canary. **Purpose.** Verify Bellows's post-relocation daemon code path is healthy: planner.py loads PLANNER_TEMPLATE.md, verdict.py path-strip works, worktree creation succeeds in the new submodule arrangement. **Implementation.** Write a single canary-confirmation file at the path declared in **Deposits** below. The file content is a 4-line markdown document: title, one-sentence confirmation that the canary dispatched and executed, the running daemon's working directory (capture with `import os; cwd = os.getcwd()`), and an ISO-format timestamp. Use the canonical pattern: define `content` as a Python triple-quoted string, then `with open("/Users/marklehn/Developer/GitHub/bellows/knowledge/documentation/post-relocation-restart-canary-2026-05-15.md", "w") as f: f.write(content)`. Do not commit this file. Do not modify any source code, test, or governance file. **Output Receipt.** Standard Output Receipt at the bottom of the deposited file. Status: Complete. Files Deposited: the canary-confirmation file. Files Created or Modified (Code): None. Decisions Made: None. Flags for CEO: report the captured `cwd` value verbatim — this tells the Planner whether the canary executed in-place (cwd ends in `/bellows`) or in a worktree (cwd contains `/.bellows-worktrees/`). Flags for Next Step: None — this is a single-step plan. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/documentation/post-relocation-restart-canary-2026-05-15.md`
>
> **STOP. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
