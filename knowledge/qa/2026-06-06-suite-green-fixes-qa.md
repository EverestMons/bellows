# Suite-Green Fixes — QA Report
**Date:** 2026-06-06 | **Agent:** Bellows QA | **Step:** 3

---

## Verification Table

| Check | Expected | Status | Evidence |
|-------|----------|--------|----------|
| (1) Full suite GREEN (Rule 21) | 448 passed, 0 failed | ✅ | `pytest_full.txt` — `448 passed, 1 warning in 6.60s` |
| (2) 5 formerly-red tests pass | All 5 PASSED | ✅ | `formerly_red.txt` — 7 collected, 7 passed (5 target + 2 additional TestLoadPhrases members) |
| (3) Worktree resolution | GOVERNANCE_ROOT resolves to governance root; load_phrases() returns non-empty list | ✅ | `worktree_resolution.txt` — GOVERNANCE_ROOT=/Users/marklehn/Developer/GitHub, COMPANY.md exists: True, load_phrases() count: 44 |

---

## Check Details

### (1) Full Suite GREEN

```
448 passed, 1 warning in 6.60s
```

0 failures. Suite is fully green.

### (2) Formerly-Red Tests

All 5 target tests pass:

| Test | Status |
|------|--------|
| `test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file` | PASSED |
| `test_decisions.py::TestLoadPhrases::test_includes_known_phrases` | PASSED |
| `test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives` | PASSED |
| `test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth` | PASSED |
| `test_runner_parser.py::test_run_step_timeout` | PASSED |

### (3) Worktree Resolution

Running from worktree path `bellows/.bellows-worktrees/bellows-suite-green-fixes-2026-06-06/`:

- `GOVERNANCE_ROOT`: `/Users/marklehn/Developer/GitHub`
- `COMPANY.md` exists at governance root: True
- `PHRASES_FILE`: `/Users/marklehn/Developer/GitHub/INTERMEDIATE_DECISION_PHRASES.md` (exists: True)
- `load_phrases()` returns 44 phrases
- `decisions.__file__`: confirms module loaded from worktree path

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/bellows-suite-green-fixes-2026-06-06/knowledge/qa/evidence/executable-bellows-suite-green-fixes-2026-06-06/
Files verified: 3
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 3
**Status:** Complete

### What Was Done
Executed full QA regression for suite-green fixes: verified 448/0 suite count, confirmed all 5 formerly-red tests pass, validated worktree resolution of GOVERNANCE_ROOT, and ran Rule 20 self-check.

### Files Deposited
- `knowledge/qa/2026-06-06-suite-green-fixes-qa.md` — this QA report
- `knowledge/qa/evidence/executable-bellows-suite-green-fixes-2026-06-06/pytest_full.txt` — full suite output
- `knowledge/qa/evidence/executable-bellows-suite-green-fixes-2026-06-06/formerly_red.txt` — formerly-red tests output
- `knowledge/qa/evidence/executable-bellows-suite-green-fixes-2026-06-06/worktree_resolution.txt` — worktree resolution verification

### Files Created or Modified (Code)
- None (QA step — no source changes)

### Decisions Made
- All checks passed; no deviations from expected outcomes

### Flags for CEO
- None

### Flags for Next Step
- None
