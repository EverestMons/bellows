# Suite-Green Fixes — Implementation Log
**Date:** 2026-06-06 | **Agent:** Bellows Developer | **Step:** 2

---

## Changes

### Fix #1 — `resolve_governance_root()` in `decisions.py`

Added `resolve_governance_root()` between the `logger` definition and `GOVERNANCE_ROOT` assignment. The function walks up from `Path(__file__).resolve().parent` through parent directories until it finds one containing `COMPANY.md`, returning that path. Falls back to legacy `parent.parent` with a warning if no marker is found.

Rewrote line 11 from:
```python
GOVERNANCE_ROOT = Path(__file__).parent.parent.resolve()
```
to:
```python
GOVERNANCE_ROOT = resolve_governance_root()
```

`PHRASES_FILE` (line 12, now line 24) unchanged — already derives from `GOVERNANCE_ROOT`.

### Fix #2 — `test_run_step_timeout` rewrite in `tests/test_runner_parser.py`

Replaced the stale test (which mocked `subprocess.run`, never intercepted by the real `Popen` path) with a `FakeProcess` stub:

- `FakeProcess.__init__(*args, **kwargs)`: sets `stdout`/`stderr` to `iter([])` (empty iterators)
- `FakeProcess.poll()`: returns `None` (process appears running)
- `FakeProcess.kill()`: no-op

Patching strategy:
- `runner.subprocess.Popen` → returns `FakeProcess()` (no real process spawned, no `claude` launched)
- `runner.time.sleep` → no-op (skip 1s poll sleep)
- `timeout=0` passed to `run_step` → inactivity condition fires immediately

Assertions: `is_error is True`, `stop_reason == "timeout"`, `escalate is True`.

---

## Per-Edit Pytest Results

### After Fix #1 (`decisions.py`)
The 4 `test_decisions.py` tests that were failing due to `GOVERNANCE_ROOT` misresolution now pass:
- `TestLoadPhrases::test_loads_phrases_from_file` — PASSED
- `TestLoadPhrases::test_includes_known_phrases` — PASSED
- `TestLoadPhrases::test_splits_slash_alternatives` — PASSED
- `TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth` — PASSED

### After Fix #2 (`tests/test_runner_parser.py`)
- `test_run_step_timeout` — PASSED

### Final Suite Count
```
448 passed, 1 warning in 6.03s
```
**448 passed, 0 failed.**

---

## Worktree-Resolution Demonstration

Running from worktree path `.bellows-worktrees/bellows-suite-green-fixes-2026-06-06/`:

```
GOVERNANCE_ROOT: /Users/marklehn/Developer/GitHub
COMPANY.md exists: True
PHRASES_FILE: /Users/marklehn/Developer/GitHub/INTERMEDIATE_DECISION_PHRASES.md
PHRASES_FILE exists: True
load_phrases() count: 44
First 5 phrases: ['had to', 'decided to', 'on initiative', 'noticed that', 'chose to']
```

The walk-up from the worktree path traverses:
```
.bellows-worktrees/bellows-suite-green-fixes-2026-06-06/ → COMPANY.md: ✗
.bellows-worktrees/                                      → COMPANY.md: ✗
bellows/                                                 → COMPANY.md: ✗
GitHub/                                                  → COMPANY.md: ✓  ← governance root
```

---

## Confirmation: `claude` Not Launched

The timeout test uses `FakeProcess` with `patch("runner.subprocess.Popen")` — no real subprocess is spawned. The 7 targeted tests complete in 0.08s total.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 2
**Status:** Complete

### What Was Done
Implemented two fixes per blueprint: (1) added `resolve_governance_root()` to `decisions.py` with walk-up-to-`COMPANY.md` marker, replacing brittle `parent.parent`; (2) rewrote `test_run_step_timeout` to mock `subprocess.Popen` with `FakeProcess` stub exercising the inactivity-timeout path. Full suite: 448 passed, 0 failed.

### Files Deposited
- `knowledge/development/suite-green-fixes-impl-2026-06-06.md` — this implementation log

### Files Created or Modified (Code)
- `decisions.py` — added `resolve_governance_root()`, rewrote `GOVERNANCE_ROOT` derivation
- `tests/test_runner_parser.py` — rewrote `test_run_step_timeout` with `FakeProcess` + `Popen` mock

### Decisions Made
- Implemented blueprint exactly as specified; no deviations

### Flags for CEO
- None

### Flags for Next Step
- `test_decisions.py` was NOT edited — its 4 failures resolved purely from the `GOVERNANCE_ROOT` fix, as predicted
- The `_cached_phrases` module-level cache in `decisions.py` is reset between test runs by conftest fixtures; no change needed
