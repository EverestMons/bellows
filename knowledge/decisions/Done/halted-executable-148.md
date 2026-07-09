# Bellows — Session-limit pause-and-hold (park + auto-resume)
**Date:** 2026-07-09 | **Tier:** Medium | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV runner detect+parse) → Step 2 (DEV daemon park+auto-resume) → Step 3 (QA) | **qa_steps:** 3 | **pause_for_verdict:** always

## CEO Context

This is the paired **trigger** fix for the session-limit failures that hit 3× on 2026-07-07 (plans 132, 136, + the 137/138 tangle trigger). Plan 141 shipped the *mechanism* fix (claim-dedup guard) and explicitly deferred this one: "session-limit **pause-and-hold** … a design decision (parse resets-at + park vs hold-for-CEO), authored separately." CEO decision **2026-07-09: park + auto-resume** (not hold-for-CEO).

**Diagnostic already done (this authoring session).** The exact on-disk signature of a session-limit hit, from `logs/20260706-222137-step.json` (plan 132) — the terminal NDJSON result event on **stdout**:

```json
{"type":"result","subtype":"success","is_error":true,"api_error_status":429,
 "duration_ms":416,"num_turns":1,
 "result":"You've hit your session limit · resets 11:50pm (America/Chicago)",
 "stop_reason":"stop_sequence","total_cost_usd":0,
 "usage":{"input_tokens":0,"output_tokens":0,...}}
```

