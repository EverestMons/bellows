# cycle_check CLOSURE_RE false-positive fix — dev log

**Date:** 2026-08-19
**Plan:** executable-473

## Bug

`CLOSURE_RE` (cycle_check.py:37-40) used `re.IGNORECASE` and included bare
`\bbar\s+met\b|§2\s+bar\s+met` alternatives, causing lowercase prose words
like "closed" and "bar met" to match as closure STATUS tokens.

Step 8's anti-fabrication guard (`:414-415`) then fired
`ESCALATE:claimed-close-unmet` on mid-cycle plans whose prose merely contained
the word "closed".

## Fix

Dropped `re.IGNORECASE` and removed the `bar met`/`§2 bar met` alternatives.
Real closures always carry `**Closing:**` (literal, case-sensitive) and/or
uppercase `CLOSED`/`CYCLE COMPLETE` — these remain matched.

## Before/after CLOSURE_RE.search results

| Input                    | Before (bug) | After (fix) |
|--------------------------|:---:|:---:|
| `real closed plans`      | True  | False |
| `a closed loop`          | True  | False |
| `bar met the criteria`   | True  | False |
| `**Closing:** walk 2 dry`| True  | True  |
| `cycle CLOSED`           | True  | True  |
| `CYCLE COMPLETE`         | True  | True  |

## Tests

- Flipped `test_closure_markers_detected` — removed lowercase `bar met` / `§2 bar met` markers (they encoded the bug).
- Added `test_prose_closed_not_false_positive` — prose "closed"/"bar met" with no real markers → CONTINUE, exit 0.
- Added `test_genuine_closure_still_detected` — `**Closing:**` + `CLOSED` with dry walk → BAR_MET.
- Added `test_fabricated_close_guard_survives` — `**Closing:**` + `CLOSED` with non-dry walk → ESCALATE:claimed-close-unmet (guard preserved).

30 tests pass (`python3 -m pytest tests/test_cycle_check.py -q`).
