# QA Report — Bellows Phase 4 Reliability Fixes
**Date:** 2026-04-15 | **Plan:** executable-bellows-phase4-reliability-fixes-2026-04-15.md | **Step:** 2 (QA)

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|-------------|----------|--------|----------|
| `parser.py` — stop_reason logic | `stop_reason == "end_turn"` → Complete | ✅ | `grep_parser.txt`: line 17 confirms logic; old `for status in` loop absent |
| `parser.py` — old text-scan removed | `for status in ("Complete"...` absent | ✅ | `grep_parser.txt`: "(not found — confirmed removed)" |
| `bellows.py` — Fix 2c logging | `Planner decision for` in stdout | ✅ | `grep_bellows.txt`: line 184 |
| `bellows.py` — Fix 2a break | `break` (not `return`) at escalation timeout | ✅ | `grep_bellows.txt`: line 196 shows `break`; `strand_path_audit.txt` confirms no `return` between lines 196-220 |
| `planner.py` — retry logic | `time.sleep(5)` for auth retry | ✅ | `grep_planner.txt`: lines 146, 153 |
| `planner.py` — consultation log | `planner-consultation.jsonl` path | ✅ | `grep_planner.txt`: lines 88-89 |
| `planner.py` — auth error detection | `_is_auth_error` helper | ✅ | `grep_planner.txt`: lines 103, 150 |
| `planner.py` — fallback to continue | `"defaulting to continue"` | ✅ | `grep_planner.txt`: lines 167, 172 |

## Verification 1 — Parser Fix Unit Tests

3 new tests in `tests/test_phase4_parser.py`:

| Test | Result |
|------|--------|
| `test_parser_returns_complete_for_end_turn` | PASSED |
| `test_parser_returns_blocked_for_error` | PASSED |
| `test_parser_returns_partial_for_max_tokens` | PASSED |

Evidence: `parser_unit_tests.txt`

## Verification 2 — Strand Check Coverage on Escalation Path

**Before (pre-fix):** Line 195 `return` inside the while loop's escalation handler bypassed the strand check at lines 218-223. Plans halted by escalation timeout stayed as `in-progress-*` with no STRANDED notification.

**After (post-fix):** Line 196 `break` exits the while loop. Execution falls through to line 219-220 where `_is_plan_stranded()` runs, detects the in-progress file, and fires the STRANDED notification via Pushover.

**Confirmed:** No `return` exists between the `break` at line 196 and the strand check at line 220.

Evidence: `strand_path_audit.txt`

## Verification 3 — Planner Retry Behavior

2 new tests in `tests/test_phase4_planner_retry.py`:

| Test | Result |
|------|--------|
| `test_planner_retries_on_auth_failure` | PASSED |
| `test_planner_falls_back_to_continue_on_persistent_failure` | PASSED |

- First test: mocked subprocess returns 401 on first call, success on second. Verified `consult()` retries after 5s sleep and returns the success result.
- Second test: mocked subprocess returns 401 on both calls. Verified `consult()` returns `decision="continue"` with fallback reason containing "Planner unavailable" and "401".

Evidence: `planner_retry_tests.txt`

## Verification 4 — Full Test Suite Regression

**26/26 passed** (12 bellows + 3 notifier/server + 3 parser Phase 4 + 2 planner retry Phase 4 + 3 planner + 3 runner/parser).

No failures. No pre-existing tests broken.

Evidence: `pytest_full.txt`

## Verification 5 — Smoke Test

4-substep diagnostic plan (write marker + append feedback + git commit + move-to-Done) via direct `claude -p`:

| Substep | Expected | Status |
|---------|----------|--------|
| A — Marker file | `SMOKE_OK` in `research/smoke-marker.md` | ✅ |
| B — Append feedback | Original entry preserved + new section appended | ✅ |
| C — Git commit | `test: smoke` commit in log | ✅ |
| D — Move-to-Done | Plan in `decisions/Done/`, not elsewhere | ✅ |

`stop_reason=end_turn`. Agent completed all 4 substeps. Temp artifacts cleaned up.

Evidence: `smoke_test.txt`

## Output Receipt

- **Status:** Complete
- **Files Created or Modified (Code):**
  - `tests/test_phase4_parser.py` — 3 new unit tests for parser stop_reason inference
  - `tests/test_phase4_planner_retry.py` — 2 new unit tests for planner retry/fallback
- **Decisions Made:** All 5 verifications passed. No pre-existing test regressions. Smoke test confirmed agent completes all 4 substeps.
- **Flags for CEO:** None. All verifications green. Ready to ship.

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-bellows-phase4-reliability-fixes-2026-04-15/
Files verified: 8
```
