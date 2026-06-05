# QA Report — scope_check Directory-Mention Authorization

**Date:** 2026-06-05
**Plan:** executable-scope-check-dir-mention-2026-06-04
**Step:** 2 (QA)
**Scope:** Code-level ONLY — no daemon start, no live deposit

---

## DEV Output Receipt Status

DEV Step 1 deposit at `knowledge/development/scope-check-dir-mention-2026-06-04.md` — Output Receipt Status: **Complete**.

---

## Deliverable Verification (Rule 17)

| # | Deliverable | Expected | Status | Evidence |
|---|---|---|---|---|
| 1 | Clause present and correct | `parent = os.path.dirname(fpath)`, `authorized_by_dir` flag, `while parent:` ancestor walk with `parent.count("/") >= 1 and (parent + "/") in step_text`, `parent = os.path.dirname(parent)` decrement, `if authorized_by_dir: continue` — placed AFTER `fpath in step_text or basename in step_text` and BEFORE `out_of_scope.append(fpath)` | PASS | `evidence/clause_body.txt` |
| 2 | Depth guard correct | Predicate is `parent.count("/") >= 1` — rejects single-segment dirs | PASS | `evidence/depth_guard.txt` |
| 3 | Existing clauses byte-unchanged | Four pre-existing in-scope clauses, allowlist constants, `out_of_scope.append`, failure-append, evidence string all unchanged | PASS | `evidence/clause_context.txt` |
| 4 | Diff scope | `git diff` shows changes confined to single inserted clause (18 added lines); nothing else in `gates.py` changed | PASS | `evidence/diff_scope.txt` |
| 5 | Four new tests exist | `test_scope_check_accepts_child_file_under_trailing_slash_dir` (416), `test_scope_check_accepts_child_file_under_dir_placeholder_pattern` (428), `test_scope_check_depth_guard_rejects_shallow_dir_mention` (440), `test_scope_check_dir_mention_does_not_authorize_unmentioned_sibling_dir` (453) — all present | PASS | `evidence/new_tests_grep.txt` |
| 6 | Existing scope_check tests intact | `test_scope_check_passes_when_files_in_plan` (172), `test_scope_check_fails_when_file_not_in_plan` (178), `test_scope_check_allowlist` (184), `test_scope_check_prefix_allowlist_does_not_suppress_real_violations` (408) — all present and passing | PASS | `evidence/existing_tests.txt` |
| 7 | Dev log complete | 6856 bytes, contains clause verbatim, byte-unchanged confirmation, depth-guard rationale, pre-edit verification, both pytest runs (pre: 5 failed/448 passed, post: 5 failed/452 passed) | PASS | `evidence/dev_log_check.txt` |

**Result:** 7/7 PASS — no blockers.

---

## Test Execution

Full suite: `python3 -m pytest tests/ -v`

**Results:** 5 failed, 452 passed, 1 warning in 9.17s

**(a) All four new tests PASSED:**
- `test_scope_check_accepts_child_file_under_trailing_slash_dir` — PASSED
- `test_scope_check_accepts_child_file_under_dir_placeholder_pattern` — PASSED
- `test_scope_check_depth_guard_rejects_shallow_dir_mention` — PASSED (NEGATIVE: gate correctly flags shallow dir)
- `test_scope_check_dir_mention_does_not_authorize_unmentioned_sibling_dir` — PASSED (NEGATIVE: gate correctly flags unrelated dir)

**(b) All four existing scope_check tests PASSED:**
- `test_scope_check_passes_when_files_in_plan` — PASSED
- `test_scope_check_fails_when_file_not_in_plan` — PASSED
- `test_scope_check_allowlist` — PASSED
- `test_scope_check_prefix_allowlist_does_not_suppress_real_violations` — PASSED

**(c) ZERO new failures** — same 5 carry-over as DEV's pre-edit baseline:
- `test_decisions.py` x4 (phrase file not found in worktree)
- `test_runner_parser.py` x1 (`test_run_step_timeout`)

**(d) Total pass count:** 452 == DEV's reported post-edit number.

Evidence: `evidence/pytest_full.txt`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/scope-check-dir-mention-2026-06-04/
Files verified: 8
```

---

## Flags for CEO

- **REMINDER: restart the Bellows daemon to activate the scope_check directory-mention clause.** The running daemon evaluated this plan under the pre-edit gates.py; the fix activates on the next gate evaluation after restart. Also owed: capture this plan's organic Opus baseline (turns/wall/cost) from the step logs for the Opus<->Sonnet A/B.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 7 DEV deliverables (clause correctness, depth guard, existing clauses unchanged, diff scope, new tests, existing tests, dev log). Ran full test suite confirming 452 passed / 5 carry-over failures / zero new regressions. Rule 20 self-check PASSED.

### Files Deposited
- `knowledge/qa/scope-check-dir-mention-2026-06-04.md` — this QA report
- `knowledge/qa/evidence/scope-check-dir-mention-2026-06-04/clause_body.txt` — full clause extract
- `knowledge/qa/evidence/scope-check-dir-mention-2026-06-04/depth_guard.txt` — depth guard predicate
- `knowledge/qa/evidence/scope-check-dir-mention-2026-06-04/clause_context.txt` — surrounding loop region
- `knowledge/qa/evidence/scope-check-dir-mention-2026-06-04/diff_scope.txt` — git diff of gates.py
- `knowledge/qa/evidence/scope-check-dir-mention-2026-06-04/new_tests_grep.txt` — 4 new tests grep
- `knowledge/qa/evidence/scope-check-dir-mention-2026-06-04/existing_tests.txt` — 4 existing tests grep
- `knowledge/qa/evidence/scope-check-dir-mention-2026-06-04/dev_log_check.txt` — dev log verification
- `knowledge/qa/evidence/scope-check-dir-mention-2026-06-04/pytest_full.txt` — full test suite output

### Files Created or Modified (Code)
- `PROJECT_STATUS.md` — prepended 2026-06-04 Completed entry

### Decisions Made
- Used `testing/qa/evidence/bar-2026-06-04/` in sibling-dir test per DEV's documented test adjustment (within specialist authority — test intent preserved)

### Flags for CEO
- REMINDER: restart the Bellows daemon to activate the scope_check directory-mention clause. The running daemon evaluated this plan under the pre-edit gates.py; the fix activates on the next gate evaluation after restart. Also owed: capture this plan's organic Opus baseline (turns/wall/cost) from the step logs for the Opus<->Sonnet A/B.

### Flags for Next Step
- None — this is the final step
