# QA Receipt — step-status-transition — 2026-09-11 [100073]

## DEV numstat (68a6a7a..ace7e54 — 9 files)

```
6	0	bellows.py
31	0	knowledge/development/dev-log-step-status-transition-2026-09-11.md
45	0	knowledge/mutants/step-status-transition.json
17	0	knowledge/mutants/step-status-transition.run.txt
21	0	lifecycle.py
138	0	tests/test_consume_verdicts.py
62	0	tests/test_lifecycle.py
108	0	tests/test_reconcile_steps.py
116	0	tools/reconcile_steps.py
```

## Verification

| Item | Observation | Status |
|------|-------------|--------|
| Item 1 — Full suite | 2242 passed, one skip (test_gate_watcher, live-DB); zero failures | ✅ |
| Item 2 — Reconcile LIST/apply on copy | LIST on copy: 17 closed/awaiting, 6 halted/awaiting, 1 running phantom; --apply on live-copy refused (100073 in_progress — in-flight guard correct); --apply on clean copy: 17 rows flipped rowcount=1 each; LIST-again: 0 closed/awaiting, 6 halted unchanged | ✅ |
| Item 3 — Production writes | None beyond the two evidence files; scratch dir removed; live lifecycle.db opened once read-only for backup | ✅ |

## Item 1 suite output (tail)

```
2242 passed, 1 skipped in 97.54s (0:01:37)
```

## Item 2 detail

### LIST on lifecycle-copy.db (backup of live DB, read-only)

```
--- awaiting_verdict on closed plans ---
  id=4 plan_id=3 step_number=2 lifecycle_state=closed total_steps=2
  id=7 plan_id=100001 step_number=2 lifecycle_state=closed total_steps=2
  id=20 plan_id=100007 step_number=3 lifecycle_state=closed total_steps=3
  id=22 plan_id=100008 step_number=2 lifecycle_state=closed total_steps=2
  id=29 plan_id=100013 step_number=1 lifecycle_state=closed total_steps=1
  id=49 plan_id=100023 step_number=2 lifecycle_state=closed total_steps=2
  id=56 plan_id=100027 step_number=2 lifecycle_state=closed total_steps=2
  id=69 plan_id=100037 step_number=1 lifecycle_state=closed total_steps=2
  id=70 plan_id=100037 step_number=2 lifecycle_state=closed total_steps=2
  id=77 plan_id=100042 step_number=2 lifecycle_state=closed total_steps=2
  id=81 plan_id=100045 step_number=2 lifecycle_state=closed total_steps=2
  id=91 plan_id=100052 step_number=1 lifecycle_state=closed total_steps=2
  id=92 plan_id=100052 step_number=2 lifecycle_state=closed total_steps=2
  id=93 plan_id=100053 step_number=1 lifecycle_state=closed total_steps=2
  id=94 plan_id=100053 step_number=2 lifecycle_state=closed total_steps=2
  id=98 plan_id=100056 step_number=1 lifecycle_state=closed total_steps=1
  id=99 plan_id=100057 step_number=1 lifecycle_state=closed total_steps=1

--- awaiting_verdict on halted plans ---
  id=1 plan_id=1 step_number=1 lifecycle_state=halted total_steps=1
  id=17 plan_id=100006 step_number=2 lifecycle_state=halted total_steps=2
  id=47 plan_id=100022 step_number=2 lifecycle_state=halted total_steps=2
  id=62 plan_id=100031 step_number=1 lifecycle_state=halted total_steps=2
  id=82 plan_id=100046 step_number=1 lifecycle_state=halted total_steps=1
  id=95 plan_id=100054 step_number=1 lifecycle_state=halted total_steps=2

--- running steps on non-in_progress plans (listed, not touched) ---
  id=90 plan_id=100051 step_number=2 lifecycle_state=abandoned

Totals: 23 awaiting_verdict (17 closed, 6 halted), 1 running phantom(s)
```

P2 at drafting: 17 closed, 6 halted. Confirmed — counts match exactly.

### --apply on lifecycle-copy.db (first attempt)

```
REFUSED: plans in flight or awaiting verdict: 100073
```

In-flight guard correct — plan 100073 is in_progress during QA execution.

### --apply on lifecycle-apply.db (copy with 100073 marked closed)

```
  plan_id=3 step_number=2 rowcount=1
  plan_id=100001 step_number=2 rowcount=1
  plan_id=100007 step_number=3 rowcount=1
  plan_id=100008 step_number=2 rowcount=1
  plan_id=100013 step_number=1 rowcount=1
  plan_id=100023 step_number=2 rowcount=1
  plan_id=100027 step_number=2 rowcount=1
  plan_id=100037 step_number=1 rowcount=1
  plan_id=100037 step_number=2 rowcount=1
  plan_id=100042 step_number=2 rowcount=1
  plan_id=100045 step_number=2 rowcount=1
  plan_id=100052 step_number=1 rowcount=1
  plan_id=100052 step_number=2 rowcount=1
  plan_id=100053 step_number=1 rowcount=1
  plan_id=100053 step_number=2 rowcount=1
  plan_id=100056 step_number=1 rowcount=1
  plan_id=100057 step_number=1 rowcount=1

Applied: 17 row(s) flipped to complete.
```

### LIST again on lifecycle-apply.db after --apply

```
--- awaiting_verdict on halted plans ---
  id=1 plan_id=1 step_number=1 lifecycle_state=halted total_steps=1
  id=17 plan_id=100006 step_number=2 lifecycle_state=halted total_steps=2
  id=47 plan_id=100022 step_number=2 lifecycle_state=halted total_steps=2
  id=62 plan_id=100031 step_number=1 lifecycle_state=halted total_steps=2
  id=82 plan_id=100046 step_number=1 lifecycle_state=halted total_steps=1
  id=95 plan_id=100054 step_number=1 lifecycle_state=halted total_steps=2

--- running steps on non-in_progress plans (listed, not touched) ---
  id=90 plan_id=100051 step_number=2 lifecycle_state=abandoned
  id=127 plan_id=100073 step_number=2 lifecycle_state=closed

Totals: 6 awaiting_verdict (0 closed, 6 halted), 2 running phantom(s)
```

Zero closed/awaiting after apply. Six halted rows unchanged.
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100073/knowledge/qa/evidence/
Files verified: 1
