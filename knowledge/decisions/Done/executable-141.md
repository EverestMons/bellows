# Bellows — Robustness batch: claim-dedup guard + worktree-health probe/cleanup
**Date:** 2026-07-07 | **Tier:** Medium | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV cleanup+probe) → Step 2 (DEV dedup fix) → Step 3 (QA) | **qa_steps:** 3 | **pause_for_verdict:** always

## CEO Context

Consolidates the robustness follow-ups from the 2026-07-07 plan_lint dispatch tangle (diagnostic 139: `knowledge/research/plan-double-claim-137-138-2026-07-07.md`). Two distinct problems, plus cleanup:

1. **Claim-dedup gap (root of the 137/138 double-claim).** A dual-deposit spawned two plans because the claim path has no dedup against active plans: `plans.deposit_placeholder_name` (lifecycle.py:48) has no uniqueness guard, and `_invalidate_seen_on_redeposit` (bellows.py:1633) clears the `_seen` guard on any second copy without checking for an in-progress plan. 139's 3-item fix (Step 2).
2. **Worktree-bypass anomaly.** Plan 140 ran in the **main checkout with no worktree** (no `bellows-wt/140` was created; commits landed directly on main), whereas 137/138/139 got worktrees. This appeared right after the 137/138 worktree-teardown failures. Needs a diagnostic probe (Step 1) — cause unknown, so NO worktree code change is pre-specified; if Step 1 finds a code bug, halt and report for a dedicated fix.
3. **Cruft** from the tangle: stale `halted-executable-136/137/138.md`, orphan worktrees `.bellows-worktrees/137` + `138`, and `git stash@{0}` (the superseded buggy plan_lint variant). Cleared in Step 1.

**NOT in this plan (carried, separate):** session-limit **pause-and-hold** (3× 429 today: 132, 136, +near-misses) — a design decision (parse resets-at + park vs hold-for-CEO), authored separately. It is the paired *trigger* fix; this plan fixes the *mechanism*.

**Deposit-once discipline:** this file was deposited exactly once. If a second copy appears, that is the bug from problem 1 — do not double-claim.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. Execute Step 1 ONLY, then STOP for CEO verdict. Proceed step-by-step on verdict; never auto-chain.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-daemon-robustness-batch-dedup-worktree-2026-07-07.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2.
```

---
---

## STEP 1 — DEV (worktree-health probe + cruft cleanup)

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. All commands run from `/Users/marklehn/Developer/GitHub/bellows`. **This step is investigation + git hygiene only — NO product-code changes.**
>
> **Scope:**
> - `knowledge/development/daemon-robustness-batch-step1-2026-07-07.md`
>
> **Task A — worktree-health probe (READ-ONLY analysis).** Determine why plan 140 ran in the main checkout with no worktree. Read `_create_worktree` (and its call site in `run_plan`, bellows.py ~line 371-460) and any try/except or fallback around worktree creation. Check `git worktree list`, `git branch -a | grep wt/`, and daemon logs (`logs/`) around 140's claim (~16:xx) for a worktree-creation error or fallback-to-main path. Answer in the dev-log: did worktree creation raise and get swallowed into a main-checkout fallback, or is there no worktree path for this claim shape? Classify as `benign` (expected for some claim types) or `bug` (worktree silently skipped — isolation lost). **If `bug` and the fix is non-trivial code: STOP and report — do not fix it here; it warrants a dedicated plan.**
>
> **Task B — cruft cleanup (bounded git hygiene).** Retire the tangle's dead state, recording each action in the dev-log: (1) `git worktree remove --force .bellows-worktrees/137` and `.bellows-worktrees/138`, then delete branches `bellows-wt/137` and `bellows-wt/138` (`git branch -D`) — these are for stopped/halted duplicate plans. Confirm `bellows-wt/139` handling per its Done state (leave if the daemon still references it; note either way). (2) Move `knowledge/decisions/halted-executable-136.md`, `halted-executable-137.md`, `halted-executable-138.md` into `knowledge/decisions/Done/` (keep the `halted-` prefix in the filename so history is legible) — they are terminal duplicates/environmental halts. (3) `git stash drop stash@{0}` — confirm first via `git stash show stash@{0}` that it is the buggy plan_lint variant (message contains "stray plan_lint qa_steps impl"); if the message differs, DO NOT drop — report instead.
>
> **Self-verify.** After cleanup: `git worktree list` shows no 137/138 entries; `ls knowledge/decisions/ | grep halted` is empty; `git stash list` no longer shows the stray. Run the FULL suite `python3 -m pytest tests/ -v` (use `python3 -m pytest`, NOT the `timeout` binary — unavailable on macOS) to an explicit pass/fail and READ THE TAIL — confirm cleanup broke nothing.
>
> **Commit** the cleanup (the halted-file moves) with a descriptive message, e.g. `chore(bellows): retire 137/138 tangle cruft — worktrees, halted plans, stray stash`.
>
> **Deposit:** `bellows/knowledge/development/daemon-robustness-batch-step1-2026-07-07.md` — the worktree-health finding (benign/bug + evidence), the cleanup action log, the full-suite tail, commit hash, and an Output Receipt with status. Canonical Python file-write pattern — no heredoc. In `### Ledger Updates` include `#### Prompt Feedback` (daemon-owned; do NOT edit any feedback file directly).
>
> **Deposits:**
> - `bellows/knowledge/development/daemon-robustness-batch-step1-2026-07-07.md`
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

