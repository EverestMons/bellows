# QA Report — Rename-first ordering at all 4 pause sites

**Plan:** `executable-rename-first-ordering-2026-05-24`
**Step:** 2 (QA)
**Date:** 2026-05-25
**DEV Commit:** `10b5fc3` (`fix(bellows): rename-first ordering at all 4 pause sites — closes RV-1 boundary (items #2, #3)`)
**Prompt-feedback Commit:** `1385d3f` (`docs: prompt feedback — bellows DEV rename-first ordering`)

---

## Deliverable Verification (Rule 17)

| # | Deliverable | Expected | Status | Evidence |
|---|---|---|---|---|
| 1 | Rename-first comments in bellows.py | `grep -c` returns 4 | ✅ | `rename_first_comments_count.txt` |
| 2 | verdict.post_verdict_request call count | `grep -c` returns 4 | ✅ | `post_verdict_count.txt` |
| 3a | Site 1 ordering (worktree-creation failure) | rename block BEFORE verdict.post_verdict_request | ✅ | `site_1_ordering.txt` |
| 3b | Site 2 ordering (intermediate-step gate_failure) | rename block BEFORE verdict.post_verdict_request | ✅ | `site_2_ordering.txt` |
| 3c | Site 3 ordering (final-step gate_failure) | rename block BEFORE verdict.post_verdict_request | ✅ | `site_3_ordering.txt` |
| 3d | Site 4 ordering (auto-close-failure) | rename block BEFORE verdict.post_verdict_request | ✅ | `site_4_ordering.txt` |
| 4 | Import smoke test | `python3 -c "import bellows"` exits cleanly | ✅ | `import_smoke.txt` |
| 5 | 4 new test functions present | `grep -n 'def test_pause_site_'` returns 4 | ✅ | `new_tests_present.txt` |
| 6 | Dev log with sections (a)-(f) + Output Receipt | All 6 documentation items present | ✅ | `dev_log_present.txt` |
| 7 | agent-prompt-feedback.md has 2026-05-25 DEV entry | Entry present for rename-first-ordering | ✅ | `feedback_entry.txt` |

---

## Site Ordering Verification Detail

**Site 1 (worktree-creation failure, ~line 437):** Diff shows `verdict_pending_path = os.path.join(...)` and `shutil.move(inprogress_path, verdict_pending_path)` appear BEFORE `verdict.post_verdict_request(...)`. New 2-line RV-1 closure comment precedes the rename block. Confirmed correct.

**Site 2 (intermediate-step gate_failure, ~line 519):** Diff shows the old `# Rename plan to verdict-pending` comment and rename block (3 lines) removed from AFTER `verdict.post_verdict_request`, and new RV-1 closure comment + rename block (5 lines) added BEFORE it. `notifier.notify_verdict_request` stays after `verdict.post_verdict_request`. `record_run` stays at end. Confirmed correct.

**Site 3 (final-step gate_failure, ~line 611):** Diff shows rename block (3 lines) removed from AFTER `verdict.post_verdict_request`, new RV-1 closure comment + rename block (5 lines) added BEFORE it. Same structural pattern as Site 2. Confirmed correct.

**Site 4 (auto-close-failure, ~line 642):** Diff shows `verdict.post_verdict_request(...)` (2 lines) removed from BEFORE the rename block, new RV-1 closure comment (2 lines) added before rename block, `verdict.post_verdict_request(...)` (2 lines) added AFTER the rename block. Confirmed correct.

---

## Full Pytest Suite (Test Scope: full)

```
390 collected, 385 passed, 5 failed, 1 warning in 6.58s
```

**Failures (all pre-existing carry-overs):**
- `tests/test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file` — worktree artifact (missing INTERMEDIATE_DECISION_PHRASES.md)
- `tests/test_decisions.py::TestLoadPhrases::test_includes_known_phrases` — worktree artifact
- `tests/test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives` — worktree artifact
- `tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth` — worktree artifact
- `tests/test_runner_parser.py::test_run_step_timeout` — pre-existing carry-over

**4 new `test_pause_site_*` tests:** All PASSED. No skips.

**No new regressions.**

---

## Structural Compliance Check

**DEV commit stat (`git show --stat 10b5fc3`):**
```
 bellows.py                                         |  29 +--
 .../rename-first-ordering-2026-05-24.md            | 209 +++++++++++++++++++++
 tests/test_bellows.py                              | 202 ++++++++++++++++++++
 3 files changed, 429 insertions(+), 11 deletions(-)
```

Exactly 3 paths: `bellows.py`, `knowledge/development/rename-first-ordering-2026-05-24.md`, `tests/test_bellows.py`. Confirmed correct.

**Diff balance (bellows.py):** 18 insertions, 11 deletions. Net +7 lines. Breakdown:
- 4 sites x 2-line RV-1 closure comment = +8 comment lines
- Site 2: removed old `# Rename plan to verdict-pending` comment = -1 comment line
- All `verdict.post_verdict_request(...)` and `shutil.move(...)` lines are reordered, not added/deleted
- No additions or deletions of substantive logic. Only reordering + comments. Confirmed correct.

---

## Rule 20 Self-Check

**Output:**
```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-rename-first-ordering-2026-05-24/
Files verified: 13
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified rename-first ordering at all 4 pause sites in bellows.py, confirmed 4 new regression tests pass, ran full pytest suite (385 passed, 5 pre-existing carry-over failures, 0 new regressions), validated structural compliance of the DEV commit, and executed Rule 20 self-check.

### Files Deposited
- `knowledge/qa/executable-rename-first-ordering-2026-05-24.md` — this QA report
- `knowledge/qa/evidence/executable-rename-first-ordering-2026-05-24/` — 13 evidence files

### Files Created or Modified (Code)
- `PROJECT_STATUS.md` — prepended 2026-05-25 Completed entry for rename-first ordering

### Decisions Made
- Used `python3 -m pytest` instead of `pytest` (macOS worktree environment has `python3` only)
- Site anchor grep patterns adapted to match diff output format (awk-based section extraction for sites 2-4)

### Flags for CEO
- None

### Flags for Next Step
- None
