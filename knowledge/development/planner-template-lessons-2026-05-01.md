# Dev Log — PLANNER_TEMPLATE Lessons 2026-05-01

**Plan:** `executable-planner-template-lessons-2026-05-01`
**Step:** 1 (Documentation Analyst)
**Date:** 2026-05-01

## Summary

Added two new Lessons Learned entries to the bottom of the Lessons Learned table in `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` (v4.29).

### Entry 1 — Diagnostic verification end-to-end thought-experiment
- **Line:** 1238
- **Topic:** Rule 22 verification of a diagnostic's recommendation must include end-to-end thought-experiment of the proposed fix against the actual observed bug pattern, not categorical mapping. Derived from the failed close on the parallel-plan scope_check fix (file-checksum snapshot reverted via `executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01`).

### Entry 2 — Test naming vs assertion mismatch
- **Line:** 1239
- **Topic:** Test names that imply a property must have assertions that verify that property. Derived from `test_diff_immune_to_sibling_changes_in_unrelated_files` passing when the named property was violated.

## Commit

- **Repo:** `/Users/marklehn/Desktop/GitHub/` (governance root)
- **SHA:** `8006e3e`
- **Message:** `docs(planner): add 2026-05-01 lessons — diagnostic verification + test naming`

## Output Receipt

- **Status:** Complete
- **Deposits:**
  - `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` (2 rows added to Lessons Learned table)
  - `bellows/knowledge/development/planner-template-lessons-2026-05-01.md` (this file)
