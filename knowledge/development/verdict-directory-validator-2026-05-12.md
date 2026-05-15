# Verdict Directory Validator — Dev Log

**Date:** 2026-05-12
**Plan:** `parallel-1-executable-verdict-directory-validator-2026-05-12.md`
**Commit:** `30964f7`

---

## Summary

Implemented a directory validator that scans `verdicts/pending/` for verdict response files that were incorrectly deposited there instead of `verdicts/resolved/`. This closes the silent-skip failure mode where a verdict file in the wrong directory is never consumed by `_consume_verdicts()`, causing plans to strand indefinitely.

## Changes

### `bellows.py`

1. **Module-level constants:**
   - `_NOTIFIED_MISPLACED: set[tuple[str, str]]` — dedup set keyed by `(filename, "misplaced_directory")` to prevent repeated Pushover notifications for the same file across daemon ticks.
   - `MISPLACED_VERDICT_SCAN_VERBOSE = False` — debug toggle for scan-level logging.

2. **`_scan_misplaced_verdicts(self, pending_dir)` method on `Bellows` class:**
   - Scans `pending_dir` for files matching `verdict-*.md` but NOT `verdict-request-*.md`.
   - Logs a WARN for each match with the full filepath and expected location.
   - Sends a Pushover notification deduped per `(fname, "misplaced_directory")`.
   - Wraps Pushover call in try/except to swallow notification failures.
   - Emits a DEBUG-level scan summary when `MISPLACED_VERDICT_SCAN_VERBOSE` is True.

3. **`_consume_verdicts()` integration:**
   - Added `pending_dir = BELLOWS_ROOT / "verdicts" / "pending"` resolution.
   - Calls `self._scan_misplaced_verdicts(pending_dir)` BEFORE the existing resolved-directory consumption loop.

### `tests/test_misplaced_verdicts.py` (new, 7 tests)

| Test | Assertion |
|---|---|
| `test_scan_misplaced_verdicts_warns_on_verdict_in_pending` | WARN emitted with correct format; push called once |
| `test_scan_misplaced_verdicts_ignores_verdict_request_files` | No WARN; no push |
| `test_scan_misplaced_verdicts_ignores_non_md_files` | No WARN; no push |
| `test_scan_misplaced_verdicts_pushover_deduped_per_file` | Two scans, one push |
| `test_scan_misplaced_verdicts_pushover_failure_swallowed` | Push raises; scan completes; WARN still fires |
| `test_scan_misplaced_verdicts_invoked_from_consume_verdicts` | End-to-end via `_consume_verdicts()`; WARN and push fire |
| `test_scan_misplaced_verdicts_empty_pending_directory` | No WARN; no push; no errors |

## Test Results

- `pytest tests/test_misplaced_verdicts.py -v` — 7/7 pass
- `pytest tests/test_bellows.py tests/test_consume_verdicts.py -v` — 110/110 pass
- `pytest -x --tb=short` — 262 pass, 1 fail (pre-existing `test_run_step_timeout`)

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented `_scan_misplaced_verdicts` directory validator on the `Bellows` class in `bellows.py` with module-level dedup set and verbose toggle. Integrated the scan into `_consume_verdicts()` to run before the resolved-directory consumption loop. Created 7 pytest tests covering all edge cases.

### Files Deposited
- `bellows/knowledge/development/verdict-directory-validator-2026-05-12.md` — this dev log

### Files Created or Modified (Code)
- `bellows/bellows.py` — added `_NOTIFIED_MISPLACED`, `MISPLACED_VERDICT_SCAN_VERBOSE`, `_scan_misplaced_verdicts()`, and `_consume_verdicts()` integration
- `bellows/tests/test_misplaced_verdicts.py` — 7 new tests for the directory validator

### Decisions Made
- Made `_scan_misplaced_verdicts` a method on the `Bellows` class (not module-level) to match the convention of `_consume_verdicts` and access `self.config` for Pushover credentials
- Placed dedup set at module level (not instance level) so it persists across daemon ticks for the process lifetime, matching the plan's "deduped for daemon lifetime" requirement

### Flags for CEO
- None

### Flags for Next Step
- Daemon restart required to load this change
- `MISPLACED_VERDICT_SCAN_VERBOSE` can be toggled to `True` for diagnostic runs
