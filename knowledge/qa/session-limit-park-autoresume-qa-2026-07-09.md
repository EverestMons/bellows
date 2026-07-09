# QA Report — Session-limit park + auto-resume (Plan 148)
**Date:** 2026-07-09
**Agent:** Bellows QA
**Plan:** 148 — Session-limit pause-and-hold (park + auto-resume)
**Steps verified:** Step 1 (runner detect+parse) + Step 2 (daemon park+auto-resume)

---

## Verification Checklist

### 1. Detection precision — PASS

**Plan-132 signature parses and parks:**
- `_check_session_limit` (runner.py:74–101) checks `is_error == True`, `api_error_status == 429`, result text contains `"session limit"` or `"usage limit"` (case-insensitive), and the no-progress guard: `num_turns <= 1`, `total_cost_usd == 0`, `output_tokens == 0`.
- Test: `test_check_plan_132_event_is_parkable` (test_session_limit_park.py:141) feeds the exact plan-132 event dict and asserts `session_limit=True`, epoch in future.

**Transient stderr 429 unchanged:**
- The transient-retry guard (runner.py:248–256) is on the non-zero-exit path and greps stderr only. The session-limit check (runner.py:373–393) is on the success/NDJSON-parse path and greps the stdout result event. Mutually exclusive by construction — confirmed by comment at runner.py:247–248.
- Test: `test_check_transient_rate_limit_not_session_limit` (test_session_limit_park.py:159) feeds a `"429 Too Many Requests - rate limit exceeded"` event → returns `None`.

**429 session-limit with progress does NOT park:**
- Guard at runner.py:91: `num_turns > 1 or total_cost > 0 or output_tokens > 0` → returns `None`.
- WARN logged at runner.py:395–398 for visibility.
- Test: `test_check_session_limit_with_progress_not_parkable` (test_session_limit_park.py:203) tests all three dimensions independently.

### 2. resets-at parse + tz — PASS

**11:50pm (America/Chicago) maps correctly:**
- `_parse_session_reset` (runner.py:36–71) regex extracts `h[:mm]am/pm (Area/City)`, converts via `ZoneInfo`, computes next-future epoch (roll to tomorrow if past).
- Test: `test_parse_plan_132_string` (test_session_limit_park.py:51) verifies hour=23, minute=50, epoch > now.

**Alternate forms parse:**
- `test_parse_hour_only_pm` (11pm, New_York), `test_parse_am_with_minutes` (3:30am, US/Eastern), `test_parse_12pm_noon` (hour=12), `test_parse_12am_midnight` (hour=0). All pass.

**Unparseable fallback — ~now+5h, WARN, no crash:**
- `test_parse_unparseable_falls_back`: asserts epoch in [now+5h-1, now+5h+1], WARN captured on stdout.
- `test_parse_bad_timezone_falls_back`: valid time form but invalid zone → same 5h fallback + WARN.

### 3. Restart safety — PASS

**Dual persistence:**
- Disk: `shutil.move(inprogress_path, parked_path)` at bellows.py:439.
- DB: `record_park(db_path, ...)` at bellows.py:442 writes to `parked_steps` table (schema: `plan_slug TEXT PRIMARY KEY, plan_path TEXT, project TEXT, resume_step INTEGER, resets_at_epoch REAL, parked_at TEXT`).

**Resume from BOTH paths:**
- `_rescan` (bellows.py:1958): `self._resume_parked(handler)` — called every 30s rescan.
- Startup scan (bellows.py:2287): `self._resume_parked(handler)` — called once at daemon start, after `_perform_startup_sweep`.

**DB round-trip tests:**
- `test_record_park_queryable_at_epoch`: persist then query with `now >= resets_at` → row returned.
- `test_record_park_not_returned_before_epoch`: `now < resets_at` → no rows.
- `test_clear_park_removes_row`: insert + clear → 0 rows.
- `test_resume_unpark_rename`: simulates full un-park cycle (rename `parked-` → `in-progress-`, clear DB row).

### 4. No-progress safety — PASS