---
---

## STEP 2 — DEV (claim-dedup guard)

---

> **Before starting, read the Step 1 dev-log at `bellows/knowledge/development/daemon-robustness-batch-step1-2026-07-07.md` and confirm its Output Receipt status is Complete. If Step 1's worktree probe found a `bug` requiring separate work, note it but proceed with the dedup fix (independent).**
>
> You are the Bellows Developer. All commands run from `/Users/marklehn/Developer/GitHub/bellows`. Read `knowledge/research/plan-double-claim-137-138-2026-07-07.md` §3 (the fix list) before coding.
>
> **Scope:**
> - `lifecycle.py`
> - `bellows.py`
> - `tests/` (only test files for the modules touched — e.g. `tests/test_lifecycle.py`)
> - `knowledge/development/daemon-robustness-batch-step2-2026-07-07.md`
>
> **Active-state set:** the non-terminal lifecycle states are `('claimed', 'in_progress', 'awaiting_verdict')` (per the CHECK constraint at lifecycle.py:46). "Active plan" = a `plans` row in one of those states.
>
> **Fix 1 — DB partial unique index (lifecycle.py, plans table init ~line 38-48).** Add, idempotently (`CREATE UNIQUE INDEX IF NOT EXISTS`), a partial unique index: `idx_plans_active_placeholder ON plans (deposit_placeholder_name) WHERE lifecycle_state IN ('claimed','in_progress','awaiting_verdict')`. This must run in the same guarded init path that creates the table (follow the existing `CREATE TABLE IF NOT EXISTS` pattern so pre-existing DBs get it). Defense-in-depth: `mint_and_claim` will raise `sqlite3.IntegrityError` on a duplicate active placeholder.
>
> **Fix 2 — application check in `run_plan` before `mint_and_claim` (bellows.py ~line 457).** Before minting, derive the deposit placeholder basename and query lifecycle.db: `SELECT id FROM plans WHERE deposit_placeholder_name = ? AND lifecycle_state IN ('claimed','in_progress','awaiting_verdict')`. If a row exists, `_log("WARN", ...)` naming the existing plan id ("duplicate deposit — active plan {id} already claimed from same placeholder; refusing second claim"), route this deposit to `halted-` (do NOT mint a new id, do NOT create a worktree), and return cleanly. Add a helper in lifecycle.py if a clean query entry point is needed (e.g. `active_plan_for_placeholder(name, db_path=None)`).
>
> **Fix 3 — guard `_invalidate_seen_on_redeposit` (bellows.py:1633).** Before `self.orchestrator._seen.discard(slug)`, query for an active plan whose placeholder/slug matches; if one exists, `_log("INFO", "re-deposit ignored — active plan {id} in progress for slug {slug}")` and return WITHOUT discarding from `_seen`. This closes the watchdog window that let the second copy through.
>
> **Tests (tests/test_lifecycle.py or a new test file named in scope).** Use THROWAWAY temp DBs only (never canonical lifecycle.db). Cover: (a) partial unique index blocks a second active row with the same placeholder (IntegrityError) but ALLOWS a new claim once the first is terminal (`closed`/`halted`); (b) `active_plan_for_placeholder` returns the id for an active plan and None for a terminal/absent one; (c) the run_plan-level guard refuses a duplicate (simulate an active plan, assert no second id minted + routed to halted) — mock/seam as needed; (d) `_invalidate_seen_on_redeposit` does NOT discard from `_seen` when an active plan exists, and DOES when none exists. Existing tests must pass UNCHANGED — if any fails, halt and report.
>
> **Self-verify.** Run the FULL suite `python3 -m pytest tests/ -v` (not `timeout`) to explicit pass/fail; READ THE TAIL.
>
> **Commit** e.g. `feat(bellows): claim-dedup guard — refuse duplicate active-placeholder claims (diagnostic 139)`.
>
> **Deposit:** `bellows/knowledge/development/daemon-robustness-batch-step2-2026-07-07.md` — diff hunks for all 3 fixes, the active-state rationale, new test names + one-line rationale each, full-suite tail, commit hash, Output Receipt with status. Canonical Python file-write pattern. In `### Ledger Updates` include `#### Prompt Feedback`.
>
> **Deposits:**
> - `bellows/knowledge/development/daemon-robustness-batch-step2-2026-07-07.md`
>
> **STOP. Do NOT proceed to Step 3. Do NOT move the plan to Done. Wait for CEO verdict.**

