# QA Report: lint-s4-hardening-2026-08-09

**Plan:** executable-332
**Step:** 2 (QA)
**Date:** 2026-08-09

---

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `scripts/plan_lint.py` | M2 cold-panel content check and M3 bounded-gap negation | ✅ | Lines 195-216 (M2) and line 232 (M3) match dev log before/after |
| `tests/test_plan_lint.py` | 13 new tests (8 M2 + 5 M3) | ✅ | 110 passed (97 baseline + 13 new) |
| `knowledge/development/lint-s4-hardening-dev-log-2026-08-09.md` | Output Receipt with PRE_EDIT_BLOB, fixture source text, before/after pairs, fold-side proof, test counts, live-run output | ✅ | All sections present and complete |

## Evidence and Narrative

### Task Q0 — Re-Pin Before Measuring

Last commit touching `scripts/plan_lint.py tests/test_plan_lint.py gates.py knowledge/development/lint-s4-hardening-dev-log-2026-08-09.md`:
```
97ece9a [332] Step 1: harden plan_lint §4 cold-panel content check (M2) and bounded-gap negation strip (M3)
```
Working tree status for those four paths: EMPTY (clean).

### Verification Table

| # | Claim | Status | Evidence |
|---|---|---|---|
| 1 | Full suite passes | ✅ | 928 passed, 1 warning in 24.08s |
| 2 | Targeted suite: count rose by new tests, no pre-existing test weakened | ✅ | 110 passed (97 baseline + 13 new), 818 deselected; no fixture edits reported in dev log |
| 3 | Sweep-diff: empty diff, both blob assertions hold | ✅ | DIFF: none; files_compared=1391; 0 crashes; CURRENT_BLOB (1cc8f69…) == STEP_1_COMMIT_BLOB and ≠ PRE_EDIT_BLOB (8288606…); gates.__file__ resolves under bellows for both streams; round 2 corpus root pins stable |
| 4 | Fold-side and message integrity (C3) | ✅ | Both fold-side tests byte-identical (content diff empty, line numbers shifted by M2 insertion); `grep -c -F -e "dry lens pass" scripts/plan_lint.py` = 2; test-file count = 19 (≥ 14 floor) |
| 5 | Regression direction from live fixtures | ✅ | M2 hollow bold: WARN; M2 hollow dash: WARN; M2 substantive bold: no WARN; M3 not-yet-dry: WARN; M3 no-longer-dry: WARN; M3 never-quite-dry: WARN; M3 legitimate dry at distance: no WARN; M3 adjacent not-dry: WARN; all EXIT=0 |
| 6 | WARN-only by mechanism (C1) | ✅ | Neither M2 nor M3 check regions contain `results` or `all_passed`; positive control confirms grep finds `results.append` in other checks; both WARNs fire on combined fixture, EXIT=0 |

### Sweep-Diff Detail

Round 1 pre/post pins showed a delta on `invoice-pulse` (concurrent activity: `5df7e85…` → `fd9b77f…`). Per plan instructions, re-pinned and re-ran the sweep. Round 2 bookend stable — all five roots identical pre and post sweep.

Pre-edit plan_lint materialized via `git cat-file -p 8288606eefe5a93720aa40017073aa4a52ca2f51`. Both streams ran via in-process import with `PYTHONPATH=/Users/marklehn/Developer/GitHub/bellows`, `PLAN_LINT_UNCAP=1`. gates.__file__ confirmed at `/Users/marklehn/Developer/GitHub/bellows/gates.py` for both streams.

### Fold-Side Detail (Row 4)

Primary fold-side test (line 231):
```python
has_fold = 'fold' in ll_lower
```

Legacy fallback (line 240):
```python
if 'fold' in closing_text and 'dry' not in closing_text:
```

Both byte-identical to pre-edit content (only line numbers shifted due to M2 code insertion above).

WARN message text in source: `grep -c -F -e "dry lens pass" scripts/plan_lint.py` = **2** (the two print sites).
WARN message text in tests: `grep -c -F -e "dry lens pass" tests/test_plan_lint.py` = **19** (≥ 14 floor).

### Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/332/knowledge/qa/evidence/lint-s4-hardening-2026-08-09/
Files verified: 3
```

## Output Receipt

- **PRE_EDIT_BLOB:** `8288606eefe5a93720aa40017073aa4a52ca2f51`
- **CURRENT_BLOB:** `1cc8f69dd3fb993b2f2b5ad32a76099bd5808754`
- **STEP_1_COMMIT_BLOB:** `1cc8f69dd3fb993b2f2b5ad32a76099bd5808754`
- **Full suite:** 928 passed, 1 warning
- **Targeted suite:** 110 passed (97 + 13 new), 818 deselected
- **Sweep-diff:** DIFF: none; files_compared=1391; 0 crashes
- **Fold-side:** both sites byte-identical; message count in source = 2
- **Fixture regression:** all 8 fixtures produce expected WARN/no-WARN with EXIT=0
- **WARN-only mechanism:** confirmed by grep; EXIT=0 on combined tripping fixture

### Ledger Updates

#### Forward Register

- DRAFTING_CYCLE.md §4 describes the T2 panel check as line-anchored-only and enumerates the negation strip as `not dry` / `no dry` / `never dry`; M2 and M3 changed both mechanics, so §4's descriptions are now understatements and owe a governance-root edit (deferred per §6's pair-or-defer-and-say).

- Row 25 remains OPEN and unchanged in scope; this plan attempted its check, measured it, and cut it. 1379 of 1390 corpus plans already emit at least 1 warning (99.2%) and exactly one declares, so the check would have fired approximately 1378 times against check (i)'s eleven; the newest-20 bellows rate is 15/20. Any successor must state its expected firing population as a MEASURED number before authoring. Note: row 25 is already open in bellows/knowledge/FORWARD.md; the Planner must consolidate this update into row 25 at wrap via the Rule 42 direct edit.

#### Prompt Feedback

None.
