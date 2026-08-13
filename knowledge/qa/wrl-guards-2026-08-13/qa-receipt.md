# QA Receipt — wrl-guards-2026-08-13 (Plan 392, Step 2)

**CAPTURE_COMMIT:** `a38801b`
**Precondition:** Step 1 commit `a38801b` exists on `scripts/walk_register_lint.py`, made by a prior dispatch — independence satisfied.
**Worktree root:** `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/392`

---

## Deliverable Verification

| Item | Check | Status | Evidence |
|------|-------|--------|----------|
| 1 | Task C probe battery re-run against CAPTURE_COMMIT extractions: v0.3 header=1, v0.3 section=1, v0.2 retired=0, VERBATIM_ELLIPSIS_MARKER=2, _structural_guards=3, test_headerless def=1, targeted tests 27 passed 0 failures, corpus sweep truncated_pre_fold_text=39 headerless_rows=46 duplicate_row=0 duplicate_adjacent_line=0 | ✅ | probes-raw.txt |
| 2 | C1 byte-identity: validator diff_exit=0, tests diff_exit=0, builder porcelain empty, builder last commit 7c933ad (non-empty), builder output OK, schema committed vs builder-from-pre-edit diff_exit=0 | ✅ | probes-raw.txt |
| 3 | C4 numstat: schema 18/2, dev-note 60/0, validator 88/4, tests 99/0; toplevel printed; one parent; subject matches Task D form | ✅ | probes-raw.txt |
| 4 | Full suite: 1025 passed, 0 failed in 26.74s (DELTA NOTE: Item 4 text says 1024 = 1017+7, header says 1025 = 1017+8; actual 1025 matches header authoring-time measurement); sweep tally matches Step 1 dev note exactly (39/46/0/0); register porcelain clean (no dirty registers) | ✅ | probes-raw.txt |
| 5 | Gate-neutrality: verbatim_ellipsis_annotated 0 in plan_lint.py and gates.py; headerless_rows 0 in both; duplicate_adjacent_line 0 in both; positive control Drafting Cycle in plan_lint.py = 11 | ✅ | probes-raw.txt |
| 6 | Raw output captured throughout in probes-raw.txt | ✅ | probes-raw.txt |

---

## Full Suite Delta

Plan header expected **1025 passed / 0 failed**. Item 4 body text stated 1024 (arithmetic: 1017 + 7 = 1024, but the plan ships 8 new tests: 19→27 targeted = +8, so 1017 + 8 = 1025). Actual result: **1025 passed, 0 failed**. Matches the header's authoring-time measurement. The body's "7" appears to be an arithmetic slip (the commit message also says "7 tests" but 8 new test functions exist in the diff).

## Corpus Sweep Tally Comparison

| Note | Step 1 | QA Re-run | Delta |
|------|--------|-----------|-------|
| truncated_pre_fold_text | 39 | 39 | 0 |
| headerless_rows | 46 | 46 | 0 |
| duplicate_row | 0 | 0 | 0 |
| duplicate_adjacent_line | 0 | 0 | 0 |

No delta within the ten named files.

---

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/392/knowledge/qa/wrl-guards-2026-08-13/
Files verified: 2
