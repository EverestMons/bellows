# QA Evidence — R2 wiring (plan 560, Step 2)

**Date:** 2026-08-26
**Commit under test:** `5eb27e0` — `[560] R2 actuation: fail-open registry information line in wrap_check (subprocess seam, never suppressing) + ritual wrap-record step`
**Branch:** `bellows-wt/560`

## Diff scope (Step 1)

| File | Lines | Change |
|---|---|---|
| hooks/eluvian/wrap_check.py | +62 | `_tuyere_checkout()`, `_session_wraps_today()`, R2 registry print block in `check()` |
| hooks/commands/wrap.md | +7 | Step 5 (Record the wrap) inserted after Y4 anchor |
| tests/test_wrap_r2_registry.py | +185 | New: 7 tests (6 seam + 1 never-suppress) |
| requirements.txt | +1 | `pytest` pin |

## Full test suite

**Result: 1483 passed, 0 failed, 1 warning (50.93s)**

Full verbose pytest output: `r2-wiring-pytest-2026-08-26.txt` (1498 lines).

## Pre-existing wrap test files (unchanged)

```
.venv/bin/python -m pytest tests/test_wrap_hooks.py tests/test_wrap_3b_keyed.py tests/test_wrap_receipts.py tests/test_wrap_sentinel.py -q
115 passed, 1 warning in 6.01s
```

All four files green, unchanged by the Step 1 diff.

## R2 registry tests (test_wrap_r2_registry.py)

```
tests/test_wrap_r2_registry.py::TestSessionWrapsToday::test_today_rows_returned_yesterday_filtered PASSED
tests/test_wrap_r2_registry.py::TestSessionWrapsToday::test_empty_output_returns_empty_list PASSED
tests/test_wrap_r2_registry.py::TestSessionWrapsToday::test_no_wraps_message_returns_empty_list PASSED
tests/test_wrap_r2_registry.py::TestSessionWrapsToday::test_nonzero_exit_returns_none PASSED
tests/test_wrap_r2_registry.py::TestSessionWrapsToday::test_timeout_returns_none PASSED
tests/test_wrap_r2_registry.py::TestSessionWrapsToday::test_missing_checkout_returns_none PASSED
tests/test_wrap_r2_registry.py::TestNeverSuppressPositivePrint::test_fails_equal_and_registry_line_presence PASSED
7 passed, 1 warning in 1.95s
```

## Never-suppress test (test 6) — detailed

Test `TestNeverSuppressPositivePrint::test_fails_equal_and_registry_line_presence` (line 142) verifies:

1. `check(session_id=None, caller="debt")` returns **identical** `fails` lists whether `_session_wraps_today` returns rows or None
2. `len(fails_with) > 0` — confirms debt was actually detected (non-vacuous test)
3. `"[R2/registry]"` appears in stdout when rows are present
4. The registry row text appears verbatim in stdout
5. `"[R2/registry]"` is absent from stdout when `_session_wraps_today` returns None

**Conclusion:** The `fails` list is never modified by the registry seam. The registry line is purely informational stdout output.

## Fail-open branches exercised

| Branch | Test | Return | Demonstrated |
|---|---|---|---|
| Missing checkout | `test_missing_checkout_returns_none` | None | ✅ |
| Nonzero exit | `test_nonzero_exit_returns_none` | None | ✅ |
| Timeout | `test_timeout_returns_none` | None | ✅ |
| Empty output | `test_empty_output_returns_empty_list` | `[]` | ✅ |
| "no session wraps" msg | `test_no_wraps_message_returns_empty_list` | `[]` | ✅ |
| Today filter | `test_today_rows_returned_yesterday_filtered` | `[1 row]` | ✅ |

## A2 probe: tuyere checkout resolution

```
$ python3 -c "from hooks.eluvian.wrap_check import _tuyere_checkout; print(_tuyere_checkout())"
/Users/marklehn/Developer/tuyere
```

**Resolution:** `~/Developer/tuyere` candidate resolved (second in the Y6 priority order). The registry read is ACTIVE on this machine.

## A2 probe: wrap_check debt mode

```
$ python3 hooks/eluvian/wrap_check.py "" debt
[2r/receipts] SKIPPED (blocking arm) — no session_id provided; receipt check requires session context.
SESSION WRAP INCOMPLETE — the following steps are not verifiably done:

  ✗ [1/project] bellows: 1 commit(s) not pushed — push bellows.
  ✗ [2/bellows] 1 uncommitted file(s) under verdicts/resolved/ — commit consumed verdicts.
  ✗ [2/bellows] 1 commit(s) not pushed — push bellows.
  ✗ [3/root] bellows gitlink is uncommitted — `git add bellows` and commit the bump.

Complete these, then this lock clears automatically.
Exit code: 1
```

**Observed:** Debt exists (4 fails) but no `[R2/registry]` line printed — because `_session_wraps_today()` returned an empty list (no wraps recorded today in the registry). This is correct: the information line prints only when `fails` is non-empty AND `rows` is non-empty. The tuyere checkout resolves, the CLI runs, the registry is queried — the path is live but today has no wrap records yet.

## wrap.md step 5 positioning

```
line 98:   commit/push half is N/A.
line 99: 5. **Record the wrap (R2)** — from a tuyere checkout with DB access:
line 107: Use the current model's `Co-Authored-By:` trailer.
```

Step 5 sits correctly between the Y4 anchor (line 98: `commit/push half is N/A.`) and the trailer line (line 107: `Use the current model's`). Step numbering intact.

## py_compile

```
$ python3 -m py_compile hooks/eluvian/wrap_check.py
OK (no output — clean compile)
```

## Code structure verification

| Check | Expected | Observed |
|---|---|---|
| `caller == "debt"` gate (R2 block) | Strict — not the `or not session_id` arm | Line 269: `if caller == "debt" and fails:` — correct |
| `return fails` count | 1 | Line 279: single occurrence — correct |
| R2 block position | Before `return fails` | Lines 269–278, return at 279 — correct |
| Subprocess never in stop path | R2 gate is `caller == "debt"` only | Confirmed — stop calls never reach the registry code |

## Verification Table

| # | Claim | Method | Status |
|---|---|---|---|
| 1 | Full test suite green | `pytest --tb=long -v`: 1483 passed, 0 failed | ✅ |
| 2 | Four pre-existing wrap test files unchanged and green | `pytest` on the 4 files: 115 passed | ✅ |
| 3 | R2 registry tests (7) all pass | `pytest tests/test_wrap_r2_registry.py -v`: 7 passed | ✅ |
| 4 | Never-suppress test proves fails-list equality | Test asserts `fails_with == fails_without` and `len > 0` | ✅ |
| 5 | Registry line appears in stdout only when rows present | Test asserts `[R2/registry]` in/out of capsys | ✅ |
| 6 | Fail-open: at least one None branch exercised | Tests 4–6: timeout, nonzero exit, missing checkout all → None | ✅ |
| 7 | wrap.md step 5 between Y4 anchor and trailer | Lines 98→99→107 verified | ✅ |
| 8 | py_compile clean | No errors | ✅ |
| 9 | Tuyere checkout resolves on this machine | `~/Developer/tuyere` resolved | ✅ |
| 10 | Debt mode: registry line absent when no wraps today | Live run shows 4 fails, no `[R2/registry]` line | ✅ |
| 11 | R2 gate strictly `caller == "debt"` (not stop path) | Line 269 confirmed | ✅ |
| 12 | `return fails` is single exit point | Line 279 is the only occurrence | ✅ |

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/560/knowledge/research/
Files verified: 2
```
