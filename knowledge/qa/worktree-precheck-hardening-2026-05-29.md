# QA Report — Worktree & Dirty-Tree Pre-Check Hardening

**Date:** 2026-05-29
**Plan:** executable-worktree-precheck-hardening-2026-05-29
**Step:** 2 (QA)

---

## DEV Output Receipt Status

**Status:** Complete
**Source:** `knowledge/development/worktree-precheck-hardening-2026-05-29.md`
No blocker — proceeding with QA verification.

---

## Deliverable Verification (Rule 17)

| # | Deliverable | Expected | Status | Evidence |
|---|---|---|---|---|
| 1 | Item a — stranded-worktree cleanup present | `_create_worktree` contains existence guard with `git worktree remove --force` + `shutil.rmtree` + `git worktree prune` + WARN log, positioned after mkdir and before `git worktree add` | ✅ | `evidence/create_worktree_cleanup.txt` |
| 2 | Item a — WARN string present | `grep -n "stranded worktree found" bellows.py` returns at least 1 hit | ✅ | `evidence/item_a_warn_grep.txt` |
| 3 | Item f — rstrip in pre-check | Pre-check uses `.rstrip()` not `.strip()` on porcelain result | ✅ | `evidence/item_f_rstrip.txt` |
| 4 | Item f — leading-space tolerance | `_is_lifecycle_artifact` handles space-prefixed porcelain lines via `porcelain_line[3:]` extraction | ✅ | `evidence/item_f_predicate.txt` |
| 5 | Item g — `.bellows-worktrees/` ignore | `_LIFECYCLE_IGNORE_RE` contains `.bellows-worktrees` pattern in ignore logic (not just comment/test) | ✅ | `evidence/item_g_ignore.txt` |
| 6 | Item g — no fixture/.gitignore change | `git diff HEAD~2 HEAD --stat` shows no fixture or .gitignore modifications; fix is in pre-check logic only | ✅ | `evidence/item_g_no_fixture_change.txt` |
| 7 | Regression tests exist | 4 new test functions found in `tests/test_worktree.py` | ✅ | `evidence/new_tests_grep.txt` |
| 8 | Dev log complete | Three change sections with before/after, pre-edit verification, both pytest runs, anchor verification, Output Receipt | ✅ | `evidence/dev_log_check.txt` |

All deliverables verified. No blockers.

---

## Test Execution

**Command:** `python3 -m pytest tests/ -v 2>&1 | tail -160`
**Result:** 432 passed, 5 failed, 1 warning in 6.61s
**Evidence:** `evidence/pytest_full.txt`

### Previously-failing worktree tests now PASS

| Test | Status |
|---|---|
| `test_teardown_removes_worktree_directory` | PASSED |
| `test_teardown_cherry_picks_commits` | PASSED |
| `test_teardown_copies_uncommitted_files` | PASSED |

### New regression tests all PASS

| Test | Item | Status |
|---|---|---|
| `test_create_worktree_cleans_stranded_directory` | a | PASSED |
| `test_create_worktree_cleans_stranded_registered_worktree` | a | PASSED |
| `test_pre_check_recognizes_space_prefixed_lifecycle_line` | f | PASSED |
| `test_pre_check_ignores_bellows_worktrees_dir` | g | PASSED |

### Remaining failures (all pre-existing carry-over)

- `test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file` — phrase file not found (pre-existing)
- `test_decisions.py::TestLoadPhrases::test_includes_known_phrases` — phrase file not found (pre-existing)
- `test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives` — phrase file not found (pre-existing)
- `test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth` — phrase file not found (pre-existing)
- `test_runner_parser.py::test_run_step_timeout` — pre-existing

**Zero new failures.** Total pass count matches DEV's post-edit report (432).

---

## Structural-Compliance Checks

### (a) Blocking behavior preserved

The dirty-tree pre-check still raises `WorktreeTeardownError` on genuine uncommitted changes. Filter-negative tests are green:

- `test_teardown_aborts_on_cherry_pick_conflict` — PASSED
- Negative controls in new regression tests (`" M README.md"` returns False, `"?? src/untracked.py"` returns False) — all PASSED

No filter-negative tests were weakened or removed. No safety regression detected.
**Evidence:** `evidence/blocking_preserved.txt`

### (b) Item a scope & symmetry

Item a's change is bounded to `_create_worktree`. Subprocess invocation mirrors `Bellows.__init__` startup-prune style:
- Both use `["git", "--no-pager", ...]` with `capture_output=True, text=True, timeout=10`
- Both wrap in `try/except Exception`
- Minor divergence: `__init__` logs on exception; `_create_worktree` silently passes (acceptable — path may not be a registered worktree, so failure is expected)

**Evidence:** `evidence/item_a_symmetry.txt`

### (c) Item g pattern anchoring

Pattern `^\.bellows-worktrees(/|$)`:
- `^` anchor: matches only at path start
- `\.` literal dot: prevents matching without leading dot
- `(/|$)` alternation: matches directory or bare entry only, not substrings like `.bellows-worktreesfoo`
- Confirmed by test negative control: `"?? bellows-worktrees-imposter/foo.py"` returns False

**Evidence:** `evidence/item_g_anchor.txt`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/worktree-precheck-hardening-2026-05-29/
Files verified: 12
```

---

## Flags for CEO

REMINDER: restart the Bellows daemon to activate (a) stranded-worktree cleanup in `_create_worktree`, (f) the `rstrip()` + leading-space pre-check tolerance, and (g) `.bellows-worktrees/` lifecycle-ignore. The running daemon executed this plan with pre-edit code; the three fixes activate on the next plan dispatched after restart.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all three DEV hardening changes (stranded-worktree cleanup, rstrip tolerance, .bellows-worktrees/ ignore) via deliverable verification table, full-suite test execution (432 passed, 5 pre-existing failures), structural-compliance checks (blocking behavior preserved, subprocess symmetry confirmed, pattern anchoring verified), and Rule 20 self-check.

### Files Deposited
- `knowledge/qa/worktree-precheck-hardening-2026-05-29.md` — this QA report
- `knowledge/qa/evidence/worktree-precheck-hardening-2026-05-29/` — 12 evidence files

### Files Created or Modified (Code)
- `PROJECT_STATUS.md` — prepended 2026-05-29 Completed entry

### Decisions Made
- Accepted minor subprocess-pattern divergence in item a (silent pass vs. logged exception) as intentional and appropriate

### Flags for CEO
- REMINDER: restart the Bellows daemon to activate (a) stranded-worktree cleanup in `_create_worktree`, (f) the `rstrip()` + leading-space pre-check tolerance, and (g) `.bellows-worktrees/` lifecycle-ignore. The running daemon executed this plan with pre-edit code; the three fixes activate on the next plan dispatched after restart.

### Flags for Next Step
- None
