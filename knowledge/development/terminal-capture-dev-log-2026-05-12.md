# Terminal Output Redesign + Log Capture — Dev Log

**Date**: 2026-05-12
**Plan**: `executable-terminal-capture-2026-05-12`
**Commit**: `b11ecc4`

---

## HEAD Refresh Result

Audit (2026-05-11) counted 64 print() calls across bellows.py. HEAD at execution time had 66 — delta of +2, traced to 3 commits landed after the audit:
- Module fingerprint observability
- `_seen` slug refactor
- Fence-strip parsers

All 66 accounted for; no missed call sites.

---

## Per-Stage Completion Checklist

| Stage | Description | Status |
|-------|-------------|--------|
| 1a | `_log()` helper with 5-level taxonomy | Done |
| 1b | `_last_plan_event_time` + threading.Lock | Done |
| 1c | Python logging config (RotatingFileHandler + StreamHandler) | Done |
| 1d | `_rotate_logs()` for session JSON (30d) and planner-consultation (10MB) | Done |
| 1e | Session-start log line (`slug_for()` helper) | Done |
| 2 | bellows.py: 56 call-site migrations | Done |
| 3 | runner.py: 6 call-site migrations + signature extension | Done |
| 4 | notifier.py: 1 call-site migration | Done |
| 5 | Heartbeat redesign (300s cadence, state-bearing, suppression) | Done |
| 6 | Prefix audit — no `Bellows:` or `[runner]` outside banners | Done |

---

## Design Choices

### Stage 3 — Runner heartbeat suppression mechanism

Chose **Option (b): `suppress_timer_update` parameter** on `_log()`.

The 3 runner heartbeat/timeout log calls pass `suppress_timer_update=True`, preventing them from resetting `_last_plan_event_time`. This keeps the main heartbeat from being indefinitely suppressed by runner activity during long-running steps.

### Stage 4 — Notifier stderr routing

Routed notifier errors to **stdout via `_log()`** (same as all other log output). Did not add a `to_stderr` parameter — the notifier's single error site (`requests.RequestException`) does not warrant a separate routing path. This is a behavioral change: notifier errors previously went to stderr, now go to stdout and the terminal log file.

---

## Test Results

- **Total**: 269 tests
- **Passed**: 268
- **Failed**: 1 (pre-existing: `test_run_step_timeout` — mocks `subprocess.run` but runner.py uses `subprocess.Popen`; verified failing on clean HEAD before changes)
- **Tests modified**: 2
  - `test_extract_total_steps_case_mismatch_warning`: assertion updated `"WARNING"` -> `"[WARN]"` (new format)
  - `test_skip_logging_fires_once`: assertion updated from filename-in-message to slug-bracket format
- **_log() test compatibility**: Added fallback `print()` when logger has no handlers, so capsys capture works in pytest without logger setup

---

## Remaining print() Calls (11, all legitimate)

- 8 startup banner prints (pre-logger, decorative)
- 3 `_rotate_logs()` prints (pre-logger, runs before logger init)

---

## Output Receipt

```
Step 1 complete.
Files modified: bellows.py, runner.py, notifier.py, tests/test_bellows.py
Commit: b11ecc4
Tests: 268/269 passed (1 pre-existing failure)
Call sites migrated: 63 (56 bellows + 6 runner + 1 notifier)
print() remaining: 11 (all pre-logger, legitimate)
```
