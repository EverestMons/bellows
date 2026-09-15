# dev-log-def-time-union-nested-2026-09-15

## Pins re-derived (P1)
`tests/test_tools_safe_to_invoke.py`, 323 lines, 6 test functions: t5 `test_every_module_parses_under_python39` :219, its `OLD = "/usr/bin/python3"` :220; `_def_time_unions` :262 — the future-import check :269–273 (`__future__` :270), `_has_union` :275–279, the function-annotation walk :281–296, `_check_stmts` :298–303, its call `_check_stmts(tree.body)` :305, `return hits` :307; t6 :310–323, the file's last line :323

## Failing-first (red, then green)
14 failed, 10 passed in 3.54s
24 passed in 3.40s
exit:0
2395 passed, 2 skipped, 9 warnings in 234.12s (0:03:54)

## The scopes observed (t7, t8)
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[if] PASSED [  5%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[elif] PASSED [ 11%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[else] PASSED [ 16%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[for] PASSED [ 22%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[for-else] PASSED [ 27%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[while] PASSED [ 33%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[with] PASSED [ 38%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[try] PASSED [ 44%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[except] PASSED [ 50%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[try-else] PASSED [ 55%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[finally] PASSED [ 61%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[class-in-function] PASSED [ 66%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[class-in-if] PASSED [ 72%]
tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope[match] PASSED [ 77%]
tests/test_tools_safe_to_invoke.py::test_t6_passes_over_unevaluated_scopes[function-local] PASSED [ 83%]
tests/test_tools_safe_to_invoke.py::test_t6_passes_over_unevaluated_scopes[block-in-function] PASSED [ 88%]
tests/test_tools_safe_to_invoke.py::test_t6_passes_over_unevaluated_scopes[function-in-if] PASSED [ 94%]
tests/test_tools_safe_to_invoke.py::test_t6_passes_over_unevaluated_scopes[future-import] PASSED [100%]

## Mutation run
MUTATION: 8 killed, 0 survived, 0 error