---
---

## STEP 3 — QA

---

> **Before starting, read both dev-logs (`daemon-robustness-batch-step1-2026-07-07.md` and `-step2-2026-07-07.md`) and confirm both Output Receipts are Complete. If either is not, halt and report.**
>
> You are Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first.
>
> **Rule 20 self-check is gate-enforced on this step.** Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line; end with a self-grep confirming the banner is present.
>
> **Scope:**
> - `knowledge/qa/daemon-robustness-batch-qa-2026-07-07.md`
>
> Verify AT CODE LEVEL. Verification table, one row per claim: (1) partial unique index created idempotently in the guarded init path — quote the DDL, confirm the WHERE clause matches the active-state set; (2) `mint_and_claim` now raises IntegrityError on a duplicate active placeholder — cite test (a); (3) `run_plan` guard queries before minting and routes duplicates to `halted-` without a new id — quote the guard, cite test (c); (4) `_invalidate_seen_on_redeposit` no longer discards `_seen` while an active plan exists — quote the guard, cite test (d); (5) all new tests pass in isolation; (6) pre-existing tests unchanged — `git diff` shows additions only; (7) full suite green — re-run `python3 -m pytest tests/ -v`, show the tail; (8) Step 1 cleanup confirmed — `git worktree list` has no 137/138, `ls knowledge/decisions/ | grep halted` empty, stash cleared; (9) Step 1's worktree-health finding is recorded (benign/bug) — restate it and flag if a follow-up plan is needed. Any row fails → report and halt.
>
> **Deposit:** `bellows/knowledge/qa/daemon-robustness-batch-qa-2026-07-07.md` — verification table, full-suite tail, Rule 20 self-check block, Output Receipt with status. Commit the QA report. In `### Ledger Updates` include: `#### Project Status` — one milestone paragraph (claim-dedup guard shipped 2026-07-07, closes the 137/138 double-claim class; worktree-health probed; tangle cruft retired); `#### Prompt Feedback` — standard.
>
> **Deposits:**
> - `bellows/knowledge/qa/daemon-robustness-batch-qa-2026-07-07.md`
>
> **STOP. Do NOT move the plan to Done until the CEO issues a verdict.**
