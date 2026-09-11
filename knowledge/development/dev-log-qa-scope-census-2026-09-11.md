# Dev log — QA-scope census — 2026-09-11

**Plan:** diagnostic-100071 | **Thread:** 262 | **Corpus:** #100005–#100070

## Pins re-derived (P1, P2)

own-step Scope 153; earlier-step Scope only 1 — `100061` step 2 `scripts/close_cycle.py`; no Scope block 3 — `100052` step 1 `tests/test_step_files_record.py`, `100053` step 1 `tests/test_substrate_check.py`, `100054` step 1 `tests/conftest.py`; 157 rows, 153 own, 1 union-only, 3 unscoped

Walk-0 and the DEV's classifier (using gates._gate_scope_check, SCOPE_ALLOWLIST, SCOPE_ALLOWLIST_PREFIXES) agree exactly. Deposits arm and allowlist moved no rows. Calibration passed (8 assertions: six P4 undeclared, one P2 earlier-step-only; collapse check for 100061 step 2 = 1 extractable step in own_text).

lifecycle.db data_version: 2 before and after — DB unchanged.

## The rate (Q3)

**1 of 37 QA steps** committed a change to a file in an earlier step's declared set only (genuine edit in a step-N commit, not Planner-commit residue).

The one instance: plan=100061 step=2 `scripts/close_cycle.py` (production), sha `d6da69b` and `849c784b`. Q5 WARN rate over the full corpus: **18 of 95 steps**.

## Q1–Q5 in one table

| Q | question | answer |
|---|---|---|
| Q1 | step_files arm by role | DEV: 121 rows (118 own, 3 undeclared); QA: 31 rows (30 own, 1 earlier-step-only); DIAGNOSTIC: 5 rows (5 own) |
| Q2 | commits arm + agreement | 411 paths; 329 own, 74 earlier-step-only, 8 undeclared; 24 steps in both arms, 11 with disagreement (all "Planner commit after gate ran"); genuine edits=1, residue=0 |
| Q3 | rate | 1 of 37 QA steps; 1 production file of 1 flagged |
| Q4 | gate ledger (control) | pass=117, fail=6; all 6 fail on test files; 100061 step 2 is a pass (union rule); 5 of 6 overridden, 1 halted |
| Q5 | per-step arm simulated | 18 of 95 steps would WARN; 11 steps include record files (false-positive candidates); 10 steps include production files (thread 262 class); three numbers: residue=0, genuine=1, record-candidates=11 |

## What the doc does not establish

- ~250 pre-lifecycle Done files are outside the corpus.
- Commits arm sees Planner commits as earlier-step-only; they are not the genuine-edit class thread 262 names.
- Kind is path-convention only, not content-derived.
- One benign instance says nothing about the next.
- Q3's rate is over QA steps; Q5's WARN rate (18/95) is over all steps. Threshold not derived here.
- The per-step arm, its threshold, and the PLANNER_TEMPLATE sentence are thread 262's next act.
