# Dev Log — Rule 26 Evidence Path Fix

**Date:** 2026-05-11
**Plan:** executable-rule-26-evidence-path-fix-2026-05-11
**Step:** 1
**Agent:** Documentation Analyst

---

## Edits Applied

### Edit 1 — Version bump (line 5-6)
- `4.36` → `4.37`
- `2026-05-10 (v4.36)` → `2026-05-11 (v4.37)`

### Edit 2 — Rule 26 evidence-file guidance tightening (line 695)
- Changed "do NOT need individual bullets" → "MUST be represented by the evidence directory as a single bullet"
- Added explicit prohibition on individual evidence-file bullets
- Added rationale: bare `evidence/<file>` paths don't resolve, directory+children is redundant
- Added gate acceptance note: `os.path.isfile() or os.path.isdir()` at every strategy

### Edit 3 — Three new Lessons rows (after line 1220)
- Row 1: Stale-lesson retraction (2026-04-19 `isfile()`-only claim invalidated by commit `e609ad3`)
- Row 2: Cause 5 capture (18 gate failures from bare evidence paths, Rule 26 language fix)
- Row 3: Diagnostic-before-executable discipline win (canary caught contradiction pre-ship)

---

## Verification Grep Output

```
grep -c "Version:.*4.37"                                            → 1
grep -c "MUST be represented by the evidence directory"             → 1
grep -c "Do NOT list individual evidence files"                     → 1
grep -c "is \*\*stale\*\*. Commit"                                  → 1
grep -c "Cause 5 — plan-agent evidence path convention mismatch"    → 1
grep -c "Pre-executable scan-for-contradictions caught a stale rule" → 1
```

All 6 checks returned exactly 1. No failures.

---

## Adaptation Notes

The plan was authored against PLANNER_TEMPLATE.md v4.34 (line 738 anchor). The file
had advanced to v4.36 with an additional Lessons row at line 1220 (Rule 20
single-source migration, 2026-05-10). Adaptations made:

- Edit 1: bumped 4.36 → 4.37 (not 4.34 → 4.35)
- Edit 2: anchor found at line 695 (not 738) — content identical, only line number shifted
- Edit 3: anchor adapted from `matches. |` (line 1219) to `was 30%. |` (line 1220, the actual last Lessons row)

---

## Commit

**Repo:** governance-root (`/Users/marklehn/Desktop/GitHub/`)
**SHA:** 75904fd
**Message:** `docs(planner): Rule 26 evidence-path tightening, v4.37`
