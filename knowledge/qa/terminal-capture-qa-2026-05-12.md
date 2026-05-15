# Terminal Output Redesign + Log Capture — QA Report

**Date:** 2026-05-12
**Plan:** `executable-terminal-capture-2026-05-12`
**Step:** 2 (Bellows QA)
**Dev log:** `knowledge/development/terminal-capture-dev-log-2026-05-12.md`
**Design spec:** `knowledge/research/terminal-notification-capture-design-2026-05-11.md`

---

## Verification Table

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | `_log()` helper presence — signature, format, level validation | ✅ | `evidence/executable-terminal-capture-2026-05-12/log_helper_present.txt` |
| 2 | Print call audit — bellows.py 11, runner.py 0, notifier.py 0 | ✅ | `evidence/executable-terminal-capture-2026-05-12/print_audit.txt` |
| 3 | `Bellows:` prefix audit — only in `_rotate_logs()` + class decl; `[runner]` 0 matches | ✅ | `evidence/executable-terminal-capture-2026-05-12/bellows_prefix_audit.txt` |
| 4 | Logging configuration — StreamHandler(stdout) + RotatingFileHandler, propagate=False | ✅ | See Section 4 below |
| 5 | `_rotate_logs()` — exists, called before logger config, correct retention | ✅ | See Section 5 below |
| 6 | Heartbeat redesign — 300s cadence, state-bearing, suppression within 120s | ✅ | `evidence/executable-terminal-capture-2026-05-12/heartbeat_block.txt` |
| 7 | Runner heartbeat carries plan identity + suppress_timer_update=True | ✅ | See Section 7 below |
| 8 | Format spot-checks — 5 categories verified | ✅ | See Section 8 below |
| 9 | Test suite — 268/269 passed (1 pre-existing failure) | ✅ | `evidence/executable-terminal-capture-2026-05-12/pytest_result.txt` |
| 10 | Static format-string validation — all levels valid, no legacy prefixes | ✅ | See Section 10 below |
| 11 | Rule 20 self-check | ✅ | See Section 11 below |

---

## Section 4 — Logging Configuration Detail

Verified at `bellows.py:1316-1339` (main block):

- `_rotate_logs()` called at line 1318 (before logger config)
- Logger: `logging.getLogger("bellows")` at line 1321
- Level: `DEBUG` at line 1322
- `propagate = False` at line 1323
- StreamHandler to `sys.stdout` at lines 1325-1328, formatter `%(message)s`
- `os.makedirs("logs/terminal", exist_ok=True)` at line 1330
- Log path: `logs/terminal/bellows-{datetime.now().strftime('%Y-%m-%d')}.log` at lines 1331-1334
- `_log_existed = os.path.exists(_session_log_path)` checked before handler creation at line 1335
- RotatingFileHandler at line 1336: `maxBytes=50*1024*1024, backupCount=5`

All parameters match the design spec.

---

## Section 5 — Rotation Function Detail

Verified at `bellows.py:70-95`:

- `_rotate_logs()` defined as module-level function
- Called at line 1318 in main block, BEFORE logger configuration at line 1320
- Terminal logs: deletes files in `logs/terminal/` older than 14 days (line 77: `14 * 86400`)
- Step JSON: deletes `.json` files in `logs/` older than 30 days (line 86: `30 * 86400`)
- Planner consultation: rotates `planner-consultation.jsonl` when >10MB (line 90: `10 * 1024 * 1024`)
- Uses `print()` for rotation messages (legitimate — logger not yet configured)

---

## Section 7 — Runner Heartbeat Detail

Verified at `runner.py:117, 122, 129`:

- Line 117: `_log("INFO", f"runner: {int(elapsed)}s elapsed, last output {int(age)}s ago (step {step_num})", slug=plan_slug, suppress_timer_update=True)`
- Line 122: `_log("ERROR", f"runner: inactivity timeout ({timeout}s with no output), killing process (step {step_num})", slug=plan_slug, suppress_timer_update=True)`
- Line 129: `_log("ERROR", f"runner: hard wall-clock cap reached ({max_wall_clock}s), killing process (step {step_num})", slug=plan_slug, suppress_timer_update=True)`

