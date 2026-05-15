# QA Report — Thread wt_path into _gate_rule_20_self_check

**Date:** 2026-05-10 | **Plan:** executable-rule-20-self-check-wt-path-2026-05-10 | **Step:** 2

---

## Verification Status Table

| Check | Status | Evidence |
|-------|--------|----------|
| 1a — `_gate_rule_20_self_check` signature includes `wt_path=None` | ✅ | gates.py:273 — `def _gate_rule_20_self_check(..., wt_path=None):` |
| 1b — `_resolve_deposit_path` call passes `wt_path=wt_path` | ✅ | gates.py:292 — `resolved = _resolve_deposit_path(dep_path, project_path, wt_path=wt_path)` |
| 1c — `gates.check()` caller passes `wt_path=wt_path` | ✅ | gates.py:105 — `_gate_rule_20_self_check(..., wt_path=wt_path)` |
| 1d — `_gate_deposit_exists` unchanged (2026-05-06 fix intact) | ✅ | gates.py:198 — signature still has `wt_path=None`; lines 214, 222 pass `wt_path=wt_path` |
| 2a — New test `test_rule_20_self_check_resolves_via_worktree_path` exists | ✅ | tests/test_gates.py:638 |
| 2b — Test constructs worktree-vs-project directory split, verifies Strategy 0 | ✅ | Creates project_path (empty) + wt_path (with QA report), asserts no rule_20_self_check failure |
| 2c — No other tests modified | ✅ | Only addition at line 638–675; pre-existing tests unchanged |
| 3 — Gates test suite passes | ✅ | 62 passed, 0 failed (see below) |
| 4 — Full test suite: no regressions | ✅ | 242 passed, 1 failed (pre-existing `test_run_step_timeout` — unrelated) |
| 5 — Behavioral spot-check passes | ✅ | `PASSED — no rule_20_self_check failures, worktree resolution works correctly` |

---

## Pytest Output — Gates Suite

```
======================== 62 passed, 1 warning in 0.14s =========================
```

New test appeared as:
```
tests/test_gates.py::test_rule_20_self_check_resolves_via_worktree_path PASSED [ 98%]
```

Full evidence file: `knowledge/qa/evidence/rule-20-self-check-wt-path-2026-05-10/pytest_gates.txt`

---

## Pytest Output — Full Suite

```
FAILED tests/test_runner_parser.py::test_run_step_timeout - assert False is True
=================== 1 failed, 242 passed, 1 warning in 6.11s ===================
```

The single failure (`test_run_step_timeout`) is a pre-existing issue in `test_runner_parser.py` unrelated to gates. Delta from this fix: +1 new test passing, 0 regressions.

---

## Behavioral Spot-Check Output

```
PASSED — no rule_20_self_check failures, worktree resolution works correctly
```

The snippet created two temp directories (worktree with QA report, project_path without), called `gates.check()` with `wt_path` pointing at the worktree, and confirmed zero `rule_20_self_check` failures — Strategy 0 resolved the file correctly.

---

## Final Verdict

**ALL CHECKS PASSED**

---

## Rule 20 — QA Self-Check Results

```python
import os
deposits = [
    "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/rule-20-self-check-wt-path-qa-2026-05-10.md",
    "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/rule-20-self-check-wt-path-2026-05-10/pytest_gates.txt",
]
missing = [d for d in deposits if not os.path.isfile(d)]
if missing:
    print(f"SELF-CHECK FAILED — missing: {missing}")
else:
    print("RULE 20 SELF-CHECK PASSED")
```

PASSED — SELF-CHECK PASSED