**Guard present and tested:**
- `_check_session_limit` (runner.py:87–91): parking requires `num_turns <= 1 AND total_cost_usd == 0 AND output_tokens == 0`. If any shows progress, returns `None` — falls through to existing Blocked/escalate path.
- Three test sub-cases in `test_check_session_limit_with_progress_not_parkable`: `num_turns=3`, `total_cost_usd=0.14`, `output_tokens=50` — all return `None`.

### 5. Scan exclusion — PASS

**`is_runnable_plan` excludes `parked-`:**
- bellows.py:1690: `filename.startswith("parked-")` → returns `False`.
- Test: `test_is_runnable_plan_excludes_parked` (test_session_limit_park.py:305).

**Slug-strip lists include `parked-`:**
- `slug_for` (bellows.py:82), `_shadow_path` (bellows.py:258), `run_plan` base_filename strip (bellows.py:482).

**Startup sweep does NOT delete parked files:**
- `_perform_startup_sweep` (bellows.py:2236–2238): `parked-` files are treated as active slugs (added to `active_slugs` set), not orphans. Only verdicts/pending files matching non-active slugs are deleted.

**Lifecycle prefix lists include `parked-`:**
- `LIFECYCLE_PREFIXES` at bellows.py:1760, `_invalidate_seen_on_redeposit` guard, and `_rescan` slug list.

### 6. Notification — PASS

**CEO paged once per park (dedup):**
- `_NOTIFIED_PARKED: set[tuple[str, int]]` at bellows.py:35, keyed on `(plan_slug, current_step)`.
- Guard at bellows.py:451: `if dedup_key not in _NOTIFIED_PARKED:` → `notifier.push(...)` → `_NOTIFIED_PARKED.add(dedup_key)`.

**Message content:**
- bellows.py:455–456: includes plan name, step number, `resets_at_raw`, and "Will auto-resume at reset time."

---

## Step 1 + Step 2 Deposits

| Deposit | Present | Content |
|---|---|---|
| `knowledge/development/session-limit-detection-runner-2026-07-09.md` | Yes | Step 1 dev log |
| `runner.py` | Yes | Session-limit detection + parse |
| `tests/test_session_limit_park.py` | Yes | 26 tests (12 Step 1 + 14 Step 2) |
| `knowledge/development/session-limit-park-autoresume-daemon-2026-07-09.md` | Yes | Step 2 dev log |
| `bellows.py` | Yes | Park + persist + auto-resume wiring |

---

## Full Test Suite

```
python3 -m pytest tests/ -v
788 passed, 1 warning in 20.13s
```

0 regressions. Warning is urllib3/LibreSSL compatibility (pre-existing, not plan-related).

---

## Verdict

**PASS** — all 6 checklist items verified. Detection is precise (session-limit only, not transient 429s), no-progress guard prevents parking mid-step work, restart safety is dual-persisted (disk + DB) with resume from both `_rescan` and startup, scan exclusion is complete, notification is deduped.

---

### Ledger Updates

#### PROJECT_STATUS
Plan 148: session-limit park + auto-resume shipped. Runner detects session-limit 429 result events and parses `resets-at` time+zone. Daemon parks the plan (rename + DB persist), notifies CEO once, and auto-resumes at reset time. Restart-safe (resume fires from both rescan and startup scan). 26 new tests, full suite 788 passed. **DAEMON RESTART REQUIRED.**

#### Prompt Feedback
- Session-limit detection logic is clean — separate from transient-retry guard by construction (stderr vs stdout result event), well-tested, no edge-case confusion.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 3
**Status:** Complete

### What Was Done
Verified all 6 QA checklist items against Step 1 (runner detection + parse) and Step 2 (daemon park + persist + auto-resume) implementations. Ran full test suite (788 passed, 0 regressions). Deposited QA report with per-item PASS verdicts and evidence.

### Files Deposited
- `knowledge/qa/session-limit-park-autoresume-qa-2026-07-09.md` — this QA report

### Files Created or Modified (Code)
- None (QA is verification only)

### Decisions Made
- All 6 checklist items PASS — no blockers found

### Flags for CEO
- **DAEMON RESTART REQUIRED** to activate session-limit park + auto-resume (both runner.py and bellows.py changes load at startup)

### Flags for Next Step
- None
