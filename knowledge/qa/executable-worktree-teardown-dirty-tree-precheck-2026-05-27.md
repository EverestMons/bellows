# QA Report — Worktree Teardown Dirty-Tree Pre-Check

**Date:** 2026-05-28 | **Agent:** Bellows QA | **Step:** 2 (QA)
**DEV commit:** `6252f8c feat: worktree teardown dirty-tree pre-check (worktree_teardown_dirty_tree gate)`
**SA surface:** `knowledge/research/worktree-teardown-dirty-tree-precheck-surface-2026-05-27.md`

---

## Verification Checklist

| # | Check | Status | Evidence |
|---|---|---|---|
| 1 | **Pre-check location** — `git status --porcelain` sits before cherry-pick loop, runs with `cwd=project_path` (NOT `wt_path`) | ✅ PASS | bellows.py:855-894 — after index.lock cleanup (line 853), before cherry-pick loop (line 896). `cwd=project_path` at line 859. |
| 2 | **fail-open** — `git status` error/non-zero does NOT raise `WorktreeTeardownError`; successful non-empty result DOES raise | ✅ PASS | Lines 891-894: `except WorktreeTeardownError: raise` re-raises dirty-tree errors; generic `except Exception:` logs warning and proceeds. Dirty predicate at line 861: `returncode == 0 and stdout.strip()`. Test `test_teardown_proceeds_when_git_status_errors` confirms returncode=128 → no raise. |
| 3 | **Gate name visible** — `worktree_teardown_dirty_tree` appears in evidence string and surfaces in verdict request | ✅ PASS | Evidence string leads with `worktree_teardown_dirty_tree:` (line 868-869). All three caller sites (521-525, 614-618, 643-658) pass `str(e)` as `evidence` in the failure dict `{"gate": "worktree_teardown", "evidence": str(e)}`. DEV used the "simpler and preferred" approach per plan — gate name embedded in evidence string, no caller-site overrides needed. |
| 4 | **Evidence content** — dirty-file listing (10-line truncation), both recovery sub-variants, LESSONS.md 2026-05-27 pointer | ✅ PASS | Truncation: lines 863-867 (splitlines, `[:10]`, `... (N more files)` suffix). Sub-variant A: line 877. Sub-variant B: line 882. LESSONS pointer: line 889 (`LESSONS.md 2026-05-27 R2 recovery shape`). `project_path` interpolated in recovery commands (lines 878, 883). |
| 5 | **New tests present and green** — 3+ new tests exist and pass | ✅ PASS | 4 new tests all pass: `test_teardown_pauses_when_local_main_dirty`, `test_teardown_proceeds_when_local_main_clean`, `test_teardown_dirty_tree_evidence_contains_recovery_commands`, `test_teardown_proceeds_when_git_status_errors` (fail-open bonus). Teardown suite: **9 passed in 0.20s**. |
| 6 | **No cherry-pick on dirty** — `test_teardown_pauses_when_local_main_dirty` asserts cherry-pick never called | ✅ PASS | Test tracks cherry-pick calls via `cherry_pick_called` list (line 2893); asserts `len(cherry_pick_called) == 0` at line 2914. Also returns dirty output ONLY when `cwd == project_path` (line 2899), catching wrong-cwd regression per SA Section 5.2. |
| 7 | **Existing teardown tests green** — no regressions in existing teardown tests | ✅ PASS | All 5 existing tests pass: `test_teardown_worktree_noop_when_wt_equals_project`, `test_teardown_worktree_removes_stale_index_lock`, `test_teardown_worktree_waits_for_fresh_index_lock`, `test_teardown_worktree_force_removes_orphaned_directory`, `test_pause_site_4_auto_close_teardown_failure_renames_before_post`. Existing fixtures return `stdout=""` which the pre-check treats as clean — no fixture changes needed. |
| 8 | **Adjacent suite** — full `test_bellows.py` green | ✅ PASS | **122 passed, 0 failed, 0.83s**. No failures attributable to this change or otherwise. |

---

## Deviations from SA Spec

None. The implementation matches the SA surface map (Sections 2-4) verbatim. Evidence string format, truncation logic, fail-open error handling, and test coverage all align with the spec.

---

RULE 20 SELF-CHECK: PASSED
- All checklist rows have explicit status: yes
- Positive-status rows use {✅, OK, PASS, [x], done, complete, verified}: yes
- Test counts reported with timing: yes
- Any deviation from SA spec flagged: yes (none found)

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2 (QA)
**Status:** Complete

### What Was Done
Verified the dirty-tree pre-check implementation against the SA surface map across all 8 checklist items. Confirmed correct insertion point, cwd targeting, fail-open behavior, gate name visibility through verdict path, evidence string content, 4 new tests green, no regressions in existing teardown tests, and full adjacent suite green (122/122).

### Files Deposited
- `knowledge/qa/executable-worktree-teardown-dirty-tree-precheck-2026-05-27.md` — QA report (8-row checklist + Rule 20 banner)

### Files Created or Modified (Code)
- None (verification only)

### Decisions Made
- Confirmed DEV's approach of embedding gate name in evidence string (rather than overriding at caller sites) is correct per plan's "simpler and preferred" guidance
- Confirmed existing test fixtures needed no changes (stdout="" is clean by default)

### Flags for CEO
- None

### Flags for Next Step
- None
