# Bellows — Cycle-Nudge Trigger (plans-closed-since-last-ingestion → Pushover)
**Date:** 2026-07-06 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

## CEO Context

Implements Gap Assessment row 2 of diagnostic-127 (`lessons-forge/knowledge/research/learning-loop-routing-audit-2026-07-06.md`). Finding: the learning loop went dormant 28+ days with zero mechanical signal — no code evaluates any counter or fires a nudge. Design decision from the diagnostic: the trigger counts PLANS CLOSED SINCE LAST INGESTION, not unclassified entries — the diagnostic proved unclassified reads 0 during dormancy (the backlog was drained; ingestion is what stopped), so an unclassified-count trigger would stay silent through exactly the failure it exists to catch. Both sides of the counter are schema-confirmed: `lifecycle.db` plans table (`lifecycle_state`, `closed_at`) and `lessons-forge.db` `MAX(ingested_at)`. Hook point is option D1 (daemon rescan loop + notifier.py) — D2's session-start check misses the between-sessions dormancy this closes. CRITICAL: new daemon code is INERT until a daemon restart — this plan ships code and tests only; no live validation is possible or attempted here. A post-restart live canary is a mandatory follow-up (silent/best-effort write path — LESSONS 2026-06-14). Companion plan (independent, parallel): `lessons-forge/knowledge/decisions/executable-route-field-lesson-proposals-2026-07-06.md`.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation before proceeding to Step 2. The agent must never skip steps, auto-chain, or move the plan to Done without completing all steps including QA.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-cycle-nudge-trigger-2026-07-06.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
>
> **Scope:**
> - `bellows.py`
> - `notifier.py`
> - `config.json`
> - `tests/` (only test files for the modules you touch)
> - `knowledge/development/cycle-nudge-trigger-2026-07-06.md`
>
> **Mechanical-only invariant reminder:** the nudge is a counter comparison and a notification — zero domain judgment. It never blocks dispatch, never writes to any DB, and every failure path is log-and-continue. A broken nudge must never take the daemon down.
>
> **Change 1 — config.** Add to `config.json` a `cycle_nudge` block: `{"enabled": true, "plans_closed_threshold": 10, "interval_hours": 24}`, and add `"cycle_nudge": true` to `notifications.events`. Config reads use safe defaults when the block is absent (absent = disabled) — an old config must never crash the daemon.
>
> **Change 2 — evaluator.** New function (e.g. `_evaluate_cycle_nudge()`) in `bellows.py`: (a) read `MAX(ingested_at)` from `/Users/marklehn/Developer/GitHub/lessons-forge/lessons-forge.db` via read-only URI (`file:...?mode=ro`); (b) count `SELECT COUNT(*) FROM plans WHERE lifecycle_state = 'closed' AND closed_at > ?` against lifecycle.db with that timestamp (if `MAX(ingested_at)` is NULL, count all closed plans); (c) if count >= `plans_closed_threshold`, call the notifier. EVERY failure (missing DB file, missing table, malformed timestamp) is caught, logged, and returns without effect — never raises into the rescan loop.
>
> **Change 3 — cadence + suppression.** Hook the evaluator into the daemon rescan loop (`bellows.py`, the `_rescan(handler)` call site ~line 2070) gated by an in-memory last-evaluation timestamp: evaluate at most once per `interval_hours`. After a nudge fires, suppress further nudges until `MAX(ingested_at)` advances past the value at fire time (i.e., an ingestion happened) — in-memory state; a daemon restart resetting it (worst case one repeat nudge) is accepted and documented in the dev log.
>
> **Change 4 — notifier.** `notify_cycle_nudge(count, since_ts)` in `notifier.py` following the existing named-function pattern (`notify_plan_complete` etc.), gated by the `notifications.events["cycle_nudge"]` flag, message naming the count and the last-ingestion date. Non-urgent priority — this must coalesce like routine notifications, not page like a failure.
>
> **Change 5 — tests.** New tests using THROWAWAY temp DBs only (never the canonical lifecycle.db or lessons-forge.db): (a) count-since query correctness incl. the NULL-ingestion branch; (b) threshold boundary (count == threshold fires, count == threshold-1 does not); (c) missing lessons-forge.db → logged no-op, no exception; (d) interval gating (second evaluation inside the window is a no-op); (e) post-fire suppression until ingested_at advances; (f) absent `cycle_nudge` config block → disabled, no exception. Existing tests must pass UNCHANGED — if any fails, halt and report; do NOT rewrite assertions.
>
> **Self-verify.** Run the FULL suite with `timeout 600 python3 -m pytest tests/ -v` to an explicit pass/fail and READ THE TAIL — never infer green from a subset or collect count. Do NOT restart the daemon — the new code is intentionally inert this session.
>
> **Commit** with a descriptive message (e.g. `feat(bellows): cycle-nudge trigger — plans-closed-since-ingestion threshold to Pushover (diagnostic-127 gap 2)`).
>
> **Deposit:** `bellows/knowledge/development/cycle-nudge-trigger-2026-07-06.md` — dev log with: exact diff hunks (or verbatim old/new blocks), the rescan hook location, the suppression-state design note, new test names + one-line rationale each, the full-suite tail verbatim, commit hash, and an Output Receipt with status. Use the canonical Python file-write pattern — no heredoc. In `### Ledger Updates` include `#### Prompt Feedback` (daemon-owned; do NOT edit any feedback file directly).
>
> **Deposits:**
> - `bellows/knowledge/development/cycle-nudge-trigger-2026-07-06.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO verdict before continuing.**

---
---

## STEP 2 — QA

---

> **Before starting, read the Step 1 dev-log deposit at `bellows/knowledge/development/cycle-nudge-trigger-2026-07-06.md` and check its Output Receipt status. If status is not Complete, halt and report the blocker before proceeding.**
>
> You are Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first.
>
> **Rule 20 self-check is gate-enforced on this step.** Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line; the verification table below does NOT by itself satisfy the gate — end with a self-grep confirming the banner is present in your deposited report.
>
> **Scope:**
> - `knowledge/qa/cycle-nudge-trigger-qa-2026-07-06.md`
>
> Verify the cycle-nudge trigger AT CODE LEVEL ONLY — do NOT restart the daemon, do NOT attempt live validation; the code is inert until restart by design. Produce a verification table, one row per claim: (1) `config.json` has the `cycle_nudge` block and the `notifications.events` flag — quote both; (2) absent-config path proven by test (f) passing in isolation; (3) the evaluator's two queries match the plan (quote the SQL; confirm read-only URI on the lessons-forge.db read and the NULL-ingestion branch); (4) every failure path in the evaluator is log-and-continue — cite the exception handling and run test (c) in isolation; (5) rescan hook present at the loop call site and interval-gated — quote the hook; (6) suppression logic proven by test (e) in isolation; (7) `notify_cycle_nudge` follows the existing named-function pattern and is event-gated — quote it; (8) pre-existing tests pass with assertions untouched — verify via `git diff HEAD~1 -- tests/` that no existing assertion lines were modified (additions only); (9) full suite green: re-run `timeout 600 python3 -m pytest tests/ -v` to an explicit pass/fail and show the tail. If any row fails, report it and halt — do not pass a broken deliverable.
>
> **Deposit:** `bellows/knowledge/qa/cycle-nudge-trigger-qa-2026-07-06.md` — verification table, full-suite tail, the Rule 20 self-check block, an explicit line stating the daemon was NOT restarted and a post-restart live canary is the mandatory follow-up, and an Output Receipt with status. Commit the QA report. In `### Ledger Updates` include: `#### Project Status` — one milestone paragraph: cycle-nudge trigger shipped 2026-07-06 (code-level verified, inert until daemon restart, live canary pending); `#### Prompt Feedback` — standard.
>
> **Deposits:**
> - `bellows/knowledge/qa/cycle-nudge-trigger-qa-2026-07-06.md`
>
> On full completion, move the plan file to `bellows/knowledge/decisions/Done/` as the absolute last operation.
