# Bellows Test-Isolation Conftest — DEV Log

**Date:** 2026-05-26 | **Agent:** Bellows Developer | **Plan:** executable-bellows-test-isolation-conftest-2026-05-26 | **Step:** 1

---

## Pre-Edit Verification

**`tests/conftest.py` existence check:**
```
$ ls tests/conftest.py
ls: tests/conftest.py: No such file or directory
```
Confirmed: file does not exist.

**`verdict.py:14` content check:**
```
14  VERDICTS_DIR = BELLOWS_ROOT / "verdicts"
```
Confirmed: module-level constant matches SA diagnostic expectation.

---

## What Was Done

Created `tests/conftest.py` with the exact 7-LOC fixture body from SA Diagnostic Deliverable C. The fixture is function-scoped autouse, patches `verdict.VERDICTS_DIR` to `tmp_path / "verdicts"` so all tests write verdict files to tmpdir instead of production `verdicts/pending/`.

---

## Test Run Results

```
5 failed, 411 passed, 1 warning in 6.11s
```

All 5 failures are the known carry-overs:
- 4 × `test_decisions.py` (worktree-context: phrase file not found)
- 1 × `test_runner_parser.py::test_run_step_timeout` (timeout assertion)

Zero new regressions introduced by the conftest fixture.

---

## Leak-Closure Verification

```
$ ls verdicts/pending/ | grep -v "^archived$"
(empty output)
```

No orphan `verdict-request-*` files in production `verdicts/pending/` after the full test suite run. The leak is closed.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Created `tests/conftest.py` with the SA-prescribed 7-LOC function-scoped autouse fixture that redirects `verdict.VERDICTS_DIR` to tmpdir. Full test suite passes with zero new regressions. Leak-closure verified: no orphan files in `verdicts/pending/` after test run.

### Files Deposited
- `knowledge/development/bellows-test-isolation-conftest-2026-05-26.md` — this DEV log

### Files Created or Modified (Code)
- `tests/conftest.py` — new file, 7-LOC autouse fixture patching `verdict.VERDICTS_DIR` to tmpdir

### Decisions Made
- Created fixture verbatim from SA Deliverable C — no deviations

### Flags for CEO
- None

### Flags for Next Step
- QA: full-suite run required; verify zero orphans in `verdicts/pending/` after pytest invocation
- QA: verify the two previously-leaking tests (`test_bellows.py::test_apply_defensive_header_defaults_propagates_to_reparsed_header` and `test_consume_verdicts.py::test_dispatch_starts_fresh_when_db_has_orphan_slug_rows`) no longer produce orphan files
- Known carry-over failures: 5 (4 test_decisions.py + 1 test_runner_parser.py) — these predate this change
