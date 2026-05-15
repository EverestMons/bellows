# Bellows Phase 6 — Runner Timeout + Observability Fixes
**Date:** 2026-04-16 | **Developer:** Claude Code

## Summary of Fixes

**Fix 1 — Configurable timeout (lines 31, 48).** Added a `timeout` parameter to `run_step()` with default `600`. The hardcoded `timeout=300` in `subprocess.run()` now uses this parameter. Both call sites in `bellows.py` (lines 164-165 and 206-209) pass `config.get("step_timeout_seconds", 600)`. Added `"step_timeout_seconds": 600` to `config.example.json`.

**Fix 2 — Cost as None on timeout/error (lines 63, 78).** Both the `TimeoutExpired` handler and generic `Exception` handler now return `"cost_usd": None` instead of `0.0`. In `bellows.py`, the `total_cost +=` lines use `or 0.0` to safely handle None arithmetic. The timeout handler's `ceo_flags` now includes the actual timeout value via f-string. The generic exception handler's `ceo_flags` now shows the actual exception message instead of the misleading "Step timed out after 300s".

**Fix 3 — Log files on every code path (lines 18-22, 56-60, 70-73, 113-118).** Added `_write_log(log_path, data)` helper that writes JSON to the logs directory. It is called on all four code paths: timeout, generic exception, JSON decode error, and success. Each path writes structured data including `success`, `error`, and relevant context (stderr, raw_output, elapsed_seconds, etc.).

**Fix 4 — Capture stderr on success (lines 84-85).** Added a check after `subprocess.run` completes: if `result.stderr` is non-empty, it is printed to Bellows' stdout with `[runner]` prefix. The success log also includes `result.stderr`.

**Fix 5 — Try/except around json.loads and parse() (lines 88-120).** Wrapped `json.loads(result.stdout)` in `try/except json.JSONDecodeError`. On decode failure, writes a log with the raw output and stderr, and returns a Blocked result with `cost_usd: None`. Also wrapped `parse(raw)` in a separate `try/except Exception` to handle unexpected JSON shapes that pass JSON decoding but fail parser logic.

## Test Results

```
tests/test_runner.py: 11 passed in 0.02s
tests/test_runner_parser.py: 3 passed (existing, no regressions)
```

Tests cover:
1. Configurable timeout passed to subprocess (timeout=10)
2. Default timeout is 600
3. Timeout returns cost=None
4. Generic exception returns cost=None
5. Generic exception ceo_flags contains actual error message
6. Timeout writes log file with success=False
7. Success writes log file with success=True
8. Generic exception writes log file with exception_type
9. stderr printed on success path
10. JSONDecodeError returns Blocked with cost=None
11. JSONDecodeError writes log with raw output

## Output Receipt

- **Status:** Complete
- **Files Created or Modified (Code):**
  - `runner.py` — all 5 fixes: configurable timeout, cost=None on error, log on all paths, stderr capture, JSON/parse error handling
  - `bellows.py` — pass step_timeout_seconds config to runner, handle None cost in arithmetic
  - `config.example.json` — added step_timeout_seconds: 600
  - `tests/test_runner.py` — 11 new tests covering all 5 fixes
- **Decisions Made:**
  - Added a separate try/except for `parse(raw)` (Fix 5b) since parser could also fail on unexpected JSON shapes — plan mentioned this as desirable
  - Used `or 0.0` pattern in bellows.py for None cost arithmetic rather than explicit if/else — simpler and Pythonic
  - `stop_reason` on generic exception changed from "timeout" to "error" for accuracy
- **Flags for CEO:** None
- **Flags for Next Step:** QA step verifies all 5 fixes landed and all tests pass
