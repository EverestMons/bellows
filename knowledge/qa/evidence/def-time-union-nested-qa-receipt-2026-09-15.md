# QA Receipt — def-time-union-nested-2026-09-15

## DEV Commits

Base: `41f529a7` — DEV head: `a3de019e` (two commits: `f7969c1d`, `a3de019e`)

### numstat (41f529a7..a3de019e)

```
33	0	knowledge/development/dev-log-def-time-union-nested-2026-09-15.md
61	0	knowledge/mutants/def-time-union-nested.json
16	0	knowledge/mutants/def-time-union-nested.run.txt
95	5	tests/test_tools_safe_to_invoke.py
```

### Unchanged tests checked — hunk ranges in test file

`git diff -U0 41f529a7..a3de019e -- tests/test_tools_safe_to_invoke.py | grep -F '@@'`

```
@@ -298 +298,2 @@ def _def_time_unions(path):
@@ -300 +301 @@ def _def_time_unions(path):
@@ -303,3 +304,14 @@ def _def_time_unions(path):
@@ -323,0 +336,78 @@ def test_no_def_time_union_without_future_import():
```

All 4 hunks: base ranges `-298`, `-300`, `-303,3` are inside `_check_stmts` and its call (:298–305); `-323,0` is an addition after the file's last line (:323). No hunk touches a MUST-PRESERVE test function. ✓

## Item 2 — Helper read through its tests (19 PASSED lines)

```
tests/test_tools_safe_to_invoke.py::test_no_def_time_union_without_future_import PASSED [  5%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[if] PASSED [ 10%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[elif] PASSED [ 15%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[else] PASSED [ 21%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[for] PASSED [ 26%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[for-else] PASSED [ 31%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[while] PASSED [ 36%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[with] PASSED [ 42%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[try] PASSED [ 47%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[except] PASSED [ 52%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[try-else] PASSED [ 57%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[finally] PASSED [ 63%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[class-in-function] PASSED [ 68%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[class-in-if] PASSED [ 73%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[match] PASSED [ 78%]
tests/test_tools_safe_to_invoke.py::test_t6_passes_over_unevaluated_scopes[function-local] PASSED [ 84%]
tests/test_tools_safe_to_invoke.py::test_t6_passes_over_unevaluated_scopes[block-in-function] PASSED [ 89%]
tests/test_tools_safe_to_invoke.py::test_t6_passes_over_unevaluated_scopes[function-in-if] PASSED [ 94%]
tests/test_tools_safe_to_invoke.py::test_t6_passes_over_unevaluated_scopes[future-import] PASSED [100%]
```

## Item 3 — Production writes

None outside the two evidence files: no lane file, no live lifecycle row, no daemon act.

## Verification

| Item | Evidence | Status |
|------|----------|--------|
| 1 — Full suite | `2395 passed, two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate)` — last line of `def-time-union-nested-suite-2026-09-15.txt` | ✅ |
| 2 — Helper through its tests | 19 PASSED lines above: t6 over real tree, t7 fourteen cases, t8 four cases | ✅ |
| 3 — Production writes | None beyond the two evidence files | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100103/knowledge/qa/evidence/
Files verified: 1
