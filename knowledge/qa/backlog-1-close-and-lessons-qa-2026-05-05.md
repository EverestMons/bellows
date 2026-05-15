# QA Report — BACKLOG #1 Close + Bellows-Self Constraint + Lessons Capture

**Plan:** `executable-backlog-1-close-and-lessons-2026-05-05`
**Date:** 2026-05-05
**Agent:** Bellows QA
**Step:** 2

## Verification Table

| # | Verification | Expected | Status | Evidence |
|---|---|---|---|---|
| 1 | BACKLOG #1 removal from Open | Zero matches in Open section; at most one match in Closed section (cross-reference) | ✅ | `knowledge/qa/evidence/executable-backlog-1-close-and-lessons-2026-05-05/grep_backlog_1_removal.txt` — 1 match at line 59 (Closed section, after `## Closed` at line 57). Zero matches in Open section (lines 7–56). |
| 2 | New Open entry exists | Exactly one match, before `## Closed` | ✅ | `knowledge/qa/evidence/executable-backlog-1-close-and-lessons-2026-05-05/grep_new_open_entry.txt` — 1 match at line 9 (Open section, between `## Open` at line 7 and `## Closed` at line 57). |
| 3 | New Closed entry exists | Exactly one match, after `## Closed` | ✅ | `knowledge/qa/evidence/executable-backlog-1-close-and-lessons-2026-05-05/grep_new_closed_entry.txt` — 2 matches: line 59 (new Closed entry, correct) and line 61 (pre-existing Closed entry cross-referencing "scope_check diff-collision" in body text). Both in Closed section. New entry at line 59 is the target; line 61 is an incidental pattern match on a cross-reference in an unrelated entry. |
| 4 | PLANNER_TEMPLATE version bump to 4.33 | Exactly one match for 4.33; zero matches for stale 4.32 | ✅ | `knowledge/qa/evidence/executable-backlog-1-close-and-lessons-2026-05-05/grep_planner_version.txt` — 1 match at line 5 for `**Version:** 4.33`. Stale 4.32 count: 0. |
| 5 | PLANNER_TEMPLATE Lessons row appended | Exactly one match for `2026-05-05.*hypothesis-from-memory` | ✅ | `knowledge/qa/evidence/executable-backlog-1-close-and-lessons-2026-05-05/grep_planner_lessons_row.txt` — 1 match at line 1257. |
| 6 | Split commit verification | bellows: `docs(backlog): close #1` commit exists; governance: `docs(planner): v4.33` is most recent | ✅ | `knowledge/qa/evidence/executable-backlog-1-close-and-lessons-2026-05-05/git_log_bellows.txt` — `56c26d4 docs(backlog): close #1` is second-most-recent (the later governance commit `1708ef4 docs(planner): v4.33` appears first because bellows/ shares the governance-root .git — monorepo structure, no separate bellows .git). `knowledge/qa/evidence/executable-backlog-1-close-and-lessons-2026-05-05/git_log_governance.txt` — `1708ef4 docs(planner): v4.33` is most recent. Both commits present in correct chronological order. |

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/executable-backlog-1-close-and-lessons-2026-05-05/
Files verified: 7
```
