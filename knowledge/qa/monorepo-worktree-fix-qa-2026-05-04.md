# QA Report — executable-monorepo-worktree-fix-2026-05-04

**Date:** 2026-05-04 | **QA Agent:** Bellows QA | **Plan Tier:** Small

---

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `.git` detection check in `_create_worktree` | `os.path.exists(os.path.join(project_path, ".git"))` at line 528 | ✅ | `grep_detection_check.txt` — 1 match at line 528 |
| In-place fallback log message | Warning printed when `.git` absent | ✅ | `grep_log_message.txt` — matches at lines 524 (docstring) and 530 (print) |
| New unit tests in test file | test_bellows.py shows new test functions in commit stat | ✅ | `git_show_commit.txt` — 4 files changed, test_bellows.py +51 lines |
| 2026-05-03 type-fix intact (3 sites) | `"gate": "worktree_teardown"` at lines 340, 405, 433 | ✅ | `grep_type_fix_intact.txt` — all 3 matches confirmed |
| Commit message correct | `fix: skip worktree creation when project_path has no .git (bellows-self monorepo trap)` | ✅ | `git_show_commit.txt` — commit `06aa938` |

---

## Test Regression

### Targeted (test_bellows.py + test_verdict.py)
- **90 passed, 0 failed**
- 3 new tests all pass: `test_create_worktree_returns_project_path_when_no_git`, `test_teardown_worktree_noop_when_wt_equals_project`, `test_create_worktree_proceeds_when_git_exists`
- Evidence: `pytest_targeted.txt`

### Full Suite
- **193 passed, 1 failed**
- Single failure: `test_run_step_timeout` (pre-existing, unrelated — known baseline failure in test_runner_parser.py)
- No regressions introduced
- Evidence: `pytest_full.txt`

### Cross-Project Regression
- `test_create_worktree_proceeds_when_git_exists` — creates a temp directory with `.git` subdir, confirms `_create_worktree` invokes `git worktree add` and returns the worktree subdirectory path (not project_path). Confirms fix does NOT affect projects with their own `.git`.
- Evidence: `pytest_cross_project.txt` — 1 passed

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all Step 1 deliverables: `.git` detection check, in-place fallback log message, 3 new unit tests, 2026-05-03 type-fix preservation, commit message correctness. Ran targeted (90 pass) and full suite (193 pass, 1 pre-existing failure). Cross-project regression confirmed no impact on `.git`-having projects.

### Files Deposited
- `bellows/knowledge/qa/monorepo-worktree-fix-qa-2026-05-04.md` — this QA report
- `bellows/knowledge/qa/evidence/executable-monorepo-worktree-fix-2026-05-04/` — 7 evidence files

### Decisions Made
- Used Step 1's existing `test_create_worktree_proceeds_when_git_exists` as the cross-project regression smoke (already covers the contract: .git present -> worktree created)

### Flags for CEO
- None

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/executable-monorepo-worktree-fix-2026-05-04/
Files verified: 7
```
