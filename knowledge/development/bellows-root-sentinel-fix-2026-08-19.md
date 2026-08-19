# bellows_root.py sentinel fix — dev log

**Date:** 2026-08-19 | **Plan:** 457 | **Step:** 1 (DEV)

## Rationale

`resolve_bellows_root()` had a silent `return start` fallback when no `config.json` ancestor existed. This is the bug: any resolution from a non-bellows tree (e.g. a watched project) returns the start dir itself, and downstream `sqlite3.connect()` calls deposit a stray 0-byte `lifecycle.db` there.

### Two-walk design

The fix implements two sequential walks, NOT a combined check:

1. **Walk 1 — `config.json`:** unchanged semantics, but the terminal `return start` is replaced with `break` to fall through. This walk MUST run to exhaustion first because a bellows worktree CONTAINS a tracked `bellows.py`; a combined "config.json OR bellows.py" check would stop at the worktree and return it instead of canonical, regressing worktree-safety.
2. **Walk 2 — `bellows.py`:** secondary sentinel for CI/fresh-clone where the gitignored `config.json` is absent but the tracked `bellows.py` is present.
3. **Raise:** if neither sentinel is found, `raise ValueError(f"resolve_bellows_root: no bellows sentinel (config.json or bellows.py) found in any ancestor of {start}")`.

### Why bellows.py as sentinel

`bellows.py` is tracked (present in every clone and worktree), unique to the bellows repo (no watched project has it), and stable (the daemon entry point).

## Test results (4 environments)

```
$ python3 -m pytest tests/test_bellows_root.py -q
....                                                                     [100%]
4 passed, 1 warning in 0.11s
```

| Test | Environment | Result |
|---|---|---|
| `test_resolves_to_dir_with_config` | Canonical (config.json at start) | PASS |
| `test_walks_up_to_config` | Worktree with bellows.py → canonical (config.json wins) | PASS |
| `test_non_bellows_tree_raises` | Non-bellows tree (no sentinel) | PASS |
| `test_fresh_clone_resolves_via_bellows_py` | Fresh clone (bellows.py, no config.json) | PASS |

### Test changes

- **Updated:** `test_falls_back_when_no_config` → renamed `test_non_bellows_tree_raises`, flipped to `pytest.raises(ValueError, match="no bellows sentinel")`. The old assertion encoded the bug.
- **Strengthened:** `test_walks_up_to_config` — added `bellows.py` inside `wt1/` worktree dir. Under the correct two-walk order, config.json still wins; a wrong combined-check would return wt1.
- **Added:** `test_fresh_clone_resolves_via_bellows_py` — temp tree with `bellows.py` at root and no `config.json` → resolves to that root.
- **Unchanged:** `test_resolves_to_dir_with_config` — still passes as-is.

## Import-safety check

```
$ cd /Users/marklehn/Developer/GitHub/bellows && python3 -c "import lifecycle, runner"
(no error — imports succeed)
```

Both `lifecycle.py:21` and `runner.py:23` resolve at import time from the canonical `__file__`, which finds `config.json`. No production import-time raise.

## Output Receipt

- **Status:** Complete
- **DEV commit sha:** PENDING_COMMIT
- **Deposits:** `bellows_root.py`, `tests/test_bellows_root.py`, `knowledge/development/bellows-root-sentinel-fix-2026-08-19.md`
