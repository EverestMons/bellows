# QA Report — Verdict Directory Validator

**Date:** 2026-05-12
**Plan:** `parallel-1-executable-verdict-directory-validator-2026-05-12.md`
**Dev Commit:** `30964f7`
**Agent:** Bellows QA
**Step:** 2

---

## Verification Table

| # | Check | Present | Content Filled | Evidence |
|---|---|---|---|---|
| 1 | `_scan_misplaced_verdicts` function exists with correct filter logic | ✅ | ✅ | `bellows.py:1050-1071` — `fname.startswith("verdict-") and fname.endswith(".md") and not fname.startswith("verdict-request-")` |
| 2 | `_consume_verdicts` invokes scan BEFORE resolved-directory loop | ✅ | ✅ | `bellows.py:1075-1076` — scan called at line 1076, resolved-dir loop starts at line 1078 |
| 3 | Module-level `_NOTIFIED_MISPLACED` set declared | ✅ | ✅ | `bellows.py:25` — `_NOTIFIED_MISPLACED: set[tuple[str, str]] = set()` |
| 4 | `MISPLACED_VERDICT_SCAN_VERBOSE` constant declared | ✅ | ✅ | `bellows.py:26` — `MISPLACED_VERDICT_SCAN_VERBOSE = False` |
| 5 | 7 new tests in `tests/test_misplaced_verdicts.py` with exact function names | ✅ | ✅ | All 7 tests verified — names match Step 1 spec, assertions match test name claims |
| 6 | Targeted `pytest tests/test_misplaced_verdicts.py -v` — all 7 pass | ✅ | ✅ | 7 passed, 0 failed |
| 7 | Regression `pytest tests/test_bellows.py tests/test_consume_verdicts.py -v` — no regressions | ✅ | ✅ | 110 passed, 0 failed |
| 8 | Full suite `pytest --tb=short` — only pre-existing failures | ✅ | ✅ | 305 passed, 2 failed (`test_run_step_timeout` pre-existing + `test_server_respond` port collision — environment-specific) |
| 9 | Behavioral spot-check: REPL mixed-files test | ✅ | ✅ | `evidence/verdict-directory-validator-2026-05-12/repl-mixed-files-spot-check.txt` — misplaced triggers WARN, request file silent |

---

## Test Coverage Summary

| Function | Test Coverage |
|---|---|
| `_scan_misplaced_verdicts` — verdict file detection | `test_warns_on_verdict_in_pending` |
| `_scan_misplaced_verdicts` — verdict-request exclusion | `test_ignores_verdict_request_files` |
| `_scan_misplaced_verdicts` — non-.md exclusion | `test_ignores_non_md_files` |
| `_scan_misplaced_verdicts` — Pushover dedup | `test_pushover_deduped_per_file` |
| `_scan_misplaced_verdicts` — Pushover failure resilience | `test_pushover_failure_swallowed` |
| `_consume_verdicts` → `_scan_misplaced_verdicts` integration | `test_invoked_from_consume_verdicts` |
| `_scan_misplaced_verdicts` — empty directory | `test_empty_pending_directory` |

---

## Check 5 — Test Assertion Detail

1. **test_scan_misplaced_verdicts_warns_on_verdict_in_pending** — writes `verdict-some-slug-step-1.md`, asserts `[WARN]` in stdout, filename in output, `expected location: verdicts/resolved/` in output, `notifier.push` called exactly once with `"Bellows — Misplaced Verdict"` in title.
2. **test_scan_misplaced_verdicts_ignores_verdict_request_files** — writes `verdict-request-some-slug-step-1.md`, asserts no `[WARN]`, push not called.
3. **test_scan_misplaced_verdicts_ignores_non_md_files** — writes `verdict-something.txt`, asserts no `[WARN]`, push not called.
4. **test_scan_misplaced_verdicts_pushover_deduped_per_file** — writes misplaced file, calls scan twice, asserts push called exactly once.
5. **test_scan_misplaced_verdicts_pushover_failure_swallowed** — monkeypatches push to raise `RuntimeError`, asserts scan completes normally, WARN still fires.
6. **test_scan_misplaced_verdicts_invoked_from_consume_verdicts** — sets up temp verdicts directory with misplaced file, patches `BELLOWS_ROOT`, calls `_consume_verdicts()`, asserts WARN and push fire.
7. **test_scan_misplaced_verdicts_empty_pending_directory** — empty pending dir, asserts no WARN, no push, no errors.

All assertions match test name claims.

---

## Check 8 — Full Suite Note

Two failures in full suite:
- `test_run_step_timeout` — pre-existing, documented in dev log
- `test_server_respond` — port 15432 in use (environment-specific, not a regression from this change)

---

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/verdict-directory-validator-2026-05-12/
Files verified: 1
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 9 deliverable checks for the verdict directory validator. All code checks pass (filter logic, ordering, constants, test names/assertions). All test runs pass (7/7 targeted, 110/110 regression, 305/307 full suite with only pre-existing + environment failures). Behavioral spot-check confirms correct discrimination between misplaced verdict files and legitimate request files.

### Files Deposited
- `bellows/knowledge/qa/verdict-directory-validator-qa-2026-05-12.md` — this QA report
- `bellows/knowledge/qa/evidence/verdict-directory-validator-2026-05-12/repl-mixed-files-spot-check.txt` — REPL spot-check output

### Files Created or Modified (Code)
- `bellows/PROJECT_STATUS.md` — appended 2026-05-12 entry for this ship

### Decisions Made
- Accepted `test_server_respond` failure as environment-specific (port collision), not a regression

### Flags for CEO
- REMINDER: restart Bellows daemon to load the directory validator fix

### Flags for Next Step
- None
