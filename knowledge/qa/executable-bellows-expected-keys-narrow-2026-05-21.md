# QA Report — expected-keys warning narrow to pause_for_verdict only

**Date:** 2026-05-21
**Plan:** executable-bellows-expected-keys-narrow-2026-05-21
**Step:** 2 (QA)

---

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `bellows.py` no longer contains `expected_keys = {` | 0 grep matches | ✅ | `evidence/executable-bellows-expected-keys-narrow-2026-05-21/no_expected_keys.txt` |
| `bellows.py` contains new narrowed predicate | 1 grep match at line 416 | ✅ | `evidence/executable-bellows-expected-keys-narrow-2026-05-21/new_predicate.txt` |
| New warning message text present | 1 grep match at line 417 | ✅ | `evidence/executable-bellows-expected-keys-narrow-2026-05-21/new_warning_text.txt` |
| Sparse-header warning at line 383 unchanged | 1 grep match at line 383 | ✅ | `evidence/executable-bellows-expected-keys-narrow-2026-05-21/sparse_header_preserved.txt` |
| Dev log exists with required sections | File present with anchor/replacement/context/grep/authority sections | ✅ | `evidence/executable-bellows-expected-keys-narrow-2026-05-21/dev_log_present.txt` |
| `agent-prompt-feedback.md` has 2026-05-21 DEV entry | Entry present at line 6 | ✅ | `evidence/executable-bellows-expected-keys-narrow-2026-05-21/feedback_entry.txt` |

## Targeted Test Run

Initial run: 1 failure — `test_warning_multi_step_plan_without_pause_for_verdict` (test_bellows.py:2569) asserted against old warning text `"parsed header is missing"`. This is an expected failure: the test creates a sparse header where the defensive default inserts `pause_for_verdict` before the new check runs (Case 3 from the shape-choice diagnostic), so the narrowed warning correctly does NOT fire.

**Fix applied:** Updated assertion from positive match on old text to negative match confirming the narrowed warning does not fire when the defensive default already handled the key. Updated docstring to document Case 3 behavior. Committed separately as `test(bellows): update assertion for narrowed expected-keys warning`.

**Re-run result:** 116 passed, 0 failed. See `evidence/executable-bellows-expected-keys-narrow-2026-05-21/pytest_targeted.txt`.

## Structural Compliance Check

Diff of bellows.py change (commit `e2301f7`):

- Removed 4 lines at 416-419: `expected_keys` set, `missing_keys` computation, broad `if` check, and verbose `_log("WARN", ...)` message
- Added 2 lines: targeted `"pause_for_verdict" not in header` check and concise warning message
- No other modifications to bellows.py
- Line count: -4/+2 as expected

See `evidence/executable-bellows-expected-keys-narrow-2026-05-21/diff.txt`.

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-bellows-expected-keys-narrow-2026-05-21/
Files verified: 8
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all Step 1 (DEV) deliverables via grep-based evidence collection. Ran targeted pytest suite — identified and fixed one expected test assertion failure caused by the warning text change. Verified structural compliance of the bellows.py diff (-4/+2 lines). Executed Rule 20 self-check. Updated PROJECT_STATUS.md.

### Files Deposited
- `knowledge/qa/executable-bellows-expected-keys-narrow-2026-05-21.md` — this QA report
- `knowledge/qa/evidence/executable-bellows-expected-keys-narrow-2026-05-21/` — 8 evidence files

### Files Created or Modified (Code)
- `tests/test_bellows.py` — updated `test_warning_multi_step_plan_without_pause_for_verdict` assertion and docstring for narrowed warning behavior

### Decisions Made
- Updated test assertion to negative match (confirming warning does NOT fire) rather than positive match with new text, because the defensive default inserts `pause_for_verdict` before the check runs in the sparse-header scenario (Case 3)

### Flags for CEO
- None

### Flags for Next Step
- None
