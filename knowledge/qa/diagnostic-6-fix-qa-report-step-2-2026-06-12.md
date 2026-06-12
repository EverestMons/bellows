# QA Report — Diagnostic 6 Fix Verification (Step 2: Live Resume Canary)

**Date:** 2026-06-12
**Plan ID:** 7
**Step:** 2 of 2
**Agent:** Bellows QA
**Fix Commit:** `2df6d91`
**Derived Plan ID:** 7 (parsed from plan filename `executable-7.md.pristine`; confirmed by `[7]` commit tag in Step 1)

---

## Context

This is Step 2 of a 2-step QA plan. Step 1 verified the diagnostic-6 fix code is present and the test suite is green. This step was dispatched via the post-verdict RESUME path — the exact path the fix (commit `2df6d91`) repaired. The verification checks below confirm, live and from inside the resumed run, that the daemon's lifecycle DB writes happened correctly.

---

## Verification Table

| # | Item | Method | Evidence File | Result |
|---|------|--------|---------------|--------|
| 1 | Plans row exists with type='executable', total_steps=2 | `SELECT id, type, lifecycle_state, total_steps FROM plans WHERE id = 7` | `db_plan_row.txt` | PASS |
| 2 | Derivations lineage: executable_id=7, diagnostic_id=6 | `SELECT executable_id, diagnostic_id FROM derivations WHERE executable_id = 7` | `db_derivations.txt` | PASS |
| 3 | Step-1 end data: status='complete', turns=25 (NOT NULL), cost_usd=0.634 (NOT NULL) | `SELECT step_number, status, cost_usd, turns, duration_s FROM steps WHERE plan_id = 7 AND step_number = 1` | `db_step1_row.txt` | PASS |
| 4 | Step-2 row exists: status='running' (G1 headline check) | `SELECT step_number, status, step_started_at FROM steps WHERE plan_id = 7 AND step_number = 2` | `db_step2_row.txt` | PASS |
| 5 | [7] commit tag in Step 1 deposit commit (G4 live) | `git log --oneline -25` grep for `[7]` | `id_tag_gitlog.txt` | PASS |

---

## G1 Headline Result

The Step-2 row (`step_number=2, status='running', step_started_at=2026-06-12T11:41:42.192080`) exists in the `steps` table. Before the fix, the resume dispatch left `plan_id=None` and skipped the `INSERT INTO steps` call entirely — so this row's presence is the end-to-end proof that `recover_plan_id_from_filename()` (G1) works on the live resume path.

## Note for CEO: Step 2 End-of-Step Data

This step's own row (step_number=2) gets its end-of-step data (status='complete', turns, cost_usd) written by the daemon only AFTER this step finishes — so those fields cannot be checked from inside this run. The post-close CEO query to confirm is:

```sql
SELECT * FROM steps WHERE plan_id = 7;
```

This should then show two complete rows with `turns` populated on both.

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/7/knowledge/qa/evidence/diagnostic-6-fix-qa-step-2-2026-06-12/
Files verified: 5
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 5 lifecycle DB checks from inside the resumed dispatch. All checks pass: the plans row, derivations lineage, Step-1 end data (turns + cost populated), Step-2 in-flight row (G1 headline proof), and [7] commit tag are all present and correct.

### Files Deposited
- `knowledge/qa/diagnostic-6-fix-qa-report-step-2-2026-06-12.md` — this QA report
- `knowledge/qa/evidence/diagnostic-6-fix-qa-step-2-2026-06-12/db_plan_row.txt` — plans table query
- `knowledge/qa/evidence/diagnostic-6-fix-qa-step-2-2026-06-12/db_derivations.txt` — derivations lineage query
- `knowledge/qa/evidence/diagnostic-6-fix-qa-step-2-2026-06-12/db_step1_row.txt` — Step 1 end data query
- `knowledge/qa/evidence/diagnostic-6-fix-qa-step-2-2026-06-12/db_step2_row.txt` — Step 2 in-flight row query
- `knowledge/qa/evidence/diagnostic-6-fix-qa-step-2-2026-06-12/id_tag_gitlog.txt` — git log [7] tag check

### Files Created or Modified (Code)
- None (QA-only step)

### Decisions Made
- All 5 checks passed; no escalation needed

### Flags for CEO
- Post-close verification query: `SELECT * FROM steps WHERE plan_id = 7;` — should show two complete rows with turns populated on both

### Flags for Next Step
- None (final step)
