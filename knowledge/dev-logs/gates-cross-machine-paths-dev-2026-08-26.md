# Dev Log — gates-cross-machine-paths — 2026-08-26

## Pre-flight measurements

### G1 — the resolver
- `def _resolve_deposit_path` count: 1 (line 324 in gates.py)
- Final `    return None` within the function: line 362 (count-1 within the function, verified by grep -nF between def at 324 and next def at 365)
- Two-line pair anchor (`return os.path.abspath(p3)` + `return None`): count-1 file-wide (verified by Python string search)

### G2 — call sites
- `grep -cF '_resolve_deposit_path(' gates.py` → 8
- Minus the def → **7 call sites** (derivation: 8 total – 1 definition = 7)

## Task B — Strategy 4 edit

Edit anchor: the unique two-line pair at lines 361–362:
```
        return os.path.abspath(p3)
    return None
```

Replaced with Strategy 4 (cross-machine re-root) block: rfind-last-marker on the project basename, try worktree-first then project root, resolve only if file/dir exists on disk.

### Post-probes
```
$ grep -cF 'Strategy 4 (cross-machine re-root)' gates.py
1

$ grep -cF 'rfind(marker)' gates.py
1

Function still ends 'return None': True (fail-closed unchanged)
```

## Task C — tests

Created `tests/test_gates_cross_machine_paths.py` with 6 tests:
1. test_560_shape_resolves — THE measured incident shape
2. test_560_shape_absent_returns_none — fail-closed guard
3. test_foreign_absolute_no_project_basename — no false positives
4. test_worktree_first — wt copy returned when both exist
5. test_nested_marker_uses_last — rfind selects the LAST marker
6. test_relative_path_unchanged — regression guard (Strategy 4 untouched for relative paths)

### Targeted run
```
$ python3 -m pytest tests/test_gates_cross_machine_paths.py tests/test_gates.py -k "gates or deposit" --tb=short -q
175 passed, 1 warning in 1.32s
```
Derivation: 6 new cross-machine tests + 169 existing gates/deposit tests = 175.
