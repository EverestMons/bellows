# Override — plan 100053 STEP 1 — scope_check

**Date:** 2026-09-09 | **Ruled by:** CEO (verdict question answered in session d04ebd33) | **Gate:** scope_check | **Failure:** `out-of-scope files: tests/test_substrate_check.py`

**What happened.** Change 6 re-pointed `scripts/substrate_check.py:80` from the literal `"CONFORMANT"` to `walk_register_lint.STATUS_CONFORMANT`. In the worktree, `tests/test_substrate_check.py` kept importing the CANONICAL checkout's `substrate_check` (old literal): `depositor.py`, imported via `test_admission_flip.py` → `bellows.py`, resolves the bellows root from `config.json` and puts the main branch's `scripts/` at `sys.path[0]`. The DEV added an 11-line eviction-and-reimport shim to the test file, which the plan lists as UNCHANGED.

**Why the override is granted.** The shim tests the worktree's code instead of the canonical checkout's — the only way the plan's own change could be tested in the environment the daemon provides; no behaviour, no assertion changed.

**What is recorded against it, not excused.** (1) A systemic hazard, not this plan's: any worktree test that imports a `scripts/` module can silently test the MAIN branch's copy — a probe's location is part of its environment (LESSONS 2026-09), now measured inside pytest itself. Thread filed. (2) The plan named `tests/test_substrate_check.py` unchanged and QA Item 6 asserts its diff EMPTY; the receipt must report the shim honestly — a rule_22 pause on that row returns to the CEO.

**Files changed in the step:** 17, sixteen declared plus the shim.
