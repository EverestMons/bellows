# Per-Plan Diff Baseline Fix — QA Report
**Date:** 2026-06-12 | **Plan:** 28 | **Step:** 2 (QA) | **Agent:** Bellows QA

---

## Verification Table

| # | Item | Method | Evidence File | Status |
|---|------|--------|---------------|--------|
| 1 | Full suite — 538 passed, 0 failures, +3 new tests | Executed `python3 -m pytest tests/`, captured tail | `full_suite_tail.txt` | PASS |
| 2 | Mechanism landed — `plan_baseline_sha` at dispatch start, `_parse_diff_stat` uses `post_diff` | grep callsites + `git diff HEAD~1 -- bellows.py` | `mechanism_check.txt` | PASS |
| 3 | Behavioral proof — 3 contamination tests pass in isolation | Executed `pytest -v -k` isolation run | `behavior_check.txt` | PASS |
| 4 | FORWARD reconciliation — row 21 closed-by-plan-28, row 16 withdrawn | Edited FORWARD.md, captured diff | `forward_reconciliation.txt` | PASS |

---

## Verification Details

### 1. Full Suite
- **Command:** `python3 -m pytest tests/`
- **Result:** 538 passed, 1 warning in 10.10s
- **New test count:** 3 (matches dev log: before=535, after=538)
- **Failures/errors:** 0

### 2. Mechanism Landed
- `bellows.py:534` — `plan_baseline_sha = _capture_git_diff(wt_path)` captures baseline ONCE at dispatch start
- `bellows.py:535` — `pre_diff = plan_baseline_sha` sets initial pre_diff from stored baseline
- `bellows.py:577-578` — `post_diff` captured at step end, passed to `_parse_diff_stat` as first arg
- `bellows.py:687-688` — same pattern for subsequent steps
- `bellows.py:855-859` — `_parse_diff_stat` now branches on `post_diff`: when non-empty, uses two-commit diff (`pre_diff..post_diff`); when empty, falls back to working-tree diff
- `bellows.py:816` — `_capture_git_diff` returns HEAD SHA via `git rev-parse HEAD` (diagnostic Section 5 verification block confirmed)

### 3. Behavioral Proof
Three integration tests using real git repos, all PASS:
1. `test_parse_diff_stat_excludes_concurrent_plan_changes` — files from concurrent plan excluded
2. `test_parse_diff_stat_includes_own_step_changes_with_post_diff` — own changes included
3. `test_parse_diff_stat_multistep_per_step_isolation` — step 2 only shows step 2 changes

### 4. FORWARD Reconciliation (Rule 42)
- **Row 21:** Status `open` -> `closed-by-plan-28`, Plan-id link set to `28`
- **Row 16:** Status `open` -> `withdrawn`, Item suffixed: `— withdrawn 2026-06-12: already fixed pre-id by union scope_check (commit 706fbe7); per diagnostic 27`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/28/knowledge/qa/evidence/diff-baseline-fix-2026-06-12/
Files verified: 4
```

---

## Receipt Flags for CEO

- **DAEMON RESTART REQUIRED** — new `_parse_diff_stat` behavior takes effect on restart
- **Live canary:** the next pair of overlapping same-repo plans gates without foreign files in `files_changed`

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified per-plan diff baseline fix (plan 28): full suite pass (538/538), mechanism confirmed at all callsites, behavioral proof via 3 isolation tests, FORWARD reconciliation for rows 16 and 21. Rule 20 self-check executed with all evidence files present.

### Files Deposited
- `knowledge/qa/diff-baseline-fix-qa-report-2026-06-12.md` — this QA report
- `knowledge/qa/evidence/diff-baseline-fix-2026-06-12/full_suite_tail.txt` — full suite tail
- `knowledge/qa/evidence/diff-baseline-fix-2026-06-12/mechanism_check.txt` — mechanism verification
- `knowledge/qa/evidence/diff-baseline-fix-2026-06-12/behavior_check.txt` — behavioral proof
- `knowledge/qa/evidence/diff-baseline-fix-2026-06-12/forward_reconciliation.txt` — FORWARD diff

### Files Created or Modified (Code)
- `knowledge/FORWARD.md` — row 21 closed-by-plan-28, row 16 withdrawn

### Decisions Made
- All 4 verification checks PASS — plan is ready for closure
- Row 16 withdrawal per diagnostic 27 + CEO fork disposition (already fixed by commit 706fbe7)

### Flags for CEO
- DAEMON RESTART REQUIRED after plan close
- Live canary: next pair of overlapping same-repo plans gates without foreign files in files_changed

### Flags for Next Step
- None (terminal QA step)
