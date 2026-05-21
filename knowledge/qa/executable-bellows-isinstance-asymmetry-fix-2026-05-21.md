# QA Report — isinstance Asymmetry Fix at bellows.py:594

**Date:** 2026-05-21
**Plan:** executable-bellows-isinstance-asymmetry-fix-2026-05-21
**Step:** 2 (QA)
**Agent:** Bellows QA
**Test Scope:** targeted

---

## Deliverable Verification (Rule 17)

| # | Deliverable | Expected | Status | Evidence |
|---|---|---|---|---|
| 1 | `bellows.py:594` has new pattern | `isinstance(f, dict) and f.get("gate") == "rule_22_verification"` at line 594 | ✅ | `line_594.txt` |
| 2 | `bellows.py:505` unchanged | Same pattern at line 505 | ✅ | `line_505.txt` |
| 3 | New pattern occurrence count | Exactly 2 | ✅ | `new_pattern_count.txt` |
| 4 | Old pattern occurrence count | Exactly 0 | ✅ | `old_pattern_count.txt` |
| 5 | Dev log exists | `knowledge/development/bellows-isinstance-asymmetry-fix-2026-05-21.md` present, non-empty, with before/after snippets and diagnostic citation | ✅ | `dev_log_present.txt` |
| 6 | Prompt feedback entry | 2026-05-21 entry in `agent-prompt-feedback.md` | ✅ | `feedback_entry.txt` |

---

## Targeted Test Run

**Command:** `python3 -m pytest tests/test_bellows.py -v`
**Result:** 116 passed, 0 failed, 1 warning (urllib3 SSL warning, unrelated)
**Evidence:** `pytest_targeted.txt`

The change is purely defensive (adds `isinstance(f, dict)` guard without changing behavior on dict inputs). All 116 tests pass unchanged.

---

## Structural Compliance Check

**Command:** `git diff 6fdda11~1 6fdda11 -- bellows.py`
**Result:** Exactly 1 line removed, 1 line added, at line 594. No other modifications to bellows.py.
**Evidence:** `diff.txt`

Diff summary:
- Removed: `if all(f["gate"] == "rule_22_verification" for f in gate_result["failures"]):`
- Added: `if all(isinstance(f, dict) and f.get("gate") == "rule_22_verification" for f in gate_result["failures"]):`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-bellows-isinstance-asymmetry-fix-2026-05-21/
Files verified: 8
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 6 deliverables from Step 1 (DEV). Ran targeted pytest (116/116 pass). Confirmed structural compliance via git diff (exactly 1 line changed at line 594). Ran Rule 20 self-check. Updated PROJECT_STATUS.md.

### Files Deposited
- `knowledge/qa/executable-bellows-isinstance-asymmetry-fix-2026-05-21.md` — this QA report
- `knowledge/qa/evidence/executable-bellows-isinstance-asymmetry-fix-2026-05-21/` — 8 evidence files

### Files Created or Modified (Code)
- `PROJECT_STATUS.md` — prepended 2026-05-21 completed entry

### Decisions Made
- None beyond plan specification (fully mechanical QA verification)

### Flags for CEO
- None

### Flags for Next Step
- None
