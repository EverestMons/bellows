# Component 3: In-Bellows Depositor + Dashboard DEPOSITS Panel — DEV Log

**Date:** 2026-08-20
**Plan:** executable-481, Step 1
**Dispatch:** bellows worktree

## What Was Built

### 1. `depositor.py` — Depositor class
- Constructor takes injected dependencies (W5): `disk_preflight_fn`, `shutting_down_check`, `config`, `lifecycle_db_path` — no `import bellows` (circular import avoidance + import whitelist discipline)
- `evaluate(path)` — single entry point under a global `threading.Lock` (A5)
- `reevaluate_on_startup()` — re-evaluates all `ready-` (full eval) and `hold-` (update reason, never auto-clear — A2)
- Evaluation pipeline: parse writes/reads → DISC-4 empty check → sibling scan (global, A4) → in-flight resolution (DISC-1 via `deposit_placeholder_name`/`plan_doc_ref`) → collision check → validation re-run → class assignment → disk preflight → decide (clear vs. hold)
- Class assignment from writes paths: `read-only` (strict allowlist: `knowledge/research/`, `scratch/`), `register-writing`, `governed-tooling`
- Collision detection: writes∩writes (HARD-HOLD), reads∩writes (HOLD), with file-vs-file, prefix-vs-file, prefix-vs-prefix (V4)
- Validation re-run: `cycle_check.run_check(Path(plan))` (EXEC-1: pathlib.Path, not str) + `plan_lint` subprocess (V3: absolute paths); benign FAIL filtering for `(c)` QA banner and `(d)` scope-empty (CAP-1/CAP-2)
- HOLD ordering: rename first, then write `.hold.json` (A3)
- Transient dedup: 5-second window, not lifetime `_seen` (DISC-3/CAP-3)
- Clear deletes stale `.hold.json` (DISC-6)
- Pre-clear TOCTOU recheck (A2)

### 2. `bellows.py` — Wiring
- `_handle`: `ready-` files route to `depositor.evaluate()` on a worker thread (W3) BEFORE the existing skip logic — purely additive (D1); `hold-` added to exclusion list to suppress WARN
- `Bellows.__init__`: instantiates `Depositor` with injected deps
- Startup: calls `depositor.reevaluate_on_startup()` after the existing plan scan
- Periodic `_rescan`: sweeps `ready-` files via `depositor.evaluate()` threads (DISC-2 recovery net)

### 3. Dashboard DEPOSITS panel
- `dashboard.py`: `COLOR_DEPOSITS = 5` (magenta); `assemble_state` reads `config.json` for `watched_projects` and enumerates `ready-`/`hold-` files; `render_screen` adds DEPOSITS section between AWAITING VERDICT and EVENT FEED with row cap
- `status.py`: `render_depositor_status(rows, max_rows=8)` with `…(N more)` overflow

### 4. Tests — `tests/test_depositor.py` (24 tests)
- Import whitelist assertion (W1)
- Class assignment: read-only, register-writing, governed-tooling, empty
- Class mismatch → HOLD (D2)
- Collision: in-flight writes∩writes, sibling writes∩writes, file-vs-file, prefix-vs-file, prefix-vs-prefix (V4)
- Fail-safe: empty writes → HOLD (DISC-4)
- Read-only no collision → CLEAR + is_runnable_plan True after
- HOLD mechanics: hold- file + .hold.json + is_runnable_plan False
- _handle additive: roadmap- still skipped (D1)
- _handle wiring: ready- calls depositor.evaluate (DISC-5)
- Concurrent evaluate: two threads → at most one clear (W2/R4)
- Restart re-eval: hold stays held (A2)
- Path B: legacy Deposits block extraction (EXEC-2)
- Dashboard: DEPOSITS render with data, empty, row cap
- Disk low → HOLD
- Clear deletes stale .hold.json (DISC-6)

### 5. Existing test updates (W6)
- `tests/test_dashboard.py`: `_make_state` gains `deposit_rows: []`; `test_all_none` count 3→4; separator count 3→4

## Verification

- `python3 -m pytest tests/test_depositor.py -q`: 24 passed
- `python3 -m pytest tests/ -q -rf`: 1177 passed, 0 failed
- `python3 scripts/cycle_check.py <plan>`: BAR_MET

## Citation Verification (I1)

All bellows.py/status.py/dashboard.py citations verified by content grep at edit time:
- `is_runnable_plan` at :2030 (regex match)
- `_handle` at :2057 with branch at :2063
- `_disk_preflight` at :334
- `Bellows.__init__` at :2174
- `_rescan` at :2309
- Startup plan scan at :2686
- `status.query_in_flight` at :188
- `render_in_flight`/`render_awaiting_verdict` at :138/:163
- `assemble_state` at :104, `render_screen` at :176
