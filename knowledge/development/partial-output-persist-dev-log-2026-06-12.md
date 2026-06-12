# Partial-Output Persist on Timeout Kill — Dev Log

**Date:** 2026-06-12
**Plan:** 24
**Agent:** Bellows Developer
**Diagnostic:** `knowledge/research/partial-output-timeout-loss-2026-06-12.md`

---

## Verification Blocks

All three diagnostic verification blocks confirmed before editing:

- **V1:** `runner.py:153-159` — `_write_log` dict had `success`, `error`, `timeout_type`, `elapsed_seconds`, `stderr_partial` — no `raw_output`. Confirmed.
- **V2:** `runner.py:169` — `"result_text": ""`. Confirmed.
- **V3:** `raw_output` census: 4 occurrences (3× `[:5000]` at non-zero-exit/no-result-event/parse-error, 1× full at success, 0× on timeout path). Confirmed.

No divergence from diagnostic claims.

## Edits

### G1: Add `raw_output` to timeout `_write_log` dict

**File:** `runner.py`
**Line:** 159 (after edit)
**Change:** Added `"raw_output": result_stdout[:5000]` to the timeout-path `_write_log` dict literal.

### G2: Populate `result_text` in timeout return dict

**File:** `runner.py`
**Line:** 170 (after edit)
**Change:** Changed `"result_text": ""` to `"result_text": result_stdout[:5000]`.

## Tests Added

**File:** `tests/test_runner.py`

| Test | Purpose |
|---|---|
| `test_timeout_persists_accumulated_output` | Timeout-killed process with accumulated stdout → `result_text` and log `raw_output` carry the output |
| `test_timeout_truncates_output_at_5000` | Output > 5000 chars is capped at 5000 in both `result_text` and `raw_output` |
| `test_timeout_silent_stall_empty_strings` | Genuinely-silent stall (empty buffer) → empty `result_text` and `raw_output`, no exception |

## Suite Results

**Before:** 532 tests, 532 passed
**After:** 535 tests, 535 passed (3 new tests added)

### Suite tail (last 5 lines):

```
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 535 passed, 1 warning in 9.75s ========================
```

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Applied the two-site fix for partial-output loss on the inactivity-timeout kill path in `runner.py`. G1: added `raw_output: result_stdout[:5000]` to the timeout `_write_log` dict. G2: changed timeout return dict's `result_text` from `""` to `result_stdout[:5000]`. Added 3 tests covering accumulated output persistence, 5000-char truncation, and silent-stall regression.

### Files Deposited
- `knowledge/development/partial-output-persist-dev-log-2026-06-12.md` — this dev log

### Files Created or Modified (Code)
- `runner.py` — G1: added `raw_output` to timeout log dict (line 159); G2: changed `result_text` from `""` to `result_stdout[:5000]` (line 170)
- `tests/test_runner.py` — added 3 tests: `test_timeout_persists_accumulated_output`, `test_timeout_truncates_output_at_5000`, `test_timeout_silent_stall_empty_strings`

### Decisions Made
- Used `fake_monotonic` callable (incrementing counter) for thread-safe timeout mocking in tests with accumulated stdout data — avoids race between reader and main threads on `side_effect` list ordering

### Flags for CEO
- DAEMON RESTART REQUIRED — no hot reload; the fix takes effect on next daemon start

### Flags for Next Step
- None
