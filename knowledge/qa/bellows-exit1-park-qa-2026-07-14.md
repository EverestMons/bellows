# QA Report: Bellows exit-1 rate-limit auto-park (plan 185)

**Date:** 2026-07-14
**Plan:** executable-185
**Step:** 2 — QA: full-suite + code-level verification of the guards
**Commit under test:** `38c1670`

---

## 1. Full Suite

```
805 passed, 1 warning in 20.78s
```

RAW tail deposited to `evidence/bellows-exit1-park-qa-2026-07-14/full-suite.txt`.

**Baseline reconciliation:** Step 1 added 10 new tests to `tests/test_session_limit_park.py` (21 → 31). Total suite 805, all passing. No new failures, no regressions.

---

## 2. Code-Level Verification Table

| # | Claim | Verdict | Evidence |
|---|-------|---------|----------|
| 1 | `_check_exit1_rate_limit` returns `None` unless a `five_hour` rate_limit_event is present (guard b) | **PASS** | `runner.py:162` — `if five_hour_event is None: return None`. The function only proceeds to evaluate progress guards when a `rate_limit_event` with `rateLimitType == "five_hour"` was found in the stream (line 141). |
| 2 | Progress guard is `num_turns<=1 AND total_output_tokens<500 AND NOT has_mutating_tool_use` | **PASS** | `runner.py:165` — `if num_turns > 1 or total_output_tokens >= 500 or has_mutating_tool_use:` → returns `None`. Mutating tools defined at line 124: `{"Write", "Edit", "Bash", "NotebookEdit"}`. |
| 3 | Exit-1 block calls helper AFTER transient-retry check, merges `session_limit` only when non-None | **PASS** | `runner.py:336` — `exit1_sl = _check_exit1_rate_limit(result_stdout, plan_slug)` appears after the transient-retry block (lines 327–333). Line 337: `if exit1_sl is not None:` gates the merge. The return dict at lines 351–366 includes `session_limit`, `resets_at_epoch`, `resets_at_raw`, and `stop_reason="session_limit"`. |
| 4 | Existing graceful-429 `_check_session_limit` path (lines 74–101) is UNCHANGED | **PASS** | `git --no-pager diff HEAD~1 -- runner.py` shows the diff hunk header at `@@ -101,6 +101,83 @@` — all new code is ADDED after line 101. Lines 74–101 (`_check_session_limit`) have zero deletions or modifications. The hunk context line reads `def _check_session_limit(result_event: dict)` confirming additions start after its closing brace. |
| 5 | `bellows.py` backup guard blocks park when worktree HEAD != baseline | **PASS** | `bellows.py:429–437` — `if plan_baseline_sha is not None:` → `current_sha = _capture_git_diff(wt_path)` → `if current_sha and current_sha != plan_baseline_sha:` returns `False` (not parking). Wrapped in `try/except Exception: pass` for defensive fallback. `plan_baseline_sha` threaded from call sites at lines 682 and 807 via `plan_baseline_sha=pre_diff`. |
| 6 | Tests i–iv present + passing | **PASS** | (i) `test_exit1_five_hour_zero_progress_parkable` — asserts `result["session_limit"] is True` and `result["resets_at_epoch"] == 1784053800.0` — **PASSED**. (ii) `test_exit1_no_rate_limit_event_not_parkable` — asserts `result is None` — **PASSED**. (iii) `test_exit1_five_hour_with_progress_not_parkable` — asserts `result is None` (Write tool_use + 2000 output_tokens) — **PASSED**. (iv) `test_graceful_429_session_limit_still_parkable` — asserts `result["session_limit"] is True` via existing `_check_session_limit` — **PASSED**. Integration tests: `test_exit1_rate_limit_integration_parkable`, `test_exit1_no_rate_limit_integration_gate_failure`, `test_exit1_five_hour_with_progress_integration_gate_failure`, `test_maybe_park_backup_guard_blocks_when_head_differs` — all **PASSED**. Full pytest output: `31 passed, 1 warning in 0.26s`. |
| 7 | NO change to `_resume_parked` / `record_park` / `clear_park` / `parked_steps` schema | **PASS** | `git --no-pager diff HEAD~1 -- bellows.py` shows no lines matching `_resume_parked`, `record_park`, `clear_park`, or `parked_steps`. `git --no-pager diff HEAD~1 -- runner.py` similarly shows no changes to those names. Only additions: new helpers `_reset_epoch_from_rate_limit_event` and `_check_exit1_rate_limit` in runner.py; new `plan_baseline_sha` parameter and backup guard block in bellows.py `_maybe_park_session_limit`. |

---

## Rule 20 — QA Self-Check Results

| Check | Result |
|-------|--------|
| Full test suite passes (805/805) | PASS |
| No regressions (baseline 795 + 10 new = 805) | PASS |
| Guard (b): five_hour event required for park — code quotes line 162 | PASS |
| Guard (a): progress threshold correct — code quotes line 165 | PASS |
| Call site placement after transient-retry — code quotes line 336 | PASS |
| Graceful-429 path unchanged — diff confirms zero edits to lines 74–101 | PASS |
| Backup guard blocks park on HEAD != baseline — code quotes lines 429–437 | PASS |
| 4-case test matrix (i–iv) present and passing | PASS |
| Park/resume machinery unchanged — diff confirms | PASS |

**PASSED — SELF-CHECK PASSED**

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Full test suite verification (805 passed, 0 failed) and 7-row code-level verification table confirming both guards, call-site placement, graceful-429 path preservation, backup guard, test matrix, and park/resume machinery invariance.

### Files Deposited
- `knowledge/qa/bellows-exit1-park-qa-2026-07-14.md` — this QA report
- `knowledge/qa/evidence/bellows-exit1-park-qa-2026-07-14/full-suite.txt` — RAW pytest tail (last 40 lines including summary)

### Files Created or Modified (Code)
- None (QA-only step)

### Decisions Made
- Used `tail -40` for evidence capture per plan instructions

### Flags for CEO
- None

### Flags for Next Step
- None (final step)
