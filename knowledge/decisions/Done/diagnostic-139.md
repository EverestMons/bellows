# Bellows — Double-claim forensics: one deposit → plan IDs 137 & 138
**Date:** 2026-07-07 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) | **pause_for_verdict:** always

## CEO Context

A single deposited plan file (`executable-plan-lint-qa-steps-cross-check-2026-07-07.md`, the qa_steps↔step-label WARN-only lint) was dispatched under **two plan IDs, 137 and 138**. The two plan files are **byte-identical**; both ran DEV to completion in separate worktrees (`.bellows-worktrees/137` @ `0fa4234`+`d153a8c`, `.bellows-worktrees/138` @ `a8b0a2e`+`51a666e`) and both parked at `verdict-pending`. This is a wasted duplicate execution and a merge hazard (two worktrees, same files → the second merge-back would conflict). CEO recovery already applied: 137 stopped, 138 continued, a stray uncommitted third variant stashed in main.

**Ruled OUT by hand:** a two-daemon race — `bellows.py` (pid 11018) is `dashboard.py`'s (pid 21161) lock-protected child via `_spawn_child()`, so only one logical daemon runs. The claim mechanism (rename `executable-*.md` → `in-progress-executable-<id>.md`) is supposed to make a claim exclusive; something let the same content be claimed twice. This diagnostic characterizes HOW, so a follow-up executable can close the gap. **READ-ONLY: no code changes.**

Context worth checking: plan **136** (`plan_lint qa_steps cross-check (plan-133 trap class)`, distinct earlier authoring, deposit `plan-lint-qa-steps-guard-2026-07-07.md`) died on a **session-limit 429** at 13:42 (`processed-verdict-136-step-1.md`) with a stop verdict whose text says *"identical plan will be re-deposited."* Determine whether that re-deposit, plus a separately-authored deposit this session, is how two files/IDs arose — vs a genuine single-file double-claim.

## How to Run This Plan

Single-step plan — the agent executes Step 1 and the daemon pauses for verdict at completion.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-plan-double-claim-137-138-2026-07-07.md. Execute Step 1. Do NOT move the plan to Done until Step 1 is fully complete.
```

---
---

## STEP 1 — SA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. All commands run from `/Users/marklehn/Developer/GitHub/bellows`. **READ-ONLY: no code changes, no commits except the deposit.**
>
> **Scope:**
> - `knowledge/research/plan-double-claim-137-138-2026-07-07.md`
>
> **Task 1 — reconstruct the timeline.** From `logs/` (per-run step JSON), `bellows.db` (`runs` table), `verdicts/ledger.jsonl`, and `git reflog` + the `bellows-wt/137` / `bellows-wt/138` branch histories, build a single ordered timeline of every event touching this feature on 2026-07-07: the 136 death (13:42), the deposit(s) of the WARN-only plan, each claim (executable→in-progress rename with assigned ID), each worktree creation, each DEV commit, each verdict-pending transition. Record wall-clock timestamps. Establish whether **one** source file was claimed twice, or **two** source files each got claimed once (e.g. 136's re-deposit + a fresh authoring). Cite the on-disk/db evidence for the conclusion — do not infer from filenames alone.
>
> **Task 2 — locate the claim-exclusivity gap.** Read the claim path in `bellows.py` (the `executable-*.md` scan → `shutil.move` to `in-progress-executable-<id>.md`, and how `<id>` is assigned — sequential counter? DB max+1? filename-derived?). Answer: (a) is the scan→rename atomic, or is there a window where two rescan iterations (or a rescan overlapping a re-deposit) can both act on the same/equivalent content? (b) how is the plan ID allocated, and can two claims of equivalent content get different IDs? (c) does anything dedup by CONTENT (hash) or only by filename — i.e. would two different filenames with identical body both be accepted? (d) if 136's stop verdict triggered an automated re-deposit, where is that code and does it guard against a manual re-deposit of the same feature? Quote the relevant code with file:line.
>
> **Task 3 — disposition + fix sketch.** State the root cause in one paragraph, backed by Task 1/2 evidence. Classify: `single-file double-claim` (claim not exclusive — fix the rename/lock window) vs `dual-deposit` (two files for one feature — fix = content-hash dedup at claim time and/or author-side "grep decisions/ before depositing" discipline) vs `re-deposit collision` (136's automated re-deposit raced a manual one). Give a ready-to-author fix list for the follow-up executable (exact function + change shape), and explicitly note whether the session-limit-429 pause-and-hold work (carried from plans 132/136) would have prevented this by never leaving 136 in the re-deposit-needed state. Summary table: symptom | evidence | root cause | fix.
>
> **Deposit:** `knowledge/research/plan-double-claim-137-138-2026-07-07.md` — timeline, claim-path analysis with quoted code, disposition, fix list, summary table, and an Output Receipt with status. Use the canonical Python file-write pattern — no heredoc. Commit the deposit: `git add knowledge/research/plan-double-claim-137-138-2026-07-07.md && git commit -m "docs(bellows): double-claim forensics 137/138 — claim-exclusivity analysis"`. In `### Ledger Updates` include `#### Prompt Feedback` only (no Project Status — diagnostic).
>
> **Deposits:**
> - `bellows/knowledge/research/plan-double-claim-137-138-2026-07-07.md`
