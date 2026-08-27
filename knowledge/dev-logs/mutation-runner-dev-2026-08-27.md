# mutation-runner DEV log — 2026-08-27

## C1 empirical exit-code evidence (raw)

```
$ python3 -m pytest tests/test_gate_watcher.py -k "zzz_no_such_test" -q
46 deselected in 0.03s
exit=5

$ python3 -m pytest tests/test_gate_watcher.py -q
.........................................s....                           [100%]
45 passed, 1 skipped, 1 warning in 0.43s
exit=0
```

Confirmed: exit 5 = no tests collected; exit 0 = all passed.

## Pin re-derivation (mine vs plan table)

| pin | plan value | measured | status |
|-----|-----------|----------|--------|
| C1 | exit 0=passed, 5=no tests collected | exit=0 (45p 1s), exit=5 (46 deselected) | matches |
| C2 | 4719 files, ~30.2 MB | 4722 files, ~30.2 MB (31713280 bytes) | **mine supersede** — 3 files more (recent commits) |
| C3 | `tests/test_gate_watcher.py:10-14` sys.path insert | confirmed at lines 10-11: `sys.path.insert(0, str(TOOLS_DIR.parent))` then `from tools.gate_watcher import …` | matches |
| C4 | M1 anchor at `tools/gate_watcher.py:96-98`, indented 16 then 24 | confirmed verbatim at lines 96-98, 16-space then 24-space indentation | matches |
| C5 | M2 anchor at `tools/gate_watcher.py:86` | confirmed verbatim at line 86: `        if state not in TERMINAL:` | matches |
| C6 | 46 collected; full suite 1611+1s=1612 | 46 collected (verified `--collect-only`); full suite deferred to QA | matches (partial — full suite not run in DEV) |

## Targeted tests

```
$ python3 -m pytest tests/test_mutation_check.py --collect-only -q
8 tests collected

$ python3 -m pytest tests/test_mutation_check.py -q
........                                                                 [100%]
8 passed, 1 warning in 3.58s
```
