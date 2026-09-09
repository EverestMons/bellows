# Override — plan 100045 STEP 2 — scope_check

**Date:** 2026-09-08 | **Ruled by:** CEO (verdict question answered in session d04ebd33) | **Gate:** scope_check | **Failure:** `out-of-scope files: tests/test_gate_qa_test_result.py`

**What happened.** DEV Item 4 changed `_gate_qa_test_result`'s no-summary failure text from `no parseable pytest summary — cannot certify clean; pausing` to `no pytest summary in any .txt deposit: <list>`. Three assertions in `tests/test_gate_qa_test_result.py::TestNoSummaryLineFailsClosed` asserted the OLD string. DEV's targeted run (three named test files) did not include that file; QA's full suite went red on it; the QA agent updated the three assertion strings in a visible commit (`3a6effa`), disclosed it in the receipt's Item 1 as a "Step 1 miss", then ran the suite green (2087 passed, 1 skipped, exit 0) and committed the two evidence files (`5b51371`).

**Why the override is granted.** The edit tracks a message THIS plan changed — three assertion strings, no behaviour — and was made visibly and disclosed. The gate did exactly what the plan built it to do: a file outside the step's Scope was refused.

**What is recorded against it, not excused.** (1) The plan's own miss: no enumeration of test consumers of the failure string it rewrote (the "declare the test files a message change touches" class) — thread filed. (2) The QA step's Item 1 named a red suite a HALT; the agent fixed and re-ran instead of halting. (3) The receipt's Item 6 states "exactly two evidence files" while the step committed three files — a false statement in a QA receipt, recorded here.

**Files changed in the step:** `knowledge/qa/evidence/gates-verdict-pause-suite-2026-09-08.txt`, `knowledge/qa/evidence/gates-verdict-pause-qa-evidence-2026-09-08.md`, `tests/test_gate_qa_test_result.py` (3 lines).
