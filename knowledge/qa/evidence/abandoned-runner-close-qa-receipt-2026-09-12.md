# QA Receipt — abandoned-runner-close-2026-09-12 — plan 100098 Step 2

## numstat: 06b545f..afa5515

```
557	69	bellows.py
297	0	knowledge/development/dev-log-abandoned-runner-close-2026-09-12.md
245	0	knowledge/mutants/abandoned-runner-close.json
44	0	knowledge/mutants/abandoned-runner-close.run.txt
170	8	lifecycle.py
17	0	notifier.py
1157	0	tests/test_abandoned_runner_close.py
606	0	tests/test_lifecycle.py
185	2	tests/test_reconcile_steps.py
117	3	tests/test_stop_path.py
20	2	tools/reconcile_steps.py
```

Eleven files over `06b545f..afa5515`: 100097's nine source/test/manifest/run files and this plan's dev-log (`knowledge/development/dev-log-abandoned-runner-close-2026-09-12.md`); the stray record added at `8f836ac` and removed at `afa5515` nets to no line.

## Item 1 — Full suite

File: `knowledge/qa/evidence/abandoned-runner-close-suite-2026-09-12.txt`

Command: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/abandoned-runner-close-suite-2026-09-12.txt 2>&1`

Summary line: `2364 passed, 2 skipped, 9 warnings in 231.36s (0:03:51)` (two skips: test_gate_watcher live-DB; test_fallback_live_wal_window version gate)

## Item 2 — Migration and reconcile on a COPY of the live DB

The live DB was opened once, read-only, by the backup command below — no other access to the live file:

```
/Users/marklehn/Developer/bellows/.venv/bin/python -c "import sqlite3; src = sqlite3.connect('file:/Users/marklehn/Developer/bellows/lifecycle.db?mode=ro', uri=True); dst = sqlite3.connect('/tmp/abandoned-close-qa.uQVVTU/lc.db'); src.backup(dst); src.close(); dst.close()"
```

In-flight plans on copy before patching: `[(100098, 'in_progress')]`  
Patched on copy only: `UPDATE plans SET lifecycle_state = 'closed' WHERE lifecycle_state IN ('in_progress','awaiting_verdict')`

**Pre-apply counts (from copy):**

| Table | Count | Max id |
|-------|-------|--------|
| steps | 174 | 174 |
| commits | 218 | — |
| deposits | 601 | — |
| gate_events | 1696 | — |
| step_files | 336 | — |

FK checks (all five tables): no violations.

**Reconcile LIST (before apply):**

```
--- awaiting_verdict on halted plans ---
  id=1 plan_id=1 step_number=1 lifecycle_state=halted total_steps=1
  id=17 plan_id=100006 step_number=2 lifecycle_state=halted total_steps=2
  id=47 plan_id=100022 step_number=2 lifecycle_state=halted total_steps=2
  id=62 plan_id=100031 step_number=1 lifecycle_state=halted total_steps=2
  id=82 plan_id=100046 step_number=1 lifecycle_state=halted total_steps=1
  id=95 plan_id=100054 step_number=1 lifecycle_state=halted total_steps=2
  id=140 plan_id=100080 step_number=1 lifecycle_state=halted total_steps=2
  id=172 plan_id=100097 step_number=1 lifecycle_state=halted total_steps=2

--- running steps on non-in_progress plans (listed, not touched) ---
  id=90 plan_id=100051 step_number=2 lifecycle_state=abandoned
  id=141 plan_id=100081 step_number=1 lifecycle_state=abandoned
  id=142 plan_id=100082 step_number=1 lifecycle_state=abandoned
  id=174 plan_id=100098 step_number=2 lifecycle_state=closed

Totals: 8 awaiting_verdict (0 closed, 8 halted), 4 running phantom(s)
```

**Reconcile --apply:**

```
  abandoned pass: plan_id=100051 rowcount=1
  abandoned pass: plan_id=100081 rowcount=1
  abandoned pass: plan_id=100082 rowcount=1

Abandoned pass: 3 plan(s) cleaned.
```

**Post-apply verification:**

Steps DDL (carries `'abandoned'` and `daemon_pid`):

```sql
CREATE TABLE "steps" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL REFERENCES plans(id),
                step_number INTEGER NOT NULL,
                role TEXT,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','running','awaiting_verdict','complete','abandoned')),
                step_started_at TEXT,
                step_ended_at TEXT,
                cost_usd REAL,
                turns INTEGER,
                duration_s REAL,
                log_ref TEXT,
                daemon_pid INTEGER,
                UNIQUE(plan_id, step_number)
            )
```

Step states after apply: id=90 → `abandoned`; id=141 → `abandoned`; id=142 → `abandoned`; id=174 → `running` (this step's own row, plan closed on copy only).

Counts after apply: steps 174 / commits 218 / deposits 601 / gate_events 1696 / step_files 336 — equal to pre-apply.

FK checks after apply: all five tables clean (no violations).

Bak file: `lc.db.pre-steps-abandoned-2026-09-14.bak` present in `$T`.

**Reconcile LIST (after apply):**

```
--- awaiting_verdict on halted plans ---
  id=1 plan_id=1 step_number=1 lifecycle_state=halted total_steps=1
  id=17 plan_id=100006 step_number=2 lifecycle_state=halted total_steps=2
  id=47 plan_id=100022 step_number=2 lifecycle_state=halted total_steps=2
  id=62 plan_id=100031 step_number=1 lifecycle_state=halted total_steps=2
  id=82 plan_id=100046 step_number=1 lifecycle_state=halted total_steps=1
  id=95 plan_id=100054 step_number=1 lifecycle_state=halted total_steps=2
  id=140 plan_id=100080 step_number=1 lifecycle_state=halted total_steps=2
  id=172 plan_id=100097 step_number=1 lifecycle_state=halted total_steps=2

--- running steps on non-in_progress plans (listed, not touched) ---
  id=174 plan_id=100098 step_number=2 lifecycle_state=closed

Totals: 8 awaiting_verdict (0 closed, 8 halted), 1 running phantom(s)
```

Three running phantoms (ids 90, 141, 142) resolved to `abandoned`; one remaining (id=174, this step's own row, on the copy only).

## Item 3 — Production writes

None outside the two evidence files (`abandoned-runner-close-qa-receipt-2026-09-12.md`, `abandoned-runner-close-suite-2026-09-12.txt`). Temp dir `$T` removed. No lane file, no live lifecycle row, no daemon act, no branch in the canonical checkout.

Live DB opened once, read-only:

```
grep -c -F 'lifecycle.db?mode=ro' knowledge/qa/evidence/abandoned-runner-close-qa-receipt-2026-09-12.md
```

That command prints 1 (the backup command quoted in Item 2 above; no other access).

## Verification

| Item | Description | Evidence | Status |
|------|-------------|----------|--------|
| 1 | Full suite: `2364 passed` plus two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate); no `failed` | `abandoned-runner-close-suite-2026-09-12.txt` tail | ✅ |
| 2 | Migration and reconcile on copy: DDL carries `abandoned`/`daemon_pid`; steps 90/141/142 → `abandoned`; bak file present; FK checks clean; LIST→apply→LIST passed | Item 2 output above | ✅ |
| 3 | Production writes: none outside the two evidence files; live DB opened once read-only | Item 3 statement | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100098/knowledge/qa/evidence/
Files verified: 1
