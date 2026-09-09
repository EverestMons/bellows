# Override — plan 100052 STEP 1 — scope_check

**Date:** 2026-09-09 | **Ruled by:** CEO (verdict question answered in session d04ebd33) | **Gate:** scope_check | **Failure:** `out-of-scope files: tests/test_step_files_record.py`

**What happened.** Item 7 added two names to `lifecycle.standard_gates` (thread 210's rule: a pass writes a row per standard gate). `tests/test_step_files_record.py` (plan 100049) asserted the row count LITERALLY (`== 10`, two sites); the full suite — which both DEV commits gate on — went red, and the DEV changed the two assertions to derive the count from `test_gate_transaction_mechanization.STANDARD_GATES` (+5/−2, no behaviour). The file is not in the STEP 1 Scope.

**Why the override is granted.** The edit tracks a list THIS plan lengthened, was the smallest change that keeps the suite green, and is the right shape (the count now follows the shared list). The gate did what the plan built it to do: it named a file the plan did not declare.

**What is recorded against it, not excused.** The plan's own miss, for the second time in two gates plans (100045: a message's test consumers; 100052: a list's test consumers): the author and BOTH cold seats enumerated the gate-list consumers by grepping the gate NAMES; `test_step_files_record.py` names no gate — it counts rows. The class: a consumer of a shared list can depend on its LENGTH without naming any member; enumerate by the list's effects (row counts, table sizes), not only its members. LESSONS candidate at the wrap.

**Files changed in the step:** `gates.py`, `verdict.py`, `lifecycle.py`, `scripts/plan_lint.py`, `tests/test_gates_evidence_correspondence.py`, `tests/test_gates_verdict_pause.py`, `tests/test_gate_transaction_mechanization.py`, `tests/test_step_files_record.py` (undeclared), `knowledge/mutants/gates-evidence-correspondence.json`, `knowledge/mutants/gates-evidence-correspondence.run.txt`, `knowledge/development/dev-log-gates-evidence-correspondence-2026-09-09.md` — eleven, ten declared.
