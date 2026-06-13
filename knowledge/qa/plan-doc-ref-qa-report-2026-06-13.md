# QA Report — plan_doc_ref Column (Plan #37, Step 2)

**Date:** 2026-06-13
**Agent:** Bellows QA
**Plan:** Store the Plan Document Path on plans (plan_doc_ref)
**Step:** 2 (QA)
**Receipt Flag:** DAEMON RESTART REQUIRED — the migration runs at next startup; live canary is the next claimed plan showing `plan_doc_ref` populated through its claim→close transitions.

---

## Verification Table

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Full suite — 597 passed, 0 failures, 11 new tests match dev log | ✅ | [full_suite_tail.txt](evidence/plan-doc-ref-2026-06-13/full_suite_tail.txt) |
| 2 | Column present + populated — all 37 rows have plan_doc_ref; closed→Done/, halted→halted-, in_progress→in-progress-; spot-check executable-36.md exists on disk | ✅ | [column_populated.txt](evidence/plan-doc-ref-2026-06-13/column_populated.txt) |
| 3 | Writer covers all transitions — 5 callsites (claim/auto-close/halt/continue-to-done/stop) + 2 recovery paths pass plan_doc_ref | ✅ | [write_sites.txt](evidence/plan-doc-ref-2026-06-13/write_sites.txt) |
| 4 | Backfill accounting — dev log says 37/0, live DB confirms 37 populated / 0 NULL | ✅ | [backfill_check.txt](evidence/plan-doc-ref-2026-06-13/backfill_check.txt) |
| 5 | Migration idempotent — re-running init_lifecycle_db() twice produces no error, column still present | ✅ | [migration_idempotent.txt](evidence/plan-doc-ref-2026-06-13/migration_idempotent.txt) |
| 6 | FORWARD row #22 appended — Forge reporter should prefer stored plan_doc_ref over derivation | ✅ | [forward_followup.txt](evidence/plan-doc-ref-2026-06-13/forward_followup.txt) |

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/37/knowledge/qa/evidence/plan-doc-ref-2026-06-13/
Files verified: 6
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 6 QA checks for the plan_doc_ref feature: full suite pass (597/0), column populated on all 37 rows, writer coverage at all 5 state-transition sites + 2 recovery paths, backfill accounting match, migration idempotency, and FORWARD row #22 for the Forge reader follow-up.

### Files Deposited
- knowledge/qa/plan-doc-ref-qa-report-2026-06-13.md — this QA report
- knowledge/qa/evidence/plan-doc-ref-2026-06-13/ — 6 evidence files per Rule 20 self-check

### Files Created or Modified (Code)
- knowledge/FORWARD.md — appended row #22 (Forge reader follow-up)

### Decisions Made
- Spot-checked executable-36.md (closed row) to confirm file existence on disk — representative sample

### Flags for CEO
- DAEMON RESTART REQUIRED — the migration runs at next startup; live canary is the next claimed plan showing plan_doc_ref populated through its claim→close transitions

### Flags for Next Step
- None
