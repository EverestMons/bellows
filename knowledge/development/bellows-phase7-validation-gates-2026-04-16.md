# Bellows Phase 7 — Validation Gates + Verdict Queue

**Date:** 2026-04-16
**Plan:** executable-bellows-phase7-validation-gates-2026-04-16.md
**Step:** 1 (DEV)

## Summary

Replaced planner.py AI consultation with mechanical validation gates and an async verdict queue. Bellows no longer spawns a claude -p subprocess to decide between steps. Instead, 8 gates run after each step — 5 pass/fail, 1 QA detector, 1 activity recorder, 1 scope validator. When all gates pass on a non-QA step, Bellows continues autonomously. When any gate fails or the step is QA, Bellows posts a verdict request and pauses.

## Changes Per File

### NEW: gates.py (~120 lines)
- Public function `check(parsed, plan_text, step_number, project_path, files_changed)` returns `{"passed": bool, "failures": [...], "is_qa_step": bool, "files_changed": [...]}`
- 8 gate functions:
  1. `_gate_receipt_status` — fails if receipt_status is not "Complete"
  2. `_gate_ceo_flags` — fails if CEO flags are non-empty
  3. `_gate_no_errors` — fails if is_error is True
  4. `_gate_no_permission_denials` — fails if permission denials exist
  5. `_gate_deposit_exists` — fails if deposited files don't exist on disk
  6. `_gate_is_qa_step` — detects QA steps (informational, not pass/fail)
  7. `_gate_file_change_audit` — records files_changed (informational)
  8. `_gate_scope_check` — fails if changed files are not mentioned in the step's plan text (with allowlist)

### NEW: verdict.py (~60 lines)
- `post_verdict_request()` — creates markdown verdict request in verdicts/pending/
- `check_verdict()` — reads verdict from verdicts/resolved/
- `log_to_ledger()` — appends JSON line to verdicts/ledger.jsonl

### MODIFIED: bellows.py (~60 lines changed)
- Replaced `import planner` with `import gates` and `import verdict`
- Added `_capture_git_diff()` and `_parse_diff_stat()` helpers
- `run_plan()`: pre/post git diff around each step, gates.check() after each dispatch, verdict request on failure or QA, plan renamed to verdict-pending- when paused
- `_rescan()`: now calls `_consume_verdicts()` on each 30s cycle
- `_consume_verdicts()`: scans verdicts/resolved/ for verdict files, resumes (continue) or halts (stop) plans
- `is_runnable_plan()`: now rejects verdict-pending- and halted- prefixes

### MODIFIED: notifier.py (+10 lines)
- Added `notify_verdict_request()` function

### NEW: verdicts/ directory
- `verdicts/pending/` — verdict request files
- `verdicts/resolved/` — verdict response files

### NEW: tests/test_gates.py (13 tests)
1. all_gates_pass_on_clean_parsed
2. receipt_status_blocked
3. receipt_status_partial
4. ceo_flags_nonempty
5. is_error_true
6. permission_denials_nonempty
7. deposit_path_missing (mocked os.path.isfile)
8. qa_step_detection
9. file_change_audit_populates
10. scope_check_passes_when_files_in_plan
11. scope_check_fails_when_file_not_in_plan
12. scope_check_allowlist
13. no_deposit_section_passes

### NEW: tests/test_verdict.py (5 tests)
1. post_verdict_request_creates_file
2. check_verdict_not_found
3. check_verdict_continue
4. check_verdict_stop
5. log_to_ledger_appends_json

## Verdict Flow

1. Step dispatched via runner.run_step()
2. Pre/post git diff captured around dispatch
3. gates.check() runs all 8 gates
4. If passed and not QA → continue to next step
5. If failed or QA → verdict.post_verdict_request() + Pushover notification + rename to verdict-pending-
6. Planner reads request, writes verdict to verdicts/resolved/
7. Bellows _consume_verdicts() on next 30s rescan picks up verdict
8. Continue → rename to in-progress, dispatch next step
9. Stop → rename to halted, send notification

## Test Results

```
55 passed, 1 warning in 0.72s
```

All 55 tests pass: 37 existing + 13 new gates tests + 5 new verdict tests. Zero regressions.

## Output Receipt

- **Status:** Complete
- **Files Created:** gates.py, verdict.py, tests/test_gates.py, tests/test_verdict.py, verdicts/pending/, verdicts/resolved/, knowledge/development/bellows-phase7-validation-gates-2026-04-16.md
- **Files Modified:** bellows.py, notifier.py
- **Tests:** 55 passed, 0 failed
