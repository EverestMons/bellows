# Dev Log — resolve_bellows_root() helper + runner.py BELLOWS_ROOT conversion

**Date:** 2026-06-08
**Plan:** executable-bellows-root-helper-runner-conversion-2026-06-08
**Step:** 1 (DEV)

---

## Pre-edit Verification Results (Rule 39)

1. **runner.py BELLOWS_ROOT/LOGS_DIR** — CONFIRMED. `BELLOWS_ROOT = Path(__file__).parent.resolve()` at line 20, `LOGS_DIR = BELLOWS_ROOT / "logs"` at line 21. Other `LOGS_DIR` uses (lines 28, 56) are inside functions.
2. **bellows_root.py does not exist** — CONFIRMED. `ls bellows_root.py` returned "No such file or directory".
3. **config.json is canonical-only marker** — CONFIRMED. gitignored (git check-ignore echoed it), untracked (git ls-files --cached returned empty), present at canonical root `/Users/marklehn/Developer/GitHub/bellows/config.json`, absent from worktree (as expected — this is the marker property).
4. **tests/conftest.py isolate_verdicts_dir present, no LOGS_DIR isolation** — CONFIRMED. `isolate_verdicts_dir` autouse fixture at lines 5-9; no LOGS_DIR or runner references.
5. **Circular import context** — CONFIRMED. `runner.py:12: from bellows import _log` and `bellows.py:124: import runner`. This is why `bellows_root.py` must be standalone.

---

## bellows_root.py (verbatim)

```python
"""Worktree-safe resolution of the canonical bellows root.

Under worktree execution, __file__ resolves inside .bellows-worktrees/<wt>/,
so the legacy `Path(__file__).parent` yields the worktree dir, not canonical
bellows. This walks up to the nearest ancestor containing config.json (the
gitignored, canonical-only operational config), which is absent from worktrees.
Standalone (pathlib only) to avoid the bellows<->runner import cycle.
"""
from pathlib import Path


def resolve_bellows_root(_start=None) -> Path:
    """Return the canonical bellows root (ancestor containing config.json).

    Falls back to the start dir (legacy `Path(__file__).parent` behavior) when
    no config.json is found in any ancestor -- preserves current behavior in
    CI / fresh-clone environments without a config.json.

    `_start` is for testing only; production calls resolve from this file.
    """
    start = (_start or Path(__file__).resolve().parent).resolve()
    current = start
    while True:
        if (current / "config.json").exists():
            return current
        parent = current.parent
        if parent == current:  # filesystem root reached
            return start
        current = parent
```

---

## runner.py diff

```diff
diff --git a/runner.py b/runner.py
index 4d44798..b5bf96d 100644
--- a/runner.py
+++ b/runner.py
@@ -10,6 +10,7 @@ from pathlib import Path
 from typing import Optional

 from bellows import _log
+from bellows_root import resolve_bellows_root
 from parser import parse
 import decisions

@@ -17,7 +18,7 @@ import decisions
 # setdefault respects explicit operator overrides.  (executable-disable-autoupdater-2026-05-27)
 os.environ.setdefault("DISABLE_AUTOUPDATER", "1")

-BELLOWS_ROOT = Path(__file__).parent.resolve()
+BELLOWS_ROOT = resolve_bellows_root()
 LOGS_DIR = BELLOWS_ROOT / "logs"
```

**Byte-unchanged confirmation:** `LOGS_DIR = BELLOWS_ROOT / "logs"` (line 22), `_write_log()` (line 27), `run_step()` (line 34), and all `LOGS_DIR` usages inside functions are completely untouched. The diff is confined to the import line addition and the `BELLOWS_ROOT` declaration replacement.

---

## conftest.py fixture

```python
@pytest.fixture(autouse=True)
def isolate_runner_logs_dir(monkeypatch, tmp_path):
    import runner
    monkeypatch.setattr(runner, "LOGS_DIR", tmp_path / "logs")
```

Placed immediately after the existing `isolate_verdicts_dir` fixture, mirroring its style exactly.

---

## Import-cycle safety check

`bellows_root.py` imports ONLY `pathlib.Path`. No imports of bellows, runner, planner, or verdict. The existing `bellows <-> runner` cycle is untouched; the new module is standalone.

---

## Test Runs

### Pre-edit baseline
```
======================== 448 passed, 1 warning in 6.19s ========================
```

### Post-edit
```
======================== 451 passed, 1 warning in 5.61s ========================
```

**Delta:** +3 tests (the new `test_bellows_root.py`: `test_resolves_to_dir_with_config`, `test_walks_up_to_config`, `test_falls_back_when_no_config`). Zero new failures. All 19 `test_runner.py` tests still pass with the new autouse fixture active.

---

## Canonical-logs check

`git status --porcelain logs/` — empty output. No `*-step.json` created in canonical `logs/` during the suite run. The autouse fixture successfully redirected all LOGS_DIR writes to tmpdir.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Created `bellows_root.py` with `resolve_bellows_root()` (config.json marker walk-up with fallback). Converted `runner.py`'s `BELLOWS_ROOT` to use the helper. Added `isolate_runner_logs_dir` autouse fixture in `tests/conftest.py` to close the worktree-write gap. Added three helper unit tests including the negative worktree-resolution proof.

### Files Deposited
- `knowledge/development/bellows-root-helper-runner-conversion-2026-06-08.md` — this dev log

### Files Created or Modified (Code)
- `bellows_root.py` — new module, `resolve_bellows_root()` helper
- `runner.py` — added `from bellows_root import resolve_bellows_root`, replaced `BELLOWS_ROOT = Path(__file__).parent.resolve()` with `BELLOWS_ROOT = resolve_bellows_root()`
- `tests/conftest.py` — added `isolate_runner_logs_dir` autouse fixture
- `tests/test_bellows_root.py` — new test file, 3 tests

### Decisions Made
- Used `--` (em-dash equivalent) instead of `\u2014` in docstring for ASCII safety (minor style choice within specialist authority)

### Flags for CEO
- None

### Flags for Next Step
- Pre-edit baseline: 448 passed. Post-edit: 451 passed. Delta is exactly +3 new tests, zero regressions.
- Canonical logs clean — verified via `git status --porcelain logs/`.
- The three latent instances (bellows.py, planner.py, verdict.py) remain unconverted per CEO decision.
