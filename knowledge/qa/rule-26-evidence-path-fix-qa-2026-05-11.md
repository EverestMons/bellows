# QA Report — Rule 26 Evidence Path Fix

**Date:** 2026-05-11
**Plan:** executable-rule-26-evidence-path-fix-2026-05-11
**Step:** 2
**Agent:** Bellows QA

---

## Summary

Verified that Step 1's three edits to PLANNER_TEMPLATE.md landed correctly: version bump to v4.37 (adapted from plan's v4.35 due to file drift), Rule 26 evidence-file guidance tightening at line 695, and three new Lessons rows at lines 1221-1223. All 8 grep and structural checks pass. The governance-root commit `75904fd` is the most recent PLANNER_TEMPLATE.md entry in `git log`. No hedging, no structural damage to the Lessons table, no unbalanced code fences.

---

## Results

| # | Check | Result |
|---|---|---|
| 1 | Version bumped to 4.37 | ✅ |
| 2 | Tightened guidance ("MUST be represented by the evidence directory") present at line 695 | ✅ |
| 3 | Explicit prohibition ("Do NOT list individual evidence files") present at line 695 | ✅ |
| 4 | Stale-lesson retraction row (Row A) landed at line 1221 | ✅ |
| 5 | Cause 5 capture row (Row B) landed at line 1222 | ✅ |
| 6 | Diagnostic-before-executable discipline win row (Row C) landed at line 1223 | ✅ |
| 7 | Markdown wellformedness: code fences balanced, Lessons table intact | ✅ |
| 8 | Governance-root commit `75904fd` is top entry in git log | ✅ |

---

## Adaptation Note

Step 1 adapted the plan's anchors to the current file state (v4.36 at execution time, not v4.34 as plan authored). QA verified against the actual version (4.37) and actual line numbers (695, 1221-1223). The dev log at `bellows/knowledge/development/rule-26-evidence-path-fix-dev-log-2026-05-11.md` documents all adaptations.

---

## Evidence Files

| File | Check | Content |
|---|---|---|
| `grep_version.txt` | 1 | 1 match: line 5 |
| `grep_tightened_guidance.txt` | 2 | 1 match: line 695 |
| `grep_prohibition.txt` | 3 | 1 match: line 695 |
| `grep_stale_lesson_retraction.txt` | 4 | 1 match: line 1221 |
| `grep_cause_5_lesson.txt` | 5 | 1 match: line 1222 |
| `grep_discipline_win_lesson.txt` | 6 | 1 match: line 1223 |
| `markdown_wellformed.txt` | 7 | PASS |
| `git_log.txt` | 8 | `75904fd` is top entry |

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/rule-26-evidence-path-fix-2026-05-11/
Files verified: 8
```