**Why the current code mishandles it (two confirmed defects):**
1. The transient-retry guard (`runner.py:179-186`) greps **stderr** for `["401","unauthorized","authentication","429","rate limit","too many requests"]`. But the session-limit `429` lives in the **stdout result event**, and stderr is empty. So the guard never fires for session limits — and it *shouldn't*, because a 5-second retry cannot clear a 5-hour cap. But that means the step falls straight through to the generic path.
2. The step is then returned as `receipt_status="Blocked"`, `escalate=True` (or, depending on exit code, the non-zero-exit branch), which pages the CEO and parks the plan as a **failure**. Recovery is the manual "stop → re-deposit" dance, which is fragile: a naive continue advances past a step that never ran (Precondition Failure is false, so gates don't catch it).

**The key safety fact that makes auto-resume clean:** at session-limit time the result event shows `num_turns:1, total_cost_usd:0, output_tokens:0` — the step **never started** (the first turn was rejected). So re-dispatching the **same** step at reset is byte-for-byte safe: no uncommitted work exists to lose. (This is the opposite of a mid-step death — see the step-failure-recovery lesson. If a future signature ever shows turns/cost > 0 with a session-limit result, that is out of scope here and must escalate, not park; Step 1 locks that guard.)

**Design (locked): park + auto-resume.**
- Detect the session-limit result event (distinct from transient stderr 429s).
- Parse `resets 11:50pm (America/Chicago)` → the next future epoch for that wall-clock time in that IANA zone.
- Park the plan on disk (`parked-` prefix, excluded from the runnable scan) AND persist `(plan_slug, resume_step, resets_at_epoch, plan_path, project)` in `bellows.db` so the park **survives a daemon restart** during the (possibly multi-hour) wait.
- Notify the CEO **once** via Pushover: session limit hit, resets at X, will auto-resume.
- On rescan/startup, when `now >= resets_at_epoch`, un-park (rename back to `in-progress-`) and re-dispatch via `run_plan(..., resume_step=resume_step)`.

**Deposit-once discipline:** this file was deposited exactly once. If a second copy appears, that is a claim-dedup bug — do not double-claim.

**NOT in this plan:** any change to the transient-retry guard's behavior for real short 429s / 401s (it stays as-is); the hold-for-CEO alternative (rejected); Pushover message-format redesign.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. Execute Step 1 ONLY, then STOP for CEO verdict. Proceed step-by-step on verdict; never auto-chain.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-daemon-session-limit-park-autoresume-2026-07-09.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2.
```

---
---

## STEP 1 — DEV (runner.py: detect session-limit + parse resets-at)

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
>
> **Scope:**
> - `runner.py`
> - `tests/test_session_limit_park.py`
>
> **Goal:** teach `run_step` to recognize a session-limit result event and return a distinct, structured outcome — **without changing behavior for any other case, and without yet wiring the park path** (that is Step 2). After this step, if a session limit is hit before Step 2 lands, behavior must be **no worse than today** (still escalates as Blocked) — the new fields ride alongside.
>
> **Task A — detection.** In `run_step`, after the NDJSON stream is parsed into the terminal `result_event` (success path, ~runner.py:214+), add a session-limit check: the event has `is_error == true` AND `api_error_status == 429` AND its `result` text matches session/usage-limit phrasing (case-insensitive substring of `"session limit"` or `"usage limit"`; do NOT match bare `"429"` or `"rate limit"`, which are the transient class). Guard with the safety check from CEO Context: only treat as a *parkable* session limit when the event shows the step did not progress — `num_turns <= 1` AND `total_cost_usd in (0, None)` AND no output tokens. If a `429` session-limit result appears but turns/cost indicate mid-step progress, do NOT park: fall through to the existing Blocked/escalate path (this is the out-of-scope escalate case).
>
> **Task B — parse resets-at.** Add a helper (e.g. `_parse_session_reset(result_text) -> Optional[float]`) that extracts the reset wall-clock time and IANA zone from strings like `"You've hit your session limit · resets 11:50pm (America/Chicago)"`. Support `h[:mm]am/pm` forms (`11:50pm`, `11pm`, `3:30am`) and the `(Area/City)` zone in parens. Compute the **next future** epoch for that wall-clock time in that zone using `zoneinfo.ZoneInfo` (available on the macOS system python3 via `/usr/share/zoneinfo`): if that time today (in-zone) is already past `now`, roll to tomorrow. **Robust fallback (never crash, never lose the step):** if the time or zone cannot be parsed, return `now + 5*3600` (conservative 5-hour cap) and log a WARN naming the unparsed string — the step still parks, just on a default clock.
>
> **Task C — return shape.** When a parkable session limit is detected, the `run_step` return dict must carry: `stop_reason="session_limit"`, `session_limit=True`, `resets_at_epoch=<float>`, `resets_at_raw=<original result string>`. **Preserve the current fallback fields** (`is_error=True`, `receipt_status="Blocked"`, `escalate=True`) so Step-1-only state equals today's behavior plus the new fields; Step 2 will branch on `session_limit` before the escalate path. Write a `_write_log` entry recording the detection + parsed epoch.
>
> **Confirm the retry guard does not double-fire:** the transient stderr retry (`runner.py:179-186`) is on the non-zero-exit path and greps stderr; the session-limit result is on the success/parse path and greps the stdout result event. They are mutually exclusive by construction — add a one-line comment at each site noting the split so a future editor does not merge them. A session limit must NOT consume the once-only transient retry.
>
> **Tests (`tests/test_session_limit_park.py`, new).** Unit-test the detection + parser in isolation (feed a synthetic `result_event` dict and raw strings — do NOT spawn `claude -p`): (1) the exact plan-132 string parses to a future epoch matching 11:50pm America/Chicago; (2) `11pm` and `3:30am` forms parse; (3) an unparseable string falls back to ~now+5h and logs WARN; (4) a bare `"429 rate limit"` / transient string is NOT classified as a session limit; (5) a `429` session-limit result WITH `num_turns > 1` / nonzero cost is NOT parked (falls through). Assert the returned dict fields.
>
> **Self-verify.** Run the FULL suite `python3 -m pytest tests/ -v` (use `python3 -m pytest`, NOT the `timeout` binary — unavailable on macOS). Read the tail to an explicit pass/fail; confirm 0 regressions. **Commit** with a descriptive message, e.g. `feat(runner): detect session-limit result event + parse resets-at (park groundwork)`.
>
> **Deposit:** a dev-log with the detection/parse design, the parser's supported formats + fallback, the full-suite tail, commit hash, and an Output Receipt with status. Canonical Python file-write pattern — no heredoc. In `### Ledger Updates` include `#### Prompt Feedback` (daemon-owned; do NOT edit any feedback file directly).
>
> **Deposits:**
> - `bellows/knowledge/development/session-limit-detection-runner-2026-07-09.md`
> - `bellows/runner.py`
> - `bellows/tests/test_session_limit_park.py`
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

---
---

## STEP 2 — DEV (bellows.py: park + persist + auto-resume + notify)

---

> **FIRST — post a short visible chat message confirming you are starting Step 2 and your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Re-read `bellows/agents/BELLOWS_DEVELOPER.md` if useful. All commands run from `/Users/marklehn/Developer/GitHub/bellows`. This step consumes the `session_limit` outcome Step 1 added and wires the full park + auto-resume path.
>
> **Scope:**
> - `bellows.py`
> - `tests/test_session_limit_park.py`
>
> **Task A — park on session-limit.** In `run_plan` (bellows.py), at every site where a `run_step` result is consumed (the pre-loop step ~576, the while-loop step ~682, and the bootstrap step ~563) — factor a single helper `_maybe_park_session_limit(parsed, plan_path, inprogress_path, current_step, ...) -> bool` and call it **before** the gate/escalate handling. When `parsed.get("session_limit")` is true:
> 1. Rename the in-progress plan file to `parked-<base_filename>` (mirror the existing `verdict-pending-` rename pattern, ~line 544/653; single `shutil.move`, restart-safe ordering).
> 2. Persist the park in `bellows.db`: a new `parked_steps` table `(plan_slug TEXT PRIMARY KEY, plan_path TEXT, project TEXT, resume_step INTEGER, resets_at_epoch REAL, parked_at TEXT)`. Use `INSERT OR REPLACE` keyed on `plan_slug` so a re-park overwrites cleanly. Add a `record_park(db_path, ...)` / `clear_park(db_path, plan_slug)` pair next to `record_run` (bellows.py:287).
> 3. `record_run(..., status="Parked", ...)` for dashboard/status visibility.
> 4. Notify the CEO **once** via `notifier.push(app_key, user_key, "Bellows — Session Limit", ...)` — include plan name, `resume_step`, and the human `resets_at_raw`; state it will auto-resume. Dedup so a re-park of the same slug+step does not re-page (guard set like `_NOTIFIED_MISPLACED`, keyed `(plan_slug, resume_step)`).
> 5. Return from `run_plan` (park is terminal for this dispatch; the resume loop re-enters later). Do NOT fall through to gates/escalate.
>
> **Task B — exclude parked from the runnable scan.** `is_runnable_plan` (bellows.py:1579) must return `False` for `parked-` (add alongside `in-progress-`/`verdict-pending-`/`halted-`). Also add `"parked-"` to the prefix-strip lists at bellows.py:79 and :245 so slug derivation stays correct.
>
> **Task C — auto-resume.** Add a `_resume_parked(handler)` method invoked from `_rescan` (bellows.py:1806, alongside `_consume_verdicts`) **and** from the startup scan (~line 2136, so a restart during the wait still resumes). It queries `parked_steps` for rows where `resets_at_epoch <= now`; for each: verify the `parked-<...>.md` file still exists, rename it back to `in-progress-<...>.md`, `clear_park(...)`, log an EVENT, and dispatch `run_plan(plan_path, config, response_server, resume_step=resume_step, bellows=self)`. If the parked file is missing (CEO manually intervened), `clear_park` and log a WARN — do not crash. Guard against double-dispatch with the existing `_seen` / `_active` mechanisms the parallel-group path uses.
>
> **Task D — startup sweep awareness.** Confirm `_perform_startup_sweep` (bellows.py:2071) does NOT treat `parked-` files as orphans to remove. If it might, exclude them explicitly.
>
> **Tests (extend `tests/test_session_limit_park.py`).** (1) `record_park` then a query with `now >= resets_at` returns the row; with `now < resets_at` returns nothing. (2) `is_runnable_plan("parked-executable-9-.md")` is `False`. (3) Simulate the park helper on a synthetic `parsed` with `session_limit=True`: assert the plan file is renamed to `parked-*`, a `parked_steps` row exists, and `record_run` status is `Parked` (use a temp dir + temp db; do NOT spawn the daemon or `claude -p`). (4) A resume query at/after the epoch selects the row and the un-park rename produces `in-progress-*`. Keep unit-level (no real dispatch).
>
> **Self-verify.** FULL suite `python3 -m pytest tests/ -v` (`python3 -m pytest`, not `timeout`) to an explicit pass/fail; 0 regressions. **Commit**, e.g. `feat(daemon): park session-limited steps + auto-resume at resets-at`.
>
> **Deposit:** a dev-log with the park/persist/resume wiring, the `parked_steps` schema, restart-safety argument (startup scan re-resumes), notification dedup, full-suite tail, commit hash, Output Receipt. Canonical Python file-write pattern — no heredoc. In `### Ledger Updates` include `#### Prompt Feedback` (daemon-owned).
>
> **Deposits:**
> - `bellows/knowledge/development/session-limit-park-autoresume-daemon-2026-07-09.md`
> - `bellows/bellows.py`
> - `bellows/tests/test_session_limit_park.py`
>
> **STOP. Do NOT proceed to Step 3. Wait for CEO verdict.**

---
---

## STEP 3 — QA

---

> **FIRST — post a short visible chat message confirming you are starting Step 3 (QA) and your immediate next action.** Do NOT rename the plan file.
>
> You are Bellows QA. Read `bellows/agents/BELLOWS_QA.md` if present (skip with a note if absent). All commands run from `/Users/marklehn/Developer/GitHub/bellows`. **QA is verification + reporting only — no product-code changes.** If you find a blocker, STOP and report it (do not fix forward).
>
> **Scope:**
> - `knowledge/qa/session-limit-park-autoresume-qa-2026-07-09.md`
>
> **Verify against the locked design (CEO Context):**
> 1. **Detection precision.** Confirm the plan-132 signature parses and parks, while (a) a transient stderr `429`/`rate limit` still takes the once-only retry path unchanged, and (b) a `429` session-limit result with turns/cost > 0 does NOT park (escalates). Read the Step 1 tests and assert coverage exists for all three.
> 2. **resets-at parse + tz.** Confirm `11:50pm (America/Chicago)` maps to the correct next-future epoch, alternate time forms parse, and the unparseable-string fallback is ~now+5h with a WARN (not a crash, not a lost step).
> 3. **Restart safety.** Confirm the park is persisted in `bellows.db` (`parked_steps`) AND on disk (`parked-` prefix), and that resume is driven from BOTH `_rescan` and the startup scan — i.e. a daemon restart during the wait still auto-resumes. Read the code paths and confirm the tests exercise the DB round-trip and the rename both directions.
> 4. **No-progress safety.** Confirm the "park only when the step made no progress" guard is present and tested — parking must never re-run a step that already did partial work.
> 5. **Scan exclusion.** `is_runnable_plan` excludes `parked-`; slug-strip lists include it; startup sweep does not delete parked files.
> 6. **Notification.** CEO is paged once per park (dedup), message names the resume step + resets_at_raw.
>
> **Run the FULL suite** `python3 -m pytest tests/ -v` (`python3 -m pytest`, NOT `timeout`). Read the tail; record exact pass/fail counts and confirm 0 regressions vs the pre-plan baseline. Apply mechanical Rule 20 (deposits present) / Rule 22 gates.
>
> **Deposit:** `bellows/knowledge/qa/session-limit-park-autoresume-qa-2026-07-09.md` — verdict per checklist item (PASS/FAIL + evidence), the full-suite tail with counts, and an Output Receipt with status. Canonical Python file-write pattern — no heredoc. In `### Ledger Updates` include `#### Prompt Feedback` (daemon-owned). Update `bellows/PROJECT_STATUS.md` with the shipped feature.
>
> **Deposits:**
> - `bellows/knowledge/qa/session-limit-park-autoresume-qa-2026-07-09.md`
>
> **STOP. Wait for CEO verdict.**
