verdict: continue

**Final step. The import-validation guard SET is complete. Second clean QA gate in a row — the prohibitions held.**

## Verified — including the live migration by the Planner's own hand

All 11 gates PASS with **no Monitor denial and no scope_check failure** (222 and 223 both clean now that the three prohibitions live in the prompt). All **8 rows PASS**.

- **Row 1 (the IP trap) — Planner-confirmed on the REAL Mac DB:** `SELECT version` = **19**, and `fuel_bracket_structural_issues` exists. The migrate-EXISTING path fired on canonical data — the version bump defeated the init_db fast-path, exactly as the standing IP schema lesson requires.
- **Row 6 — telemetry clean before AND after the full suite.** Plan 222's isolation fix is holding under a fresh ~2240-test run; the wrap-time revert ritual stays retired.
- **Row 7 — `2240 passed, 2 failed`** (the CLAUDE.md pair). Planner-checked arithmetic: 2229 + 11 new = 2240 exactly. Zero regressions.
- The false-positive boundary (legitimate open-ended sentinel → zero issues; config-2 shape → flagged; contiguity ≠ overlap) was Planner-verified by direct call at Step 1.

## What this closes

**The import-validation guard set is complete:**
- 219 — same-floor conflict on the section-paste path
- 220/221 — extracted to a shared helper, wired into the JSON path too
- 223 — non-last sentinel + overlapping ranges, both paths, flag-for-review

Every malformed-bracket class the fuel arc surfaced (mid-table sentinel, floor-dedup drop, structural overlap) is now caught at import. The one remaining fast-follow — the resolution UI that surfaces `fuel_bracket_conflicts` + `fuel_bracket_structural_issues` for a human to resolve — is correctly deferred: no real issue records exist yet (they arise on the work machine during real imports).

## Remaining (not code)

CEO-side PDF work: the 5 missing-continuation configs + the 7/9 window re-check. And the Windows git-gc / OneDrive question.

Move the plan to `Done/`.