All 3 runner heartbeat/timeout sites:
- Include slug (plan identity) via `slug=plan_slug`
- Include step number via `(step {step_num})`
- Pass `suppress_timer_update=True` — confirmed this prevents `_last_plan_event_time` update (bellows.py:52 checks this flag)

`run_step()` signature at runner.py:28-36 accepts `plan_slug: Optional[str] = None, step_num: Optional[int] = None`.

---

## Section 8 — Format Spot-Checks

Five migrated call sites from different categories:

| Category | Line | Code | Format OK |
|----------|------|------|-----------|
| Plan detection | bellows.py:944 | `_log("EVENT", f"⏳ detected plan", slug=slug_for(filename))` | ✅ |
| Gate evaluation | bellows.py:451 | `_log("EVENT", f"gates step {current_step}: passed={gate_result['passed']}, failures={len(gate_result['failures'])}", slug=slug_for(plan_name))` | ✅ |
| Verdict pause | bellows.py:487 | `_log("PAUSE", f"⏸️ step {current_step} — waiting for CEO verdict", slug=slug_for(plan_name))` | ✅ |
| Worktree warning | bellows.py:691 | `_log("WARN", f"⚠ {project_name} has no project-local .git — running in-place without worktree isolation", slug=slug)` | ✅ |
| Mode A error | bellows.py:431 | `_log("ERROR", f"❌ Mode A detected — agent moved to Done/ without authorization, recovering", slug=slug_for(plan_name))` | ✅ |

All 5 verified: timestamp via `_log()`, correct severity bracket, slug present, no legacy `Bellows:` prefix, no leading timestamp in message arg.

---

## Section 10 — Static Format-String Validation

Scanned all `_log()` call sites across all 3 files:

**bellows.py** (56 migrated sites): Levels used — EVENT (16), INFO (10), WARN (20), ERROR (5), PAUSE (5). All valid.
**runner.py** (6 sites): Levels used — INFO (1), ERROR (2), WARN (3). All valid.
**notifier.py** (1 site): Level used — ERROR (1). Valid.

Violations found: **0**
- No invalid level strings
- No `Bellows:` prefix in any message argument
- No leading timestamp in any message argument (all timestamps added by `_log()`)

---

## Section 11 — Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-terminal-capture-2026-05-12/
Files verified: 5
```

---

## Output Receipt

**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Performed 11-point QA verification of the terminal output redesign + log capture implementation (Plan 1). All checks passed: `_log()` helper correctly implemented with 5-level taxonomy, 63 print() calls migrated (11 legitimate remaining), logging configured with dual handlers, heartbeat redesigned to 300s/state-bearing/suppressed, runner heartbeats carry plan identity without suppressing main heartbeat, all format strings validated, 268/269 tests pass (1 pre-existing failure).

### Files Deposited
- `knowledge/qa/terminal-capture-qa-2026-05-12.md` — QA verification report with 11-check table
- `knowledge/qa/evidence/executable-terminal-capture-2026-05-12/print_audit.txt` — grep output for print() calls
- `knowledge/qa/evidence/executable-terminal-capture-2026-05-12/bellows_prefix_audit.txt` — grep output for Bellows: prefix
- `knowledge/qa/evidence/executable-terminal-capture-2026-05-12/log_helper_present.txt` — quoted _log() definition
- `knowledge/qa/evidence/executable-terminal-capture-2026-05-12/heartbeat_block.txt` — quoted heartbeat block
- `knowledge/qa/evidence/executable-terminal-capture-2026-05-12/pytest_result.txt` — full pytest output

### Files Created or Modified (Code)
- None (QA verification only)

### Decisions Made
- Accepted 11 remaining print() calls as legitimate (8 banner + 3 _rotate_logs, all pre-logger)
- Accepted test_run_step_timeout failure as pre-existing (verified on clean HEAD)
- Test count 269 vs dev log baseline of 269 — no delta

### Flags for CEO
- None

### Flags for Next Step
- None — plan is complete (2/2 steps done)
