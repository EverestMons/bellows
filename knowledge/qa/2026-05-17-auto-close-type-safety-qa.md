# QA Report: auto_close type-safety fix

**Date:** 2026-05-17
**Plan:** executable-auto-close-type-safety-qa-recovery-2026-05-17
**Agent:** Bellows QA
**Step:** 1
**DEV Commit:** 9e79e4d

---

## Verification Table

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Patch present in live source — `str(header.get("auto_close", "false")).lower() == "true"` at bellows.py:458 | ✅ | `grep_patch.txt` |
| 2 | Audit spot-check #2 — bellows.py:282 `pause_for_verdict` uses no `.lower()` on header value; compared via `==` against string literals | ✅ | `audit_spot_2.txt` |
| 3 | Audit spot-check #5 — gates.py:100 `.lower()` called on regex match group (always str), not `header.get()` | ✅ | `audit_spot_5.txt` |
| 4 | Audit spot-check #7 — gates.py:391 `.lower()` called on regex match group (always str), not `header.get()` | ✅ | `audit_spot_7.txt` |
| 5 | New tests run and pass — `test_auto_close_yaml_bool_does_not_crash` and `test_auto_close_yaml_bool_false` both PASSED | ✅ | `pytest_new_tests.txt` |
| 6 | Targeted suite passes — `pytest tests/test_bellows.py`: 106 passed, 0 failed | ✅ | `pytest_test_bellows.txt` |
| 7 | Commit 9e79e4d landed on main — confirmed in `git log --oneline -10` output | ✅ | `git_log.txt` |

---

## Reverse Repro (Check #6 from plan)

A Python REPL fixture confirmed:
- **OLD code** (`header.get("auto_close", "false").lower()` with `header = {"auto_close": True}`) raises `AttributeError: 'bool' object has no attribute 'lower'`.
- **NEW code** (`str(header.get("auto_close", "false")).lower()`) returns `"true"` cleanly with no exception.

Evidence: `bug_repro_verified.txt`

---

## Live Canary Check (Check #7 from plan)

This recovery plan (`executable-auto-close-type-safety-qa-recovery-2026-05-17`) uses bold-Markdown headers (`**Date:** 2026-05-17 | **Tier:** small | ...`), not YAML frontmatter. This was a deliberate choice by the Planner to avoid exercising the fixed code path (`str()` wrap on `header.get("auto_close")`) during the post-recovery dispatch. The bold-Markdown parser returns string values for all fields, so the `auto_close` header — if present — would already be a string, bypassing the bug entirely. By using the non-YAML format, this plan's dispatch cannot trigger the same crash that halted the original plan, making the recovery self-insulating.

---

## DEV Log Claim Verification

| DEV Log Claim | Verified |
|---|---|
| bellows.py:458 patched with `str()` wrap | Confirmed via grep (line 458 contains `str(header.get("auto_close", "false")).lower()`) |
| Full audit of 5 files, only 1 site needed fix | Spot-checked 3 of 9 "no fix needed" sites (#2, #5, #7); all dispositions accurate |
| 2 new tests added | Both tests exist and pass |
| pytest passed (106 in test_bellows.py) | Confirmed: 106 passed, 0 failed |
| Commit SHA 9e79e4d | Present in main history |

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/auto-close-type-safety-qa-recovery-2026-05-17/knowledge/qa/evidence/executable-auto-close-type-safety-qa-recovery-2026-05-17/
Files verified: 8
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 1
**Status:** Complete

### What Was Done
Verified the auto_close type-safety fix (commit 9e79e4d) across 7 verification checks: patch presence in live source, 3 audit disposition spot-checks, 2 new regression tests, full test_bellows.py suite (106 passed), commit presence in main history, reverse repro confirming the bug and fix, and live canary check documentation.

### Files Deposited
- `knowledge/qa/2026-05-17-auto-close-type-safety-qa.md` — this QA report
- `knowledge/qa/evidence/executable-auto-close-type-safety-qa-recovery-2026-05-17/grep_patch.txt` — grep output for patched line
- `knowledge/qa/evidence/executable-auto-close-type-safety-qa-recovery-2026-05-17/audit_spot_2.txt` — audit spot-check #2
- `knowledge/qa/evidence/executable-auto-close-type-safety-qa-recovery-2026-05-17/audit_spot_5.txt` — audit spot-check #5
- `knowledge/qa/evidence/executable-auto-close-type-safety-qa-recovery-2026-05-17/audit_spot_7.txt` — audit spot-check #7
- `knowledge/qa/evidence/executable-auto-close-type-safety-qa-recovery-2026-05-17/pytest_new_tests.txt` — 2 new test results
- `knowledge/qa/evidence/executable-auto-close-type-safety-qa-recovery-2026-05-17/pytest_test_bellows.txt` — full suite results
- `knowledge/qa/evidence/executable-auto-close-type-safety-qa-recovery-2026-05-17/git_log.txt` — git log confirming commit SHA
- `knowledge/qa/evidence/executable-auto-close-type-safety-qa-recovery-2026-05-17/bug_repro_verified.txt` — reverse repro output

### Files Created or Modified (Code)
- None

### Decisions Made
- Spot-checked audit items #2, #5, #7 (a representative sample of no-lower, regex-group-str, and regex-group-str dispositions); all three confirmed accurate

### Flags for CEO
- None

### Flags for Next Step
- None
