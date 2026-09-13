# dev-log: def-time-union — 2026-09-12 [100095]

## Pins re-derived (P1, P3)

`tools/fold_signal_census.py` (858 lines, blob `df36d6b9`): the module docstring ends at :41, no `from __future__` import, a PEP 604 union in the return annotation of `extract_revision` at :145 (`Path` or `None`) and in the `max_pairs` parameter of `run_census` at :510 (`int` or `None`); `tools/gate_failopen_census.py` (309 lines, blob `ba27f0c3`): the docstring ends at :20, a union in the `module_filter` parameter of `run_census` at :222 (`str` or `None`); an AST scan of all 56 modules (the root, `tools/`, `scripts/`, `hooks/eluvian/`) finds definition-time unions without the future import in these two files only — `hooks/eluvian/wrap_check.py` carries five under the import — and no runtime isinstance union anywhere

P3 re-derived: `tests/test_tools_safe_to_invoke.py` (257 lines): `_py_files()` at :33; t1 at :122, t2 at :131, t3 `test_help_does_no_work` at :140, t4 at :179, t5 `test_every_module_parses_under_python39` at :219. No mechanism mismatch.

## Failing-first (red, then green)

Red: `FAILED tests/test_tools_safe_to_invoke.py::test_no_def_time_union_without_future_import`

Three entries named:
- `/Users/marklehn/Developer/bellows/.bellows-worktrees/100095/tools/fold_signal_census.py:145`
- `/Users/marklehn/Developer/bellows/.bellows-worktrees/100095/tools/fold_signal_census.py:510`
- `/Users/marklehn/Developer/bellows/.bellows-worktrees/100095/tools/gate_failopen_census.py:222`

Green: `2314 passed, 2 skipped in 118.92s (0:01:58)`

## Both tools under Python 3.9 (before and after)

Before (TypeError):
```
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

After (usage):
```
usage: fold_signal_census.py [-h] [--json] [--max-pairs MAX_PAIRS]
usage: gate_failopen_census.py [-h] [--verbose] [--module MODULE]
```

## Mutation run

`MUTATION: 1 killed, 0 survived, 0 error`
