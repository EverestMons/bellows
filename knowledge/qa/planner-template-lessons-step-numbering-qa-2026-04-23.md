# QA Report — PLANNER_TEMPLATE Lessons: Bellows Step Parser Is 1-Indexed

**Date:** 2026-05-01
**Plan:** executable-planner-template-lessons-step-numbering-2026-04-23
**Step:** 2 (QA Agent)

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `PLANNER_TEMPLATE.md` | New Lessons Learned row appended at line 1101 (now line 1235 after subsequent edits) | ✅ | `grep_new_row.txt` — exactly 1 match at line 1235 |
| `bellows/knowledge/development/planner-template-lessons-step-numbering-dev-log-2026-04-23.md` | Dev log deposited with anchor, new row, tail-read, and issues | ✅ | File exists, Status: Complete, all sections present |

## Verification Checks

### (1) Grep new row — `grep_new_row.txt`
**Result:** ✅ Exactly 1 match at line 1235. The phrase "Bellows' step parser is positional and 1-indexed" appears once in PLANNER_TEMPLATE.md.

### (2) Tail check — `tail_check.txt`
**Result:** ✅ The tail of PLANNER_TEMPLATE.md shows the end of the Forge Observations table (lines from 2026-03-25 through 2026-03-27). The Lessons Learned table ends at line 1239 (2026-05-01 entries added after this plan's row), followed by `---` at line 1241 and the Forge Observations section. The 2026-04-23 row is properly positioned within the Lessons Learned table at line 1235, immediately after the anchor row at line 1234. No orphan rows between the new row and the anchor.

### (3) Anchor preserved — `grep_anchor_preserved.txt`
**Result:** ✅ Count = 1. The v4.26 governance sweep anchor row is present and intact.

### (4) Version check — `grep_version.txt`
**Result:** ✅ Version is 4.29. The plan expected 4.26, but subsequent governance changes (v4.27–v4.29) have incremented the version since this plan was authored. The Lessons row addition itself did not bump the version (correct per plan context: "No version bump — Lessons additions don't force a version increment").

### (5) Git commit — `git_commit.txt`
**Result:** ✅ The original Step 1 commit exists in history as `daa30a8 docs: agent prompt feedback for planner-template-lessons Step 1 (Documentation Analyst)`. The most recent commit (`4741765`) is a subsequent QA close. Both PLANNER_TEMPLATE.md and the dev log were committed.

## Rule 20 Self-Check Output

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/executable-planner-template-lessons-step-numbering-2026-04-23/
Files verified: 5
```
