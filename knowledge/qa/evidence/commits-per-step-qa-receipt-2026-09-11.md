# QA Receipt — commits-per-step — 2026-09-11

**Plan:** executable-100084 | **Step:** 2 (QA) | **Date:** 2026-09-11

## DEV numstat (`c449e60..HEAD`, eight files)

```
26	0	bellows.py
88	0	knowledge/development/dev-log-commits-per-step-2026-09-11.md
45	0	knowledge/mutants/commits-per-step.json
15	0	knowledge/mutants/commits-per-step.run.txt
22	2	lifecycle.py
154	0	tests/test_bellows.py
38	0	tests/test_lifecycle.py
47	0	tests/test_worktree.py
```

## Item 2 — History shape on DB copy

**Backup command (the only line naming the live DB):**
```
sqlite3 "file:/Users/marklehn/Developer/bellows/lifecycle.db?mode=ro" ".backup /tmp/cps-qa.F7ngim/lifecycle-copy.db"
```

**P2 at drafting (2026-09-11, bellows d3456b9) vs. copy at QA:**

| metric | P2 (drafting) | copy at QA |
|--------|--------------|------------|
| commits total | 172 | 175 |
| plans with rows by total_steps | 1→17, 2→58, 3→2 | 1→17, 2→59, 3→2 |
| rows by step_number | 1→76, 2→92, 3→4 | 1→78, 2→93, 3→4 |
| boundary `max(plan_id)` | (not measured) | 100083 |

The 3 additional rows (175 − 172) and the additional 2-step plan (59 − 58) come from plan #100083, which the daemon processed after the drafting measurement. Plan #100084's own rows are written by the daemon after the merge and daemon restart; the copy holds none of the new per-step shape.

**Boundary query:** `SELECT max(s.plan_id) FROM commits c JOIN steps s ON s.id = c.step_id` → **100083** — the last plan whose commits land entirely under the merge step.

## Item 3 — Production writes

None outside the two evidence files (`commits-per-step-qa-receipt-2026-09-11.md`, `commits-per-step-suite-2026-09-11.txt`). Scratch dir `$T` removed. No lane file, no live lifecycle row, no daemon invoked.

## Verification

| Item | Evidence | Status |
|------|----------|--------|
| 1 — full suite | `2290 passed; 2 xfails (test_gate_watcher live-DB, test_fallback_live_wal_window WAL)` — last line of `commits-per-step-suite-2026-09-11.txt`; no failures | ✅ |
| 2 — history shape on copy | counts beside P2's above; boundary plan_id = 100083; copy holds none of the new per-step shape (daemon restart owed after merge) | ✅ |
| 3 — production writes | none outside the two evidence files; no lane file, no lifecycle row, no daemon | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100084/knowledge/qa/evidence/
Files verified: 1

