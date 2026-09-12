# dev-log: census-tool-parses-under-39 — 2026-09-11

plan: 100092 | thread: 304 | tier: T0

## Pins re-derived (P1, P3)

P1: `tools/cycle_log_projection_census.py:192` reads `a(f"      expected       : {'AGREEING' if exp['agree'] else f'DIVERGING, missing {exp[chr(34)+chr(34)] if False else exp['missing']}'}")`;  under `/usr/bin/python3` (3.9.6) `ast.parse` of the file raises `SyntaxError: f-string: f-string: unmatched '['` at :192, and it is the only file among `tools/`, `scripts/` and the root modules that fails there (measured with `ast` alone at 20:55); the venv's 3.12.14 parses it (PEP 701)

P3: `_py_files()` at :31–32 (`tools/*.py` then `scripts/*.py`); t1 `test_no_absolute_home_paths` :120, t2 `test_no_import_time_writes` :129, t3 `test_help_does_no_work` :138, t4 `test_writers_refuse_without_out` :177 — all four present; t5 `test_every_module_parses_under_python39` absent before the edit.

## Failing-first (red, then green)

Red: `tools/cycle_log_projection_census.py:192:f-string: f-string: unmatched '['`

Green: `5 passed in 4.44s`

## The line unchanged (both branches)

Original, `{'agree': True,  'missing': []}`:   `'AGREEING'`
Original, `{'agree': False, 'missing': [4, 6]}`: `'DIVERGING, missing [4, 6]'`
New,      `{'agree': True,  'missing': []}`:   `'AGREEING'`
New,      `{'agree': False, 'missing': [4, 6]}`: `'DIVERGING, missing [4, 6]'`

## Mutation run

`MUTATION: 1 killed, 0 survived, 0 error`
