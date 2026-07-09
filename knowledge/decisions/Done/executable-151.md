# Bellows — Backfill stale verdicts.outcome for qa-149 (status.py phantom)
**Date:** 2026-07-09 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** none | **Execution:** Step 1 (DEV) | **pause_for_verdict:** always

## CEO Context

Residual data repair. The typed-slug `_lc_plan_id` bug (fixed in code by plan 150, `874e38c`) left exactly one stale row in `lifecycle.db`: `verdicts(plan_id=149, step_number=1, outcome=NULL)`. `status.py query_awaiting_verdict` selects `FROM verdicts WHERE v.outcome IS NULL`, so this single row makes closed plan **qa-149 still display as "AWAITING VERDICT"** (phantom). Plan 150 repaired `plans.lifecycle_state` (clearing the separate "abandoned" mis-marking) but did NOT backfill this `verdicts` row — its QA checked `lifecycle_state`, not the `verdicts` table that status.py actually reads.

The going-forward fix is already live (plan 150's own verdicts rows are both `continue` — proof). This plan is a one-row data cleanup ONLY.

**Scope reality:** this touches `lifecycle.db` (runtime state), not code — no source file changes, no test changes. The only deposited file is the dev-log.

**Deposit-once discipline:** this file was deposited exactly once. If a second copy appears, that is a claim-dedup bug — do not double-claim.

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-verdicts-outcome-backfill-qa149-2026-07-09.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible chat message confirming you are starting this plan and your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. All commands run from `/Users/marklehn/Developer/GitHub/bellows`. **This is a bounded, idempotent one-row data repair on `lifecycle.db` — NO source-code changes, NO test changes.**
>
> **Scope:**
> - `knowledge/development/verdicts-outcome-backfill-qa149-2026-07-09.md`
>
> **Task — backfill the stale verdicts row (idempotent).**
> 1. **Read first.** Query `lifecycle.db` and log the current row: `SELECT plan_id, step_number, outcome, verdict_file_ref FROM verdicts WHERE plan_id=149 AND step_number=1`. Confirm `outcome IS NULL` before writing. Also log the full list of `verdicts WHERE outcome IS NULL` so we know the exact blast radius (expected: exactly this one row).
> 2. **Update, guarded.** Run exactly: `UPDATE verdicts SET outcome='continue' WHERE plan_id=149 AND step_number=1 AND outcome IS NULL`. The `AND outcome IS NULL` predicate makes it idempotent (a second run affects 0 rows). Log `rowcount` (expected 1). Set `outcome='continue'` to match the continue-to-done verdict that closed qa-149 (mirrors plan 150's own verdicts rows).
> 3. **Do NOT** touch any other row, table, or the `plans` table (plan 149 is already correctly `closed`). Do NOT create new rows — this is an UPDATE of the existing row only.
>
> **Self-verify (this is the whole point — verify the phantom is gone, not just that the UPDATE ran).**
> - Re-query: `SELECT outcome FROM verdicts WHERE plan_id=149 AND step_number=1` → must be `continue`.
> - Re-query: `SELECT COUNT(*) FROM verdicts WHERE outcome IS NULL` → log the count (should no longer include the 149 row).
> - Run `python3 status.py` and paste the AWAITING VERDICT section into the dev-log — it must **no longer list qa #149** (the phantom is cleared). If it still shows, STOP and report — the row driving it is elsewhere.
> - Confirm `plans` row for 149 is untouched and still `closed`.
>
> **No git commit expected** (lifecycle.db is runtime state, not tracked source). If `git status` unexpectedly shows a tracked change, note it in the dev-log and do not commit without flagging.
>
> **Deposit:** a dev-log with the before-row, the UPDATE rowcount, the three self-verify query results, the pasted status.py AWAITING VERDICT section proving qa-149 is gone, and an Output Receipt with status. Canonical Python file-write pattern — no heredoc. In `### Ledger Updates` include `#### Prompt Feedback` (daemon-owned; do NOT edit any feedback file directly).
>
> **Deposits:**
> - `bellows/knowledge/development/verdicts-outcome-backfill-qa149-2026-07-09.md`
>
> **STOP. Wait for CEO verdict.**
