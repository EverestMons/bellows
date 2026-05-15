# QA Report — Activity-Based Inactivity Timeout
**Date:** 2026-04-17 | **Plan:** `executable-activity-timeout-2026-04-17` | **Step:** 2 (QA)

## Dev Log Check
- **Output Receipt:** Complete
- **Files changed:** `runner.py`, `bellows.py`
- **Commit:** `feat: activity-based inactivity timeout — replace subprocess.run with Popen streaming`

## Deliverable Verification

| # | Check | File | Status |
|---|-------|------|--------|
| a1 | `subprocess.Popen` replaces `subprocess.run` | runner.py:48 | ✅ |
| a2 | `threading` for concurrent stdout/stderr read | runner.py:6,79,91-92 | ✅ |
| a3 | Inactivity timer with `last_output_time` reset | runner.py:78,82,87,106 | ✅ |
| a4 | `proc.kill()` on timeout | runner.py:116,123 | ✅ |
| a5 | `stderr_partial` in timeout error dict | runner.py:144 | ✅ |
| b | `step_inactivity_timeout_seconds` in bellows.py | bellows.py:238,296 | ✅ |
| c | Backward compat: both config field names checked | bellows.py:238-239,296-297 | ✅ |
| d | Hard wall-clock cap (`timeout * 10`) | runner.py:45,121-122 | ✅ |

## Evidence
- `knowledge/qa/evidence/executable-activity-timeout-2026-04-17/grep_deliverables.txt`

## Verdict
All 8 checks verified against live code via grep. Evidence file deposited.
