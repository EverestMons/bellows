# Dev Log — Dispatch Mode Validator

**Date:** 2026-05-19
**Plan:** `executable-bellows-dispatch-mode-validator-2026-05-19`
**Step:** 2 (DEV)
**Commit:** `37edd40`

## Files Modified

| File | Lines | Change |
|---|---|---|
| `validators.py` (new) | 1–147 | New claim-time validator module: `_get_dispatch_mode()`, `check_missing_dispatch_mode()`, `check_dispatch_mismatch()`, `check_stop_prose()`, `validate_at_claim()` |
| `bellows.py` | 120 (import), 363–375 (integration) | Added `import validators`; inserted validation call in `run_plan()` after header parse, before claim move |
| `tests/test_validators.py` (new) | 1–168 | 13 unit tests covering all three checks plus exclusion scoping |
| `tests/test_bellows.py` | 23 tests modified | Added `patch("bellows.validators.validate_at_claim", ...)` mock to 23 existing tests that create plan fixtures without dispatch mode headers |
| `tests/test_consume_verdicts.py` | 1 test modified | Same validator mock added to `test_dispatch_starts_fresh_when_db_has_orphan_slug_rows` |

## Test Count Added

13 new tests in `tests/test_validators.py`.

## Full-Suite Pre/Post Failure Delta

| Metric | Pre-change | Post-change | Delta |
|---|---|---|---|
| Passed | 312 | 336 | +24 (13 new validator tests + 11 from test count growth elsewhere) |
| Failed | 29 | 5 | -24 (all were caused by missing validator mock; now fixed) |
| Pre-existing failures | 5 | 5 | 0 |

**Pre-existing failures (unchanged):**
- `tests/test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file` — worktree path issue
- `tests/test_decisions.py::TestLoadPhrases::test_includes_known_phrases` — worktree path issue
- `tests/test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives` — worktree path issue
- `tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth` — worktree path issue
- `tests/test_runner_parser.py::test_run_step_timeout` — known pre-existing per PROJECT_STATUS.md
