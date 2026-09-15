# Dev log — classify-deposit-script (2026-09-14)

## Pins re-derived (P1, P2, P4)

**P1:** `tools/classify_deposit.py`, 149 lines, by #100100 (`d1f595c`): the imports `argparse` … `sys` :2–6; `main(argv=None)` :34, `parser.parse_args(argv)` :50; `import bellows_root` :55 (the default config's path); `import cycle_check` :83 and `import depositor as dep_mod` :84; no sys.path line anywhere in the file

**P2 re-derived** (`grep -n -F "sys.path.insert(0" tools/*.py`):
- `tools/check_deposit.py:25` `sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`
- `tools/cycle_log_signal_census.py:37` `sys.path.insert(0, str(BELLOWS_ROOT))` (root first)
- `tools/cycle_log_signal_census.py:38` `sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))` (scripts/ second — each at index 0, so scripts/ is searched first)
- `tools/fold_signal_census.py:60` `sys.path.insert(0, str(SCRIPTS))` (scripts/ first)
- `tools/fold_signal_census.py:61` `sys.path.insert(0, str(ROOT))` (root second)
- `tools/clear_plan.py:110,:143,:166` inside functions

**P4 re-derived:** `tests/test_classify_deposit.py`: 8 tests (c1–c8), 241 lines; root and scripts/ put on sys.path at head (:12–13); `TOOL_PATH`, `PYTHON = sys.executable` (:17–18); autouse `patch_roots` :93–99 — `tmp_path / "governance"` made and `resolve_governance_root` and `resolve_projects_parent` monkeypatched on `bellows_root` module; tool loaded by path and run in-process through `main(argv)` in c1–c6 and c8; c7 (:196–204) the one subprocess run exiting 2 in argparse; no c9 present.

No mechanism mismatch — no sys.path line in tool, no c9 in test file, no imports outside main().

## Failing-first (red, then green)

Red (unedited tool, c9 added): `1 failed, 8 passed in 2.38s`

Green (after tool fix):
- `tests/test_classify_deposit.py`: `9 passed in 0.38s`
- `tests/test_tools_safe_to_invoke.py`: `6 passed in 3.19s`
- Full suite: `2378 passed, 2 skipped in 232.13s`

## The script run observed (c9)

`tests/test_classify_deposit.py::test_c9_script_run PASSED                [100%]`

## Mutation run

`MUTATION: 2 killed, 0 survived, 0 error`
