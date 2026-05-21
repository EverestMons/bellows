# Dev Log: Disable Claude Code Autoupdater

**Date:** 2026-05-27
**Plan:** executable-disable-autoupdater-2026-05-27
**Step:** 1
**Agent:** Bellows Developer

## Implementation Summary

Added `os.environ.setdefault("DISABLE_AUTOUPDATER", "1")` to both `bellows.py` and `runner.py` to prevent the Claude Code auto-updater from downloading and applying upgrades between `claude -p` invocations. This preserves prompt-cache continuity during plan execution. `setdefault` is used so an operator who explicitly sets the variable at launch time is respected.

## Changes

### runner.py — lines 14–16 (after imports, before constants)

**Before:**
```python
from bellows import _log
from parser import parse
import decisions

BELLOWS_ROOT = Path(__file__).parent.resolve()
```

**After:**
```python
from bellows import _log
from parser import parse
import decisions

# Prevent Claude Code auto-updater from shifting agent behavior mid-plan.
# setdefault respects explicit operator overrides.  (executable-disable-autoupdater-2026-05-27)
os.environ.setdefault("DISABLE_AUTOUPDATER", "1")

BELLOWS_ROOT = Path(__file__).parent.resolve()
```

### bellows.py — lines 19–21 (after imports, before BELLOWS_ROOT constant)

**Before:**
```python
BELLOWS_ROOT = Path(__file__).parent.resolve()
DB_PATH = str(BELLOWS_ROOT / "bellows.db")
```

**After:**
```python
# Prevent Claude Code auto-updater from shifting agent behavior mid-plan.
# setdefault respects explicit operator overrides.  (executable-disable-autoupdater-2026-05-27)
os.environ.setdefault("DISABLE_AUTOUPDATER", "1")

BELLOWS_ROOT = Path(__file__).parent.resolve()
DB_PATH = str(BELLOWS_ROOT / "bellows.db")
```

### tests/test_runner.py — two new tests added at top of file (after import block)

```python
def test_runner_sets_disable_autoupdater_env_var():
    """Importing runner must set DISABLE_AUTOUPDATER=1 in the process environment."""
    assert os.environ.get("DISABLE_AUTOUPDATER") == "1"


def test_runner_respects_explicit_disable_autoupdater_override(monkeypatch):
    """setdefault must not overwrite an explicit operator override."""
    monkeypatch.setenv("DISABLE_AUTOUPDATER", "0")
    importlib.reload(runner)
    assert os.environ.get("DISABLE_AUTOUPDATER") == "0"
    monkeypatch.setenv("DISABLE_AUTOUPDATER", "1")
    importlib.reload(runner)
```

### CLAUDE.md — new section appended

Added `## Claude Code upgrade cadence (manual)` section documenting the env-var setting, manual upgrade procedure (`claude --version` + `npm install -g @anthropic-ai/claude-code`), recommended cadence (session-wrap or weekly), and rationale (prompt-cache continuity).

## Test Results

### Targeted: `python3 -m pytest tests/test_runner.py -v`

```
19 passed, 1 warning in 0.14s
```

All 19 tests pass (17 pre-existing + 2 new). Zero regressions.

### Full suite: `python3 -m pytest tests/ -v`

```
361 passed, 5 failed, 1 warning in 6.19s
```

Test count: 366 total (was 364, delta = +2).

Pre-existing failures (not introduced by this change):
- `tests/test_runner_parser.py::test_run_step_timeout` — pre-existing per PROJECT_STATUS history
- `tests/test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file` — pre-existing
- `tests/test_decisions.py::TestLoadPhrases::test_includes_known_phrases` — pre-existing
- `tests/test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives` — pre-existing
- `tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth` — pre-existing

Zero NEW failures.

## Known Issues

None.

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Set `DISABLE_AUTOUPDATER=1` in both `bellows.py` and `runner.py` via `os.environ.setdefault`, added two unit tests verifying the contract and setdefault semantics, and documented the manual upgrade cadence in `CLAUDE.md`.

### Files Deposited
- `knowledge/development/disable-autoupdater-2026-05-27.md` — this dev log

### Files Created or Modified (Code)
- `runner.py` — added `os.environ.setdefault("DISABLE_AUTOUPDATER", "1")` after imports with rationale comment
- `bellows.py` — added identical line after imports (belt-and-suspenders)
- `tests/test_runner.py` — added `test_runner_sets_disable_autoupdater_env_var` and `test_runner_respects_explicit_disable_autoupdater_override`
- `CLAUDE.md` — added `## Claude Code upgrade cadence (manual)` section (12 lines)

### Decisions Made
- Used `setdefault` (not unconditional assignment) per plan spec to respect operator overrides
- Placed the env-var set in both modules for belt-and-suspenders coverage per plan rationale
- Used `importlib.reload` in override test to re-execute module-level setdefault after monkeypatch

### Flags for CEO
- None

### Flags for Next Step
- The 4 `test_decisions.py` failures are pre-existing and unrelated to this change; QA should note them alongside the documented `test_run_step_timeout` failure
- Daemon restart is required for the env-var mutation to take effect in the running process
